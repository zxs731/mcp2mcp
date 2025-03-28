# server.py
from mcp.server.fastmcp import FastMCP
# Create an MCP server
mcp = FastMCP("MCP_KowledgeBase")
   
@mcp.tool()
def get_knowledge(query:str)-> str:
    """
    获取MCP的相关知识，包括开发MCP客户端和MCP服务器的方法和模版代码。MCP是一个基于FastAPI的MCP服务器。
    
    params: 
        query: 关键字或查询内容
    
    """
    
    kb="""
MCP 是一个开放协议，它标准化了应用程序如何向LLMs提供上下文。可以将 MCP 视为 AI 应用程序的 USB-C 端口。正如 USB-C 提供了一种标准化的方法来将您的设备连接到各种外围设备和配件一样，MCP 提供了一种标准化的方法来将 AI 模型连接到不同的数据源和工具。
MCP开发的核心是MCP Server，可以给您一个MCP Server的模版代码，您可以根据自己的需求进行修改。同时，您可以获取MCP客户端的配置方式。如果需要请告诉我。
"""
    
    return kb



@mcp.tool()       
def get_MCP_Client_Config():
    """
    获取MCP客户端配置方式
    
    return: 
       MCP客户端配置方式
    """
    template_code = """
'''In your client setting json file (eg: mcp_server_config.json), you can set the following parameters:'''
{
  "mcpServers": {
    "<server_1>": {
      "command": "python",
      "args": [
        "/<your MCP server main file path>/<MCP Server>.py"
      ]
    }
  }
}
    """
    return template_code
    

@mcp.tool()       
def get_MCP_Server_Code():
    """
    获取MCP服务端代码模版
    
    return: 
        MCP服务端代码模版
    """
    template_code = """
from mcp.server.fastmcp import FastMCP
mcp = FastMCP("<MCPServerName>")
   
@mcp.tool()
def <MCP_Tool_1>(<input_parameter_1>,<input_parameter_2>,...)-> str:
    \"\"\"
    <MCP_Tool_1>的描述
    
    params: 
        <input_parameter_1>: <input_parameter_1>的描述
        <input_parameter_2>: <input_parameter_2>的描述
        ...
    
    return: 
        <MCP_Tool_1>的返回值描述
    \"\"\"
    '''这里实现该工具<MCP_Tool_1>的业务逻辑'''

@mcp.tool()
def <MCP_Tool_2>(<input_parameter_1>,<input_parameter_2>,...)-> str:
    \"\"\"
    <MCP_Tool_2>的描述
    
    params: 
        <input_parameter_1>: <input_parameter_1>的描述
        <input_parameter_2>: <input_parameter_2>的描述
        ...
    
    return: 
        <MCP_Tool_2>的返回值描述
    \"\"\"
    '''这里实现该工具<MCP_Tool_2>的业务逻辑'''
    """
    return template_code
    
if __name__ == "__main__":
   print("Server running")
   mcp.run(transport='stdio')


