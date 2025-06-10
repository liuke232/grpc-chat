@echo off
chcp 65001 >nul

REM 聊天服务器启动脚本 (Windows)

echo 🚀 启动 gRPC 聊天服务器...

REM 检查是否在项目根目录
if not exist "pyproject.toml" (
    echo ❌ 错误: 请在项目根目录运行此脚本
    pause
    exit /b 1
)

REM 检查虚拟环境是否存在
if not exist ".venv" (
    echo 📦 虚拟环境不存在，正在创建...
    uv sync
)

REM 检查 gRPC 代码是否存在
if not exist "grpc_chat\chat_pb2.py" (
    echo 🔧 生成 gRPC 代码...
    call .venv\Scripts\activate.bat
    python -m grpc_tools.protoc ^
        --proto_path=grpc_chat/proto ^
        --python_out=grpc_chat ^
        --grpc_python_out=grpc_chat ^
        grpc_chat/proto/chat.proto
)

REM 启动服务器
echo 🌟 服务器启动中...
uv run python -m grpc_chat.start_server %* 