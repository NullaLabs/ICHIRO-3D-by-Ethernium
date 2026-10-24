bl_info = {
    "name": "Ichiro Sovereign Blender MCP Bridge",
    "author": "Ethernium Sovereign Agent",
    "version": (2, 3, 0),
    "blender": (5, 0, 0),
    "location": "View3D > Sidebar > Ichiro MCP",
    "description": "Model Context Protocol (MCP) TCP Socket Bridge for End-to-End 3D Arcane Character Generation & Control",
    "category": "System",
}

import bpy
import socket
import json
import traceback
import io
import contextlib

MCP_PORT = 9876

def execute_mcp_command(cmd_obj):
    cmd_type = cmd_obj.get("type", "ping")
    params = cmd_obj.get("params", {})
    try:
        if cmd_type == "ping":
            return {"status": "ok", "blender_version": bpy.app.version_string}
        elif cmd_type == "get_scene_info":
            objs = []
            for o in bpy.data.objects:
                info = {
                    "name": o.name,
                    "type": o.type,
                    "location": [round(x, 4) for x in o.location],
                    "dimensions": [round(x, 4) for x in o.dimensions],
                }
                if o.type == "MESH" and o.data:
                    info["vertices"] = len(o.data.vertices)
                    info["polygons"] = len(o.data.polygons)
                    info["materials"] = [s.material.name for s in o.material_slots if s.material]
                elif o.type == "ARMATURE" and o.data:
                    info["bones"] = [b.name for b in o.data.bones]
                objs.append(info)
            return {
                "status": "ok",
                "scene_name": bpy.context.scene.name,
                "render_engine": bpy.context.scene.render.engine,
                "objects": objs,
                "materials": [m.name for m in bpy.data.materials],
            }
        elif cmd_type == "execute_code":
            code = params.get("code", "")
            buf = io.StringIO()
            loc_ns = {"bpy": bpy, "result": None}
            with contextlib.redirect_stdout(buf):
                exec(code, globals(), loc_ns)
            return {
                "status": "ok",
                "stdout": buf.getvalue(),
                "result": loc_ns.get("result"),
            }
        elif cmd_type == "render_view":
            filepath = params.get("filepath", "")
            res_x = params.get("res_x", 1080)
            res_y = params.get("res_y", 1350)
            cam_loc = params.get("cam_loc")
            cam_target = params.get("cam_target", [0.0, 0.0, 0.95])
            lens = params.get("lens", 65.0)
            
            scene = bpy.context.scene
            scene.render.resolution_x = res_x
            scene.render.resolution_y = res_y
            if filepath:
                scene.render.filepath = filepath
            cam = scene.camera
            if cam and cam_loc:
                from mathutils import Vector
                cam.location = Vector(cam_loc)
                cam.data.lens = lens
                direction = Vector(cam_target) - cam.location
                cam.rotation_euler = direction.to_track_quat('-Z', 'Y').to_euler()
            bpy.ops.render.render(write_still=bool(filepath))
            return {"status": "ok", "rendered": filepath}
        else:
            return {"status": "error", "message": f"Unknown MCP command: {cmd_type}"}
    except Exception as e:
        return {"status": "error", "message": str(e), "traceback": traceback.format_exc()}

def serve_blocking(host="127.0.0.1", port=MCP_PORT):
    """Run synchronous MCP command loop on Blender's main thread."""
    srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    srv.bind((host, port))
    srv.listen(5)
    print(f"[BLENDER-MCP] Listening on {host}:{port} (Blender {bpy.app.version_string})", flush=True)
    try:
        while True:
            conn, addr = srv.accept()
            with conn:
                data = b""
                while True:
                    chunk = conn.recv(65536)
                    if not chunk:
                        break
                    data += chunk
                    if b"\n" in chunk:
                        break
                if not data:
                    continue
                req = json.loads(data.decode("utf-8").strip())
                if req.get("type") == "shutdown":
                    resp = {"status": "ok", "message": "Shutting down Blender MCP server"}
                    conn.sendall((json.dumps(resp) + "\n").encode("utf-8"))
                    break
                resp = execute_mcp_command(req)
                conn.sendall((json.dumps(resp) + "\n").encode("utf-8"))
    finally:
        srv.close()

def register():
    print("[BLENDER-MCP] Ichiro Sovereign Blender MCP Addon registered.")

def unregister():
    print("[BLENDER-MCP] Ichiro Sovereign Blender MCP Addon unregistered.")

if __name__ == "__main__":
    import sys
    if "--mcp-daemon" in sys.argv:
        serve_blocking()
