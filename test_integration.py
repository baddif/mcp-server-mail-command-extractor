#!/usr/bin/env python3
"""
End-to-End Integration Test

使用真实的gmail_skill_latest_output.json数据测试整个工作流
"""

import json
import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from mcp_server import MailCommandExtractorMcpServer


def test_with_real_gmail_data():
    """使用真实的Gmail数据进行测试"""
    print("🧪 Testing with Real Gmail Data...")
    
    # 读取真实的Gmail数据
    gmail_data_file = "gmail_skill_latest_output.json"
    if not os.path.exists(gmail_data_file):
        print(f"❌ Gmail data file not found: {gmail_data_file}")
        return False
    
    with open(gmail_data_file, 'r', encoding='utf-8') as f:
        gmail_data = json.load(f)
    
    print(f"Loaded Gmail data with {len(gmail_data['data']['matched_emails'])} emails")
    
    # 创建测试配置
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
                                        "parameters": {
                                            "type": "daily",
                                            "language": "Chinese",
                                            "include_git": True,
                                            "include_tasks": True
                                        },
                                        "priority": 10
                                    }
                                },
                                {
                                    "content_pattern": "汇总",
                                    "action": {
                                        "command": "generate_summary",
                                        "parameters": {
                                            "type": "summary",
                                            "language": "Chinese"
                                        },
                                        "priority": 20
                                    }
                                }
                            ]
                        },
                        {
                            "title_pattern": "报告",
                            "content_rules": [
                                {
                                    "content_pattern": "生成",
                                    "action": {
                                        "command": "generate_report",
                                        "parameters": {
                                            "type": "general",
                                            "language": "Chinese"
                                        },
                                        "priority": 15
                                    }
                                }
                            ]
                        }
                    ]
                },
                {
                    "sender": "@gmail.com",
                    "subjects": [
                        {
                            "title_pattern": "通知",
                            "content_rules": [
                                {
                                    "content_pattern": "提醒",
                                    "action": {
                                        "command": "send_notification",
                                        "parameters": {
                                            "type": "reminder"
                                        },
                                        "priority": 5
                                    }
                                }
                            ]
                        }
                    ]
                }
            ]
        },
        "email_list": gmail_data["data"],
        "merge_duplicates": True
    }
    
    # 执行测试
    server = MailCommandExtractorMcpServer()
    result = server.call_tool("mail_command_extractor", test_config)
    
    if "content" in result:
        response_data = json.loads(result["content"][0]["text"])
        if response_data.get("success"):
            print("✅ Real data processing successful")
            print(f"   Emails processed: {response_data['data']['processed_emails']}")
            print(f"   Commands generated: {response_data['data']['total_commands']}")
            
            # 显示生成的命令详情
            commands = response_data['data']['extracted_commands']
            if commands:
                print("\n📋 Generated Commands:")
                for i, cmd in enumerate(commands, 1):
                    print(f"   {i}. {cmd['command']}")
                    print(f"      Priority: {cmd['priority']}")
                    print(f"      Parameters: {json.dumps(cmd['parameters'], ensure_ascii=False)}")
                    print(f"      Matched emails: {len(cmd['matched_emails'])}")
                    for email in cmd['matched_emails']:
                        print(f"        - From: {email['sender']}")
                        print(f"          Subject: {email['subject']}")
                        print(f"          Content: {email['content']}")
                    print()
            else:
                print("   No commands generated (no matching emails)")
            
            return True
        else:
            print("❌ Real data processing failed")
            print(f"   Error: {response_data.get('error', {}).get('message', 'Unknown')}")
            return False
    else:
        print(f"❌ Tool execution error: {result.get('error', 'Unknown error')}")
        return False


