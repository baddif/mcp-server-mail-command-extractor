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
    server = MailCommandExtractorMcpServer()

    # 1. 测试资源列表
    resources = server.list_resources()
    assert isinstance(resources, list)

    # 2. 测试配置模板资源
    template_result = server.read_resource("skill://mail_command_extractor/config_template")
    assert "contents" in template_result, "Config template resource missing contents"
    template_data = json.loads(template_result["contents"][0]["text"])
    assert "detection_rules" in template_data and "rules" in template_data["detection_rules"]
    assert "email_list" in template_data and "matched_emails" in template_data["email_list"]

    # 3. 测试最新结果资源（应该为空或结构化）
    result_data = server.read_resource("skill://mail_command_extractor/latest_result")
    assert "contents" in result_data, "Latest result resource missing contents"

    # 4. 测试无效资源
    invalid_result = server.read_resource("skill://invalid/resource")
    assert "contents" in invalid_result, "Invalid resource should return contents"


def test_mcp_tool_execution():
    """测试MCP工具执行"""
    server = MailCommandExtractorMcpServer()

    # 使用本地配置进行测试（如果存在）
    config_file = "mail_command_extractor_config_local.json"
    if os.path.exists(config_file):
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)

        result = server.call_tool("mail_command_extractor", config)
        assert result is not None
        assert ("content" in result) or ("error" in result)
        if "content" in result:
            response_data = json.loads(result["content"][0]["text"])
            assert response_data.get("success"), f"Tool execution failed: {response_data.get('error')}"
    else:
        # 使用示例配置进行验证
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
        assert result is not None
        assert "content" in result, f"Tool execution with example config failed: {result}"
        response_data = json.loads(result["content"][0]["text"])
        assert response_data.get("success"), f"Tool execution with example config failed: {response_data.get('error')}"


def test_mcp_protocol_compatibility():
    """测试MCP协议兼容性"""
    server = MailCommandExtractorMcpServer()

    server_info = server.get_server_info()
    for field in ["name", "version", "description", "capabilities"]:
        assert field in server_info, f"Missing required field: {field}"

    tools = server.list_tools()
    assert isinstance(tools, list) and len(tools) > 0, "No tools found"
    tool = tools[0]
    for field in ["name", "description", "inputSchema"]:
        assert field in tool, f"Missing tool field: {field}"

    resources = server.list_resources()
    assert isinstance(resources, list) and len(resources) > 0, "No resources found"
    resource = resources[0]
    for field in ["uri", "name", "description", "mimeType"]:
        assert field in resource, f"Missing resource field: {field}"


def test_error_handling():
    """测试错误处理"""
    server = MailCommandExtractorMcpServer()

    # 无效工具名
    result = server.call_tool("invalid_tool", {})
    assert "error" in result, "Invalid tool name not handled properly"

    # 无效参数
    result = server.call_tool("mail_command_extractor", {"invalid": "params"})
    invalid_handled = False
    if "error" in result:
        invalid_handled = True
    elif "content" in result:
        try:
            resp = json.loads(result["content"][0]["text"])
            # If the skill returned success but indicates empty input, consider it handled
            if not resp.get("success", True):
                invalid_handled = True
            else:
                data = resp.get("data", {})
                if data.get("total_commands", 1) == 0 and data.get("empty_input_reason"):
                    invalid_handled = True
        except Exception:
            invalid_handled = True
    assert invalid_handled, "Invalid parameters not handled properly"

    # 空邮件列表
    empty_config = {"detection_rules": {"rules": []}, "email_list": {"matched_emails": []}, "merge_duplicates": True}
    result = server.call_tool("mail_command_extractor", empty_config)
    assert "content" in result, "Empty email list caused error"
    response_data = json.loads(result["content"][0]["text"])
    assert response_data.get("success") and response_data["data"]["total_commands"] == 0, "Empty email list not handled properly"


if __name__ == "__main__":
    # Allow running as a script for quick debugging
    for fn in [test_mcp_resources, test_mcp_tool_execution, test_mcp_protocol_compatibility, test_error_handling]:
        try:
            fn()
            print(f"{fn.__name__}: PASS")
        except AssertionError as e:
            print(f"{fn.__name__}: FAIL - {e}")
        except Exception as e:
            print(f"{fn.__name__}: ERROR - {e}")