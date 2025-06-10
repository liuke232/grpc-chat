"""
gRPC聊天系统

一个基于Python和gRPC的分布式在线聊天系统，支持多房间实时聊天功能。
"""

import sys
import os

# 添加当前包目录到Python路径，使生成的gRPC代码可以被找到
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

__version__ = "0.1.0"
__author__ = "liuke"
__email__ = "liuke3090@gmail.com"

# 只导入服务端相关模块（无GUI依赖）
from .server import ChatServer, serve

__all__ = ["ChatServer", "serve"]
