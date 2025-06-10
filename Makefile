.PHONY: help install dev-install server-install clean proto run-server run-client format lint test test-server

# 默认目标
help:
	@echo "可用的命令:"
	@echo "  install        - 安装项目依赖"
	@echo "  server-install - 仅安装服务端依赖（无GUI）"
	@echo "  dev-install    - 安装开发依赖"
	@echo "  proto          - 生成 gRPC 代码"
	@echo "  run-server     - 启动服务器"
	@echo "  run-client     - 启动客户端"
	@echo "  format         - 格式化代码"
	@echo "  lint           - 代码检查"
	@echo "  test           - 运行测试"
	@echo "  test-server    - 测试服务端功能"
	@echo "  clean          - 清理生成的文件"

# 安装项目依赖
install:
	uv sync

# 仅安装服务端依赖（无GUI）
server-install:
	uv sync --no-dev

# 安装开发依赖
dev-install:
	uv sync --extra dev

# 生成 gRPC 代码
proto:
	@echo "生成 gRPC 代码..."
	. .venv/bin/activate && python -m grpc_tools.protoc \
		--proto_path=grpc_chat/proto \
		--python_out=grpc_chat \
		--grpc_python_out=grpc_chat \
		grpc_chat/proto/chat.proto
	@echo "gRPC 代码生成完成"

# 启动服务器
run-server:
	uv run python -m grpc_chat.start_server

# 启动客户端
run-client:
	uv run python -m grpc_chat.start_client_gui

# 格式化代码
format:
	@echo "格式化代码..."
	uv run black grpc_chat/
	uv run isort grpc_chat/
	@echo "代码格式化完成"

# 代码检查
lint:
	@echo "运行代码检查..."
	uv run flake8 grpc_chat/
	uv run mypy grpc_chat/
	@echo "代码检查完成"

# 运行测试
test:
	uv run pytest

# 测试服务端功能
test-server:
	python scripts/test_server.py

# 清理生成的文件
clean:
	@echo "清理生成的文件..."
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	@echo "清理完成"

# 完整设置（安装依赖 + 生成代码）
setup: install proto
	@echo "项目设置完成"

# 服务端设置（仅服务端依赖 + 生成代码）
server-setup: server-install proto
	@echo "服务端设置完成" 