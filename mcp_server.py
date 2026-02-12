#!/usr/bin/env python3
"""
MCP Server for Mail Command Extractor

Provides Model Context Protocol (MCP) server implementation
for AI agent integration.

Usage: python mcp_server.py
Test: python mcp_server.py --test
"""

import json
import sys
import asyncio
import logging
from typing import Any, Dict, List

# Import version information
try:
    from version import __version__, get_version_string, get_version_info
except ImportError:
    __version__ = "1.0.0"
    get_version_string = lambda: f"Mail Command Extractor MCP Server v{__version__}"
    get_version_info = lambda: {"version": __version__}

# Import skill with fallback
try:
    from mail_command_extractor_skill import MailCommandExtractorSkill
    from skill_compat import ExecutionContext
except ImportError as e:
    logging.error(f"Failed to import: {e}")
    sys.exit(1)


class MailCommandExtractorMcpServer:
    """MCP Server for Mail Command Extractor"""
    
    def __init__(self):
        self.skill = MailCommandExtractorSkill()
        self.context = ExecutionContext()
    
    def get_server_info(self) -> Dict[str, Any]:
        return {
            "name": "mail-command-extractor-mcp-server",
            "version": __version__,
            "description": f"MCP server for mail command extraction and processing - {get_version_string()}",
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
        if name != "mail_command_extractor":
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
    print(f"Testing {get_version_string()}...")
    server = MailCommandExtractorMcpServer()
    
    print("\n1. Server Info:")
    print(json.dumps(server.get_server_info(), indent=2))
    
    print("\n2. Available Tools:")
    print(json.dumps(server.list_tools(), indent=2))
    
    print("\n3. Available Resources:")
    print(json.dumps(server.list_resources(), indent=2))
    
    # Test with sample data
    print("\n4. Testing with sample data:")
    sample_config = {
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
            "matched_emails": [
                {
                    "sender": "=?UTF-8?B?5LiB5LiA5aSr?= <baddif@gmail.com>",
                    "subject": "日报",
                    "content": "生成日报",
                    "date_received": "Thu, 12 Feb 2026 15:20:17 +0800",
                    "message_id": "<CADg8Hs+csR-gCkZLTw_jUynAK4HHbEXwJFit3MLtKOFOL3D98w@mail.gmail.com>",
                    "email_id": "42e4e831f7f44713b34e82ea7dc5ad0f"
                }
            ]
        },
        "merge_duplicates": True
    }
    
    result = server.call_tool("mail_command_extractor", sample_config)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    
    print("\n✅ MCP Server test completed!")


async def main():
    """Main entry point"""
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        test_server()
        return
    
    server = MailCommandExtractorMcpServer()
    transport = StdioTransport(server)
    await transport.run()


if __name__ == "__main__":
    asyncio.run(main())