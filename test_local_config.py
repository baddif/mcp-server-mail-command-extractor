#!/usr/bin/env python3
"""测试本地配置文件是否能正确调用"""

import json
import sys
from mail_command_extractor_skill import MailCommandExtractorSkill
from skill_compat import ExecutionContext

def test_local_config():
    """测试本地配置文件调用"""
    print("🧪 测试本地配置文件调用...")
    
    # 读取本地配置文件
    try:
        with open('mail_command_extractor_config_local.json', 'r', encoding='utf-8') as f:
            config = json.load(f)
        print("✅ 本地配置文件读取成功")
    except Exception as e:
        print(f"❌ 配置文件读取失败: {e}")
        assert False, f"配置文件读取失败: {e}"
    
    # 验证配置结构
    required_fields = ['detection_rules', 'email_list', 'merge_duplicates']
    for field in required_fields:
        if field not in config:
            print(f"❌ 缺少必需字段: {field}")
            assert False, f"缺少必需字段: {field}"
    
    print("✅ 配置文件结构验证通过")
    
    # 验证邮件数据格式
    emails = config['email_list']['matched_emails']
    for i, email in enumerate(emails):
        required_email_fields = ['sender', 'sender_email', 'subject', 'content']
        for field in required_email_fields:
            if field not in email:
                print(f"❌ 邮件 {i+1} 缺少字段: {field}")
                assert False, f"邮件 {i+1} 缺少字段: {field}"
    
    print(f"✅ {len(emails)} 封邮件数据格式验证通过")
    
    # 执行技能
    skill = MailCommandExtractorSkill()
    ctx = ExecutionContext()
    
    print("🔄 执行邮件命令提取...")
    try:
        result = skill.execute(ctx, **config)
    except Exception as e:
        print(f"❌ 执行出错: {e}")
        import traceback
        traceback.print_exc()
        assert False, f"执行出错: {e}"
    
    # 显示结果
    print(f"📊 执行结果: {result['success']}")
    if result['success']:
        data = result['data']
        print(f"📧 处理邮件数: {data['processed_emails']}")
        print(f"🎯 生成命令数: {data['total_commands']}")
        print(f"⚡ 匹配邮件数: {data['matched_emails']}")
        
        if data['extracted_commands']:
            for i, cmd in enumerate(data['extracted_commands'], 1):
                print(f"\n命令 {i}:")
                print(f"  - 命令: {cmd['command']}")
                print(f"  - 优先级: {cmd['priority']}")
                print(f"  - 参数: {cmd['parameters']}")
                
                # 处理邮件信息
                if 'matched_emails' in cmd:
                    emails = cmd['matched_emails']
                else:
                    emails = [cmd['matched_email']]
                    
                for email in emails:
                    print(f"  - 发件人: {email['sender_email']}")
                    print(f"  - 主题: {email['subject']}")
                    
            return
        else:
            print("⚠️ 没有生成任何命令")
            assert False, "没有生成任何命令"
    else:
        print(f"❌ 执行失败: {result['error']['message']}")
        assert False, f"执行失败: {result['error']['message']}"
if __name__ == "__main__":
    # Allow running as a script
    try:
        test_local_config()
        print("\n✅ 本地配置文件调用测试成功！")
    except AssertionError as e:
        print(f"\n❌ 本地配置文件调用测试失败: {e}")
        sys.exit(1)