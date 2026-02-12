# Mail Command Extractor MCP Server - 版本控制与用户更新指南

## 📋 概述

Mail Command Extractor MCP Server 现已配备完整的版本控制系统，为已安装的用户提供简单、安全的更新机制。

## 🚀 快速更新

### 最简单的更新方法

```bash
# 进入项目目录
cd mcp-server-mail-command-extractor

# 一键自动更新
./update.sh
```

该脚本会：
- 📋 自动备份您的配置文件
- 🔍 检查更新可用性
- ⬇️ 下载最新代码
- 📦 更新依赖包
- ✅ 验证更新结果
- 🔄 恢复您的个人配置

### 使用版本管理工具

```bash
# 检查当前版本
python3 version.py --info

# 检查是否有更新
python3 version.py --check-updates

# 自动更新
python3 version.py --update
```

## 📊 版本信息查看

### 基本版本信息
```bash
python3 version.py --version
```

### 详细版本信息
```bash
python3 version.py --info
```

### JSON格式输出（用于编程集成）
```bash
python3 version.py --json
```

## 🔧 手动更新步骤

如果自动更新失败，可以按照以下步骤手动更新：

### 1. 备份配置文件
```bash
# 备份本地配置
cp mail_command_extractor_config_local.json mail_command_extractor_config_local.json.backup

# 备份其他个人文件（如果有）
cp claude_desktop_config.json claude_desktop_config.json.backup
```

### 2. 更新代码
```bash
# 获取最新代码
git fetch origin main
git pull origin main

# 或者如果有合并冲突
git stash  # 临时保存本地更改
git pull origin main
git stash pop  # 恢复本地更改
```

### 3. 更新依赖
```bash
# 更新Python包（如果requirements.txt有更改）
pip3 install -r requirements.txt --upgrade
```

### 4. 验证更新
```bash
# 运行测试确保更新成功
python3 test_mail_command_extractor.py

# 测试MCP服务器
python3 mcp_server.py --test
```

### 5. 恢复配置
```bash
# 如果配置文件被覆盖，恢复备份
cp mail_command_extractor_config_local.json.backup mail_command_extractor_config_local.json
```

## 🔍 更新检查机制

### 自动检查
系统会定期检查：
- 🏷️ Git标签版本
- 📊 提交落后数量
- 🔄 远程仓库状态

### 手动检查
```bash
# 检查更新状态
python3 version.py --check-updates

# 查看Git状态
git status
git log --oneline -5  # 查看最近5个提交
```

## ⚠️ 注意事项与故障排除

### 更新前检查清单
- [ ] 备份重要的配置文件
- [ ] 确保没有正在运行的MCP服务器进程
- [ ] 检查本地是否有未提交的更改
- [ ] 确保网络连接正常

### 常见问题解决

#### 问题1：Git合并冲突
```bash
# 查看冲突文件
git status

# 解决冲突后
git add .
git commit -m "Resolve merge conflicts"
```

#### 问题2：权限问题
```bash
# 给更新脚本添加执行权限
chmod +x update.sh

# 或者使用Python直接运行
python3 version.py --update
```

#### 问题3：依赖安装失败
```bash
# 尝试使用用户安装模式
pip3 install -r requirements.txt --user --upgrade

# 或者使用虚拟环境
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

#### 问题4：测试失败
```bash
# 查看详细错误信息
python3 test_mail_command_extractor.py -v

# 检查配置文件
python3 -c "import json; print(json.load(open('mail_command_extractor_config_local.json')))"
```

### 紧急恢复

如果更新导致系统不稳定：

```bash
# 1. 回滚到上一个稳定版本
git log --oneline -10  # 查找稳定的提交
git reset --hard <commit-hash>

# 2. 或者重新克隆项目
cd ..
git clone https://github.com/baddif/mcp-server-mail-command-extractor.git mcp-server-mail-command-extractor-new
cd mcp-server-mail-command-extractor-new

# 3. 恢复配置文件
cp ../mcp-server-mail-command-extractor/mail_command_extractor_config_local.json.backup ./mail_command_extractor_config_local.json
```

## 📈 版本发布周期

### 版本命名规范
- **主版本 (Major)**: 重大功能变更或不兼容更新
- **次版本 (Minor)**: 新功能添加，向后兼容
- **修订版本 (Patch)**: 错误修复和小改进

### 示例版本号
- `1.0.0` - 初始发布
- `1.1.0` - 添加新功能
- `1.1.1` - 错误修复
- `2.0.0` - 重大更新（可能不兼容）

### 发布通知渠道
- 📢 GitHub Release页面
- 📝 CHANGELOG.md更新记录
- 🔔 项目README.md通知

## 🤝 社区支持

### 获取帮助
- 📖 查看文档：[README.md](README.md)
- 🐛 报告问题：GitHub Issues
- 💬 讨论功能：GitHub Discussions

### 贡献代码
- 🍴 Fork项目
- 🌿 创建功能分支
- 📝 提交Pull Request

## 🔄 配置迁移指南

### 配置文件变更
当新版本引入配置格式变更时：

```bash
# 检查配置文件兼容性
python3 -c "
from mail_command_extractor_skill import MailCommandExtractorSkill
import json
with open('mail_command_extractor_config_local.json') as f:
    config = json.load(f)
    skill = MailCommandExtractorSkill()
    # 验证配置格式
    try:
        result = skill.execute(None, **config)
        print('✅ 配置文件兼容')
    except Exception as e:
        print(f'❌ 配置需要更新: {e}')
"
```

### 自动配置迁移
```bash
# 运行配置迁移工具（如果有）
python3 migrate_config.py --from-version 1.0.0 --to-version 1.1.0
```

---

**📞 需要帮助？**

如果更新过程中遇到问题，请：
1. 查看本指南的故障排除部分
2. 检查GitHub Issues中的相关问题
3. 创建新的Issue描述您的问题

我们致力于让更新过程尽可能简单和可靠！