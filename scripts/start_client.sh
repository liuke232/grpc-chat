#!/bin/bash

# 聊天客户端启动脚本

echo "🖥️ 启动 gRPC 聊天客户端..."

# 检查是否在项目根目录
if [ ! -f "pyproject.toml" ]; then
    echo "❌ 错误: 请在项目根目录运行此脚本"
    exit 1
fi

# 检查虚拟环境是否存在
if [ ! -d ".venv" ]; then
    echo "📦 虚拟环境不存在，正在创建..."
    uv sync
fi

# 检查 gRPC 代码是否存在
if [ ! -f "grpc_chat/chat_pb2.py" ]; then
    echo "🔧 生成 gRPC 代码..."
    source .venv/bin/activate
    python -m grpc_tools.protoc \
        --proto_path=grpc_chat/proto \
        --python_out=grpc_chat \
        --grpc_python_out=grpc_chat \
        grpc_chat/proto/chat.proto
fi

# 启动客户端
echo "🌟 客户端启动中..."
uv run python -m grpc_chat.start_client_gui "$@" 