#!/usr/bin/env python3
"""
Test script for Mail Command Extractor Skill

Tests the functionality of the mail command extraction skill.
"""

import json
import sys
import os

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from mail_command_extractor_skill import MailCommandExtractorSkill
from skill_compat import ExecutionContext


def test_skill_schema():
    """测试技能Schema"""
    print("🧪 Testing skill schema...")
    skill = MailCommandExtractorSkill()
    
    schema = skill.get_openai_schema()
    assert "function" in schema
    assert "name" in schema["function"]
    assert schema["function"]["name"] == "mail_command_extractor"
    assert "description" in schema["function"]
    assert "parameters" in schema["function"]
    
    print("✅ Schema validation passed")


def test_basic_extraction():
    """测试基本命令提取"""
    print("\n🧪 Testing basic command extraction...")
    skill = MailCommandExtractorSkill()
    ctx = ExecutionContext()
    
    # 准备测试数据
    test_config = {
        "detection_rules": {
            "rules": [
                {
                    "sender": "baddif@gmail.com",
                    "subjects": [
                        {
                            "title_pattern": "日报",
                            "content_rules": [
                                {
                                    "content_pattern": "生成日报",
                                    "action": {
                                        "command": "generate_daily_report",
                                        "parameters": {"type": "daily", "language": "Chinese"},
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
                    "sender": "=?UTF-8?B?5LiB5LiA5aSr?= <baddif@gmail.com>",
                    "subject": "日报",
                    "content": "生成日报",
                    "date_received": "Thu, 12 Feb 2026 15:20:17 +0800",
                    "message_id": "<test-message-id>",
                    "email_id": "test-email-id"
                }
            ]
        },
        "merge_duplicates": True
    }
    
    result = skill.execute(ctx, **test_config)
    
    assert result["success"] == True
    assert "data" in result
    assert "extracted_commands" in result["data"]
    assert len(result["data"]["extracted_commands"]) == 1
    
    command = result["data"]["extracted_commands"][0]
    assert command["command"] == "generate_daily_report"
    assert command["priority"] == 10
    
    print("✅ Basic extraction test passed")


def test_multiple_rules():
    """测试多规则匹配"""
    print("\n🧪 Testing multiple rules matching...")
    skill = MailCommandExtractorSkill()
    ctx = ExecutionContext()
    
    test_config = {
        "detection_rules": {
            "rules": [
                {
                    "sender": "baddif@gmail.com",
                    "subjects": [
                        {
                            "title_pattern": "报告",
                            "content_rules": [
                                {
                                    "content_pattern": "日报",
                                    "action": {
                                        "command": "generate_daily_report",
                                        "parameters": {"type": "daily"},
                                        "priority": 10
                                    }
                                },
                                {
                                    "content_pattern": "周报",
                                    "action": {
                                        "command": "generate_weekly_report", 
                                        "parameters": {"type": "weekly"},
                                        "priority": 20
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
                    "sender": "Test User <baddif@gmail.com>",
                    "subject": "报告请求",
                    "content": "请生成日报和周报",
                    "date_received": "2026-02-12T15:20:17+08:00",
                    "message_id": "test-1",
                    "email_id": "test-1"
                }
            ]
        }
    }
    
    result = skill.execute(ctx, **test_config)
    
    assert result["success"] == True
    assert len(result["data"]["extracted_commands"]) == 2
    
    # 验证优先级排序
    commands = result["data"]["extracted_commands"]
    assert commands[0]["priority"] <= commands[1]["priority"]
    
    print("✅ Multiple rules test passed")


def test_duplicate_merging():
    """测试重复命令合并"""
    print("\n🧪 Testing duplicate command merging...")
    skill = MailCommandExtractorSkill()
    ctx = ExecutionContext()
    
    test_config = {
        "detection_rules": {
            "rules": [
                {
                    "sender": "user@gmail.com",
                    "subjects": [
                        {
                            "title_pattern": "任务",
                            "content_rules": [
                                {
                                    "content_pattern": "处理",
                                    "action": {
                                        "command": "process_task",
                                        "parameters": {"type": "task"},
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
                    "sender": "user@gmail.com",
                    "subject": "任务1",
                    "content": "需要处理",
                    "email_id": "email-1",
                    "date_received": "2026-02-12T10:00:00Z"
                },
                {
                    "sender": "user@gmail.com", 
                    "subject": "任务2",
                    "content": "需要处理",
                    "email_id": "email-2",
                    "date_received": "2026-02-12T09:00:00Z"
                }
            ]
        },
        "merge_duplicates": True
    }
    
    result = skill.execute(ctx, **test_config)
    
    assert result["success"] == True
    # 应该合并成一个命令
    assert len(result["data"]["extracted_commands"]) == 1
    
    command = result["data"]["extracted_commands"][0]
    assert len(command["matched_emails"]) == 2
    
    print("✅ Duplicate merging test passed")


def test_no_merging():
    """测试不合并重复命令"""
    print("\n🧪 Testing no duplicate merging...")
    skill = MailCommandExtractorSkill()
    ctx = ExecutionContext()
    
    test_config = {
        "detection_rules": {
            "rules": [
                {
                    "sender": "user@gmail.com",
                    "subjects": [
                        {
                            "title_pattern": "任务",
                            "content_rules": [
                                {
                                    "content_pattern": "处理",
                                    "action": {
                                        "command": "process_task",
                                        "parameters": {"type": "task"},
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
                    "sender": "user@gmail.com",
                    "subject": "任务1",
                    "content": "需要处理",
                    "email_id": "email-1",
                    "date_received": "2026-02-12T10:00:00Z"
                },
                {
                    "sender": "user@gmail.com",
                    "subject": "任务2", 
                    "content": "需要处理",
                    "email_id": "email-2",
                    "date_received": "2026-02-12T09:00:00Z"
                }
            ]
        },
        "merge_duplicates": False
    }
    
    result = skill.execute(ctx, **test_config)
    
    assert result["success"] == True
    # 不合并，应该有两个命令
    assert len(result["data"]["extracted_commands"]) == 2
    
    print("✅ No merging test passed")


def test_mcp_resources():
    """测试MCP资源"""
    print("\n🧪 Testing MCP resources...")
    skill = MailCommandExtractorSkill()
    
    resources = skill.get_mcp_resources()
    assert len(resources) == 2
    
    # 测试资源读取
    template_data = skill.read_resource("skill://mail_command_extractor/config_template")
    assert "contents" in template_data
    
    print("✅ MCP resources test passed")


def test_with_local_config():
    """使用本地配置测试"""
    print("\n🧪 Testing with local configuration...")
    
    config_file = "mail_command_extractor_config_local.json"
    if os.path.exists(config_file):
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        skill = MailCommandExtractorSkill()
        ctx = ExecutionContext()
        
        result = skill.execute(ctx, **config)
        print(f"Local config test result: {result.get('success')}")
        
        if result.get("success"):
            print(f"Commands extracted: {len(result['data']['extracted_commands'])}")
            for cmd in result['data']['extracted_commands']:
                print(f"  - {cmd['command']} (priority: {cmd['priority']})")
        
        print("✅ Local config test completed")
    else:
        print("⚠️ Local config file not found, skipping test")


def main():
    """运行所有测试"""
    print("🚀 Mail Command Extractor Skill Test Suite")
    print("=" * 50)
    
    try:
        test_skill_schema()
        test_basic_extraction()
        test_multiple_rules()
        test_duplicate_merging()
        test_no_merging()
        test_mcp_resources()
        test_with_local_config()
        
        print("\n" + "=" * 50)
        print("✅ All tests passed successfully!")
        
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Test error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()