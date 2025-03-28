import asyncio
from contextlib import AsyncExitStack
import json
from dotenv import load_dotenv 
import os
import sys
from typing import Optional
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from openai import AsyncOpenAI
load_dotenv("./deepseek.env")  
model=os.getenv("model")
class MCPClient:
    def __init__(self):
        self.session: Optional[ClientSession] = None
        self.sessions={}
        self.exit_stack = AsyncExitStack()
        self.tools=[]
        self.messages=[]
        self.client = AsyncOpenAI(api_key=os.environ["api_key"], base_url=os.environ["base_url"])


    async def cleanup(self):
        """Clean up resources"""
        await self.exit_stack.aclose()

    async def connect_to_server(self):
        with open("mcp_server_config.json", "r") as f:
            config = json.load(f)
            print(config["mcpServers"])  
        conf=config["mcpServers"]
        print(conf.keys())
        for key in conf.keys():
            v = conf[key]
            command = v['command']
            args=v['args']
            print(command)
            print(args)
            server_params = StdioServerParameters(
                command=command,
                args=args,
                env=None
            )
            
            stdio_transport = await self.exit_stack.enter_async_context(stdio_client(server_params))
            stdio1, write1 = stdio_transport
            session = await self.exit_stack.enter_async_context(ClientSession(stdio1, write1))
            
            await session.initialize()
            
            # 列出可用工具
            response = await session.list_tools()
            tools = response.tools
            print("\nConnected to server with tools:", [tool.name for tool in tools])
            for tool in tools:
                self.sessions[tool.name]=session
            self.tools=self.tools+tools
            print(self.sessions)

    async def process_query(self, query: str) -> str:
        """使用 LLM 和 MCP 服务器提供的工具处理查询"""
        self.messages=self.messages+[
            {
                "role": "user",
                "content": query
            }
        ]
        messages =self.messages[-20:]
        
        #print(messages)
        available_tools = [{
            "type": "function",
            "function": {
                "name": tool.name,
                "description": tool.description,
                "parameters": tool.inputSchema
            }
        } for tool in self.tools]

        # 初始化 LLM API 调用
        response = await self.client.chat.completions.create(
            model=model,
            messages=messages,
            tools=available_tools
        )

    
        final_text = []
        message = response.choices[0].message
        final_text.append(message.content or "")

        # 处理响应并处理工具调用
        while message.tool_calls:
            # 处理每个工具调用
            for tool_call in message.tool_calls:
                tool_name = tool_call.function.name
                tool_args = json.loads(tool_call.function.arguments)
                
                # 执行工具调用
                result = await self.sessions[tool_name].call_tool(tool_name, tool_args)
                #final_text.append(f"[Calling tool {tool_name} with args {tool_args}]")
                
                print(f"MCP: [Calling tool {tool_name} with args {tool_args}]")

                # 将工具调用和结果添加到消息历史
                messages.append({
                    "role": "assistant",
                    "tool_calls": [
                        {
                            "id": tool_call.id,
                            "type": "function",
                            "function": {
                                "name": tool_name,
                                "arguments": json.dumps(tool_args)
                            }
                        }
                    ]
                })
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": str(result.content)
                })

            # 将工具调用的结果交给 LLM
            response = await self.client.chat.completions.create(
                model=model,
                messages=messages,
                tools=available_tools
            )
            
            message = response.choices[0].message
            if message.content:
                final_text.append(message.content)
        
        answer="\n".join(final_text)
        self.messages=self.messages+[{"role": "assistant","content":answer}]
        return answer

    async def chat_loop(self):
        """运行交互式聊天循环"""
        print("\nMCP Client Started!")
        print("Type your queries or 'quit' to exit.")
        
        while True:
            try:
                query = input("\nYou: ").strip()
                if query.lower() == 'quit':
                    break
                response = await self.process_query(query)
                print("\nAI: " + response)
            except Exception as e:
                print(f"\nError: {str(e)}")

async def main():
    client = MCPClient()
    try:
        await client.connect_to_server()
        await client.chat_loop()
    finally:
        await client.cleanup()
        print("AI: Bye! See you next time!")

if __name__ == "__main__":
    asyncio.run(main())

#uv run client.py 启动客户端
