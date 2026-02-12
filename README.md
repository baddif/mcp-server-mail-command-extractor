# Mail Command Extractor - MCP Server

一个基于Model Context Protocol (MCP)的邮件命令提取器，用于检测邮件内容并生成对应的处理命令。

## 🚀 功能特性

- 🔍 **智能邮件检测**: 支持邮件发送者、标题和内容的模糊匹配
- ⚡ **命令自动生成**: 根据预定义规则自动生成处理命令
- 🔄 **重复命令合并**: 自动合并相同的命令，避免重复执行
- 📊 **优先级排序**: 按照定义顺序和优先级对命令进行排序
- 🛠️ **MCP协议支持**: 完整的Model Context Protocol支持
- 🔌 **AI代理集成**: 与Claude Desktop等AI代理无缝集成

## 📦 快速安装

```bash
# 克隆项目
git clone https://github.com/baddif/mcp-server-mail-command-extractor.git
cd mcp-server-mail-command-extractor

# 自动安装
chmod +x install.sh
./install.sh

# 或手动安装
python3 test_mail_command_extractor.py
python3 mcp_server.py --test
```

## 🔧 配置

### 创建本地配置

```bash
cp mail_command_extractor_config_example.json mail_command_extractor_config_local.json
```

### 编辑配置文件

```json
{
  "detection_rules": {
    "rules": [
      {
        "sender": "boss@company.com",
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
    "matched_emails": [...]
  }
}
```

## 🤖 AI代理集成

### Claude Desktop

1. 编辑配置文件：
   - macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
   - Windows: `%APPDATA%\Claude\claude_desktop_config.json`

2. 添加MCP服务器配置：
```json
{
  "mcpServers": {
    "mail-command-extractor": {
      "command": "python3",
      "args": ["/path/to/mcp_server.py"],
      "env": {
        "PYTHONPATH": "/path/to/mcp-server-mail-command-extractor"
      }
    }
  }
}
```

3. 重启Claude Desktop

## 💡 使用示例

### 基本用法

```bash
# 启动MCP服务器
python3 mcp_server.py

# 测试功能
python3 mcp_server.py --test
```

### 在AI对话中使用

```
使用mail_command_extractor工具处理邮件：

{
  "detection_rules": {...},
  "email_list": {...},
  "merge_duplicates": true
}
```

## 📖 详细文档

- [使用指南](MAIL_COMMAND_EXTRACTOR_USAGE.md) - 详细的使用说明和配置
- [MCP部署指南](MCP_DEPLOYMENT.md) - MCP服务器部署和集成
- [技能生成规则](SKILL_GENERATION_RULES.md) - 技能开发规范

## 🧪 测试

```bash
# 运行所有测试
python3 test_mail_command_extractor.py

# 测试MCP服务器
python3 mcp_server.py --test
```

## 📁 项目结构

```
mcp-server-mail-command-extractor/
├── mail_command_extractor_skill.py    # 主要技能实现
├── mcp_server.py                      # MCP协议服务器
├── skill_compat.py                    # 框架兼容层
├── test_mail_command_extractor.py     # 测试脚本
├── mail_command_extractor_config_example.json  # 配置示例
├── mail_command_extractor_config_local.json    # 本地配置
├── install.sh                         # 安装脚本
├── MCP_DEPLOYMENT.md                  # 部署指南
├── MAIL_COMMAND_EXTRACTOR_USAGE.md    # 使用指南
└── README.md                          # 项目说明
```

## 🔍 工作原理

1. **邮件检测**: 根据发件人、标题和内容进行模糊匹配
2. **规则匹配**: 按照优先级顺序匹配预定义的检测规则  
3. **命令生成**: 为匹配的邮件生成相应的处理命令
4. **重复合并**: 自动合并相同的命令避免重复执行
5. **结果排序**: 按照优先级和规则顺序对命令进行排序

## 🛡️ 安全说明

- 本地配置文件 (`*_config_local.json`) 不会被提交到Git
- 配置文件中避免包含敏感信息
- MCP服务器仅处理结构化的数据，不执行任意代码

## 🤝 贡献

欢迎提交Issues和Pull Requests来改进这个项目。

## 📄 许可证

本项目采用MIT许可证，详见 [LICENSE](LICENSE) 文件。

## 🔗 相关链接

- [Model Context Protocol](https://modelcontextprotocol.io/)
- [Claude Desktop](https://claude.ai/desktop)
- [OpenAI Function Calling](https://platform.openai.com/docs/guides/function-calling)
Extract commands from mails
