# Mail Command Extractor Skill Usage Guide

## 概述

Mail Command Extractor Skill 是一个用于检测邮件内容并生成对应命令的技能。它支持根据邮件来源、标题和内容的模糊匹配来触发特定的动作命令。

## 主要功能

- 🔍 **邮件来源匹配**: 支持邮件发送者地址的模糊匹配
- 📝 **标题检测**: 支持邮件标题关键词的模糊匹配
- 📄 **内容分析**: 支持邮件内容语句的模糊匹配
- ⚡ **命令生成**: 根据匹配规则自动生成相应的处理命令
- 🔄 **重复合并**: 自动合并相同的命令，避免重复执行
- 📊 **优先级排序**: 按照定义顺序和优先级对命令进行排序

## 配置结构

### 检测规则配置 (detection_rules)

```json
{
  "detection_rules": {
    "rules": [
      {
        "sender": "邮件发送者模式",
        "subjects": [
          {
            "title_pattern": "标题匹配模式",
            "content_rules": [
              {
                "content_pattern": "内容匹配模式",
                "action": {
                  "command": "命令名称",
                  "parameters": {
                    "参数名": "参数值"
                  },
                  "priority": 优先级数字
                }
              }
            ]
          }
        ]
      }
    ]
  }
}
```

### 邮件列表格式 (email_list)

使用gmail_check输出的标准格式：

```json
{
  "email_list": {
    "matched_emails": [
      {
        "sender": "发件人信息",
        "subject": "邮件标题",
        "content": "邮件内容",
        "date_received": "接收时间",
        "message_id": "消息ID",
        "email_id": "邮件ID"
      }
    ]
  }
}
```

## 匹配规则说明

### 1. 发件人匹配
- **模糊匹配**: 包含指定关键词即可
- **示例**: `"sender": "baddif@gmail.com"` 可以匹配 `"=?UTF-8?B?5LiB5LiA5aSr?= <baddif@gmail.com>"`

### 2. 标题匹配
- **模糊匹配**: 标题中包含指定关键词即可
- **示例**: `"title_pattern": "日报"` 可以匹配 `"今日日报"` 或 `"日报请求"`

### 3. 内容匹配
- **模糊匹配**: 内容中包含指定关键词即可
- **示例**: `"content_pattern": "生成日报"` 可以匹配 `"请生成日报"` 或 `"需要生成日报"`

### 4. 优先级规则
- **数字越小优先级越高**: priority=1 > priority=10
- **规则顺序**: 相同优先级按照在配置中的定义顺序排序

## 使用示例

### 基本日报生成配置

```json
{
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
                    "include_git": true
                  },
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
        "sender": "用户 <baddif@gmail.com>",
        "subject": "日报请求",
        "content": "请生成今日的工作日报",
        "date_received": "2026-02-12T15:20:17+08:00",
        "message_id": "msg-123",
        "email_id": "email-123"
      }
    ]
  },
  "merge_duplicates": true
}
```

### 多类型报告配置

```json
{
  "detection_rules": {
    "rules": [
      {
        "sender": "manager@company.com",
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
  }
}
```

### 紧急任务处理配置

```json
{
  "detection_rules": {
    "rules": [
      {
        "sender": "@company.com",
        "subjects": [
          {
            "title_pattern": "紧急",
            "content_rules": [
              {
                "content_pattern": "处理",
                "action": {
                  "command": "urgent_alert",
                  "parameters": {
                    "priority": "high",
                    "type": "urgent"
                  },
                  "priority": 1
                }
              }
            ]
          }
        ]
      }
    ]
  }
}
```

## 输出格式

### 成功响应

```json
{
  "success": true,
  "function_name": "mail_command_extractor",
  "data": {
    "extracted_commands": [
      {
        "command": "generate_daily_report",
        "parameters": {
          "type": "daily",
          "language": "Chinese"
        },
        "priority": 10,
        "rule_index": 0,
        "matched_emails": [
          {
            "email_id": "email-123",
            "sender": "用户 <baddif@gmail.com>",
            "subject": "日报请求",
            "content": "请生成今日的工作日报",
            "date_received": "2026-02-12T15:20:17+08:00",
            "message_id": "msg-123"
          }
        ],
        "matching_details": {
          "sender_pattern": "baddif@gmail.com",
          "title_pattern": "日报",
          "content_pattern": "生成日报"
        }
      }
    ],
    "processed_emails": 1,
    "matched_emails": 1,
    "total_commands": 1,
    "processing_time": "2026-02-12T07:23:19Z"
  },
  "statistics": {
    "rules_processed": 1,
    "emails_processed": 1,
    "commands_generated": 1
  }
}
```

