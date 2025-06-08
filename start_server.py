#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
聊天服务器启动脚本
"""

import sys
import os
import argparse

# 确保可以导入本地模块
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

if __name__ == '__main__':
    try:
        from server import serve
        
        # 创建命令行参数解析器
        parser = argparse.ArgumentParser(description='启动聊天服务器')
        parser.add_argument('--host', type=str, default='[::]',
                          help='监听地址 (默认: [::], 表示所有IPv4和IPv6地址)')
        parser.add_argument('--port', type=int, default=50051,
                          help='监听端口 (默认: 50051)')
        
        # 解析命令行参数
        args = parser.parse_args()
        
        print("🚀 正在启动聊天服务器...")
        serve(args.host, args.port)
    except ImportError as e:
        print(f"❌ 导入模块失败: {e}")
        print("请确保已安装所有依赖: pip install -r requirements.txt")
    except KeyboardInterrupt:
        print("\n👋 服务器已停止")
    except Exception as e:
        print(f"❌ 服务器启动失败: {e}") 