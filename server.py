#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import grpc
import threading
import time
import queue
import argparse
from concurrent import futures
from typing import Dict, Set, Iterator, Any
import chat_pb2
import chat_pb2_grpc


class StreamHandler:
    """处理单个用户的流连接"""
    def __init__(self, user_name: str, room_id: str):
        self.user_name = user_name
        self.room_id = room_id
        self.message_queue = queue.Queue()
        self.active = True
        
    def send_message(self, message):
        """向用户发送消息"""
        if self.active:
            try:
                self.message_queue.put(message, block=False)
            except queue.Full:
                print(f"[WARNING] 用户 {self.user_name} 的消息队列已满")
    
    def get_messages(self):
        """获取待发送的消息生成器"""
        while self.active:
            try:
                message = self.message_queue.get(timeout=0.5)
                if message is None:  # 停止信号
                    break
                yield message
            except queue.Empty:
                continue
            except Exception as e:
                print(f"[ERROR] 处理用户 {self.user_name} 消息时出错: {e}")
                break
    
    def stop(self):
        """停止处理消息"""
        self.active = False
        self.message_queue.put(None)


class ChatServer(chat_pb2_grpc.ChatServiceServicer):
    def __init__(self):
        # 预定义的聊天室
        self.rooms = {
            "general": {"handlers": {}, "max_capacity": 20},
            "tech": {"handlers": {}, "max_capacity": 20}, 
            "gaming": {"handlers": {}, "max_capacity": 20},
            "random": {"handlers": {}, "max_capacity": 20}
        }
        # 全局用户名集合，确保唯一性
        self.global_users: Set[str] = set()
        # 线程锁
        self.lock = threading.Lock()
        
    def ListRooms(self, request, context):
        """获取房间列表 (一元RPC)"""
        with self.lock:
            rooms_info = []
            for room_id, room_data in self.rooms.items():
                room_info = chat_pb2.RoomInfo(
                    room_id=room_id,
                    participant_count=len(room_data["handlers"])
                )
                rooms_info.append(room_info)
            
            response = chat_pb2.ListRoomsResponse(rooms=rooms_info)
            print(f"[INFO] 房间列表请求：返回 {len(rooms_info)} 个房间")
            return response
    
    def Chat(self, request_iterator, context):
        """聊天双向流RPC"""
        handler = None
        user_left = False
        user_name = None
        room_id = None
        try:
            # 必须第一个消息是 join_request
            first_message = next(request_iterator)
            if not first_message.HasField("join_request"):
                # 非法连接，直接关闭
                return
            join_req = first_message.join_request
            user_name = join_req.user_name
            room_id = join_req.room_id

            # 校验房间和容量
            success, message = self._handle_join_request(user_name, room_id)
            if success:
                handler = StreamHandler(user_name, room_id)
                with self.lock:
                    self.rooms[room_id]["handlers"][user_name] = handler
                join_response = chat_pb2.JoinResponse(success=True, message=message)
                join_msg = chat_pb2.ServerMessage(join_response=join_response)
                handler.send_message(join_msg)
                self._broadcast_user_joined(user_name, room_id)
                print(f"[INFO] 用户 {user_name} 成功加入房间 {room_id}")
            else:
                handler = StreamHandler(user_name, "")
                join_response = chat_pb2.JoinResponse(success=False, message=message)
                join_msg = chat_pb2.ServerMessage(join_response=join_response)
                handler.send_message(join_msg)
                handler.stop()
                print(f"[WARNING] 用户 {user_name} 加入房间 {room_id} 失败: {message}")
                return

            # 后续消息处理
            def process_client_messages():
                nonlocal handler, user_left
                try:
                    for client_message in request_iterator:
                        if client_message.HasField("chat_message"):
                            if handler and handler.active:
                                chat_msg = client_message.chat_message
                                print(f"[INFO] 房间 {handler.room_id} 中的用户 {handler.user_name} 发送消息: {chat_msg.text}")
                                self._broadcast_chat_message(handler.user_name, handler.room_id, chat_msg.text)
                            else:
                                print(f"[ERROR] 收到聊天消息但用户未正确加入房间")
                        elif client_message.HasField("leave_request"):
                            if handler and handler.active:
                                leave_req = client_message.leave_request
                                print(f"[INFO] 用户 {leave_req.user_name} 请求离开房间 {leave_req.room_id}")
                                self._handle_user_disconnect(leave_req.user_name, leave_req.room_id, remove_from_global=False)
                                user_left = True
                                handler.stop()
                                return
                except Exception as e:
                    print(f"[ERROR] 处理客户端消息时出错: {e}")
            client_thread = threading.Thread(target=process_client_messages)
            client_thread.daemon = True
            client_thread.start()
            for message in handler.get_messages():
                yield message
        except Exception as e:
            print(f"[ERROR] 聊天流异常: {e}")
        finally:
            # 在连接断开时，从全局用户集合中移除用户名
            with self.lock:
                self.global_users.discard(user_name)
                print(f"[INFO] 用户 {user_name} 已从全局用户集合中移除")
            
            if handler and handler.room_id and handler.user_name and not user_left:
                with self.lock:
                    if (handler.room_id in self.rooms and 
                        handler.user_name in self.rooms[handler.room_id]["handlers"]):
                        self._handle_user_disconnect(handler.user_name, handler.room_id, remove_from_global=False)
                        print(f"[INFO] 用户 {handler.user_name} 离开房间 {handler.room_id}")
    
    def _handle_join_request(self, user_name: str, room_id: str) -> tuple[bool, str]:
        """处理加入房间请求"""
        with self.lock:
            # 检查房间是否存在
            if room_id not in self.rooms:
                return False, f"房间 '{room_id}' 不存在"
            # 检查房间是否已满
            room = self.rooms[room_id]
            if len(room["handlers"]) >= room["max_capacity"]:
                return False, f"房间 '{room_id}' 已满 ({room['max_capacity']}/{room['max_capacity']})"
            return True, f"欢迎来到房间 '{room_id}'！当前在线人数: {len(room['handlers']) + 1}"
    
    def _broadcast_user_joined(self, new_user: str, room_id: str):
        """广播用户加入通知"""
        with self.lock:
            if room_id in self.rooms:
                # 获取当前房间人数（包括新加入的用户）
                current_count = len(self.rooms[room_id]["handlers"])
                notification = chat_pb2.UserJoinedNotification(
                    user_name=new_user,
                    current_count=current_count
                )
                server_message = chat_pb2.ServerMessage(user_joined=notification)
                
                # 发送给房间内的所有其他用户（不包括刚加入的用户）
                for user_name, handler in self.rooms[room_id]["handlers"].items():
                    if user_name != new_user:
                        handler.send_message(server_message)
    
    def _broadcast_chat_message(self, sender: str, room_id: str, text: str):
        """广播聊天消息"""
        with self.lock:
            if room_id in self.rooms:
                timestamp = int(time.time())
                broadcast_msg = chat_pb2.BroadcastMessage(
                    sender_name=sender,
                    text=text,
                    timestamp=timestamp
                )
                server_message = chat_pb2.ServerMessage(broadcast=broadcast_msg)
                
                # 发送给房间内的所有用户（包括发送者）
                for user_name, handler in list(self.rooms[room_id]["handlers"].items()):
                    handler.send_message(server_message)
    
    def _handle_user_disconnect(self, user_name: str, room_id: str, remove_from_global: bool = True):
        """处理用户断开连接"""
        with self.lock:
            self._remove_user_from_room(user_name, room_id, remove_from_global)
            self._broadcast_user_left(user_name, room_id)
    
    def _remove_user_from_room(self, user_name: str, room_id: str, remove_from_global: bool = True):
        """从房间移除用户"""
        if room_id in self.rooms and user_name in self.rooms[room_id]["handlers"]:
            handler = self.rooms[room_id]["handlers"][user_name]
            handler.stop()
            del self.rooms[room_id]["handlers"][user_name]
            # 只在需要时从全局用户集合中移除用户
            if remove_from_global:
                self.global_users.discard(user_name)
                print(f"[INFO] 用户 {user_name} 已从全局用户集合中移除")
    
    def _broadcast_user_left(self, left_user: str, room_id: str):
        """广播用户离开通知"""
        if room_id in self.rooms:
            # 获取当前房间人数（不包括离开的用户）
            current_count = len(self.rooms[room_id]["handlers"])
            notification = chat_pb2.UserLeftNotification(
                user_name=left_user,
                current_count=current_count
            )
            server_message = chat_pb2.ServerMessage(user_left=notification)
            
            # 发送给房间内的剩余用户
            for user_name, handler in list(self.rooms[room_id]["handlers"].items()):
                handler.send_message(server_message)

    def CheckUsername(self, request, context):
        """校验用户名唯一性"""
        user_name = request.user_name
        with self.lock:
            # 检查全局用户名集合
            if user_name in self.global_users:
                return chat_pb2.CheckUsernameResponse(available=False, message=f"用户名 '{user_name}' 已被占用")
            # 用户名可用，立即添加到全局集合
            self.global_users.add(user_name)
            return chat_pb2.CheckUsernameResponse(available=True, message="用户名可用")


