#!/usr/bin/env python3
"""
MCP Server Startup Test

测试MCP服务器的启动和基本通信能力
"""

import subprocess
import json
import time
import os
import signal


def test_mcp_server_startup():
    """测试MCP服务器启动"""
    print("🧪 Testing MCP Server Startup...")
    
    # 启动MCP服务器
    process = subprocess.Popen(
        ["python3", "mcp_server.py"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    try:
        # 发送初始化请求
        init_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {
                    "name": "test-client",
                    "version": "1.0.0"
                }
            }
        }
        
        print("发送初始化请求...")
        process.stdin.write(json.dumps(init_request) + "\n")
        process.stdin.flush()
        
        # 读取响应
        response_line = process.stdout.readline()
        if response_line:
            response = json.loads(response_line.strip())
            # MCP响应直接包含结果字段，不在"result"包装器中
            assert "serverInfo" in response, f"初始化响应格式错误: {response}"
            server_info = response["serverInfo"]
            # 测试工具列表请求
            tools_request = {
                "jsonrpc": "2.0",
                "id": 2,
                "method": "tools/list"
            }

            process.stdin.write(json.dumps(tools_request) + "\n")
            process.stdin.flush()

            tools_response_line = process.stdout.readline()
            assert tools_response_line, "工具列表响应超时"
            tools_response = json.loads(tools_response_line.strip())
            assert "tools" in tools_response, f"工具列表请求失败: {tools_response}"
            tools = tools_response["tools"]
            assert isinstance(tools, list), "工具列表格式错误"
            return
    
    except Exception as e:
        print(f"❌ 测试过程中出错: {e}")
        return False
    
    finally:
        # 清理进程
        try:
            process.terminate()
            process.wait(timeout=2)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait()


def test_mcp_server_tool_call():
    """测试MCP服务器工具调用"""
    print("\n🧪 Testing MCP Server Tool Call...")
    
    process = subprocess.Popen(
        ["python3", "mcp_server.py"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    try:
        # 初始化
        init_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {"protocolVersion": "2024-11-05", "capabilities": {}}
        }
        
        process.stdin.write(json.dumps(init_request) + "\n")
        process.stdin.flush()
        init_response = process.stdout.readline()
        
        assert init_response, "初始化失败"
        
        # 工具调用
        tool_request = {
            "jsonrpc": "2.0", 
            "id": 2,
            "method": "tools/call",
            "params": {
                "name": "mail_command_extractor",
                "arguments": {
                    "detection_rules": {
                        "rules": [
                            {
                                "sender": "test@example.com",
                                "subjects": [
                                    {
                                        "title_pattern": "测试",
                                        "content_rules": [
                                            {
                                                "content_pattern": "命令",
                                                "action": {
                                                    "command": "test_command",
                                                    "priority": 10
                                                }
                                            }
                                        ]
                                    }
                                ]
                            }
                        ]
                    },
                    "email_list": {
                        "matched_emails": [
                            {
                                "sender": "test@example.com",
                                "subject": "测试邮件",
                                "content": "这是一个测试命令",
                                "email_id": "test-1"
                            }
                        ]
                    },
                    "merge_duplicates": True
                }
            }
        }
        
        print("发送工具调用请求...")
        process.stdin.write(json.dumps(tool_request) + "\n")
        process.stdin.flush()
        
        tool_response_line = process.stdout.readline()
        if tool_response_line:
            tool_response = json.loads(tool_response_line.strip())
            # MCP工具调用响应格式检查
            assert "content" in tool_response, f"工具调用失败: {tool_response}"
            content = tool_response["content"][0]["text"]
            result_data = json.loads(content)
            assert result_data.get("success"), f"工具执行失败: {result_data.get('error')}"
            commands = result_data["data"]["extracted_commands"]
            assert isinstance(commands, list)
            return
        else:
            assert False, "工具调用响应超时"
    
    except Exception as e:
        print(f"❌ 工具调用测试出错: {e}")
        return False
    
    finally:
        try:
            process.terminate()
            process.wait(timeout=2)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait()


def main():
    """主函数"""
    print("🚀 MCP Server Communication Test")
    print("=" * 50)
    
    tests = [
        test_mcp_server_startup,
        test_mcp_server_tool_call
    ]
    
    passed = 0
    total = len(tests)
    
    for test_func in tests:
        try:
            if test_func():
                passed += 1
                print("✅ Test passed")
            else:
                print("❌ Test failed")
        except Exception as e:
            print(f"💥 Test error: {e}")
    
    print("\n" + "=" * 50)
    print(f"Communication Test Results: {passed}/{total} tests passed")
    assert passed == total, "Some communication tests failed"


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)