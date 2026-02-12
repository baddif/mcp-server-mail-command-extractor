"""
Framework Compatibility Layer for Mail Command Extractor Skill

Provides fallback implementations when the main framework is not available.
"""

from typing import Any, Dict, List, Protocol
from abc import abstractmethod


class ExecutionContext:
    """简单的执行上下文实现"""
    
    def __init__(self):
        self._data = {}
    
    def set(self, key: str, value: Any) -> None:
        """设置上下文数据"""
        self._data[key] = value
    
    def get(self, key: str, default: Any = None) -> Any:
        """获取上下文数据"""
        return self._data.get(key, default)
    
    def clear(self) -> None:
        """清空上下文"""
        self._data.clear()


class McpResource:
    """MCP资源定义"""
    
    def __init__(self, uri: str, name: str, description: str, mime_type: str = "text/plain", annotations: Dict[str, Any] = None):
        self.uri = uri
        self.name = name
        self.description = description
        self.mime_type = mime_type
        self.annotations = annotations or {}


class McpPrompt:
    """MCP提示定义"""
    
    def __init__(self, name: str, description: str, arguments: List[Dict[str, Any]] = None):
        self.name = name
        self.description = description
        self.arguments = arguments or []


class Skill(Protocol):
    """技能接口协议"""
    
    @abstractmethod
    def execute(self, ctx: ExecutionContext, **kwargs) -> Any:
        """执行技能"""
        pass


class McpCompatibleSkill(Skill):
    """MCP兼容的技能基类"""
    
    @abstractmethod
    def get_openai_schema(self) -> Dict[str, Any]:
        """返回OpenAI函数调用兼容的JSON Schema"""
        pass
    
    @abstractmethod
    def execute(self, ctx: ExecutionContext, **kwargs) -> Any:
        """执行技能"""
        pass
    
    def get_mcp_resources(self) -> List[McpResource]:
        """获取MCP资源（可选覆盖）"""
        return []
    
    def get_mcp_prompts(self) -> List[McpPrompt]:
        """获取MCP提示（可选覆盖）"""
        return []
    
    def read_resource(self, uri: str) -> Dict[str, Any]:
        """读取MCP资源（可选覆盖）"""
        return {
            "contents": [
                {
                    "uri": uri,
                    "mimeType": "text/plain",
                    "text": f"Resource {uri} not implemented"
                }
            ]
        }
    
    def get_prompt(self, name: str, arguments: Dict[str, Any] = None) -> Dict[str, Any]:
        """获取MCP提示（可选覆盖）"""
        return {
            "description": f"Prompt {name} not implemented",
            "messages": []
        }