def serve(host: str = '[::]', port: int = 50051):
    """启动聊天服务器
    
    Args:
        host: 监听地址，默认为 '[::]'（所有IPv4和IPv6地址）
        port: 监听端口，默认为 50051
    """
    # 创建gRPC服务器
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    
    # 添加服务到服务器
    chat_service = ChatServer()
    chat_pb2_grpc.add_ChatServiceServicer_to_server(chat_service, server)
    
    # 监听地址和端口
    listen_addr = f'{host}:{port}'
    server.add_insecure_port(listen_addr)
    
    # 启动服务器
    server.start()
    print(f"🚀 聊天服务器已启动，监听地址: {listen_addr}")
    print("📋 可用房间: general, tech, gaming, random")
    print("👥 每个房间最大容量: 20 人")
    print("⌨️  按 Ctrl+C 停止服务器\n")
    
    try:
        server.wait_for_termination()
    except KeyboardInterrupt:
        print("\n⏹️  正在关闭服务器...")
        server.stop(0)
        print("✅ 服务器已关闭")


if __name__ == '__main__':
    # 创建命令行参数解析器
    parser = argparse.ArgumentParser(description='启动聊天服务器')
    parser.add_argument('--host', type=str, default='[::]',
                      help='监听地址 (默认: [::], 表示所有IPv4和IPv6地址)')
    parser.add_argument('--port', type=int, default=50051,
                      help='监听端口 (默认: 50051)')
    
    # 解析命令行参数
    args = parser.parse_args()
    
    # 启动服务器
    serve(args.host, args.port) 