# MCP Deployment Guide for Mail Command Extractor

## 概述

本指南介绍如何部署和集成Mail Command Extractor Skill的MCP (Model Context Protocol) 服务器。

## 快速安装

### 1. 自动安装

```bash
cd /Users/dif/Projects/LectureProject/mcp-server-mail-command-extractor
chmod +x install.sh
./install.sh
```

### 2. 手动安装

```bash
# 克隆或下载项目
cd /path/to/mcp-server-mail-command-extractor

# 测试功能
python3 test_mail_command_extractor.py

# 测试MCP服务器
python3 mcp_server.py --test

# 配置本地设置
cp mail_command_extractor_config_example.json mail_command_extractor_config_local.json
```

## AI代理集成

### Claude Desktop 集成

1. **配置文件位置**:
   - macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
   - Windows: `%APPDATA%\Claude\claude_desktop_config.json`

2. **添加配置**:
```json
{
  "mcpServers": {
    "mail-command-extractor": {
      "command": "python3",
      "args": ["/Users/dif/Projects/LectureProject/mcp-server-mail-command-extractor/mcp_server.py"],
      "env": {
        "PYTHONPATH": "/Users/dif/Projects/LectureProject/mcp-server-mail-command-extractor"
      }
    }
  }
}
```

3. **重启Claude Desktop**

### 其他MCP客户端

对于支持MCP协议的其他AI代理：

```json
{
  "servers": {
    "mail-command-extractor": {
      "command": "python3",
      "args": ["/path/to/mcp_server.py"],
      "capabilities": ["tools", "resources"]
    }
  }
}
```

## 使用方法

### 在AI对话中使用

1. **检查可用工具**:
   ```
   请列出可用的MCP工具
   ```

2. **使用邮件命令提取**:
   ```
   使用mail_command_extractor工具处理以下邮件数据：
   [提供邮件数据和检测规则]
   ```

3. **查看配置模板**:
   ```
   请显示mail_command_extractor的配置模板
   ```

### 配置示例

```json
{
  "detection_rules": {
    "rules": [
      {
        "sender": "boss@company.com",
        "subjects": [
          {
            "title_pattern": "报告",
            "content_rules": [
              {
                "content_pattern": "日报",
                "action": {
                  "command": "generate_daily_report",
                  "parameters": {"language": "Chinese"},
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
    "matched_emails": [...]
  }
}
```

## 故障排除

### 常见问题

1. **服务器无法启动**
   ```bash
   # 检查Python版本
   python3 --version
   
   # 检查脚本权限
   ls -la mcp_server.py
   
   # 直接运行测试
   python3 mcp_server.py --test
   ```

2. **Claude Desktop未识别**
   - 确认配置文件路径正确
   - 检查JSON语法是否有错误
   - 重启Claude Desktop应用

3. **工具无法调用**
   - 检查环境变量PYTHONPATH
   - 确认脚本文件存在且可执行
   - 查看Claude Desktop的开发者控制台

### 调试模式

```bash
# 启动调试模式
PYTHONPATH=/path/to/skill python3 -u mcp_server.py

# 查看详细日志
python3 mcp_server.py --test 2>&1 | tee debug.log
```

## 高级配置

### 环境变量

```bash
export MAIL_COMMAND_EXTRACTOR_CONFIG="/path/to/config.json"
export MAIL_COMMAND_EXTRACTOR_DEBUG="true"
```

### 自定义配置文件

```python
# 在mcp_server.py中自定义配置加载
import os

config_path = os.getenv('MAIL_COMMAND_EXTRACTOR_CONFIG', 'default_config.json')
with open(config_path) as f:
    default_config = json.load(f)
```

### 性能优化

1. **缓存配置**: 将常用配置缓存到内存
2. **异步处理**: 对于大量邮件使用异步处理
3. **资源限制**: 设置最大邮件处理数量

## 安全考虑

### 配置文件安全

- 将敏感配置放在`*_config_local.json`文件中
- 确保`.gitignore`包含本地配置文件
- 避免在配置中硬编码敏感信息

### 访问控制

```python
# 在mcp_server.py中添加访问控制
def is_authorized(request):
    # 实现授权逻辑
    return True

def handle_request(self, request):
    if not is_authorized(request):
        return {"error": "Unauthorized"}
    # 处理请求
```

## 监控和日志

### 日志配置

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('mcp_server.log'),
        logging.StreamHandler()
    ]
)
```

### 监控指标

- 处理的邮件数量
- 生成的命令数量  
- 处理时间统计
- 错误率

## 维护和更新

### 版本更新

```bash
# 备份配置
cp mail_command_extractor_config_local.json config_backup.json

# 更新代码
git pull origin main

# 运行测试
python3 test_mail_command_extractor.py

# 重启服务（如果使用systemd）
systemctl restart mail-command-extractor-mcp
```

### 配置迁移

```python
# 配置升级脚本示例
def upgrade_config_v1_to_v2(old_config):
    new_config = old_config.copy()
    # 添加新字段
    for rule in new_config['detection_rules']['rules']:
        for subject in rule['subjects']:
            for content_rule in subject['content_rules']:
                if 'priority' not in content_rule['action']:
                    content_rule['action']['priority'] = 100
    return new_config
```

## 集成示例

### 与其他系统集成

```python
# 与任务管理系统集成
from task_manager import TaskManager

class EnhancedMcpServer(MailCommandExtractorMcpServer):
    def __init__(self):
        super().__init__()
        self.task_manager = TaskManager()
    
    def call_tool(self, name, arguments):
        result = super().call_tool(name, arguments)
        
        # 自动创建任务
        if result.get('success'):
            for command in result['data']['extracted_commands']:
                self.task_manager.create_task(command)
        
        return result
```

### 与通知系统集成

```python
# 发送处理结果通知
import smtplib

def send_notification(extracted_commands):
    msg = f"处理了{len(extracted_commands)}个命令"
    # 发送通知逻辑
```

## 技术支持

### 获取帮助

- 查看详细使用文档：`MAIL_COMMAND_EXTRACTOR_USAGE.md`
- 运行测试脚本：`python3 test_mail_command_extractor.py`
- 检查MCP服务器状态：`python3 mcp_server.py --test`

### 报告问题

提供以下信息：
- Python版本
- 操作系统
- 错误日志
- 测试结果
- 配置文件（去除敏感信息）

### 性能基准

在标准环境下的性能指标：
- 处理100封邮件：< 1秒
- 内存使用：< 50MB
- 启动时间：< 2秒