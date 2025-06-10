# grpc-chat: 分布式在线聊天系统

这是一个基于 Python 和 gRPC 的分布式在线聊天系统，支持多房间实时聊天功能。

## 🌟 功能特性

- 🏠 **多房间支持**: 预设4个聊天室（general, tech, gaming, random）
- 👥 **用户管理**: 唯一用户名验证，房间容量限制（20人/房间）
- 💬 **实时通信**: 基于 gRPC 双向流的实时消息传递
- 🔔 **系统通知**: 用户加入/离开房间通知
- 🖥️ **图形界面**: 美观的 GUI 用户界面
- 🔧 **灵活配置**: 支持通过命令行参数配置服务器地址和端口
- 📦 **现代化管理**: 使用 uv 进行依赖管理和项目构建

## 🛠️ 技术栈

- **语言**: Python 3.8.1+
- **包管理**: uv (现代Python包管理器)
- **通信框架**: gRPC
- **数据序列化**: Protocol Buffers (Protobuf)
- **GUI框架**: Tkinter
- **架构**: 客户端/服务端

## 📦 环境要求

- Python 3.8.1 或更高版本
- uv (现代Python包管理器)
- 支持 Tkinter 的系统环境

### 安装 uv

```bash
# Linux/macOS
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# 或者使用 pip
pip install uv
```

## 🚀 快速开始

### 1. 克隆项目

```bash
git clone https://github.com/liuke232/grpc-chat.git
cd grpc-chat
```

### 2. 安装依赖

```bash
# 使用 uv 安装项目依赖
uv sync

# 或者仅安装服务端依赖（如果只需要运行服务端）
uv sync --no-dev
```

### 3. 生成 gRPC 代码

```bash
# 激活虚拟环境并生成 gRPC 代码
source .venv/bin/activate
python -m grpc_tools.protoc --proto_path=grpc_chat/proto --python_out=grpc_chat --grpc_python_out=grpc_chat grpc_chat/proto/chat.proto
```

### 4. 启动服务器

基本用法：
```bash
# 方式1: 使用启动脚本（推荐）
./scripts/start_server.sh

# 方式2: 使用 uv run
uv run python -m grpc_chat.start_server

# 方式3: 激活虚拟环境后运行
source .venv/bin/activate
python -m grpc_chat.start_server
```

高级用法（指定监听地址和端口）：
```bash
# 使用启动脚本
./scripts/start_server.sh --host 0.0.0.0 --port 8080

# 使用 uv run
uv run python -m grpc_chat.start_server --host 0.0.0.0 --port 8080
```

参数说明：
- `--host`: 监听地址（默认: [::]，表示所有IPv4和IPv6地址）
- `--port`: 监听端口（默认: 50051）

### 5. 启动客户端

基本用法：
```bash
# 方式1: 使用启动脚本（推荐）
./scripts/start_client.sh

# 方式2: 使用 uv run
uv run python -m grpc_chat.start_client_gui

# 方式3: 激活虚拟环境后运行
source .venv/bin/activate
python -m grpc_chat.start_client_gui
```

高级用法（指定服务器地址和端口）：
```bash
# 使用启动脚本
./scripts/start_client.sh --host 192.168.1.100 --port 8080

# 使用 uv run
uv run python -m grpc_chat.start_client_gui --host 192.168.1.100 --port 8080
```

参数说明：
- `--host`: 服务器地址（默认: localhost）
- `--port`: 服务器端口（默认: 50051）

### 6. 查看帮助信息

服务器帮助：
```bash
uv run python -m grpc_chat.start_server --help
```

客户端帮助：
```bash
uv run python -m grpc_chat.start_client_gui --help
```

## 🏗️ 项目结构

```
grpc-chat/
├── pyproject.toml          # 项目配置和依赖管理
├── uv.lock                 # uv 锁定文件
├── Makefile                # 开发任务自动化脚本
├── .venv/                  # 虚拟环境目录
├── grpc_chat/              # 主包目录
│   ├── __init__.py         # 包初始化文件
│   ├── proto/              # Protocol Buffers 定义
│   │   └── chat.proto      # gRPC 服务定义
│   ├── chat_pb2.py         # 生成的 Protobuf 消息类
│   ├── chat_pb2_grpc.py    # 生成的 gRPC 服务类
│   ├── server.py           # 聊天服务器实现
│   ├── client.py           # GUI图形界面聊天客户端
│   ├── start_server.py     # 服务器启动脚本
│   └── start_client_gui.py # GUI客户端启动脚本
├── scripts/                # 便捷启动脚本
│   ├── start_server.sh     # 服务器启动脚本
│   └── start_client.sh     # 客户端启动脚本
├── .gitignore              # Git 忽略文件
├── LICENSE                 # 许可证文件
└── README.md              # 项目文档
```

## 🛠️ 开发指南

### 使用 Makefile（推荐）

项目提供了 Makefile 来简化常用任务：

```bash
# 查看所有可用命令
make help

# 完整项目设置（安装依赖 + 生成代码）
make setup

# 服务端设置（仅服务端依赖 + 生成代码）
make server-setup

# 安装项目依赖
make install

# 仅安装服务端依赖（无GUI）
make server-install

# 安装开发依赖
make dev-install

# 生成 gRPC 代码
make proto

# 启动服务器
make run-server

# 启动客户端
make run-client

# 格式化代码
make format

# 代码检查
make lint

# 清理生成的文件
make clean
```

