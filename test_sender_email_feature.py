#!/usr/bin/env python3
"""
sender_email字段功能测试

这个测试专门验证新增的sender_email字段功能：
1. 使用sender_email字段进行精确匹配
2. 降级到从sender字段解析邮箱地址
3. 精确匹配 vs 模糊匹配的区别
"""

import json
from mail_command_extractor_skill import MailCommandExtractorSkill
from skill_compat import ExecutionContext

def test_sender_email_exact_matching():
    """测试sender_email精确匹配功能"""
    print("🧪 Testing sender_email exact matching feature...")
    
    skill = MailCommandExtractorSkill()
    ctx = ExecutionContext()
    
    # 测试数据：包含不同sender_email字段的邮件
    test_data = {
        "detection_rules": {
            "rules": [
                {
                    "sender": "exact@test.com",  # 精确匹配这个邮箱
                    "subjects": [
                        {
                            "title_pattern": "任务",
                            "content_rules": [
                                {
                                    "content_pattern": "处理",
                                    "action": {
                                        "command": "process_exact_match",
                                        "parameters": {"match_type": "exact"},
                                        "priority": 10
                                    }
                                }
                            ]
                        }
                    ]
                },
                {
                    "sender": "partial",  # 这个会被模糊匹配（如果没有精确匹配的话）
                    "subjects": [
                        {
                            "title_pattern": "任务",
                            "content_rules": [
                                {
                                    "content_pattern": "处理",
                                    "action": {
                                        "command": "process_partial_match",
                                        "parameters": {"match_type": "partial"},
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
                    "sender": "用户1 <exact@test.com>",
                    "sender_email": "exact@test.com",  # 精确匹配第一个规则
                    "subject": "任务1",
                    "content": "需要处理这个任务",
                    "date_received": "2026-02-12T10:00:00Z",
                    "email_id": "email-1"
                },
                {
                    "sender": "用户2 <different@test.com>",
                    "sender_email": "different@test.com",  # 不匹配任何规则
                    "subject": "任务2",
                    "content": "需要处理另一个任务",
                    "date_received": "2026-02-12T09:00:00Z",
                    "email_id": "email-2"
                },
                {
                    "sender": "用户3 <fallback@test.com>",  # 没有sender_email，从sender解析
                    "subject": "任务3",
                    "content": "这个任务也要处理",
                    "date_received": "2026-02-12T08:00:00Z",
                    "email_id": "email-3"
                }
            ]
        },
        "merge_duplicates": False
    }
    
    result = skill.execute(ctx, **test_data)
    
    print(f"✅ 测试结果: {result['success']}")
    assert result["success"] == True
    
    commands = result["data"]["extracted_commands"]
    print(f"📊 生成命令数: {len(commands)}")
    
    # 应该只匹配第一封邮件（精确匹配exact@test.com）
    assert len(commands) == 1, f"期望1个命令，实际得到{len(commands)}个"
    
    command = commands[0]
    assert command["command"] == "process_exact_match"
    assert command["parameters"]["match_type"] == "exact"
    
    # 检查匹配的邮件
    if "matched_emails" in command:
        matched_email = command["matched_emails"][0]
    else:
        matched_email = command["matched_email"]
        
    assert matched_email["sender_email"] == "exact@test.com"
    
    print("✅ sender_email精确匹配测试通过")
    return True

def test_fallback_extraction():
    """测试从sender字段解析邮箱地址的降级功能"""
    print("\n🧪 Testing fallback email extraction...")
    
    skill = MailCommandExtractorSkill()
    ctx = ExecutionContext()
    
    test_data = {
        "detection_rules": {
            "rules": [
                {
                    "sender": "fallback@test.com",  # 匹配从sender解析的邮箱
                    "subjects": [
                        {
                            "title_pattern": "测试",
                            "content_rules": [
                                {
                                    "content_pattern": "降级",
                                    "action": {
                                        "command": "test_fallback",
                                        "parameters": {"source": "extracted"},
                                        "priority": 15
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
                    "sender": "测试用户 <fallback@test.com>",  # 没有sender_email字段
                    "subject": "测试邮件",
                    "content": "这是降级测试",
                    "date_received": "2026-02-12T10:00:00Z",
                    "email_id": "email-fallback"
                }
            ]
        }
    }
    
    result = skill.execute(ctx, **test_data)
    
    print(f"✅ 测试结果: {result['success']}")
    assert result["success"] == True
    
    commands = result["data"]["extracted_commands"]
    assert len(commands) == 1
    
    command = commands[0]
    assert command["command"] == "test_fallback"
    
    print("✅ 邮箱地址降级解析测试通过")
    return True

def test_with_real_gmail_data():
    """使用真实的Gmail数据测试"""
    print("\n🧪 Testing with real Gmail data...")
    
    try:
        with open('gmail_check_output_20260212_142541.json', 'r', encoding='utf-8') as f:
            gmail_data = json.load(f)
    except FileNotFoundError:
        print("⚠️ Gmail测试数据文件不存在，跳过此测试")
        return True
    
    skill = MailCommandExtractorSkill()
    ctx = ExecutionContext()
    
    # 针对LinkedIn邮件的精确匹配
    test_config = {
        "detection_rules": {
            "rules": [
                {
                    "sender": "jobalerts-noreply@linkedin.com",  # 精确匹配LinkedIn
                    "subjects": [
                        {
                            "title_pattern": "软件工程师",
                            "content_rules": [
                                {
                                    "content_pattern": "职位订阅",
                                    "action": {
                                        "command": "process_linkedin_jobs",
                                        "parameters": {
                                            "source": "linkedin",
                                            "category": "software_engineering",
                                            "action": "review"
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
        "email_list": gmail_data["gmail_check_result"]["data"],
        "merge_duplicates": True
    }
    
    result = skill.execute(ctx, **test_config)
    
    print(f"✅ 测试结果: {result['success']}")
    assert result["success"] == True
    
    commands = result["data"]["extracted_commands"]
    print(f"📊 从{result['data']['processed_emails']}封邮件中生成{len(commands)}个命令")
    
    if commands:
        cmd = commands[0]
        print(f"🎯 命令: {cmd['command']}")
        print(f"📧 匹配邮件数: {len(cmd['matched_emails'])}")
        
        # 验证所有匹配的邮件都是来自LinkedIn
        for email in cmd['matched_emails']:
            assert email['sender_email'] == 'jobalerts-noreply@linkedin.com'
        
        print("✅ LinkedIn邮件精确匹配验证通过")
    
    return True

def main():
    """运行所有sender_email功能测试"""
    print("🚀 sender_email字段功能测试")
    print("=" * 50)
    
    tests = [
        test_sender_email_exact_matching,
        test_fallback_extraction,
        test_with_real_gmail_data
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ 测试失败: {e}")
    
    print("\n" + "=" * 50)
    print(f"🎉 测试完成: {passed}/{total} 通过")
    
    if passed == total:
        print("✅ 所有sender_email功能测试通过!")
        print("\n📋 新功能总结:")
        print("- ✅ sender_email字段用于精确邮件地址匹配")
        print("- ✅ 缺失sender_email时自动从sender字段解析")
        print("- ✅ 精确匹配避免了意外的模糊匹配")
        print("- ✅ 与现有邮件数据格式兼容")
        return True
    else:
        print("❌ 部分测试失败")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)