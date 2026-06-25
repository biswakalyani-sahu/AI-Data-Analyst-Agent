import asyncio
import os
import sys
import json
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def run_tool_async(tool_name: str, arguments: dict) -> str:
    """
    Asynchronously runs the MCP server as a subprocess, connects to it,
    calls the specified tool with arguments, and returns the string response.
    """
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir)
    server_path = os.path.join(project_root, "mcp_server", "server.py")
    
    # Configure the server subprocess params
    server_params = StdioServerParameters(
        command=sys.executable,  # Uses the current python environment executable
        args=[server_path],
        env=os.environ.copy()    # Pass environment variables, including GEMINI_API_KEY
    )
    
    # Establish standard I/O connection to the MCP server
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # Initialize connection
            await session.initialize()
            
            # Call the target tool
            result = await session.call_tool(tool_name, arguments)
            
            if result and result.content:
                return result.content[0].text
            return json.dumps({"error": "No content returned from MCP server."})

def call_mcp_tool(tool_name: str, arguments: dict) -> str:
    """
    Synchronous wrapper to execute the async MCP tool call.
    This simplifies the logic when called within standard Streamlit or script cycles.
    """
    try:
        # Create a new event loop or use the existing one to run the async function
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
        if loop.is_running():
            # If an event loop is already running (e.g. inside Streamlit async elements),
            # use a helper execution pattern or run in thread
            import nest_asyncio
            nest_asyncio.apply()
            return loop.run_until_complete(run_tool_async(tool_name, arguments))
        else:
            return loop.run_until_complete(run_tool_async(tool_name, arguments))
    except Exception as e:
        return json.dumps({"error": f"MCP client invocation failed: {str(e)}"})
