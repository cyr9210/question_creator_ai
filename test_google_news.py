from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client
from config_local import SMITHERY_API_KEY as LOCAL_SMITHERY_API_KEY

# Construct server URL with authentication
from urllib.parse import urlencode
base_url = "https://server.smithery.ai/@jmanek/google-news-trends-mcp/mcp"
params = {"api_key": LOCAL_SMITHERY_API_KEY}
url = f"{base_url}?{urlencode(params)}"

async def main():
    # Connect to the server using HTTP client
    async with streamablehttp_client(url) as (read, write, _):
        async with ClientSession(read, write) as session:
            # Initialize the connection
            await session.initialize()
            
            # List available tools
            result = await session.call_tool(
                "get_news_by_keyword",
                arguments={
                    "keyword": "AAPL",
                    "max_results": 3,
                    "period": 3,
                    "summarize": False  # 요약 기능 비활성화
                }
            )
            print(f"Google News MCP 실제 결과: {result}")

async def main2():
    async with streamablehttp_client(url) as (read, write, _):
        async with ClientSession(read, write) as session:
            # Initialize the connection
            await session.initialize()
            
            # List available tools
            result = await session.call_tool(
                "get_top_news",
                arguments={
                    "max_results": 3,
                    "period": 1,
                    "summarize": False  # 요약 기능 비활성화
                }
            )
            print(f"Google News MCP 실제 결과: {result}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main2())