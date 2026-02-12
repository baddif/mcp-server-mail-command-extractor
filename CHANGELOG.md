# Changelog

All notable changes to Mail Command Extractor MCP Server will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.2.0] - 2026-02-12

### 🆕 Added
- **sender_email字段支持**: 新增精确邮件地址匹配机制
- **精确匹配功能**: 避免模糊匹配可能产生的误匹配
- **降级处理机制**: 缺失sender_email时自动从sender字段解析
- **专门测试套件**: test_sender_email_feature.py验证新功能
- **真实数据验证**: 支持gmail_check_output格式的sender_email字段

### 🔧 Improved
- **Schema增强**: 邮件列表Schema新增sender_email字段描述
- **匹配精度**: sender规则现在进行精确匹配而非模糊匹配
- **向后兼容**: 完全兼容没有sender_email字段的旧数据格式
- **错误处理**: 增强邮件地址解析的鲁棒性

### 🐛 Fixed
- **匹配准确性**: 解决sender字段模糊匹配可能的误判问题
- **数据完整性**: 确保匹配结果包含完整的sender_email信息

### 📚 Documentation
- **测试用例**: 完整的sender_email功能测试和验证
- **使用说明**: 新字段的使用指南和最佳实践
- **Schema文档**: 更新API文档说明精确匹配行为

## [1.1.0] - 2026-02-12

### 🆕 Added
- Enhanced empty input handling with clear reason reporting
- Time-based command merging to avoid duplicate execution
- Advanced date parsing supporting multiple formats and timezones
- Safe error handling for edge cases in date processing
- Empty input reason tracking in API responses

### 🔧 Improved
- Command merging now sorts by time (newest first)
- Enhanced duplicate detection based on command + parameters
- Robust date parsing with fallback mechanisms
- Better error handling for year boundary issues
- Improved sorting algorithm with time prioritization

### 🐛 Fixed
- Fixed "year 0 is out of range" error in date parsing
- Resolved timestamp calculation issues for edge cases
- Corrected empty list handling in command processing
- Fixed timezone parsing edge cases

### 📚 Documentation
- Updated SKILL_GENERATION_RULES.md with version control standards (v2.1.0)
- Enhanced code comments for date handling functions
- Improved test coverage documentation

## [1.0.0] - 2026-02-12log

All notable changes to the Mail Command Extractor MCP Server project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-02-12

### 🆕 Added
- **Intelligent Email Detection**: Advanced pattern matching for sender, subject, and content
- **Command Generation**: Automatic command generation based on detection rules
- **Fuzzy Pattern Matching**: Flexible keyword-based matching for all email components
- **Priority-based Sorting**: Commands sorted by priority and rule order
- **Duplicate Command Merging**: Automatic merging of identical commands to avoid duplication
- **MCP Protocol Support**: Full Model Context Protocol compatibility with tools and resources
- **Multi-rule Processing**: Support for complex detection rules with multiple conditions
- **Context-aware Processing**: Smart context handling for data sharing between operations
- **Version Control System**: Complete version management with automatic update capabilities

### 🔧 Features
- **Email Source Matching**: Pattern matching for email sender addresses
- **Subject Line Detection**: Fuzzy matching for email subject patterns
- **Content Analysis**: Intelligent content pattern recognition
- **Rule-based Actions**: Configurable actions triggered by pattern matches
- **Command Parameters**: Rich parameter support for generated commands
- **Configuration Templates**: Pre-built configuration examples and templates
- **Resource Access**: MCP resources for configuration and results

### 📚 Documentation
- Comprehensive README.md with installation and usage instructions
- Detailed usage guide (MAIL_COMMAND_EXTRACTOR_USAGE.md)
- MCP deployment guide (MCP_DEPLOYMENT.md)
- Skill generation rules documentation (SKILL_GENERATION_RULES.md)
- Configuration examples and templates

### 🧪 Testing
- Complete test suite for skill functionality
- MCP server integration tests
- End-to-end workflow testing
- Communication protocol validation
- Error handling verification

### 🚀 Deployment
- Automated installation script
- MCP server with stdio transport
- Claude Desktop integration configuration
- Framework compatibility layer
- Cross-platform support (macOS, Linux, Windows)

### 🔧 Technical Implementation
- OpenAI Function Calling JSON Schema compliance
- MCP Tools and Resources implementation
- Standalone operation capability
- Framework-agnostic design
- Error handling and validation
- Context management system

### 📊 Performance
- Efficient pattern matching algorithms
- Optimized command generation
- Minimal memory footprint
- Fast startup and response times

### 🔒 Security
- Input validation and sanitization
- Safe configuration file handling
- No external dependencies for core functionality
- Local configuration file exclusion from version control

### 🛠️ Developer Experience
- Clear API documentation
- Comprehensive error messages
- Detailed logging capabilities
- Extensible architecture
- Well-commented code base