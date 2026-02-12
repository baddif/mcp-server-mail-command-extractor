# Skill Generation Rules for AI-Powered Applications

**Version**: 2.0.0  
**Last Updated**: 2026-02-11  
**Purpose**: AI-readable specification for generating new skills compatible with modern AI frameworks

---

## Overview

This document defines the complete standards and requirements for creating skills in AI-powered applications. Skills must support both **OpenAI Function Calling** and **MCP (Model Context Protocol)** standards for maximum compatibility across different AI agents and platforms.

### Dual Standard Support

All modern skills should implement:
1. **OpenAI Function Calling** - JSON Schema based function definitions
2. **MCP (Model Context Protocol)** - Tools, Resources, and Prompts interfaces
3. **Standalone Operation** - Independent execution without framework dependencies

---

## 1. Core Skill Interface

### 1.1 Base Protocol

Every skill MUST implement the `Skill` protocol:

```python
from typing import Protocol, Any
from ..context import ExecutionContext

class Skill(Protocol):
    """Skill interface. Each skill must implement execute(ctx, **kwargs) -> Any"""
    
    def execute(self, ctx: ExecutionContext, **kwargs) -> Any:
        ...
```

### 1.2 MCP Compatible Skill (Recommended)

For full MCP support, extend `McpCompatibleSkill`:

```python
# Framework compatibility layer
try:
    from framework.mcp.base import McpCompatibleSkill
    from framework.context import ExecutionContext
except ImportError:
    # Fallback to standalone implementation
    from skill_compat import McpCompatibleSkill, ExecutionContext

class YourSkill(McpCompatibleSkill):
    
    @abstractmethod
    def get_openai_schema(self) -> Dict[str, Any]:
        """Return OpenAI Function Calling compatible JSON Schema"""
        pass
    
    @abstractmethod
    def execute(self, ctx, **kwargs) -> Any:
        """Execute the skill with given parameters"""
        pass
    
    # Optional: Override for MCP Resources
    def get_mcp_resources(self) -> List[McpResource]:
        return []
    
    # Optional: Override for MCP Prompts
    def get_mcp_prompts(self) -> List[McpPrompt]:
        return []

### 1.3 Standalone MCP Server Implementation

Every skill should include a standalone MCP server for AI agent integration:

```python
#!/usr/bin/env python3
"""
MCP Server for [Skill Name]

Provides Model Context Protocol (MCP) server implementation
for AI agent integration.
"""

import json
import sys
import asyncio
from typing import Any, Dict, List

