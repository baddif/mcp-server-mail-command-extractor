#!/usr/bin/env python3
"""
MCP Server Resource Test

测试MCP服务器的资源访问功能
"""

import json
import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from mcp_server import MailCommandExtractorMcpServer


def test_mcp_resources():
    """测试MCP资源"""
    print("🧪 Testing MCP Resources...")
    
    server = MailCommandExtractorMcpServer()
    
    # 1. 测试资源列表
    print("\n1. Testing resource list:")
    resources = server.list_resources()
    print(f"Found {len(resources)} resources:")
    for resource in resources:
        print(f"  - {resource['name']}: {resource['uri']}")
    
    # 2. 测试配置模板资源
    print("\n2. Testing config template resource:")
    template_result = server.read_resource("skill://mail_command_extractor/config_template")
    if "contents" in template_result:
        template_data = json.loads(template_result["contents"][0]["text"])
        print("✅ Config template loaded successfully")
        print(f"   Rules count: {len(template_data['detection_rules']['rules'])}")
        print(f"   Sample emails: {len(template_data['email_list']['matched_emails'])}")
    else:
        print("❌ Failed to load config template")
        return False
    
    # 3. 测试最新结果资源（应该为空）
    print("\n3. Testing latest result resource:")
    result_data = server.read_resource("skill://mail_command_extractor/latest_result")
    if "contents" in result_data:
        print("✅ Latest result resource accessible")
    else:
        print("❌ Failed to access latest result resource")
        return False
    
    # 4. 测试无效资源
    print("\n4. Testing invalid resource:")
    invalid_result = server.read_resource("skill://invalid/resource")
    if "contents" in invalid_result:
        print("✅ Invalid resource handled gracefully")
    else:
        print("❌ Invalid resource not handled properly")
        return False
    
    return True


def test_mcp_tool_execution():
    """测试MCP工具执行"""
    print("\n🧪 Testing MCP Tool Execution...")
    
    server = MailCommandExtractorMcpServer()
    
    # 使用本地配置进行测试
    config_file = "mail_command_extractor_config_local.json"
    if os.path.exists(config_file):
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        print("1. Executing tool with local config:")
        result = server.call_tool("mail_command_extractor", config)
        
        if "content" in result:
            response_data = json.loads(result["content"][0]["text"])
            if response_data.get("success"):
                print("✅ Tool execution successful")
                print(f"   Commands generated: {len(response_data['data']['extracted_commands'])}")
                for cmd in response_data['data']['extracted_commands']:
                    print(f"   - {cmd['command']} (priority: {cmd['priority']})")
                return True
            else:
                print("❌ Tool execution failed")
                print(f"   Error: {response_data.get('error', {}).get('message', 'Unknown')}")
                return False
        elif "error" in result:
            print(f"❌ Tool execution error: {result['error']}")
            return False
    else:
        print("⚠️ Local config not found, using example config")
        
        # 使用示例配置
        example_config = {
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
                                            "parameters": {"type": "test"},
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
                        "sender": "Test User <test@example.com>",
                        "subject": "测试邮件",
                        "content": "这是一个命令测试",
                        "date_received": "2026-02-12T15:20:17+08:00",
                        "message_id": "test-message",
                        "email_id": "test-email"
                    }
                ]
            },
            "merge_duplicates": True
        }
        
        result = server.call_tool("mail_command_extractor", example_config)
        if "content" in result:
            response_data = json.loads(result["content"][0]["text"])
            if response_data.get("success"):
                print("✅ Tool execution with example config successful")
                print(f"   Commands generated: {len(response_data['data']['extracted_commands'])}")
                return True
        
        print("❌ Tool execution with example config failed")
        return False


def test_mcp_protocol_compatibility():
    """测试MCP协议兼容性"""
    print("\n🧪 Testing MCP Protocol Compatibility...")
    
    server = MailCommandExtractorMcpServer()
    
    # 1. 测试服务器信息
    print("1. Testing server info:")
    server_info = server.get_server_info()
    required_fields = ["name", "version", "description", "capabilities"]
    
    for field in required_fields:
        if field in server_info:
            print(f"   ✅ {field}: {server_info[field]}")
        else:
            print(f"   ❌ Missing required field: {field}")
            return False
    
    # 2. 测试工具列表
    print("\n2. Testing tools list:")
    tools = server.list_tools()
    if len(tools) > 0:
        tool = tools[0]
        required_tool_fields = ["name", "description", "inputSchema"]
        for field in required_tool_fields:
            if field in tool:
                print(f"   ✅ Tool {field} present")
            else:
                print(f"   ❌ Missing tool field: {field}")
                return False
    else:
        print("   ❌ No tools found")
        return False
    
    # 3. 测试资源列表
    print("\n3. Testing resources list:")
    resources = server.list_resources()
    if len(resources) > 0:
        resource = resources[0]
        required_resource_fields = ["uri", "name", "description", "mimeType"]
        for field in required_resource_fields:
            if field in resource:
                print(f"   ✅ Resource {field} present")
            else:
                print(f"   ❌ Missing resource field: {field}")
                return False
    else:
        print("   ❌ No resources found")
        return False
    
    return True


def test_error_handling():
    """测试错误处理"""
    print("\n🧪 Testing Error Handling...")
    
    server = MailCommandExtractorMcpServer()
    
    # 1. 测试无效工具名
    print("1. Testing invalid tool name:")
    result = server.call_tool("invalid_tool", {})
    if "error" in result:
        print("   ✅ Invalid tool name handled correctly")
    else:
        print("   ❌ Invalid tool name not handled properly")
        return False
    
    # 2. 测试无效参数
    print("2. Testing invalid parameters:")
    result = server.call_tool("mail_command_extractor", {"invalid": "params"})
    if "error" in result or ("content" in result and "success" in json.loads(result["content"][0]["text"]) and not json.loads(result["content"][0]["text"])["success"]):
        print("   ✅ Invalid parameters handled correctly")
    else:
        print("   ❌ Invalid parameters not handled properly")
        return False
    
    # 3. 测试空邮件列表
    print("3. Testing empty email list:")
    empty_config = {
        "detection_rules": {"rules": []},
        "email_list": {"matched_emails": []},
        "merge_duplicates": True
    }
    result = server.call_tool("mail_command_extractor", empty_config)
    if "content" in result:
        response_data = json.loads(result["content"][0]["text"])
        if response_data.get("success") and response_data["data"]["total_commands"] == 0:
            print("   ✅ Empty email list handled correctly")
        else:
            print("   ❌ Empty email list not handled properly")
            return False
    else:
        print("   ❌ Empty email list caused error")
        return False
    
    return True


def main():
    """主测试函数"""
    print("🚀 MCP Server Comprehensive Test")
    print("=" * 50)
    
    tests = [
        test_mcp_resources,
        test_mcp_tool_execution, 
        test_mcp_protocol_compatibility,
        test_error_handling
    ]
    
    passed = 0
    total = len(tests)
    
    for test_func in tests:
        try:
            if test_func():
                passed += 1
                print("✅ Test passed\n")
            else:
                print("❌ Test failed\n")
        except Exception as e:
            print(f"💥 Test error: {e}\n")
    
    print("=" * 50)
    print(f"Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! MCP Server is fully functional!")
        return True
    else:
        print("⚠️ Some tests failed. Please check the output above.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)