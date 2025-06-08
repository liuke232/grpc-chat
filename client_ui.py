#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import grpc
import threading
import time
import queue
import argparse
from datetime import datetime
from typing import Optional
import chat_pb2
import chat_pb2_grpc


class ChatClientGUI:
    def __init__(self, server_address: str = 'localhost', server_port: int = 50051):
        # gRPC 相关
        self.server_address = f'{server_address}:{server_port}'
        self.channel = None
        self.stub = None
        self.user_name = None
        self.current_room = None
        self.connected = False
        self.message_queue = queue.Queue()
        self.chat_active = False
        
        # GUI 消息处理
        self.gui_message_queue = queue.Queue()
        self.message_handler_started = False  # 新增：消息处理线程启动标志
        
    def center_window(self, window, width, height):
        """居中显示窗口"""
        screen_width = window.winfo_screenwidth()
        screen_height = window.winfo_screenheight()
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        window.geometry(f"{width}x{height}+{x}+{y}")
    
    def create_login_window(self):
        """创建登录窗口"""
        self.login_window = tk.Tk()
        self.login_window.title("登录 - 分布式聊天系统")
        self.login_window.resizable(False, False)
        
        # 设置窗口大小和位置
        window_width = 400
        window_height = 300
        self.center_window(self.login_window, window_width, window_height)
        
        # 创建主框架
        main_frame = ttk.Frame(self.login_window, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 标题
        title_label = ttk.Label(main_frame, text="欢迎使用分布式聊天系统", font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # 用户名输入
        ttk.Label(main_frame, text="请输入用户名 (1-20个字母或数字):", 
                 font=("Arial", 10)).grid(row=1, column=0, columnspan=2, sticky=tk.W, pady=(0, 5))
        
        self.username_var = tk.StringVar()
        username_entry = ttk.Entry(main_frame, textvariable=self.username_var, 
                                 font=("Arial", 11), width=30)
        username_entry.grid(row=2, column=0, columnspan=2, pady=(0, 20))
        
        # 登录按钮
        login_button = ttk.Button(main_frame, text="登录", 
                                command=self.handle_login)
        login_button.grid(row=3, column=0, columnspan=2, pady=(0, 10))
        
        # 退出按钮
        quit_button = ttk.Button(main_frame, text="退出", 
                               command=self.quit_application)
        quit_button.grid(row=4, column=0, columnspan=2)
        
        # 绑定回车键
        username_entry.bind('<Return>', lambda e: self.handle_login())
        
        # 设置焦点
        username_entry.focus()
        
        # 关闭窗口事件
        self.login_window.protocol("WM_DELETE_WINDOW", self.quit_application)
    
    def handle_login(self):
        """处理登录请求"""
        username = self.username_var.get().strip()
        
        # 本地校验
        if not username:
            messagebox.showerror("错误", "用户名不能为空")
            return
        if not username.isalnum():
            messagebox.showerror("错误", "用户名只能包含字母和数字")
            return
        if len(username) > 20:
            messagebox.showerror("错误", "用户名长度不能超过20个字符")
            return
        
        try:
            # 每次都新建 channel 和 stub，避免复用旧连接
            if self.channel:
                self.channel.close()
            self.channel = grpc.insecure_channel(self.server_address)
            self.stub = chat_pb2_grpc.ChatServiceStub(self.channel)
            
            # 先校验用户名唯一性
            check_req = chat_pb2.CheckUsernameRequest(user_name=username)
            print(f"check_req: {check_req}")
            check_resp = self.stub.CheckUsername(check_req)
            print(f"check_resp: {check_resp}")
            if not check_resp.available:
                messagebox.showerror("错误", check_resp.message)
                return
            
            self.connected = True
            self.user_name = username
            self.login_window.withdraw()  # 隐藏登录窗口
            self.show_lobby()
        except Exception as e:
            messagebox.showerror("连接错误", f"无法连接到服务器: {e}")
            self.connected = False
    
    def show_lobby(self):
        """显示大厅窗口"""
        self.lobby_window = tk.Toplevel()
        self.lobby_window.title(f"聊天大厅 - {self.user_name}")
        self.lobby_window.resizable(False, False)
        
        # 设置窗口大小和位置
        window_width = 600
        window_height = 400
        self.center_window(self.lobby_window, window_width, window_height)
        
        # 创建主框架
        main_frame = ttk.Frame(self.lobby_window, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 标题
        title_label = ttk.Label(main_frame, 
                              text=f"欢迎, {self.user_name}! 请选择聊天室", 
                              font=("Arial", 14, "bold"))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # 房间列表
        self.room_listbox = tk.Listbox(main_frame, width=40, height=15, 
                                     font=("Arial", 11))
        self.room_listbox.grid(row=1, column=0, columnspan=2, pady=(0, 10))
        self.room_listbox.bind('<Double-Button-1>', lambda e: self.join_selected_room())
        
        # 按钮框架
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=2, column=0, columnspan=2, pady=(0, 10))
        
        # 刷新按钮
        ttk.Button(button_frame, text="刷新列表", 
                  command=self.refresh_rooms).pack(side=tk.LEFT, padx=5)
        
        # 加入按钮
        ttk.Button(button_frame, text="加入房间", 
                  command=self.join_selected_room).pack(side=tk.LEFT, padx=5)
        
        # 退出按钮
        ttk.Button(button_frame, text="退出登录", 
                  command=self.handle_logout).pack(side=tk.LEFT, padx=5)
        
        # 状态标签（新增）
        self.lobby_status_label = ttk.Label(main_frame, text="请选择房间并加入", foreground="blue")
        self.lobby_status_label.grid(row=3, column=0, columnspan=2, pady=(10, 0))
        
        # 关闭窗口事件
        self.lobby_window.protocol("WM_DELETE_WINDOW", self.handle_logout)
        
        # 初始刷新房间列表
        self.refresh_rooms()
    
    def handle_logout(self):
        """处理退出登录"""
        if messagebox.askyesno("确认退出", "确定要退出登录吗？"):
            # 如果用户在聊天室中，先离开房间
            if self.chat_active and self.current_room:
                self.leave_room()
            
            # 关闭大厅窗口
            if self.lobby_window:
                self.lobby_window.destroy()
                self.lobby_window = None
            
            # 重置状态
            self.user_name = None
            self.current_room = None
            self.connected = False
            if self.channel:
                self.channel.close()
                self.channel = None
            
            # 显示登录窗口
            if self.login_window:
                self.login_window.deiconify()  # 显示登录窗口
                self.username_var.set("")  # 清空用户名输入框
    
    def refresh_rooms(self):
        """刷新房间列表"""
        try:
            request = chat_pb2.ListRoomsRequest()
            response = self.stub.ListRooms(request)
            
            # 清空列表
            self.room_listbox.delete(0, tk.END)
            
            # 添加房间信息
            for room in response.rooms:
                room_info = f"🏠 {room.room_id:<12} | 👥 {room.participant_count}/20"
                self.room_listbox.insert(tk.END, room_info)
            
            self.lobby_status_label.config(text=f"已加载 {len(response.rooms)} 个房间", 
                                          foreground="green")
            
        except Exception as e:
            messagebox.showerror("网络错误", f"获取房间列表失败: {e}")
            self.lobby_status_label.config(text=f"刷新失败: {e}", foreground="red")
    
    def join_selected_room(self):
        """加入选中的房间"""
        selection = self.room_listbox.curselection()
        if not selection:
            messagebox.showwarning("选择错误", "请先选择一个房间")
            return
        
        # 解析房间ID
        room_text = self.room_listbox.get(selection[0])
        room_id = room_text.split('|')[0].split('🏠')[1].strip()
        
        self.current_room = room_id
        self.chat_active = True
        
        # 关闭大厅窗口
        self.lobby_window.destroy()
        
        # 开始聊天
        self.start_chat_session()
    
    def start_chat_session(self):
        """开始聊天会话"""
        def client_message_generator():
            """生成客户端消息的生成器"""
            # 首先发送加入请求
            join_request = chat_pb2.JoinRequest(user_name=self.user_name, room_id=self.current_room)
            client_message = chat_pb2.ClientMessage(join_request=join_request)
            yield client_message
            
            # 然后持续发送聊天消息
            while self.chat_active:
                try:
                    message = self.message_queue.get(timeout=0.5)
                    if message is None:  # 停止信号
                        break
                    yield message
                except queue.Empty:
                    continue
        
        def chat_thread():
            """聊天线程"""
            try:
                response_stream = self.stub.Chat(client_message_generator())
                join_success = False
                
                for server_message in response_stream:
                    if server_message.HasField("join_response"):
                        join_resp = server_message.join_response
                        if join_resp.success:
                            join_success = True
                            self.gui_message_queue.put(('join_success', join_resp.message))
                        else:
                            # 新增：用户名被占用等失败时，弹窗提示并返回登录界面
                            def show_login_again():
                                messagebox.showerror("登录失败", join_resp.message)
                                if self.lobby_window:
                                    self.lobby_window.destroy()
                                    self.lobby_window = None
                                if self.chat_window:
                                    self.chat_window.destroy()
                                    self.chat_window = None
                                if self.login_window:
                                    self.login_window.deiconify()
                                    self.username_var.set("")
                            self.gui_message_queue.put(('login_failed', show_login_again))
                            self.chat_active = False
                            break
                            
                    elif server_message.HasField("broadcast"):
                        if join_success:
                            broadcast = server_message.broadcast
                            self.gui_message_queue.put(('message', broadcast))
                            
                    elif server_message.HasField("user_joined"):
                        if join_success:
                            user_joined = server_message.user_joined
                            self.gui_message_queue.put(('user_joined', user_joined))
                            
                    elif server_message.HasField("user_left"):
                        if join_success:
                            user_left = server_message.user_left
                            self.gui_message_queue.put(('user_left', user_left))
                            
            except Exception as e:
                self.gui_message_queue.put(('error', str(e)))
                self.chat_active = False
        
        # 启动聊天线程
        chat_thread_obj = threading.Thread(target=chat_thread)
        chat_thread_obj.daemon = True
        chat_thread_obj.start()
        
        # 创建聊天窗口并启动消息处理
        self.show_chat_window()
    
    def show_chat_window(self):
        """显示聊天窗口"""
        self.chat_window = tk.Tk()
        self.chat_window.title(f"房间: {self.current_room} - {self.user_name}")
        self.chat_window.geometry("600x500")
        self.chat_window.resizable(True, True)
        
        # 居中窗口
        self.center_window(self.chat_window, 600, 500)
        
        # 主框架
        main_frame = ttk.Frame(self.chat_window, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 配置网格权重
        self.chat_window.columnconfigure(0, weight=1)
        self.chat_window.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        # 标题
        title_label = ttk.Label(main_frame, text=f"🎉 房间: {self.current_room}", 
                               font=("Arial", 14, "bold"))
        title_label.grid(row=0, column=0, sticky=tk.W, pady=(0, 10))
        
        # 聊天显示区域
        chat_frame = ttk.LabelFrame(main_frame, text="💬 聊天记录", padding="5")
        chat_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        chat_frame.columnconfigure(0, weight=1)
        chat_frame.rowconfigure(0, weight=1)
        
        # 聊天文本框
        self.chat_text = scrolledtext.ScrolledText(chat_frame, 
                                                  wrap=tk.WORD, 
                                                  font=("Arial", 10),
                                                  state=tk.DISABLED)
        self.chat_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 消息输入框架
        input_frame = ttk.LabelFrame(main_frame, text="💭 发送消息", padding="5")
        input_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        input_frame.columnconfigure(0, weight=1)
        
        # 消息输入框
        self.message_entry = ttk.Entry(input_frame, font=("Arial", 11))
        self.message_entry.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 10))
        self.message_entry.bind('<Return>', self.send_message)
        
        # 发送按钮
        ttk.Button(input_frame, text="发送", 
                  command=self.send_message).grid(row=0, column=1)
        
        # 按钮框架
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=3, column=0)
        
        # 控制按钮
        ttk.Button(button_frame, text="离开房间", 
                  command=self.leave_room).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="清空聊天记录", 
                  command=self.clear_chat).pack(side=tk.LEFT)
        
        # 焦点设置
        self.message_entry.focus()
        
        # 关闭窗口事件
        self.chat_window.protocol("WM_DELETE_WINDOW", self.leave_room)
        
        # 启动消息处理
        self.process_gui_messages()
        
        # 启动主循环
        self.chat_window.mainloop()
    
    def process_gui_messages(self):
        """处理GUI消息队列"""
        if not self.chat_active or not self.chat_window:
            return
            
        try:
            while True:
                msg_type, data = self.gui_message_queue.get_nowait()
                
                if msg_type == 'join_success':
                    self.add_system_message(f"✅ {data}")
                elif msg_type == 'login_failed':
                    data()  # 执行 show_login_again
                    return
                elif msg_type == 'message':
                    timestamp = datetime.fromtimestamp(data.timestamp).strftime("%H:%M:%S")
                    self.add_chat_message(f"[{timestamp}] {data.sender_name}: {data.text}")
                elif msg_type == 'user_joined':
                    self.add_system_message(f"🟢 欢迎 {data.user_name} 加入房间！当前在线人数：{data.current_count} 人")
                elif msg_type == 'user_left':
                    self.add_system_message(f"🔴 {data.user_name} 离开了房间，当前在线人数：{data.current_count} 人")
                    # 如果是自己离开，则停止聊天活动
                    if data.user_name == self.user_name:
                        self.chat_active = False
                        self.message_queue.put(None)  # 发送停止信号
                        return
                elif msg_type == 'error':
                    messagebox.showerror("通信错误", f"聊天过程中出错: {data}")
                    self.leave_room()
                    return
                    
        except queue.Empty:
            pass
        
        # 继续处理消息
        if self.chat_active and self.chat_window:
            self.chat_window.after(100, self.process_gui_messages)
    
    def add_chat_message(self, message):
        """添加聊天消息"""
        if self.chat_text:
            self.chat_text.config(state=tk.NORMAL)
            self.chat_text.insert(tk.END, f"{message}\n")
            self.chat_text.config(state=tk.DISABLED)
            self.chat_text.see(tk.END)
    
    def add_system_message(self, message):
        """添加系统消息"""
        if self.chat_text:
            self.chat_text.config(state=tk.NORMAL)
            self.chat_text.insert(tk.END, f"{message}\n", "system")
            self.chat_text.tag_configure("system", foreground="blue")
            self.chat_text.config(state=tk.DISABLED)
            self.chat_text.see(tk.END)
    
    def send_message(self, event=None):
        """发送消息"""
        if not self.message_entry:
            return
            
        message_text = self.message_entry.get().strip()
        if not message_text:
            return
        
        # 清空输入框
        self.message_entry.delete(0, tk.END)
        
        # 发送消息
        chat_message = chat_pb2.ChatMessage(text=message_text)
        client_message = chat_pb2.ClientMessage(chat_message=chat_message)
        self.message_queue.put(client_message)
    
    def clear_chat(self):
        """清空聊天记录"""
        if self.chat_text:
            self.chat_text.config(state=tk.NORMAL)
            self.chat_text.delete(1.0, tk.END)
            self.chat_text.config(state=tk.DISABLED)
    
    def leave_room(self):
        """离开房间"""
        if self.chat_active and self.current_room:
            # 发送离开请求
            leave_request = chat_pb2.LeaveRequest(user_name=self.user_name, room_id=self.current_room)
            client_message = chat_pb2.ClientMessage(leave_request=leave_request)
            self.message_queue.put(client_message)
            
            # 等待一小段时间确保消息发送
            time.sleep(0.1)
            
            # 不再立即停止聊天活动，而是等待服务器的离开通知
            # 在 process_gui_messages 中处理完离开通知后再停止
            
            if self.chat_window:
                self.chat_window.destroy()
                self.chat_window = None
            
            self.current_room = None
            
            # 返回大厅
            self.show_lobby()
    
    def disconnect_from_server(self):
        """断开与服务器的连接"""
        self.chat_active = False
        if self.channel:
            self.channel.close()
        self.connected = False
    
    def quit_application(self):
        """退出应用程序"""
        try:
            # 首先停止聊天活动
            self.chat_active = False
            self.disconnect_from_server()
            
            # 销毁所有窗口
            windows_to_destroy = []
            if hasattr(self, 'chat_window') and self.chat_window:
                windows_to_destroy.append(self.chat_window)
            if hasattr(self, 'lobby_window') and self.lobby_window:
                windows_to_destroy.append(self.lobby_window)
            if hasattr(self, 'login_window') and self.login_window:
                windows_to_destroy.append(self.login_window)
            
            # 销毁所有窗口
            for window in windows_to_destroy:
                try:
                    window.quit()
                except:
                    pass
                try:
                    window.destroy()
                except:
                    pass
            
            # 清空窗口引用
            self.chat_window = None
            self.lobby_window = None
            self.login_window = None
            
            print("\n👋 客户端已退出")
            print("感谢使用分布式聊天系统！")
            
        except Exception as e:
            print(f"\n⚠️ 退出时发生错误: {e}")
        finally:
            # 确保程序退出
            import sys
            sys.exit(0)
    
    def run(self):
        """运行应用程序"""
        self.create_login_window()
        self.login_window.mainloop()


def main():
    # 创建命令行参数解析器
    parser = argparse.ArgumentParser(description='启动聊天客户端')
    parser.add_argument('--host', type=str, default='localhost',
                      help='服务器地址 (默认: localhost)')
    parser.add_argument('--port', type=int, default=50051,
                      help='服务器端口 (默认: 50051)')
    
    # 解析命令行参数
    args = parser.parse_args()
    
    # 创建并启动GUI客户端
    client = ChatClientGUI(args.host, args.port)
    client.create_login_window()
    client.login_window.mainloop()


if __name__ == '__main__':
    main() 