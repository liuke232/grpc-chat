#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
聊天客户端启动脚本
"""

import argparse

from grpc_chat.client import main

if __name__ == "__main__":
    try:
        # 创建命令行参数解析器
        parser = argparse.ArgumentParser(description="启动聊天客户端")
        parser.add_argument(
            "--host", type=str, default="localhost", help="服务器地址 (默认: localhost)"
        )
        parser.add_argument(
            "--port", type=int, default=50051, help="服务器端口 (默认: 50051)"
        )
        # 解析命令行参数
        args = parser.parse_args()
        # 启动客户端
        main()
    except Exception as e:
        print(f"❌ 客户端启动失败: {e}")
        print("如果遇到tkinter相关问题，请确保系统已正确安装Python和tkinter")
