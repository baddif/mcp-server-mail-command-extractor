#!/usr/bin/env python3
"""
Debug MCP Server Communication

调试MCP服务器通信问题
"""

import subprocess
import json


def debug_mcp_server():
    """调试MCP服务器"""
    print("🔍 Debugging MCP Server Communication...")
    
    process = subprocess.Popen(
        ["python3", "mcp_server.py"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    try:
        # 发送初始化请求
        init_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {
                    "name": "test-client",
                    "version": "1.0.0"
                }
            }
        }
        
        print(f"发送请求: {json.dumps(init_request, indent=2)}")
        process.stdin.write(json.dumps(init_request) + "\n")
        process.stdin.flush()
        
        # 读取响应
        print("\n等待响应...")
        response_line = process.stdout.readline()
        print(f"收到原始响应: {repr(response_line)}")
        
        if response_line:
            try:
                response = json.loads(response_line.strip())
                print(f"解析后的响应: {json.dumps(response, indent=2, ensure_ascii=False)}")
            except json.JSONDecodeError as e:
                print(f"JSON解析失败: {e}")
                print(f"原始数据: {response_line}")
        else:
            print("没有收到响应")
        
        # 检查stderr
        stderr_data = process.stderr.read()
        if stderr_data:
            print(f"\nStderr输出: {stderr_data}")
    
    except Exception as e:
        print(f"调试过程中出错: {e}")
    
    finally:
        try:
            process.terminate()
            process.wait(timeout=2)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait()


if __name__ == "__main__":
    debug_mcp_server()