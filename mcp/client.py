from openai import OpenAI 
from dotenv import load_dotenv
from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client
import asyncio 

# SETUP THE ENVIRONMENT
load_dotenv()
client = OpenAI()

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
             print(tool_list)

asyncio.run(main())