def test_multiple_scenarios():
    """测试多种场景"""
    print("\n🧪 Testing Multiple Scenarios...")
    
    server = MailCommandExtractorMcpServer()
    
    scenarios = [
        {
            "name": "多个相同命令合并",
            "config": {
                "detection_rules": {
                    "rules": [
                        {
                            "sender": "test@example.com",
                            "subjects": [
                                {
                                    "title_pattern": "任务",
                                    "content_rules": [
                                        {
                                            "content_pattern": "处理",
                                            "action": {
                                                "command": "process_task",
                                                "parameters": {"type": "standard"},
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
                            "subject": "任务1",
                            "content": "需要处理的任务",
                            "email_id": "1"
                        },
                        {
                            "sender": "test@example.com", 
                            "subject": "任务2",
                            "content": "另一个要处理的任务",
                            "email_id": "2"
                        }
                    ]
                },
                "merge_duplicates": True
            },
            "expected_commands": 1
        },
        {
            "name": "多个不同命令不合并",
            "config": {
                "detection_rules": {
                    "rules": [
                        {
                            "sender": "manager@company.com",
                            "subjects": [
                                {
                                    "title_pattern": "工作",
                                    "content_rules": [
                                        {
                                            "content_pattern": "日报",
                                            "action": {
                                                "command": "daily_report",
                                                "parameters": {"type": "daily"},
                                                "priority": 10
                                            }
                                        },
                                        {
                                            "content_pattern": "周报",
                                            "action": {
                                                "command": "weekly_report",
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
                            "sender": "manager@company.com",
                            "subject": "工作报告",
                            "content": "请提供日报和周报",
                            "email_id": "3"
                        }
                    ]
                },
                "merge_duplicates": True
            },
            "expected_commands": 2
        },
        {
            "name": "优先级排序测试",
            "config": {
                "detection_rules": {
                    "rules": [
                        {
                            "sender": "urgent@company.com",
                            "subjects": [
                                {
                                    "title_pattern": "紧急",
                                    "content_rules": [
                                        {
                                            "content_pattern": "处理",
                                            "action": {
                                                "command": "urgent_task",
                                                "parameters": {"priority": "high"},
                                                "priority": 1
                                            }
                                        }
                                    ]
                                },
                                {
                                    "title_pattern": "普通",
                                    "content_rules": [
                                        {
                                            "content_pattern": "处理",
                                            "action": {
                                                "command": "normal_task",
                                                "parameters": {"priority": "normal"},
                                                "priority": 50
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
                            "sender": "urgent@company.com",
                            "subject": "普通任务",
                            "content": "这是一个需要处理的普通任务",
                            "email_id": "4"
                        },
                        {
                            "sender": "urgent@company.com",
                            "subject": "紧急任务",
                            "content": "这是一个需要紧急处理的任务",
                            "email_id": "5"
                        }
                    ]
                },
                "merge_duplicates": True
            },
            "expected_commands": 2
        }
    ]
    
    for scenario in scenarios:
        print(f"\n测试场景: {scenario['name']}")
        result = server.call_tool("mail_command_extractor", scenario["config"])
        
        if "content" in result:
            response_data = json.loads(result["content"][0]["text"])
            if response_data.get("success"):
                actual_commands = len(response_data['data']['extracted_commands'])
                expected_commands = scenario["expected_commands"]
                
                if actual_commands == expected_commands:
                    print(f"   ✅ 生成了预期的 {actual_commands} 个命令")
                    
                    # 检查优先级排序
                    if scenario['name'] == "优先级排序测试":
                        commands = response_data['data']['extracted_commands']
                        if len(commands) >= 2:
                            if commands[0]['priority'] <= commands[1]['priority']:
                                print(f"   ✅ 优先级排序正确: {commands[0]['priority']} <= {commands[1]['priority']}")
                            else:
                                print(f"   ❌ 优先级排序错误: {commands[0]['priority']} > {commands[1]['priority']}")
                    
                else:
                    print(f"   ❌ 命令数量不匹配: 期望 {expected_commands}, 实际 {actual_commands}")
                    return False
            else:
                print(f"   ❌ 场景执行失败: {response_data.get('error', 'Unknown error')}")
                return False
        else:
            print(f"   ❌ 工具执行错误: {result.get('error', 'Unknown error')}")
            return False
    
    return True


def main():
    """主函数"""
    print("🚀 End-to-End Integration Test")
    print("=" * 50)
    
    tests = [
        test_with_real_gmail_data,
        test_multiple_scenarios
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
            import traceback
            traceback.print_exc()
    
    print("\n" + "=" * 50)
    print(f"Integration Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All integration tests passed! The system is ready for production use!")
        return True
    else:
        print("⚠️ Some integration tests failed. Please check the output above.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)