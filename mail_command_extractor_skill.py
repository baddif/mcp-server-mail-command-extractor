"""
Mail Command Extractor Skill - 邮件内容检测并生成对应命令

Description:
    检测邮件内容并根据预定义的规则生成相应的命令。
    支持模糊匹配标题和内容语句，按优先级顺序处理命令。
    
Features:
    - 邮件来源和标题的模糊匹配
    - 内容语句检测和命令生成
    - 重复命令合并和优先级排序
    - 灵活的匹配规则配置
    
MCP Support:
    - Tools: mail_command_extractor
    - Resources: 2 resources
    - Prompts: 0 prompts
"""

from typing import Any, Dict, List, Optional
import re
import json
from datetime import datetime

try:
    from ldr.mcp.base import McpCompatibleSkill, McpResource
    from ldr.context import ExecutionContext
except ImportError:
    # Fallback to standalone implementation
    from skill_compat import McpCompatibleSkill, McpResource, ExecutionContext


class MailCommandExtractorSkill(McpCompatibleSkill):
    """
    邮件命令提取器技能
    
    根据预定义的邮件检测规则，从邮件列表中提取匹配的邮件并生成相应的命令。
    支持邮件来源、标题和内容的模糊匹配，按照定义顺序确定命令优先级。
    """
    
    @staticmethod
    def get_schema() -> Dict[str, Any]:
        """Return OpenAI Function Calling compatible JSON Schema"""
        return {
            "type": "function",
            "function": {
                "name": "mail_command_extractor",
                "description": "检测邮件内容并根据预定义规则生成相应命令。支持邮件来源、标题、内容的模糊匹配，自动合并重复命令并按优先级排序。",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "detection_rules": {
                            "type": "object",
                            "description": "邮件检测规则配置。包含邮件来源、标题匹配规则和对应的动作命令。",
                            "properties": {
                                "rules": {
                                    "type": "array",
                                    "description": "检测规则数组，按优先级顺序排列",
                                    "items": {
                                        "type": "object",
                                        "properties": {
                                            "sender": {
                                                "type": "string",
                                                "description": "邮件发送者地址（支持模糊匹配）"
                                            },
                                            "subjects": {
                                                "type": "array",
                                                "description": "标题匹配规则数组",
                                                "items": {
                                                    "type": "object",
                                                    "properties": {
                                                        "title_pattern": {
                                                            "type": "string",
                                                            "description": "标题匹配模式（包含关键词即可）"
                                                        },
                                                        "content_rules": {
                                                            "type": "array",
                                                            "description": "内容语句检测规则",
                                                            "items": {
                                                                "type": "object",
                                                                "properties": {
                                                                    "content_pattern": {
                                                                        "type": "string",
                                                                        "description": "内容匹配模式（包含关键词即可）"
                                                                    },
                                                                    "action": {
                                                                        "type": "object",
                                                                        "description": "匹配后执行的动作",
                                                                        "properties": {
                                                                            "command": {
                                                                                "type": "string",
                                                                                "description": "命令名称"
                                                                            },
                                                                            "parameters": {
                                                                                "type": "object",
                                                                                "description": "命令参数",
                                                                                "additionalProperties": True
                                                                            },
                                                                            "priority": {
                                                                                "type": "integer",
                                                                                "description": "命令优先级（数字越小优先级越高）",
                                                                                "default": 100
                                                                            }
                                                                        },
                                                                        "required": ["command"]
                                                                    }
                                                                },
                                                                "required": ["content_pattern", "action"]
                                                            }
                                                        }
                                                    },
                                                    "required": ["title_pattern", "content_rules"]
                                                }
                                            }
                                        },
                                        "required": ["sender", "subjects"]
                                    }
                                }
                            },
                            "required": ["rules"]
                        },
                        "email_list": {
                            "type": "object",
                            "description": "要检测的邮件列表，使用gmail_check输出的格式",
                            "properties": {
                                "matched_emails": {
                                    "type": "array",
                                    "description": "邮件数组",
                                    "items": {
                                        "type": "object",
                                        "properties": {
                                            "sender": {"type": "string"},
                                            "subject": {"type": "string"},
                                            "content": {"type": "string"},
                                            "date_received": {"type": "string"},
                                            "message_id": {"type": "string"},
                                            "email_id": {"type": "string"}
                                        },
                                        "required": ["sender", "subject", "content"]
                                    }
                                }
                            },
                            "required": ["matched_emails"]
                        },
                        "merge_duplicates": {
                            "type": "boolean",
                            "description": "是否合并重复命令（相同command和parameters的命令）",
                            "default": True
                        }
                    },
                    "required": ["detection_rules", "email_list"]
                }
            }
        }
    
    def get_openai_schema(self) -> Dict[str, Any]:
        """Return OpenAI Function Calling compatible JSON Schema"""
        return self.get_schema()
    
    def execute(self, ctx: ExecutionContext, **kwargs) -> Any:
        """
        执行邮件命令提取
        
        Args:
            ctx: 执行上下文
            **kwargs: 技能参数
            
        Returns:
            包含提取的命令列表的结果
        """
        try:
            detection_rules = kwargs.get("detection_rules", {})
            email_list = kwargs.get("email_list", {})
            merge_duplicates = kwargs.get("merge_duplicates", True)
            
            # 验证输入参数
            if "rules" not in detection_rules:
                return {
                    "success": False,
                    "function_name": "mail_command_extractor",
                    "error": {
                        "message": "detection_rules.rules is required",
                        "type": "validation_error"
                    }
                }
            
            # 处理空邮件列表或空规则的情况
            if not email_list.get("matched_emails") or not detection_rules.get("rules"):
                return {
                    "success": True,
                    "function_name": "mail_command_extractor",
                    "data": {
                        "extracted_commands": [],
                        "processed_emails": len(email_list.get("matched_emails", [])),
                        "matched_emails": 0,
                        "total_commands": 0,
                        "processing_time": datetime.utcnow().isoformat() + "Z"
                    },
                    "statistics": {
                        "rules_processed": len(detection_rules.get("rules", [])),
                        "emails_processed": len(email_list.get("matched_emails", [])),
                        "commands_generated": 0
                    }
                }
            
            # 提取命令
            extracted_commands = self._extract_commands(
                detection_rules["rules"], 
                email_list["matched_emails"]
            )
            
            # 合并重复命令
            if merge_duplicates:
                extracted_commands = self._merge_duplicate_commands(extracted_commands)
            
            # 按优先级排序
            extracted_commands = self._sort_by_priority(extracted_commands)
            
            result = {
                "extracted_commands": extracted_commands,
                "processed_emails": len(email_list["matched_emails"]),
                "matched_emails": len([cmd for cmd in extracted_commands if cmd.get("matched_emails")]),
                "total_commands": len(extracted_commands),
                "processing_time": datetime.utcnow().isoformat() + "Z"
            }
            
            # 存储到上下文
            ctx.set("skill:mail_command_extractor:result", result)
            
            return {
                "success": True,
                "function_name": "mail_command_extractor",
                "data": result,
                "statistics": {
                    "rules_processed": len(detection_rules["rules"]),
                    "emails_processed": len(email_list["matched_emails"]),
                    "commands_generated": len(extracted_commands)
                }
            }
            
        except Exception as e:
            return {
                "success": False,
                "function_name": "mail_command_extractor",
                "error": {
                    "message": str(e),
                    "type": "execution_error"
                }
            }
    
    def _extract_commands(self, rules: List[Dict], emails: List[Dict]) -> List[Dict]:
        """从邮件中提取命令"""
        extracted_commands = []
        
        for email in emails:
            sender = email.get("sender", "")
            subject = email.get("subject", "")
            content = email.get("content", "")
            
            # 提取发件人邮箱地址
            sender_email = self._extract_email_address(sender)
            
            for rule_index, rule in enumerate(rules):
                # 检查发件人匹配
                if not self._matches_sender(sender_email, rule["sender"]):
                    continue
                
                # 检查标题和内容匹配
                for subject_rule in rule["subjects"]:
                    if self._matches_pattern(subject, subject_rule["title_pattern"]):
                        # 检查内容规则
                        for content_rule in subject_rule["content_rules"]:
                            if self._matches_pattern(content, content_rule["content_pattern"]):
                                # 创建命令
                                command = {
                                    "command": content_rule["action"]["command"],
                                    "parameters": content_rule["action"].get("parameters", {}),
                                    "priority": content_rule["action"].get("priority", 100),
                                    "rule_index": rule_index,
                                    "matched_email": {
                                        "email_id": email.get("email_id"),
                                        "sender": sender,
                                        "subject": subject,
                                        "content": content,
                                        "date_received": email.get("date_received"),
                                        "message_id": email.get("message_id")
                                    },
                                    "matching_details": {
                                        "sender_pattern": rule["sender"],
                                        "title_pattern": subject_rule["title_pattern"],
                                        "content_pattern": content_rule["content_pattern"]
                                    }
                                }
                                extracted_commands.append(command)
        
        return extracted_commands
    
    def _extract_email_address(self, sender_field: str) -> str:
        """从发件人字段提取邮箱地址"""
        # 处理编码的发件人名称，提取邮箱地址
        import re
        email_match = re.search(r'<([^>]+)>', sender_field)
        if email_match:
            return email_match.group(1)
        
        # 如果没有尖括号，假设整个字符串就是邮箱地址
        email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', sender_field)
        if email_match:
            return email_match.group(0)
        
        return sender_field.strip()
    
    def _matches_sender(self, email_address: str, pattern: str) -> bool:
        """检查发件人是否匹配"""
        return pattern.lower() in email_address.lower()
    
    def _matches_pattern(self, text: str, pattern: str) -> bool:
        """检查文本是否匹配模式（模糊匹配）"""
        return pattern.lower() in text.lower()
    
    def _merge_duplicate_commands(self, commands: List[Dict]) -> List[Dict]:
        """合并重复的命令"""
        command_map = {}
        
        for cmd in commands:
            # 创建命令的唯一标识
            cmd_key = self._get_command_key(cmd)
            
            if cmd_key in command_map:
                # 合并邮件信息
                existing_cmd = command_map[cmd_key]
                if "matched_emails" not in existing_cmd:
                    existing_cmd["matched_emails"] = [existing_cmd.pop("matched_email")]
                existing_cmd["matched_emails"].append(cmd["matched_email"])
                
                # 保留较高的优先级（较小的数字）
                existing_cmd["priority"] = min(existing_cmd["priority"], cmd["priority"])
                existing_cmd["rule_index"] = min(existing_cmd["rule_index"], cmd["rule_index"])
            else:
                # 重命名单个邮件为邮件列表
                cmd["matched_emails"] = [cmd.pop("matched_email")]
                command_map[cmd_key] = cmd
        
        return list(command_map.values())
    
    def _get_command_key(self, command: Dict) -> str:
        """生成命令的唯一标识"""
        cmd_name = command["command"]
        params = command.get("parameters", {})
        params_str = json.dumps(params, sort_keys=True)
        return f"{cmd_name}:{params_str}"
    
    def _sort_by_priority(self, commands: List[Dict]) -> List[Dict]:
        """按优先级排序命令"""
        return sorted(commands, key=lambda x: (x["priority"], x["rule_index"]))
    
    def get_mcp_resources(self) -> List[McpResource]:
        """定义MCP资源"""
        return [
            McpResource(
                uri="skill://mail_command_extractor/latest_result",
                name="mail_command_extractor_result",
                description="最近一次邮件命令提取的结果",
                mime_type="application/json"
            ),
            McpResource(
                uri="skill://mail_command_extractor/config_template",
                name="mail_command_extractor_config",
                description="邮件命令提取的配置模板",
                mime_type="application/json"
            )
        ]
    
    def read_resource(self, uri: str) -> Dict[str, Any]:
        """读取MCP资源"""
        if uri == "skill://mail_command_extractor/latest_result":
            # 从上下文获取最新结果
            result = getattr(self, '_latest_result', {})
            return {
                "contents": [
                    {
                        "uri": uri,
                        "mimeType": "application/json",
                        "text": json.dumps(result, ensure_ascii=False, indent=2)
                    }
                ]
            }
        
        elif uri == "skill://mail_command_extractor/config_template":
            template = self._get_config_template()
            return {
                "contents": [
                    {
                        "uri": uri,
                        "mimeType": "application/json",
                        "text": json.dumps(template, ensure_ascii=False, indent=2)
                    }
                ]
            }
        
        return {
            "contents": [
                {
                    "uri": uri,
                    "mimeType": "text/plain",
                    "text": f"Resource {uri} not found"
                }
            ]
        }
    
    def _get_config_template(self) -> Dict[str, Any]:
        """获取配置模板"""
        return {
            "detection_rules": {
                "rules": [
                    {
                        "sender": "example@gmail.com",
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
                                                "language": "Chinese"
                                            },
                                            "priority": 10
                                        }
                                    }
                                ]
                            },
                            {
                                "title_pattern": "周报",
                                "content_rules": [
                                    {
                                        "content_pattern": "生成周报",
                                        "action": {
                                            "command": "generate_weekly_report",
                                            "parameters": {
                                                "type": "weekly",
                                                "language": "Chinese"
                                            },
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
                        "sender": "example@gmail.com",
                        "subject": "日报",
                        "content": "请生成今天的日报",
                        "date_received": "2026-02-12T15:20:17+08:00",
                        "message_id": "example-message-id",
                        "email_id": "example-email-id"
                    }
                ]
            },
            "merge_duplicates": True
        }