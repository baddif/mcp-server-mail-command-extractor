#!/usr/bin/env python3
"""
测试新的输入格式和匹配逻辑
1. 输入直接是邮件数组（matched_emails字段内容）
2. sender_email精确匹配，标题和内容模糊匹配
"""

import json
from mail_command_extractor_skill import MailCommandExtractorSkill
from skill_compat import ExecutionContext

def test_new_input_format():
    """测试新的输入格式：直接传入邮件数组"""
    
    print("🚀 测试新的输入格式")
    print("=" * 60)
    
    # 创建技能实例
    skill = MailCommandExtractorSkill()
    ctx = ExecutionContext()
    
    # 从真实的Gmail数据中提取matched_emails数组
    with open('gmail_check_output_20260212_142541.json', 'r', encoding='utf-8') as f:
        gmail_data = json.load(f)
    
    # 直接使用matched_emails数组作为输入
    emails = gmail_data['gmail_check_result']['data']['matched_emails']
    
    print(f"📧 输入邮件数量: {len(emails)}")
    print("📧 邮件概览:")
    for i, email in enumerate(emails[:3]):  # 只显示前3封
        print(f"  {i+1}. {email['sender_email']} | {email['subject']}")
    
    # 定义简化的检测规则
    detection_rules = {
        "rules": [
            {
                "sender": "jobalerts-noreply@linkedin.com",  # 精确匹配
                "subjects": ["软件工程师"],  # 模糊匹配：包含"软件工程师"即可
                "contents": [],  # 空表示不检查内容
                "action": "process_linkedin_jobs",
                "parameters": {"source": "linkedin", "type": "job_alert"},
                "priority": 1
            },
            {
                "sender": "jobs-listings@linkedin.com",  # 精确匹配
                "subjects": ["工程师", "开发"],  # 模糊匹配：包含"工程师"或"开发"即可
                "contents": [],
                "action": "process_linkedin_jobs",
                "parameters": {"source": "linkedin", "type": "job_listing"},
                "priority": 2
            },
            {
                "sender": "jobalerts-noreply@linkedin.com",
                "subjects": ["推荐", "职位"],  # 模糊匹配：包含"推荐"或"职位"即可
                "contents": [],
                "action": "review_job_recommendations",
                "parameters": {"source": "linkedin"},
                "priority": 3
            }
        ]
    }
    
    # 执行命令提取 - 使用新的输入格式
    result = skill.execute(ctx, emails=emails, detection_rules=detection_rules)
    
    print(f"\n✅ 执行结果:")
    if result['success']:
        commands = result['data']['extracted_commands']
        print(f"📊 生成的命令数量: {len(commands)}")
        
        for i, command in enumerate(commands):
            print(f"\n🎯 命令 {i+1}:")
            print(f"   ▶ 动作: {command['command']}")
            print(f"   ▶ 优先级: {command['priority']}")
            print(f"   ▶ 参数: {json.dumps(command['parameters'], ensure_ascii=False)}")
            
            # 显示匹配的邮件信息
            matched_email = command['matched_email']
            print(f"   ▶ 匹配邮件:")
            print(f"     - sender_email: {matched_email['sender_email']}")
            print(f"     - subject: {matched_email['subject']}")
            
            # 显示匹配详情
            details = command['matching_details']
            print(f"   ▶ 匹配详情:")
            print(f"     - sender匹配: {details['sender_pattern']}")
            print(f"     - 标题关键词: {details.get('matched_subject_keywords', [])}")
            print(f"     - 内容关键词: {details.get('matched_content_keywords', [])}")
    else:
        print("❌ 执行失败")

