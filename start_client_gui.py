#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
聊天客户端启动脚本
"""

import sys
import os
import argparse

# 确保可以导入本地模块
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

if __name__ == '__main__':
    try:
        from client_ui import main
        
        # 创建命令行参数解析器
        parser = argparse.ArgumentParser(description='启动聊天客户端')
        parser.add_argument('--host', type=str, default='localhost',
                          help='服务器地址 (默认: localhost)')
        parser.add_argument('--port', type=int, default=50051,
                          help='服务器端口 (默认: 50051)')
        
        # 解析命令行参数
        args = parser.parse_args()
        
        # 启动客户端
        main()
    except ImportError as e:
        print(f"❌ 导入模块失败: {e}")
        print("请确保已安装所有依赖: pip install -r requirements.txt")
        print("注意: 需要tkinter支持")
    except Exception as e:
        print(f"❌ 客户端启动失败: {e}")
        print("如果遇到tkinter相关问题，请确保系统已正确安装Python和tkinter") 