"""Read-only MCP handshake and addon-status smoke test. Requires MCP runtime env."""
import asyncio
import json
import os
from pathlib import Path
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def main():
    executable='E:/WORKSPACE/ichiro-blender-mcp-env/Scripts/mcp-for-blender.exe'
    env={**os.environ,'DISABLE_TELEMETRY':'true','BLENDER_MCP_SAFE_MODE':'1',
         'BLENDER_HOST':'127.0.0.1','BLENDER_PORT':'9876'}
    params=StdioServerParameters(command=executable,env=env)
    async with stdio_client(params) as (read,write):
        async with ClientSession(read,write) as session:
            await session.initialize()
            tools=await session.list_tools()
            names=[t.name for t in tools.tools]
            status=await session.call_tool('get_addon_status',{})
            probe=await session.call_tool('execute_blender_code',{
                'code':"import bpy; print({'blender': bpy.app.version_string, 'scene_objects': len(bpy.context.scene.objects)})",
                'user_prompt':'si'})
            report={'tools':names,'status':status.model_dump(mode='json'),
                    'read_only_code_probe':probe.model_dump(mode='json'),
                    'test':'MCP initialize/list_tools/get_addon_status/read-only bpy; no scene mutation'}
            path=Path(__file__).resolve().parents[1]/'docs'/'MCP_CONNECTION_CHECK.json'
            path.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
            print(json.dumps(report,indent=2))
            if status.isError or any(getattr(c,'text','').startswith('Error') for c in status.content):
                raise RuntimeError('Addon status returned an error')
            if probe.isError or any('scene_objects' not in getattr(c,'text','') for c in probe.content):
                raise RuntimeError('Read-only code probe did not return expected scene data')

asyncio.run(main())