### 命令字段说明

- **command**: 要执行的命令名称
- **parameters**: 命令参数（JSON对象）
- **priority**: 命令优先级（数字越小优先级越高）
- **rule_index**: 匹配的规则索引
- **matched_emails**: 触发此命令的邮件列表
- **matching_details**: 匹配详情，包含匹配的模式

## 高级用法

### 1. 重复命令合并

当`merge_duplicates: true`时，相同的命令（command和parameters完全相同）会被合并：

```json
// 输入：两封邮件都匹配同样的命令
// 输出：一个命令，包含两个matched_emails

{
  "command": "process_task",
  "parameters": {"type": "task"},
  "matched_emails": [
    {"email_id": "email-1", ...},
    {"email_id": "email-2", ...}
  ]
}
```

### 2. 优先级控制

通过`priority`字段控制命令执行顺序：

```json
{
  "content_rules": [
    {
      "content_pattern": "紧急",
      "action": {
        "command": "urgent_task",
        "priority": 1  // 最高优先级
      }
    },
    {
      "content_pattern": "普通",
      "action": {
        "command": "normal_task", 
        "priority": 10  // 较低优先级
      }
    }
  ]
}
```

### 3. 多模式匹配

一个邮件可以触发多个命令：

```json
{
  "title_pattern": "工作",
  "content_rules": [
    {
      "content_pattern": "日报",
      "action": {"command": "daily_report", "priority": 10}
    },
    {
      "content_pattern": "任务",
      "action": {"command": "task_reminder", "priority": 20}
    }
  ]
}
```

## 最佳实践

### 1. 规则设计

- **从具体到一般**: 将更具体的规则放在前面
- **合理优先级**: 紧急任务设置较小的priority值
- **模式简洁**: 使用简洁明确的关键词

### 2. 性能优化

- **启用合并**: 对于可能重复的命令，设置`merge_duplicates: true`
- **合理参数**: 避免过于复杂的参数结构

### 3. 错误处理

- **验证配置**: 确保所有必需字段都存在
- **测试匹配**: 使用测试脚本验证匹配规则
- **监控日志**: 关注处理统计信息

## MCP集成

### 可用资源

1. **latest_result**: 最新的处理结果
   - URI: `skill://mail_command_extractor/latest_result`
   - 类型: JSON

2. **config_template**: 配置模板
   - URI: `skill://mail_command_extractor/config_template`
   - 类型: JSON

### MCP服务器使用

```bash
# 启动MCP服务器
python3 mcp_server.py

# 测试MCP服务器
python3 mcp_server.py --test
```

## 故障排除

### 常见问题

1. **没有匹配到邮件**
   - 检查sender模式是否正确
   - 确认title_pattern和content_pattern是否包含正确的关键词
   - 验证邮件数据格式

2. **命令重复**
   - 设置`merge_duplicates: true`
   - 检查command和parameters是否一致

3. **优先级不正确**
   - 确认priority字段设置（数字越小优先级越高）
   - 检查rule_index（规则在数组中的位置）

### 调试方法

1. **使用测试脚本**:
   ```bash
   python3 test_mail_command_extractor.py
   ```

2. **检查匹配详情**:
   查看输出中的`matching_details`字段

3. **验证配置**:
   使用配置模板创建测试配置

## 集成示例

### 与工作流集成

```python
# 在工作流中使用
from mail_command_extractor_skill import MailCommandExtractorSkill

skill = MailCommandExtractorSkill()
ctx = ExecutionContext()

# 加载配置
with open('config.json') as f:
    config = json.load(f)

# 执行提取
result = skill.execute(ctx, **config)

# 处理命令
for command in result['data']['extracted_commands']:
    execute_command(command['command'], command['parameters'])
```

### 与AI代理集成

通过MCP协议与Claude等AI代理集成，实现自动邮件处理和命令生成。