from openai import OpenAI 
from dotenv import load_dotenv
from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client
import asyncio 
import json 

# SETUP THE ENVIRONMENT
load_dotenv()
client = OpenAI()

# SYSTEM PROMPT
SYSTEM_PROMPT = """
You are an MCP Client AI assistant with access to external tools
via MCP. Once you receive the request of the user, check available tools
and make a decision on whether the user's request should be answered via a tool
or via your LLM data.

Based upon your decision, continue answering the user's query.
"""

# DYNAMIC TOOL SCHEMA GENERATION - OPENAI
def convert_tool_to_schema(tool):
    return {
        "type": "function",
        "name": tool.name,
        "description": tool.description or "",
        "parameters": tool.inputSchema
    }

async def main():
    query = input("Enter Human Query: ")
    async with streamable_http_client("http://localhost:8000/mcp") as (
        read_stream,
        write_stream,
        input_stream
    ):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()
            tool_list = await session.list_tools()
            tools = tool_list.tools
            openai_tools = []
            for t in tools:
                openai_tools.append(convert_tool_to_schema(t))
            response = client.responses.create(
                model="gpt-5.4-mini",
                instructions=SYSTEM_PROMPT,
                input=query,
                tools=openai_tools
            )
            tool_call = None
            for item in response.output:
                if item.type == "function_call":
                    tool_call = item 
                    break
            if tool_call:
                tool_name = tool_call.name
                args = json.loads(tool_call.arguments)
                print(f"LLM SELECTED TOOL: {tool_name}")
                result = await session.call_tool(tool_name,args)
                print("\nRUNNING TOOL\n")
                for item in result.content:
                    print(item.text)
            else:
                print("NO TOOL SELECTED, USING INTERNAL LLM DATA")
                print(response.output_text)
        

asyncio.run(main())