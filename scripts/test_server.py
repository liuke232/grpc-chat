#!/usr/bin/env python3
"""
测试服务端功能的简单脚本
"""

import sys
import os

# 添加项目根目录到路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

def test_server_import():
    """测试服务端模块导入"""
    try:
        from grpc_chat import ChatServer, serve
        print("✅ 服务端模块导入成功")
        return True
    except Exception as e:
        print(f"❌ 服务端模块导入失败: {e}")
        return False

def test_server_creation():
    """测试服务端创建"""
    try:
        from grpc_chat import ChatServer
        server = ChatServer()
        print("✅ 服务端创建成功")
        return True
    except Exception as e:
        print(f"❌ 服务端创建失败: {e}")
        return False

def main():
    """主测试函数"""
    print("🧪 开始测试服务端功能...")
    
    tests = [
        ("模块导入", test_server_import),
        ("服务端创建", test_server_creation),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n📋 测试: {test_name}")
        if test_func():
            passed += 1
    
    print(f"\n📊 测试结果: {passed}/{total} 通过")
    
    if passed == total:
        print("🎉 所有测试通过！服务端功能正常")
        return 0
    else:
        print("❌ 部分测试失败")
        return 1

if __name__ == '__main__':
    sys.exit(main()) 