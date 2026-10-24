#!/usr/bin/env python3
"""
Ichiro Sovereign Blender MCP Server (Model Context Protocol - stdio & TCP bridge)
Connects MCP-compatible AI agents directly to Blender 5.2 via TCP port 9876.
"""
import sys
import json
import socket

BLENDER_HOST = "127.0.0.1"
BLENDER_PORT = 9876

def send_to_blender(cmd_type, params=None, timeout=120.0):
    payload = {"type": cmd_type, "params": params or {}}
    with socket.create_connection((BLENDER_HOST, BLENDER_PORT), timeout=timeout) as sock:
        sock.sendall((json.dumps(payload) + "\n").encode("utf-8"))
        buf = b""
        while True:
            chunk = sock.recv(65536)
            if not chunk:
                break
            buf += chunk
            if b"\n" in chunk:
                break
    return json.loads(buf.decode("utf-8").strip())

TOOLS = [
    {
        "name": "get_scene_info",
        "description": "Retrieve all 3D objects, vertex/polygon counts, armatures, and materials in the active Blender 5.2 scene.",
        "inputSchema": {"type": "object", "properties": {}},
    },
    {
        "name": "execute_blender_code",
        "description": "Execute Python (bpy) code directly inside Blender 5.2 via MCP.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "code": {"type": "string", "description": "Python code using bpy to execute in Blender"}
            },
            "required": ["code"],
        },
    },
    {
        "name": "render_view",
        "description": "Configure camera position/target/lens and render a 2.3D Arcane frame in Blender 5.2.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "filepath": {"type": "string"},
                "res_x": {"type": "integer"},
                "res_y": {"type": "integer"},
                "cam_loc": {"type": "array", "items": {"type": "number"}},
                "cam_target": {"type": "array", "items": {"type": "number"}},
                "lens": {"type": "number"},
            },
            "required": ["filepath"],
        },
    },
]

def handle_jsonrpc(msg):
    method = msg.get("method")
    msg_id = msg.get("id")
    params = msg.get("params", {})

    if method == "initialize":
        return {
            "jsonrpc": "2.0",
            "id": msg_id,
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {}},
                "serverInfo": {"name": "ichiro-blender-mcp", "version": "2.3.0"},
            },
        }
    elif method == "notifications/initialized":
        return None
    elif method == "tools/list":
        return {"jsonrpc": "2.0", "id": msg_id, "result": {"tools": TOOLS}}
    elif method == "tools/call":
        tname = params.get("name")
        targs = params.get("arguments", {})
        if tname == "get_scene_info":
            res = send_to_blender("get_scene_info")
        elif tname == "execute_blender_code":
            res = send_to_blender("execute_code", {"code": targs.get("code", "")})
        elif tname == "render_view":
            res = send_to_blender("render_view", targs)
        else:
            res = {"status": "error", "message": f"Unknown tool: {tname}"}
        return {
            "jsonrpc": "2.0",
            "id": msg_id,
            "result": {
                "content": [{"type": "text", "text": json.dumps(res, indent=2)}],
                "isError": res.get("status") == "error",
            },
        }
    elif msg_id is not None:
        return {"jsonrpc": "2.0", "id": msg_id, "result": {}}
    return None

def main():
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            msg = json.loads(line)
            resp = handle_jsonrpc(msg)
            if resp is not None:
                sys.stdout.write(json.dumps(resp) + "\n")
                sys.stdout.flush()
        except Exception as e:
            sys.stderr.write(f"[MCP Error] {e}\n")
            sys.stderr.flush()

if __name__ == "__main__":
    main()