class SkillMcpServer:
    """MCP Server implementation"""
    
    def __init__(self):
        self.skill = YourSkill()
        self.context = ExecutionContext()
    
    def get_server_info(self) -> Dict[str, Any]:
        return {
            "name": "skill-mcp-server",
            "version": "1.0.0", 
            "description": "MCP server for [skill description]",
            "capabilities": {
                "tools": True,
                "resources": True,
                "prompts": False
            }
        }
    
    def list_tools(self) -> List[Dict[str, Any]]:
        schema = self.skill.get_openai_schema()
        return [{
            "name": schema["function"]["name"],
            "description": schema["function"]["description"],
            "inputSchema": schema["function"]["parameters"]
        }]
    
    def call_tool(self, name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        result = self.skill.execute(self.context, **arguments)
        if result.get("success"):
            return {
                "content": [{
                    "type": "text", 
                    "text": json.dumps(result, ensure_ascii=False, indent=2)
                }]
            }
        else:
            return {
                "error": result.get("error", {}).get("message", "Unknown error")
            }

# Standard MCP server entry point
async def main():
    server = SkillMcpServer()
    # Implement stdio transport for MCP communication
    # See full implementation in project examples
    
if __name__ == "__main__":
    asyncio.run(main())
```
        pass
    
    @abstractmethod
    def execute(self, ctx, **kwargs) -> Any:
        """Execute the skill with given parameters"""
        pass
    
    # Optional: Override for MCP Resources
    def get_mcp_resources(self) -> List[McpResource]:
        return []
    
    # Optional: Override for MCP Prompts
    def get_mcp_prompts(self) -> List[McpPrompt]:
        return []
```

---

## 2. OpenAI Function Calling JSON Schema

### 2.1 Standard Schema Structure

All skills MUST provide a `get_schema()` or `get_openai_schema()` method returning:

```python
{
    "type": "function",
    "function": {
        "name": "skill_name",              # Snake_case, lowercase
        "description": "Detailed description",  # What the skill does
        "parameters": {
            "type": "object",
            "properties": {
                "param_name": {
                    "type": "string|integer|boolean|object|array",
                    "description": "Parameter description",
                    "default": None,        # Optional default value
                    "enum": [],            # Optional: allowed values
                    "minimum": 0,          # Optional: for integers
                    "maximum": 100         # Optional: for integers
                }
            },
            "required": ["required_param"]  # List of required parameters
        }
    }
}
```

### 2.2 Schema Best Practices

#### Naming Conventions
- **Skill names**: `snake_case`, descriptive (e.g., `git_reader`, `daily_report`)
- **Parameter names**: `snake_case`, clear purpose (e.g., `include_uncommitted`, `snapshot_name`)

#### Description Guidelines
- **Function description**: 1-3 sentences explaining purpose and capabilities
- **Parameter description**: Clear explanation including behavior and constraints
- **Mention language support** explicitly if AI-powered
- **Specify defaults** clearly in descriptions

#### Type Specifications
- Use appropriate JSON Schema types: `string`, `integer`, `boolean`, `object`, `array`
- Add constraints: `minimum`, `maximum`, `enum`, `pattern`
- Set sensible defaults for optional parameters

### 2.3 Example: Complete Schema

```python
@staticmethod
def get_schema() -> Dict[str, Any]:
    """Return OpenAI Function Calling compatible JSON Schema"""
    return {
        "type": "function",
        "function": {
            "name": "git_reader",
            "description": "Extract Git repository commits and changes information. Pure data extraction without AI processing. Provides structured data for other AI-powered skills like git_summary.",
            "parameters": {
                "type": "object",
                "properties": {
                    "username": {
                        "type": "string",
                        "description": "Git username/email to filter commits. If not provided, uses current Git user automatically detected from repository configuration.",
                        "default": None
                    },
                    "include_uncommitted": {
                        "type": "boolean",
                        "description": "Whether to include uncommitted changes (staged and unstaged files) in the analysis results.",
                        "default": True
                    }
                },
                "required": []  # Both parameters are optional
            }
        }
    }
```

---

## 3. Input Parameters Specification

### 3.1 Common Parameter Types

#### Path Parameters
```python
"path": {
    "type": "string",
    "description": "Absolute or relative file/directory path",
    "default": "."  # Current directory
}
```

#### Boolean Flags
```python
"include_uncommitted": {
    "type": "boolean",
    "description": "Whether to include uncommitted changes",
    "default": True
}
```

#### Language Parameters (AI Skills)
```python
"language": {
    "type": "string",
    "description": "Language for output generation. Supports 'Chinese' (default, 中文) or 'English' only.",
    "default": "Chinese",
    "enum": ["Chinese", "English"]
}
```

#### Template Parameters (AI Skills)
```python
"template": {
    "type": "string",
    "description": "Custom prompt template. Use {placeholder1}, {placeholder2} as placeholders. If not provided, uses built-in templates.",
    "default": None
}
```

#### Numeric Parameters
```python
"days": {
    "type": "integer",
    "description": "Number of days to analyze",
    "default": 1,
    "minimum": 1,
    "maximum": 30
}
```

### 3.2 Parameter Design Principles

1. **Sensible Defaults**: Every optional parameter should have a useful default
2. **Clear Constraints**: Use `enum`, `minimum`, `maximum` to validate inputs
3. **Self-Documenting**: Descriptions should explain purpose, behavior, and defaults
4. **Minimal Required**: Only mark parameters as `required` if absolutely necessary

---

## 4. MCP (Model Context Protocol) Standard Support

### 4.1 MCP Components

Skills can provide three types of MCP components:

#### Tools (Functions)
- Automatically generated from OpenAI schema
- Represents executable functionality

#### Resources (Data Access)
- Read-only data endpoints
- URI-based addressing
- Optional caching support

#### Prompts (Templates)
- Structured prompt templates
- Can accept arguments
- Return formatted messages

### 4.2 MCP Tool Definition

Tools are automatically converted from OpenAI schemas:

```python
from ldr.mcp.base import McpTool

def get_mcp_tool(self) -> McpTool:
    """Convert to MCP Tool format"""
    openai_schema = self.get_openai_schema()
    return McpTool.from_openai_schema(openai_schema)
```

Result format:
```json
{
    "name": "skill_name",
    "description": "Skill description",
    "inputSchema": {
        "type": "object",
        "properties": {...},
        "required": [...]
    }
}
```

### 4.3 MCP Resources

Define accessible data sources:

```python
from ldr.mcp.base import McpResource

def get_mcp_resources(self) -> List[McpResource]:
    """Define MCP Resources for this skill"""
    return [
        McpResource(
            uri="skill://skill_name/resource-name",
            name="resource_name",
            description="Description of the resource",
            mime_type="application/json",  # or "text/plain", "text/html"
            annotations={
                "cached": True  # Optional: enable caching
            }
        )
    ]
```

#### Resource URI Conventions

Follow these URI patterns:
- `git://repository/*` - Git repository data
- `git://summary/*` - Git summary data
- `report://daily/*` - Daily report data
- `skill://[skill_name]/*` - Skill-specific resources
- `file://[path]` - File system resources
- `directory://[path]` - Directory resources

#### Common Resource Types

1. **Data Resources**: Current state data (JSON)
2. **Status Resources**: System/skill status (JSON)
3. **Template Resources**: Prompt templates (text)
4. **Content Resources**: Generated content (text/JSON)

### 4.4 MCP Prompts

Define prompt templates:

```python
from ldr.mcp.base import McpPrompt

def get_mcp_prompts(self) -> List[McpPrompt]:
    """Define MCP Prompts for this skill"""
    return [
        McpPrompt(
            name="skill_name_chinese",
            description="Chinese language prompt for skill_name",
            arguments=[
                {
                    "name": "context",
                    "description": "Additional context for generation",
                    "required": False
                }
            ]
        )
    ]
```

#### Prompt Naming Conventions
- `[skill]_chinese` - Chinese language prompts
- `[skill]_english` - English language prompts  
- `[skill]_template` - Template retrieval prompts
- `[skill]_analysis` - Analysis/generation prompts

---

## 5. Skill Categories and Patterns

### 5.1 Data Extraction Skills

**Purpose**: Pure data retrieval without AI processing

**Characteristics**:
- No `language` parameter
- No `template` parameter
- Focus on structured data output
- Deterministic results

**Example**: `GitReaderSkill`, `FileSkill`, `DirectorySkill`

**Schema Pattern**:
```python
{
    "name": "data_reader",
    "description": "Extract data from source. Pure data extraction without AI processing.",
    "parameters": {
        "properties": {
            "source": {"type": "string", "description": "Data source path"},
            "include_metadata": {"type": "boolean", "default": True}
        },
        "required": ["source"]
    }
}
```

### 5.2 AI-Powered Analysis Skills

**Purpose**: Intelligent processing and generation using AI

**Characteristics**:
- MUST include `language` parameter with `enum: ["Chinese", "English"]`
- SHOULD include `template` parameter for customization
- MAY include `include_context` for historical data
- Non-deterministic results

**Example**: `GitSummarySkill`, `DailyReportSkill`

**Schema Pattern**:
```python
{
    "name": "ai_analyzer",
    "description": "Analyze data and generate AI-powered insights. Supports Chinese (default) and English languages with built-in templates.",
    "parameters": {
        "properties": {
            "data": {"type": "object", "description": "Input data to analyze"},
            "language": {
                "type": "string",
                "description": "Language for output. Supports 'Chinese' (default) or 'English' only.",
                "default": "Chinese",
                "enum": ["Chinese", "English"]
            },
            "template": {
                "type": "string",
                "description": "Custom prompt template. Use {data}, {language} as placeholders.",
                "default": None
            }
        },
        "required": ["data"]
    }
}
```

### 5.3 File System Skills

**Purpose**: File and directory operations

**Characteristics**:
- `path` parameter (required)
- Optional `read` or `recurse` flags
- Metadata extraction
- Snapshot support (optional)

**Example**: `FileSkill`, `DirectorySkill`

### 5.4 Reporting Skills

**Purpose**: Generate comprehensive reports

**Characteristics**:
- Combine multiple data sources
- Multi-language support
- Template customization
- Context awareness
- Structured output (often JSON)

**Example**: `DailyReportSkill`

---

## 6. Implementation Requirements

### 6.1 Execution Method

All skills MUST implement:

```python
def execute(self, ctx: ExecutionContext, **kwargs) -> Any:
    """
    Execute the skill with given parameters
    
    Args:
        ctx: Execution context for storing and retrieving shared data
        **kwargs: Parameters matching the schema definition
        
    Returns:
        Skill-specific result (dict, list, string, etc.)
    """
    pass
```

### 6.2 Return Value Standards

#### Success Response (Data Skills)
```python
{
    "success": True,
    "function_name": "skill_name",
    "data": {
        # Structured data here
    },
    "statistics": {
        # Summary statistics
    }
}
```

#### Success Response (AI Skills)
```python
{
    "success": True,
    "function_name": "skill_name",
    "result": "Generated content...",
    "metadata": {
        "language": "Chinese",
        "template_used": "built-in",
        "timestamp": "2026-02-11T08:00:00Z"
    }
}
```

#### Error Response
```python
{
    "success": False,
    "function_name": "skill_name",
    "error": {
        "message": "Error description",
        "type": "execution_error|validation_error|file_not_found"
    }
}
```

### 6.3 Context Usage

Use ExecutionContext to share data between skills:

```python
# Store data
ctx.set("skill:skill_name:key", value)

# Retrieve data
value = ctx.get("skill:skill_name:key")

# Common patterns
ctx.set(f"skill:{skill_name}:result", result)
ctx.set(f"file:{path}", file_metadata)
ctx.set(f"git:summary", git_summary)
```

### 6.4 Error Handling

```python
def execute(self, ctx: ExecutionContext, **kwargs) -> Any:
    try:
        # Validate inputs
        if not validate_params(kwargs):
            return {
                "success": False,
                "error": {"message": "Invalid parameters", "type": "validation_error"}
            }
        
        # Execute logic
        result = perform_operation(**kwargs)
        
        # Store in context
        ctx.set(f"skill:{self.__class__.__name__}:result", result)
        
        return {
            "success": True,
            "function_name": "skill_name",
            "data": result
        }
        
    except FileNotFoundError as e:
        return {
            "success": False,
            "error": {"message": str(e), "type": "file_not_found"}
        }
    except Exception as e:
        return {
            "success": False,
            "error": {"message": str(e), "type": "execution_error"}
        }
```

---

## 7. Language Support Implementation

### 7.1 Multi-Language Skills

For AI-powered skills requiring language support:

#### Schema Definition
```python
"language": {
    "type": "string",
    "description": "Language for output. Supports 'Chinese' (default, 中文) or 'English' only.",
    "default": "Chinese",
    "enum": ["Chinese", "English"]
}
```

#### Built-in Templates
```python
TEMPLATES = {
    "Chinese": """
基于以下数据生成中文摘要：
数据：{data}
要求：{requirements}
""",
    "English": """
Generate an English summary based on the following data:
Data: {data}
Requirements: {requirements}
"""
}

def get_template(self, language: str, custom_template: str = None) -> str:
    """Get template for specified language"""
    if custom_template:
        return custom_template
    return TEMPLATES.get(language, TEMPLATES["Chinese"])
```

#### Template Placeholders

Common placeholders:
- `{language}` - Target language
- `{data}` - Input data
- `{commits}` - Git commits (for git skills)
- `{changes}` - Git changes (for git skills)
- `{git_summary}` - Git summary (for report skills)
- `{statistics}` - Statistical data
- `{context}` - Historical context

### 7.2 Template Internalization

**Best Practice**: Internalize templates in code, not external files

Reasons:
1. No file I/O overhead
2. Easier deployment
3. Version control with code
4. No missing file errors

---

## 8. MCP Resource Implementation

### 8.1 Read Resource Method

```python
def read_resource(self, uri: str) -> Dict[str, Any]:
    """
    MCP resource read interface
    
    Args:
        uri: Resource URI (e.g., "skill://skill_name/resource")
        
    Returns:
        MCP resource response
    """
    # Parse URI
    if uri == "skill://skill_name/data":
        return {
            "contents": [
                {
                    "uri": uri,
                    "mimeType": "application/json",
                    "text": json.dumps(self.get_data())
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
```

### 8.2 Resource Caching

For static or slowly-changing resources:

```python
McpResource(
    uri="skill://skill_name/static-data",
    name="static_data",
    description="Static reference data",
    mime_type="application/json",
    annotations={
        "cached": True,  # Enable caching
        "ttl": 3600     # Cache TTL in seconds (optional)
    }
)
```

---

## 9. MCP Prompt Implementation

### 9.1 Get Prompt Method

```python
def get_prompt(self, name: str, arguments: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    MCP prompt get interface
    
    Args:
        name: Prompt name
        arguments: Optional prompt arguments
        
    Returns:
        MCP prompt response with messages
    """
    arguments = arguments or {}
    
    if name == "skill_name_chinese":
        template = self.get_chinese_template()
        return {
            "description": "Generate Chinese output",
            "messages": [
                {
                    "role": "user",
                    "content": {
                        "type": "text",
                        "text": template.format(**arguments)
                    }
                }
            ]
        }
    
    return {
        "description": f"Prompt {name} not found",
        "messages": []
    }
```

---

## 10. Testing Requirements

### 10.1 Schema Validation

Test that schema is valid:

```python
def test_schema_validity():
    schema = YourSkill.get_schema()
    assert "function" in schema
    assert "name" in schema["function"]
    assert "description" in schema["function"]
    assert "parameters" in schema["function"]
```

### 10.2 Execution Tests

Test skill execution:

```python
def test_skill_execution():
    skill = YourSkill()
    ctx = ExecutionContext()
    result = skill.execute(ctx, param1="value1")
    assert result is not None
    assert "success" in result
```

### 10.3 MCP Compatibility Tests

Test MCP interfaces:

```python
def test_mcp_compatibility():
    skill = YourSkill()
    
    # Test tool conversion
    tool = skill.get_mcp_tool()
    assert tool.name == "your_skill"
    
    # Test resources
    resources = skill.get_mcp_resources()
    assert isinstance(resources, list)
    
    # Test prompts
    prompts = skill.get_mcp_prompts()
    assert isinstance(prompts, list)
```

---

## 11. MCP Server Deployment Standards

### 11.1 Required Files for MCP Skills

Every MCP-compatible skill project MUST include:

#### Core Implementation Files
- `{skill_name}_skill.py` - Main skill implementation
- `mcp_server.py` - MCP server with stdio transport
- `skill_compat.py` - Framework compatibility layer

#### Configuration Files  
- `mcp_config.json` - MCP client configuration template
- `{skill_name}_config_example.json` - Configuration example
- `claude_desktop_config.json` - Claude Desktop integration

#### Deployment Files
- `install.sh` - Automated installation script
- `requirements.txt` - Python dependencies
- `.gitignore` - Security and cache exclusions

#### Documentation Files
- `MCP_DEPLOYMENT.md` - Deployment and integration guide
- `README.md` - Project overview and usage
- `{SKILL_NAME}_USAGE.md` - Detailed skill documentation

### 11.2 MCP Server Template

```python
#!/usr/bin/env python3
"""
MCP Server for {Skill Name}

Usage: python mcp_server.py
Test: python mcp_server.py --test
"""

import json
import sys
import asyncio
import logging
from typing import Any, Dict, List

# Import skill with fallback
try:
    from {skill_name}_skill import {SkillName}Skill
    from skill_compat import ExecutionContext
except ImportError as e:
    logging.error(f"Failed to import: {e}")
    sys.exit(1)

class {SkillName}McpServer:
    """MCP Server for {Skill Name}"""
    
    def __init__(self):
        self.skill = {SkillName}Skill()
        self.context = ExecutionContext()
    
    def get_server_info(self) -> Dict[str, Any]:
        return {
            "name": "{skill-name}-mcp-server",
            "version": "1.0.0",
            "description": "MCP server for {skill description}",
            "capabilities": {
                "tools": True,
                "resources": True,
                "prompts": False
            }
        }
    
    def list_tools(self) -> List[Dict[str, Any]]:
        schema = self.skill.get_openai_schema()
        return [{
            "name": schema["function"]["name"],
            "description": schema["function"]["description"], 
            "inputSchema": schema["function"]["parameters"]
        }]
    
    def call_tool(self, name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        if name != "{skill_function_name}":
            return {"error": f"Unknown tool: {name}"}
        
        try:
            result = self.skill.execute(self.context, **arguments)
            if result.get("success"):
                return {
                    "content": [{
                        "type": "text",
                        "text": json.dumps(result, ensure_ascii=False, indent=2)
                    }]
                }
            else:
                return {
                    "error": result.get("error", {}).get("message", "Unknown error")
                }
        except Exception as e:
            return {"error": f"Tool execution failed: {str(e)}"}
    
    def list_resources(self) -> List[Dict[str, Any]]:
        resources = self.skill.get_mcp_resources()
        return [{
            "uri": resource.uri,
            "name": resource.name, 
            "description": resource.description,
            "mimeType": resource.mime_type
        } for resource in resources]
    
    def read_resource(self, uri: str) -> Dict[str, Any]:
        try:
            return self.skill.read_resource(uri)
        except Exception as e:
            return {"error": f"Failed to read resource: {str(e)}"}

class StdioTransport:
    """Standard I/O transport for MCP"""
    
    def __init__(self, server):
        self.server = server
    
    async def run(self):
        """Run stdio transport loop"""
        while True:
            try:
                line = await asyncio.get_event_loop().run_in_executor(
                    None, sys.stdin.readline
                )
                if not line:
                    break
                
                request = json.loads(line.strip())
                response = self.handle_request(request)
                
                if "id" in request:
                    response["id"] = request["id"]
                
                print(json.dumps(response, ensure_ascii=False), flush=True)
                
            except json.JSONDecodeError as e:
                error_response = {"error": f"Invalid JSON: {str(e)}", "code": -32700}
                print(json.dumps(error_response), flush=True)
            except KeyboardInterrupt:
                break
    
    def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle MCP request"""
        method = request.get("method", "")
        params = request.get("params", {})
        
        if method == "initialize":
            return {
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {}, "resources": {}},
                "serverInfo": self.server.get_server_info()
            }
        elif method == "tools/list":
            return {"tools": self.server.list_tools()}
        elif method == "tools/call":
            return self.server.call_tool(
                params.get("name", ""), 
                params.get("arguments", {})
            )
        elif method == "resources/list":
            return {"resources": self.server.list_resources()}
        elif method == "resources/read":
            return self.server.read_resource(params.get("uri", ""))
        else:
            return {"error": f"Unknown method: {method}", "code": -32601}

def test_server():
    """Test MCP server functionality"""
    print("Testing {Skill Name} MCP Server...")
    server = {SkillName}McpServer()
    
    print("\n1. Server Info:")
    print(json.dumps(server.get_server_info(), indent=2))
    
    print("\n2. Available Tools:")
    print(json.dumps(server.list_tools(), indent=2))
    
    print("\n3. Available Resources:")
    print(json.dumps(server.list_resources(), indent=2))
    
    print("\n✅ MCP Server test completed!")

async def main():
    """Main entry point"""
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        test_server()
        return
    
    server = {SkillName}McpServer()
    transport = StdioTransport(server)
    await transport.run()

if __name__ == "__main__":
    asyncio.run(main())
```

### 11.3 Installation Script Template

```bash
#!/bin/bash
# {Skill Name} MCP Server Installation Script

set -e

echo "🚀 {Skill Name} MCP Server Installation"
echo "======================================"

INSTALL_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
echo "📁 Installation directory: $INSTALL_DIR"

# Check Python
python3 --version || {
    echo "❌ Python 3 is required"
    exit 1
}

# Install dependencies
if [ -f "$INSTALL_DIR/requirements.txt" ]; then
    pip3 install -r "$INSTALL_DIR/requirements.txt" || {
        echo "⚠️ Failed to install dependencies, continuing..."
    }
fi

# Test server
echo "🧪 Testing MCP server..."
cd "$INSTALL_DIR"
python3 mcp_server.py --test || {
    echo "❌ Server test failed"
    exit 1
}

# Generate MCP configuration
MCP_CONFIG_DIR="$HOME/.config/mcp"
mkdir -p "$MCP_CONFIG_DIR"
sed "s|/path/to/skill|$INSTALL_DIR|g" "$INSTALL_DIR/mcp_config.json" > "$MCP_CONFIG_DIR/{skill-name}.json"

echo "✅ Installation completed!"
echo "📋 Next steps:"
echo "1. Configure credentials: cp {skill_name}_config_example.json {skill_name}_config_local.json"
echo "2. Test configuration: python3 test_{skill_name}.py"  
echo "3. MCP config saved to: $MCP_CONFIG_DIR/{skill-name}.json"
echo "4. Add to your AI agent's MCP settings"
```

### 11.4 AI Agent Integration

#### Claude Desktop Configuration
```json
{
  "mcpServers": {
    "{skill-name}": {
      "command": "python3",
      "args": ["/path/to/skill/mcp_server.py"],
      "env": {
        "PYTHONPATH": "/path/to/skill"
      }
    }
  }
}
```

#### Generic MCP Client Integration
```python
from mcp import ClientSession, StdioServerParameters

async def use_skill():
    server_params = StdioServerParameters(
        command="python3",
        args=["/path/to/skill/mcp_server.py"]
    )
    
    async with ClientSession(server_params) as session:
        await session.initialize()
        
        tools = await session.list_tools()
        result = await session.call_tool("skill_function", {
            "param1": "value1",
            "param2": "value2"
        })
        
        return result
```

---

## 12. File Structure and Naming

### 12.1 Standard Project Structure
```
{skill-name}/
├── Core Implementation
│   ├── {skill_name}_skill.py          # Main skill implementation
│   ├── mcp_server.py                  # MCP protocol server
│   └── skill_compat.py                # Framework compatibility layer
├── Testing & Validation
│   ├── test_{skill_name}.py           # Test scripts
│   └── test_mcp_server.py             # MCP server tests
├── Configuration
│   ├── {skill_name}_config_example.json # Public configuration template
│   ├── {skill_name}_config_local.json   # Private config (gitignored)
│   ├── mcp_config.json                  # MCP client configuration
│   └── claude_desktop_config.json      # Claude Desktop integration
├── Deployment
│   ├── install.sh                      # Installation script
│   ├── requirements.txt                # Python dependencies
│   └── .gitignore                      # Security exclusions
└── Documentation
    ├── README.md                       # Project overview
    ├── MCP_DEPLOYMENT.md               # MCP integration guide
    └── {SKILL_NAME}_USAGE.md           # Detailed usage guide
```

### 12.2 Framework-Agnostic Organization

For skills that may be integrated into existing frameworks (like LocalDailyReport), also support:

```
framework/skills/
├── __init__.py
├── base.py                    # Base Skill protocol
├── registry.py                # Skill registry
├── specs/                     # Specifications
│   └── skill_template.yaml    # Template for new skills
├── {skill_name}_skill.py      # Individual skill files
└── {skill_name}/              # Optional: skill-specific modules
    ├── __init__.py
    └── helpers.py
```

### 12.3 Skill File Template

File: `{skill_name}_skill.py`

```python
"""
{Skill Name} - {Brief Description}

Description:
    {Detailed description of what the skill does}
    
Features:
    - Feature 1
    - Feature 2
    
MCP Support:
    - Tools: {tool_name}
    - Resources: {count} resources
    - Prompts: {count} prompts
"""

from typing import Any, Dict, List
from ldr.mcp.base import McpCompatibleSkill, McpResource, McpPrompt
from ldr.context import ExecutionContext


class {SkillName}Skill(McpCompatibleSkill):
    """
    {Skill Name} Skill
    
    {Detailed description}
    """
    
    @staticmethod
    def get_schema() -> Dict[str, Any]:
        """Return OpenAI Function Calling compatible JSON Schema"""
        return {
            "type": "function",
            "function": {
                "name": "{skill_name}",
                "description": "{Description}",
                "parameters": {
                    "type": "object",
                    "properties": {
                        # Parameters here
                    },
                    "required": []
                }
            }
        }
    
    def get_openai_schema(self) -> Dict[str, Any]:
        """Return OpenAI Function Calling compatible JSON Schema"""
        return self.get_schema()
    
    def execute(self, ctx: ExecutionContext, **kwargs) -> Any:
        """
        Execute the skill
        
        Args:
            ctx: Execution context
            **kwargs: Skill parameters
            
        Returns:
            Skill result
        """
        # Implementation here
        pass
    
    def get_mcp_resources(self) -> List[McpResource]:
        """Define MCP Resources"""
        return [
            # Resources here
        ]
    
    def get_mcp_prompts(self) -> List[McpPrompt]:
        """Define MCP Prompts"""
        return [
            # Prompts here
        ]
```

### 11.3 Naming Conventions

- **Class name**: `{SkillName}Skill` (PascalCase + "Skill" suffix)
- **File name**: `{skill_name}_skill.py` (snake_case + "_skill" suffix)
- **Function name**: `{skill_name}` (snake_case, matches file prefix)

Examples:
- `GitReaderSkill` → `git_reader_skill.py` → `git_reader`
- `DailyReportSkill` → `daily_report_skill.py` → `daily_report`
- `FileSkill` → `file_skill.py` → `file`

---

## 12. Registration and Discovery

### 12.1 Skill Registry

Add new skills to `ldr/skills/registry.py`:

```python
from .{skill_name}_skill import {SkillName}Skill

SKILL_REGISTRY = {
    "{skill_name}": {SkillName}Skill,
    # ... other skills
}
```

### 12.2 Auto-Discovery

Skills are automatically discovered by the MCP server:

```python
from ldr.skills import registry

# Get all registered skills
all_skills = registry.SKILL_REGISTRY

# Instantiate a skill
skill_class = all_skills["git_reader"]
skill_instance = skill_class()
```

---

## 13. Best Practices and Guidelines

### 13.1 General Guidelines

1. **Single Responsibility**: Each skill should do one thing well
2. **Clear Naming**: Names should be descriptive and unambiguous
3. **Comprehensive Documentation**: Include docstrings and schema descriptions
4. **Error Handling**: Always handle errors gracefully
5. **Context Usage**: Use context to share data between skills
6. **Testability**: Write testable code with clear inputs/outputs

### 13.2 Schema Design

1. **Descriptive**: Descriptions should explain purpose and behavior
2. **Complete**: Include all constraints and defaults
3. **Validated**: Use JSON Schema features for validation
4. **Discoverable**: AI should understand capabilities from schema alone

### 13.3 MCP Design

1. **Meaningful Resources**: Only expose truly useful data
2. **Logical URIs**: Follow URI conventions consistently
3. **Cached Static Data**: Use caching for unchanging resources
4. **Useful Prompts**: Provide valuable prompt templates

### 13.4 Performance

1. **Lazy Loading**: Load resources only when needed
2. **Caching**: Cache expensive computations
3. **Async Support**: Consider async operations for I/O
4. **Memory Management**: Clean up large objects

### 13.5 Security

1. **Path Validation**: Validate and sanitize file paths
2. **Input Validation**: Validate all user inputs
3. **Error Messages**: Don't leak sensitive information
4. **Resource Access**: Control access to sensitive resources

---

## 14. Examples from Existing Skills

### 14.1 GitReaderSkill (Data Extraction)

**Purpose**: Extract Git repository data  
**Category**: Data Extraction  
**MCP Support**: Tools + Resources

```python
{
    "name": "git_reader",
    "description": "Extract Git repository commits and changes information. Pure data extraction without AI processing.",
    "parameters": {
        "properties": {
            "username": {
                "type": "string",
                "description": "Git username/email to filter commits. If not provided, uses current Git user",
                "default": None
            },
            "include_uncommitted": {
                "type": "boolean",
                "description": "Whether to include uncommitted changes",
                "default": True
            }
        },
        "required": []
    }
}
```

**MCP Resources**:
- `git://repository/commits`
- `git://repository/changes`
- `git://repository/status`

### 14.2 GitSummarySkill (AI Analysis)

**Purpose**: AI-powered Git activity summary  
**Category**: AI Analysis  
**MCP Support**: Tools + Resources + Prompts

```python
{
    "name": "git_summary",
    "description": "Analyze Git repository activity and generate AI-powered work summaries. Supports Chinese (default) and English languages with built-in templates.",
    "parameters": {
        "properties": {
            "username": {"type": "string", "default": None},
            "include_uncommitted": {"type": "boolean", "default": True},
            "template": {
                "type": "string",
                "description": "Custom prompt template. Use {commits}, {changes}, {language} as placeholders.",
                "default": None
            },
            "language": {
                "type": "string",
                "description": "Language for summary. Supports 'Chinese' (default) or 'English' only.",
                "default": "Chinese",
                "enum": ["Chinese", "English"]
            }
        },
        "required": []
    }
}
```

**MCP Resources**:
- `git://summary/latest`
- `git://summary/template`

**MCP Prompts**:
- `git_summary_chinese`
- `git_summary_english`

### 14.3 FileSkill (File System)

**Purpose**: Read files and extract metadata  
**Category**: File System  
**MCP Support**: Tools + Resources

```python
{
    "name": "file",
    "description": "Read file content and extract metadata information.",
    "parameters": {
        "properties": {
            "path": {
                "type": "string",
                "description": "Absolute or relative file path"
            },
            "read": {
                "type": "boolean",
                "description": "Whether to read file content",
                "default": False
            }
        },
        "required": ["path"]
    }
}
```

**MCP Resources**:
- `skill://file/file-content`

---

## 15. Validation Checklist

Use this checklist when creating a new skill:

### Schema Validation
- [ ] Schema has `type: "function"` wrapper
- [ ] Function has `name`, `description`, `parameters`
- [ ] All parameters have `type` and `description`
- [ ] Optional parameters have `default` values
- [ ] Required parameters listed in `required` array
- [ ] Language parameter includes `enum: ["Chinese", "English"]` (if AI skill)
- [ ] Template parameter explains placeholders (if AI skill)

### Implementation Validation
- [ ] Class extends `McpCompatibleSkill`
- [ ] Implements `get_openai_schema()` method
- [ ] Implements `execute(ctx, **kwargs)` method
- [ ] Proper error handling with try/except
- [ ] Returns structured response with `success` field
- [ ] Uses context for data sharing: `ctx.set()`, `ctx.get()`

### MCP Validation
- [ ] Resources follow URI conventions
- [ ] Resource descriptions are clear
- [ ] Prompts follow naming conventions
- [ ] Implements `read_resource()` if resources defined
- [ ] Implements `get_prompt()` if prompts defined

### File Structure Validation
- [ ] File named `{skill_name}_skill.py`
- [ ] Class named `{SkillName}Skill`
- [ ] Function named `{skill_name}`
- [ ] Added to `registry.py`
- [ ] Comprehensive docstrings

### Testing Validation
- [ ] Schema validation test
- [ ] Execution test with valid inputs
- [ ] Error handling test
- [ ] MCP compatibility test

---

## 16. Troubleshooting Common Issues

### Issue: Schema Not Recognized

**Problem**: AI agent cannot find or parse skill schema  
**Solution**: 
- Verify `get_schema()` or `get_openai_schema()` method exists
- Ensure return value matches OpenAI Function Calling format
- Check for syntax errors in schema dictionary

### Issue: Parameter Validation Fails

**Problem**: Skill receives unexpected parameter values  
**Solution**:
- Add input validation in `execute()` method
- Use JSON Schema constraints: `minimum`, `maximum`, `enum`
- Provide clear error messages

### Issue: MCP Resources Not Available

**Problem**: Resources cannot be accessed via MCP  
**Solution**:
- Verify `get_mcp_resources()` returns list of `McpResource` objects
- Implement `read_resource()` method
- Check URI format matches conventions

### Issue: Language Support Not Working

**Problem**: AI-generated content in wrong language  
**Solution**:
- Ensure `language` parameter has `enum: ["Chinese", "English"]`
- Implement language-specific templates
- Pass language to AI client correctly

---

## 17. Migration Guide

### From Simple Skill to MCP-Compatible Skill

**Step 1**: Add MCP base class
```python
# Before
class MySkill:
    pass

# After
from ldr.mcp.base import McpCompatibleSkill

class MySkill(McpCompatibleSkill):
    pass
```

**Step 2**: Rename schema method (if needed)
```python
# Before
@staticmethod
def get_schema():
    ...

# After
def get_openai_schema(self):
    return self.get_schema()  # Can still use static method
```

**Step 3**: Add MCP resources (optional)
```python
def get_mcp_resources(self):
    return [
        McpResource(
            uri="skill://my_skill/data",
            name="my_skill_data",
            description="My skill data"
        )
    ]
```

**Step 4**: Add MCP prompts (optional, for AI skills)
```python
def get_mcp_prompts(self):
    return [
        McpPrompt(
            name="my_skill_prompt",
            description="My skill prompt"
        )
    ]
```

---

## 18. Schema Export and MCP Server

### 18.1 Schema Export

All skills can be exported to `mcp_schema_export.json`:

```python
# Generate schema export from individual skill
python -c "from {skill_name}_skill import {SkillName}Skill; skill = {SkillName}Skill(); import json; print(json.dumps(skill.get_openai_schema(), indent=2))"
```

### 18.2 MCP Server Integration

Skills are available via dedicated MCP servers:

```bash
# Start individual skill MCP server
python mcp_server.py

# Test MCP server functionality
python mcp_server.py --test
```

### 18.3 MCP Client Integration

```python
from {skill_name}_skill import {SkillName}McpServer

server = {SkillName}McpServer()

# List all tools
tools = server.list_tools()

# Call a tool
result = server.call_tool("{skill_function_name}", {"param1": "value1"})

# Read a resource
data = server.read_resource("skill://resource/data")
```

---

## 19. Deployment Considerations

### 19.1 Standalone Skill Execution

Skills can be executed standalone:

```python
from ldr.skills.git_reader_skill import GitReaderSkill
from ldr.context import ExecutionContext

skill = GitReaderSkill()
ctx = ExecutionContext()
result = skill.execute(ctx, path=".", days=1)
```

### 19.2 Workflow Integration

Skills are used in YAML workflows:

```yaml
name: my_workflow
steps:
  - name: read_git
    skill: git_reader
    params:
      include_uncommitted: true
  
  - name: generate_summary
    skill: git_summary
    params:
      language: Chinese
```

### 19.3 MCP Server Deployment

Skills are exposed via MCP server:

```bash
# Docker deployment
docker run -p 8001:8001 local-daily-report python start_mcp_server.py

# Systemd service
systemctl start local-daily-report-mcp
```

---

## 20. Version History and Future

### Version 1.0.0 (Current)

Initial release with:
- OpenAI Function Calling support
- MCP (Model Context Protocol) support
- Dual standard compatibility
- Resource and prompt definitions
- Multi-language support (Chinese, English)

### Planned Features

- Additional language support (Japanese, Korean, etc.)
- Streaming response support
- Advanced caching strategies
- Skill composition and chaining
- Dynamic skill loading
- Skill marketplace integration

---

## 19. Version Control and Update Management

### 19.1 Version Management System

All skills MUST implement comprehensive version control capabilities including:

#### Version Information Module

Create a `version.py` module with the following structure:

```python
#!/usr/bin/env python3
"""
Version Management for [Skill Name] MCP Server

This module provides version information and update utilities for the
[Skill Name] MCP Server project.
"""

import os
import sys
import json
import subprocess
from datetime import datetime
from typing import Dict, Any, Optional

# Current version information
__version__ = "1.0.0"
__release_date__ = "2026-02-12"
__compatibility_version__ = "2024-11-05"  # MCP protocol version

# Version metadata
VERSION_INFO = {
    "version": __version__,
    "release_date": __release_date__,
    "mcp_compatibility": __compatibility_version__,
    "python_min_version": "3.7",
    "features": [
        "Feature 1",
        "Feature 2",
        # ... list all major features
    ]
}

def get_version_info() -> Dict[str, Any]:
    """Get comprehensive version information"""
    return VERSION_INFO.copy()

def get_version_string() -> str:
    """Get formatted version string"""
    return f"[Skill Name] MCP Server v{__version__} (MCP {__compatibility_version__})"

def check_git_status() -> Optional[Dict[str, Any]]:
    """Check Git repository status for version tracking"""
    try:
        commit_hash = subprocess.check_output(
            ["git", "rev-parse", "HEAD"], 
            cwd=os.path.dirname(os.path.abspath(__file__)),
            stderr=subprocess.DEVNULL
        ).decode().strip()
        
        branch = subprocess.check_output(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            cwd=os.path.dirname(os.path.abspath(__file__)),
            stderr=subprocess.DEVNULL
        ).decode().strip()
        
        # Check for uncommitted changes
        status_output = subprocess.check_output(
            ["git", "status", "--porcelain"],
            cwd=os.path.dirname(os.path.abspath(__file__)),
            stderr=subprocess.DEVNULL
        ).decode().strip()
        
        return {
            "commit_hash": commit_hash[:8],
            "full_commit_hash": commit_hash,
            "branch": branch,
            "has_uncommitted_changes": bool(status_output),
            "is_clean": not bool(status_output)
        }
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None

def check_for_updates() -> Dict[str, Any]:
    """Check for available updates"""
    update_info = {
        "update_available": False,
        "current_version": __version__,
        "remote_version": None,
        "update_instructions": [],
        "git_status": check_git_status()
    }
    
    try:
        # Fetch and compare commits
        subprocess.run(["git", "fetch", "origin", "main"], 
                      capture_output=True, check=True)
        
        local_commit = subprocess.check_output(
            ["git", "rev-parse", "HEAD"]).decode().strip()
        remote_commit = subprocess.check_output(
            ["git", "rev-parse", "origin/main"]).decode().strip()
        
        if local_commit != remote_commit:
            update_info["update_available"] = True
            update_info["update_instructions"] = [
                "Updates available! Run: python3 version.py --update",
                "Or manually: git pull origin main"
            ]
            
        return update_info
    except Exception as e:
        update_info["check_error"] = str(e)
        return update_info

def perform_update() -> Dict[str, Any]:
    """Perform automatic update"""
    result = {
        "success": False,
        "message": "",
        "previous_version": __version__,
        "steps_completed": []
    }
    
    try:
        # Validation steps
        git_status = check_git_status()
        if git_status and git_status["has_uncommitted_changes"]:
            result["message"] = "Uncommitted changes detected"
            return result
        
        # Update steps
        steps = [
            ("Fetching changes", ["git", "fetch", "origin", "main"]),
            ("Pulling updates", ["git", "pull", "origin", "main"]),
            ("Running tests", [sys.executable, "test_skill.py"]),
            ("Testing MCP server", [sys.executable, "mcp_server.py", "--test"])
        ]
        
        for step_name, command in steps:
            subprocess.run(command, check=True, capture_output=True)
            result["steps_completed"].append(step_name)
            
        result["success"] = True
        result["message"] = "Update completed successfully!"
        
    except subprocess.CalledProcessError as e:
        result["message"] = f"Update failed: {e}"
        
    return result
```

### 19.2 Command Line Interface

All skills MUST support these version management commands:

```python
def main():
    """Command-line interface for version management"""
    if len(sys.argv) < 2:
        show_version_info()
        return
    
    command = sys.argv[1]
    
    if command == "--version" or command == "-v":
        print(get_version_string())
        
    elif command == "--info":
        show_version_info()
        
    elif command == "--check-updates":
        update_info = check_for_updates()
        if update_info["update_available"]:
            print("🆕 Updates available!")
            for instruction in update_info["update_instructions"]:
                print(f"   {instruction}")
        else:
            print("✅ You are up to date!")
            
    elif command == "--update":
        result = perform_update()
        if result["success"]:
            print(f"🎉 {result['message']}")
        else:
            print(f"❌ {result['message']}")
            
    elif command == "--json":
        version_data = {
            "version_info": get_version_info(),
            "git_status": check_git_status(),
            "update_check": check_for_updates()
        }
        print(json.dumps(version_data, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()
```

### 19.3 Update Script (update.sh)

Create an automated update script:

```bash
#!/bin/bash
# Automated Update Script for [Skill Name] MCP Server

set -e  # Exit on any error

# Configuration
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKUP_DIR="$PROJECT_DIR/.update_backup_$(date +%Y%m%d_%H%M%S)"

# Utility functions
log() { echo -e "\033[0;34m[$(date +'%Y-%m-%d %H:%M:%S')]\033[0m $1"; }
success() { echo -e "\033[0;32m✅ $1\033[0m"; }
warning() { echo -e "\033[1;33m⚠️  $1\033[0m"; }
error() { echo -e "\033[0;31m❌ $1\033[0m"; }

# Main update process
main() {
    log "Starting update process..."
    
    # Check for updates
    if ! python3 version.py --check-updates | grep -q "Updates available"; then
        success "Already up to date!"
        exit 0
    fi
    
    # Backup local configuration files
    log "Creating backup..."
    mkdir -p "$BACKUP_DIR"
    for file in *_local.json claude_desktop_config.json; do
        if [ -f "$file" ]; then
            cp "$file" "$BACKUP_DIR/"
            log "Backed up: $file"
        fi
    done
    
    # Perform update
    log "Updating from Git repository..."
    if python3 version.py --update; then
        success "Update completed successfully!"
        
        # Restore configuration files
        log "Restoring configuration files..."
        for file in "$BACKUP_DIR"/*; do
            if [ -f "$file" ]; then
                basename_file=$(basename "$file")
                cp "$file" "$basename_file"
                log "Restored: $basename_file"
            fi
        done
        
        # Run post-update tests
        log "Running post-update validation..."
        if python3 mcp_server.py --test; then
            success "All tests passed!"
            rm -rf "$BACKUP_DIR"
        else
            warning "Tests failed - backup preserved at $BACKUP_DIR"
        fi
    else
        error "Update failed - backup preserved at $BACKUP_DIR"
        exit 1
    fi
}

main "$@"
```

### 19.4 Change Documentation

#### CHANGELOG.md

Maintain a comprehensive changelog following [Keep a Changelog](https://keepachangelog.com/):

```markdown
# Changelog

All notable changes to [Skill Name] will be documented in this file.

## [1.1.0] - 2026-02-13

### 🆕 Added
- New feature X with enhanced capabilities
- Additional parameter Y for better control
- Version control system integration

### 🔧 Improved  
- Enhanced error handling for edge cases
- Better performance in large dataset processing
- Updated documentation with new examples

### 🐛 Fixed
- Fixed issue with parameter validation
- Resolved memory leak in long-running processes
- Corrected timezone handling in date processing

### 📚 Documentation
- Updated README with new feature examples
- Enhanced troubleshooting guide
- Added migration instructions for v1.0.0 users

## [1.0.0] - 2026-02-12
- Initial release with core functionality
- MCP protocol integration
- Comprehensive test suite
```

#### UPDATE_GUIDE.md

```markdown
# [Skill Name] - Version Control & User Update Guide

## 🚀 Quick Update

### Automated Update (Recommended)
```bash
cd skill-directory
./update.sh
```

### Using Version Management Tool
```bash
python3 version.py --check-updates
python3 version.py --update
```

## 🔧 Manual Update Steps

1. **Check current version:**
   ```bash
   python3 version.py --info
   ```

2. **Backup configuration files:**
   ```bash
   cp *_local.json backup/
   cp claude_desktop_config.json backup/
   ```

3. **Update from Git:**
   ```bash
   git pull origin main
   ```

4. **Restore configurations:**
   ```bash
   cp backup/*_local.json ./
   cp backup/claude_desktop_config.json ./
   ```

5. **Test the update:**
   ```bash
   python3 mcp_server.py --test
   ```

## ⚠️ Troubleshooting

### Update Fails
- Check Git status: `git status`
- Resolve conflicts manually
- Run `git pull origin main` again

### Configuration Lost
- Restore from backup directory
- Check example configs for new parameters
```

### 19.5 MCP Server Version Integration

Update MCP server to include version information:

```python
# Import version information
try:
    from version import __version__, get_version_string, get_version_info
except ImportError:
    __version__ = "1.0.0"
    get_version_string = lambda: f"Skill MCP Server v{__version__}"
    get_version_info = lambda: {"version": __version__}

class SkillMcpServer:
    def __init__(self):
        self.skill = SkillImplementation()
        
    async def get_server_info(self) -> Dict[str, Any]:
        """Get server information including version details"""
        return {
            "name": "skill-mcp-server",
            "version": __version__,
            "description": f"MCP server for skill processing - {get_version_string()}",
            "capabilities": {
                "tools": True,
                "resources": True,
                "prompts": False
            },
            "version_info": get_version_info()
        }
```

### 19.6 Version Control Best Practices

#### Semantic Versioning
- **MAJOR version**: Incompatible API changes
- **MINOR version**: Backwards-compatible functionality additions  
- **PATCH version**: Backwards-compatible bug fixes

#### Release Process
1. **Update version.py**: Increment version number and update metadata
2. **Update CHANGELOG.md**: Document all changes
3. **Run tests**: Ensure all functionality works
4. **Create Git tag**: Tag the release commit
5. **Update documentation**: Reflect new features/changes

#### Required Files
Every skill project MUST include:
- `version.py` - Version management module
- `update.sh` - Automated update script
- `CHANGELOG.md` - Change documentation  
- `UPDATE_GUIDE.md` - User update instructions

---

## Appendix A: Complete Skill Template

See `ldr/skills/specs/skill_template.yaml` for the base template.

Full implementation template:

```python
"""
Skill Name - Brief Description

This skill provides [functionality description].
"""

from typing import Any, Dict, List
from ldr.mcp.base import McpCompatibleSkill, McpResource, McpPrompt
from ldr.context import ExecutionContext


class NewSkill(McpCompatibleSkill):
    """
    New Skill Implementation
    
    Purpose: [What this skill does]
    Category: [Data Extraction | AI Analysis | File System | Reporting]
    """
    
    @staticmethod
    def get_schema() -> Dict[str, Any]:
        """Return OpenAI Function Calling compatible JSON Schema"""
        return {
            "type": "function",
            "function": {
                "name": "new_skill",
                "description": "Detailed description of what the skill does",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "param1": {
                            "type": "string",
                            "description": "Description of param1",
                            "default": "default_value"
                        }
                    },
                    "required": []
                }
            }
        }
    
    def get_openai_schema(self) -> Dict[str, Any]:
        """Return OpenAI schema"""
        return self.get_schema()
    
    def execute(self, ctx: ExecutionContext, **kwargs) -> Any:
        """
        Execute the skill
        
        Args:
            ctx: Execution context
            **kwargs: Skill parameters
            
        Returns:
            Result dictionary with success status
        """
        try:
            # Implementation logic here
            result = {"data": "result"}
            
            # Store in context
            ctx.set("skill:new_skill:result", result)
            
            return {
                "success": True,
                "function_name": "new_skill",
                "data": result
            }
            
        except Exception as e:
            return {
                "success": False,
                "function_name": "new_skill",
                "error": {
                    "message": str(e),
                    "type": "execution_error"
                }
            }
    
    def get_mcp_resources(self) -> List[McpResource]:
        """Define MCP Resources"""
        return [
            McpResource(
                uri="skill://new_skill/data",
                name="new_skill_data",
                description="Data from new skill",
                mime_type="application/json"
            )
        ]
    
    def get_mcp_prompts(self) -> List[McpPrompt]:
        """Define MCP Prompts"""
        return []
    
    def read_resource(self, uri: str) -> Dict[str, Any]:
        """Read MCP resource"""
        if uri == "skill://new_skill/data":
            return {
                "contents": [
                    {
                        "uri": uri,
                        "mimeType": "application/json",
                        "text": '{"example": "data"}'
                    }
                ]
            }
        return super().read_resource(uri)
```

---

## Appendix B: JSON Schema Reference

Quick reference for JSON Schema types and constraints:

### Basic Types
- `string` - Text data
- `integer` - Whole numbers
- `number` - Decimal numbers
- `boolean` - true/false
- `object` - JSON object
- `array` - JSON array
- `null` - Null value

### String Constraints
- `minLength` - Minimum string length
- `maxLength` - Maximum string length
- `pattern` - Regular expression pattern
- `format` - Format type (email, uri, date-time, etc.)
- `enum` - Allowed values

### Number Constraints
- `minimum` - Minimum value (inclusive)
- `maximum` - Maximum value (inclusive)
- `exclusiveMinimum` - Minimum value (exclusive)
- `exclusiveMaximum` - Maximum value (exclusive)
- `multipleOf` - Value must be multiple of this

### Object Constraints
- `properties` - Property definitions
- `required` - Required property names
- `additionalProperties` - Allow additional properties
- `minProperties` - Minimum number of properties
- `maxProperties` - Maximum number of properties

### Array Constraints
- `items` - Item schema
- `minItems` - Minimum array length
- `maxItems` - Maximum array length
- `uniqueItems` - All items must be unique

---

## Appendix C: References

### Official Documentation
- OpenAI Function Calling: https://platform.openai.com/docs/guides/function-calling
- JSON Schema: https://json-schema.org/
- Model Context Protocol: https://modelcontextprotocol.io/

### AI-Powered Application Documentation
- Main README: `/README.md`
- MCP Integration Guide: `/MCP_DEPLOYMENT.md`
- Installation Guide: `/install.sh`
- Usage Documentation: `/{SKILL_NAME}_USAGE.md`

### Example Implementations
- Gmail Check Skill: `/gmail_check_skill.py`
- MCP Server Template: `/mcp_server.py`
- Configuration Management: `/skill_compat.py`
- Test Framework: `/test_gmail_skill.py`

---

## End of Specification

This document is designed to be read and understood by AI systems for automated skill generation. All standards, conventions, and examples are provided to ensure consistent, high-quality skill development that works across multiple AI agent platforms.

For questions or clarifications, refer to the example implementations or the MCP deployment documentation.

**Last Updated**: 2026-02-12  
**Document Version**: 2.1.0  
**Target Applications**: AI-Powered Skills and Agents