def test_matching_logic():
    """测试匹配逻辑：精确匹配vs模糊匹配"""
    
    print("\n🧪 测试匹配逻辑")
    print("=" * 60)
    
    skill = MailCommandExtractorSkill()
    ctx = ExecutionContext()
    
    # 构造测试邮件
    test_emails = [
        {
            "sender": "LinkedIn Jobs <jobalerts-noreply@linkedin.com>",
            "sender_email": "jobalerts-noreply@linkedin.com",  # 精确匹配
            "subject": "高级软件工程师职位推荐",  # 包含"软件工程师" - 模糊匹配✅
            "content": "新的职位机会等待您",
            "date_received": "2026-02-12T10:00:00Z",
            "email_id": "test_email_1"
        },
        {
            "sender": "LinkedIn Jobs <jobalerts-noreply@linkedin.com>",
            "sender_email": "jobalerts-noreply@linkedin.com",  # 精确匹配
            "subject": "前端开发工程师",  # 包含"工程师" - 模糊匹配✅
            "content": "React开发职位",
            "date_received": "2026-02-12T11:00:00Z",
            "email_id": "test_email_2"
        },
        {
            "sender": "Other Jobs <other@example.com>",
            "sender_email": "other@example.com",  # 不匹配❌
            "subject": "软件工程师职位",  # 虽然包含关键词，但sender不匹配
            "content": "其他公司职位",
            "date_received": "2026-02-12T12:00:00Z", 
            "email_id": "test_email_3"
        },
        {
            "sender": "LinkedIn Jobs <jobalerts-noreply@linkedin.com>",
            "sender_email": "jobalerts-noreply@linkedin.com",  # 精确匹配
            "subject": "数据科学家职位",  # 不包含关键词❌
            "content": "机器学习工程师职位",
            "date_received": "2026-02-12T13:00:00Z",
            "email_id": "test_email_4"
        }
    ]
    
    detection_rules = {
        "rules": [
            {
                "sender": "jobalerts-noreply@linkedin.com",  # 精确匹配
                "subjects": ["软件工程师", "工程师"],  # 模糊匹配
                "contents": [],
                "action": "process_engineer_jobs",
                "parameters": {"job_type": "engineer"},
                "priority": 1
            }
        ]
    }
    
    print("📋 测试场景:")
    print("  - sender_email: 精确匹配")
    print("  - subjects: 模糊匹配（包含关键词即可）")
    print("  - contents: 空数组（不检查内容）")
    
    print(f"\n📧 测试邮件数量: {len(test_emails)}")
    for i, email in enumerate(test_emails, 1):
        print(f"  {i}. {email['sender_email']} | {email['subject']}")
    
    result = skill.execute(ctx, emails=test_emails, detection_rules=detection_rules)
    
    print(f"\n🎯 匹配结果:")
    if result['success']:
        commands = result['data']['extracted_commands']
        print(f"📊 生成命令数量: {len(commands)} (预期: 2个)")
        print("📊 应该匹配:")
        print("  ✅ test_email_1: sender匹配 + 标题包含'软件工程师'")
        print("  ✅ test_email_2: sender匹配 + 标题包含'工程师'")
        print("📊 不应该匹配:")
        print("  ❌ test_email_3: sender不匹配")
        print("  ❌ test_email_4: 标题不包含关键词")
        
        print(f"\n🔍 实际匹配结果:")
        for i, command in enumerate(commands):
            matched_email = command['matched_email']
            details = command['matching_details']
            print(f"  ✅ {matched_email['email_id']}: {matched_email['subject']}")
            print(f"     匹配关键词: {details.get('matched_subject_keywords', [])}")
        
        # 验证为什么第一封邮件没有匹配
        print(f"\n🔍 调试信息:")
        for i, email in enumerate(test_emails):
            print(f"  邮件{i+1}: {email['email_id']}")
            print(f"    sender_email: {email['sender_email']}")
            print(f"    subject: {email['subject']}")
            
            # 检查每个规则
            for j, rule in enumerate(detection_rules['rules']):
                sender_match = email['sender_email'].lower() == rule['sender'].lower()
                print(f"    规则{j+1} sender匹配: {sender_match}")
                
                if sender_match:
                    subject_keywords = rule.get('subjects', [])
                    for keyword in subject_keywords:
                        keyword_match = keyword.lower() in email['subject'].lower()
                        print(f"    规则{j+1} 标题关键词'{keyword}': {keyword_match}")
        
        print(f"\n预期结果分析:")
        print(f"  - test_email_1: sender✅ + '软件工程师'✅ = 应该匹配")
        print(f"  - test_email_2: sender✅ + '工程师'✅ = 应该匹配")
    else:
        print("❌ 执行失败")

def test_content_matching():
    """测试内容匹配逻辑"""
    
    print("\n📝 测试内容匹配")
    print("=" * 60)
    
    skill = MailCommandExtractorSkill()
    ctx = ExecutionContext()
    
    # 构造测试邮件
    test_emails = [
        {
            "sender": "Test <test@example.com>",
            "sender_email": "test@example.com",
            "subject": "测试邮件",
            "content": "这是一封包含重要信息的邮件，请处理任务A",  # 包含"任务"
            "date_received": "2026-02-12T10:00:00Z",
            "email_id": "content_test_1"
        },
        {
            "sender": "Test <test@example.com>",
            "sender_email": "test@example.com", 
            "subject": "测试邮件",
            "content": "这封邮件需要生成报告",  # 包含"报告"
            "date_received": "2026-02-12T11:00:00Z",
            "email_id": "content_test_2"
        },
        {
            "sender": "Test <test@example.com>",
            "sender_email": "test@example.com",
            "subject": "测试邮件", 
            "content": "这是其他内容，不匹配任何关键词",  # 不匹配
            "date_received": "2026-02-12T12:00:00Z",
            "email_id": "content_test_3"
        }
    ]
    
    detection_rules = {
        "rules": [
            {
                "sender": "test@example.com",
                "subjects": ["测试"],  # 所有邮件都匹配标题
                "contents": ["任务", "报告"],  # 内容必须包含"任务"或"报告"
                "action": "process_content",
                "parameters": {"type": "content_based"},
                "priority": 1
            }
        ]
    }
    
    result = skill.execute(ctx, emails=test_emails, detection_rules=detection_rules)
    
    print(f"📧 测试邮件数量: {len(test_emails)}")
    print("📋 预期匹配: 2个（包含'任务'或'报告'的邮件）")
    
    if result['success']:
        commands = result['data']['extracted_commands']
        print(f"🎯 实际匹配: {len(commands)}个命令")
        
        for command in commands:
            matched_email = command['matched_email']
            details = command['matching_details']
            print(f"  ✅ {matched_email['email_id']}: 内容关键词 {details.get('matched_content_keywords', [])}")

if __name__ == "__main__":
    print("🚀 测试新的输入格式和匹配逻辑\n")
    
    # 测试1: 新的输入格式
    test_new_input_format()
    
    # 测试2: 匹配逻辑验证
    test_matching_logic()
    
    # 测试3: 内容匹配
    test_content_matching()
    
    print("\n🎉 所有测试完成!")