### 手动操作

#### 安装开发依赖

```bash
uv sync --extra dev
```

#### 代码格式化

```bash
# 使用 black 格式化代码
uv run black grpc_chat/

# 使用 isort 整理导入
uv run isort grpc_chat/
```

#### 代码检查

```bash
# 使用 flake8 检查代码风格
uv run flake8 grpc_chat/

# 使用 mypy 进行类型检查
uv run mypy grpc_chat/
```

## 📋 使用说明

### 服务端
- 服务端启动后会显示可用房间信息
- 支持多个客户端同时连接
- 实时显示用户加入/离开和消息发送日志
- 使用 `Ctrl+C` 停止服务器
- 可以通过命令行参数配置监听地址和端口

### 客户端

#### GUI图形界面版本
1. **登录窗口**: 
   - 输入用户名（1-20个字母或数字字符）
   - 点击"登录"或按回车
2. **大厅窗口**: 
   - 自动显示房间列表和在线人数
   - 双击房间名或选中后点击"加入选中房间"
   - 点击"刷新房间列表"更新信息
3. **聊天窗口**: 
   - 在输入框输入消息并按回车或点击"发送"
   - 实时显示聊天记录和系统通知
   - 点击"离开房间"返回大厅
   - 点击"清空聊天记录"清除显示内容

## 🎯 核心工作流

### 用户加入聊天
1. 客户端连接服务器并输入用户名
2. 浏览房间列表，选择要加入的房间
3. 服务器验证用户名唯一性和房间容量
4. 成功加入后，通知其他用户并开始聊天

### 消息传递
1. 用户输入消息并发送到服务器
2. 服务器将消息广播给同房间的所有用户
3. 所有客户端实时显示收到的消息

### 用户离开
1. 用户点击"离开房间"或关闭客户端
2. 服务器检测到连接断开
3. 从房间移除用户并通知其他用户

## 🔧 配置说明

### 服务器配置
- **监听地址**: 可通过 `--host` 参数指定（默认: [::]）
- **监听端口**: 可通过 `--port` 参数指定（默认: 50051）
- **房间数量**: 4个预设房间
- **房间容量**: 20人/房间
- **线程池**: 10个工作线程

### 客户端配置
- **服务器地址**: 可通过 `--host` 参数指定（默认: localhost）
- **服务器端口**: 可通过 `--port` 参数指定（默认: 50051）
- **重连**: 目前不支持自动重连
- **消息队列**: 无大小限制

## 🚨 注意事项

1. **用户名唯一性**: 同一时间不能有重复的用户名
2. **房间容量**: 每个房间最多20人
3. **网络连接**: 需要稳定的网络连接
4. **Unicode支持**: 支持中文和特殊字符
5. **GUI要求**: 需要系统支持 Tkinter
6. **Python版本**: 需要 Python 3.8.1 或更高版本
7. **网络配置**: 
   - 确保服务器和客户端使用相同的端口
   - 如果服务器和客户端在不同机器上，需要使用服务器的实际IP地址
   - 确保防火墙允许指定端口的通信

## 🔍 故障排除

### 常见问题

1. **uv 命令未找到**
   - 确保已正确安装 uv
   - 检查 PATH 环境变量是否包含 uv 路径

2. **依赖安装失败**
   - 检查 Python 版本是否符合要求（>=3.8.1）
   - 尝试重新运行 `uv sync`

3. **gRPC 代码生成失败**
   - 确保已激活虚拟环境：`source .venv/bin/activate`
   - 检查 grpcio-tools 是否正确安装

4. **tkinter 模块未找到（客户端）**
   - **Ubuntu/Debian**: `sudo apt-get install python3-tk`
   - **CentOS/RHEL**: `sudo yum install tkinter`
   - **macOS**: 重新安装Python并确保包含tkinter
   - **Windows**: 通常随Python一起安装，如缺失请重新安装Python
   - **服务器环境**: 如果只需要运行服务端，可以忽略此错误

5. **连接失败**
   - 检查服务器是否已启动
   - 确认端口未被占用
   - 检查防火墙设置
   - 验证服务器地址和端口配置是否正确

6. **用户名被占用**
   - 选择不同的用户名
   - 等待之前的连接超时

7. **房间已满**
   - 选择其他房间
   - 等待有用户离开

8. **消息发送失败**
   - 检查网络连接
   - 重新加入房间

9. **GUI相关问题**
   - 确保系统已安装 Python Tkinter
   - 检查 Python 环境是否正确配置

10. **网络连接问题**
    - 使用 `ping` 命令测试服务器可达性
    - 使用 `telnet` 或 `nc` 测试端口连通性
    - 检查服务器和客户端的网络配置是否匹配

## 🔮 扩展功能

可以考虑添加的功能：
- 私聊功能
- 消息历史记录
- 用户头像和状态
- 文件传输
- 房间管理（创建/删除房间）
- 用户权限管理
- 消息加密
- 主题切换
- 消息提醒
- 配置文件支持
- 自动重连机制

## 📄 许可证

MIT License

## 👥 贡献

欢迎提交 Issue 和 Pull Request！
