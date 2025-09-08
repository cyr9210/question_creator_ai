"""
MCP 데이터 수집 서비스
Cursor에서 설정된 Yahoo Finance와 Google News MCP를 사용하여 실제 데이터를 수집합니다.
"""

import asyncio
import subprocess
import json
from typing import Dict, Any, List
from datetime import datetime, timedelta
from mcp import ClientSession, StdioServerParameters
from mcp.client.streamable_http import streamablehttp_client
from mcp.client.stdio import stdio_client
from config_local import SMITHERY_API_KEY as LOCAL_SMITHERY_API_KEY

from urllib.parse import urlencode
google_news_base_url = "https://server.smithery.ai/@jmanek/google-news-trends-mcp/mcp"
params = {"api_key": LOCAL_SMITHERY_API_KEY}
url = f"{google_news_base_url}?{urlencode(params)}"

class MCPDataService:
    """
    MCP 데이터 수집 서비스
    """
    
    def __init__(self):
        pass
    
    async def get_comprehensive_data(self, keyword: str) -> Dict[str, Any]:
        """
        MCP를 통해 종합적인 데이터를 수집합니다.
        """
        try:
            # 1. Yahoo Finance MCP로 주식 정보 수집
            stock_info = await self._get_yahoo_stock_info(keyword)
            
            # 2. Yahoo Finance MCP로 뉴스 수집
            yahoo_news = await self._get_yahoo_news(keyword)
            
            # 3. Google News MCP로 뉴스 수집
            google_news = await self._get_google_news(keyword)
            
            # 4. Google News MCP로 주요 뉴스 수집
            top_news = await self._get_google_top_news()
            
            return {
                "stock_info": stock_info,
                "yahoo_news": yahoo_news,
                "google_news": google_news,
                "top_news": top_news,
                "collection_timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"MCP 데이터 수집 중 오류 발생: {e}")
            # 오류 시 빈 데이터 반환
            return {
                "stock_info": {},
                "yahoo_news": [],
                "google_news": [],
                "top_news": [],
                "collection_timestamp": datetime.now().isoformat(),
                "error": str(e)
            }
    
    async def _get_yahoo_stock_info(self, ticker: str) -> Dict[str, Any]:
        """
        Yahoo Finance MCP로 주식 정보를 가져옵니다.
        """
        try:
            print(f"Yahoo Finance MCP 호출 시도: {ticker}")
            
            # Yahoo Finance MCP 서버에 HTTP 요청
            import aiohttp
            
            async with aiohttp.ClientSession() as session:
                # MCP 서버는 보통 stdio를 사용하므로, 직접 HTTP 요청 대신 subprocess로 호출
                # Yahoo Finance MCP의 get_stock_info 도구를 호출
                cmd = [
                    "python3.11", "-c",
                    f"""
import sys
sys.path.append('/Users/choeyonglag/Ai/yahoo-finance-mcp')
import yfinance as yf
import json

def get_stock_info():
    try:
        # yfinance를 직접 사용하여 주식 정보 가져오기
        ticker = yf.Ticker("{ticker}")
        info = ticker.info
        
        # 기본 정보 추출
        result = {{
            "symbol": info.get("symbol", "{ticker}"),
            "name": info.get("longName", "{ticker} Corporation"),
            "price": info.get("currentPrice", 0),
            "change": info.get("regularMarketChange", 0),
            "change_percent": info.get("regularMarketChangePercent", 0),
            "market_cap": info.get("marketCap", 0),
            "volume": info.get("volume", 0)
        }}
        return result
    except Exception as e:
        return {{"error": str(e)}}

result = get_stock_info()
print(json.dumps(result))
"""
                ]
                
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                
                if result.returncode == 0:
                    try:
                        data = json.loads(result.stdout)
                        print(f"Yahoo Finance MCP 결과: {data}")
                        return data
                    except json.JSONDecodeError:
                        print(f"Yahoo Finance MCP JSON 파싱 실패: {result.stdout}")
                        return {}
                else:
                    print(f"Yahoo Finance MCP 실행 실패: {result.stderr}")
                    return {}
                    
        except Exception as e:
            print(f"Yahoo Finance MCP 호출 실패: {e}")
            return {}
    
    async def _get_yahoo_news(self, ticker: str) -> List[Dict[str, Any]]:
        """
        Yahoo Finance MCP로 뉴스를 가져옵니다.
        """
        try:
            print(f"Yahoo News MCP 호출 시도: {ticker}")
            
            # Yahoo Finance MCP의 get_yahoo_finance_news 도구를 호출
            cmd = [
                "python3.11", "-c",
                f"""
import sys
sys.path.append('/Users/choeyonglag/Ai/yahoo-finance-mcp')
import yfinance as yf
import json

def get_yahoo_news():
    try:
        # yfinance를 직접 사용하여 뉴스 가져오기
        ticker = yf.Ticker("{ticker}")
        news = ticker.news
        
        # 뉴스 데이터 정리
        result = []
        for item in news[:5]:  # 최대 5개
            result.append({{
                "title": item.get("title", ""),
                "summary": item.get("summary", ""),
                "url": item.get("link", ""),
                "published": item.get("providerPublishTime", ""),
                "provider": item.get("provider", "")
            }})
        return result
    except Exception as e:
        return [{{"error": str(e)}}]

result = get_yahoo_news()
print(json.dumps(result))
"""
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                try:
                    data = json.loads(result.stdout)
                    print(f"Yahoo News MCP 결과: {data}")
                    return data if isinstance(data, list) else []
                except json.JSONDecodeError:
                    print(f"Yahoo News MCP JSON 파싱 실패: {result.stdout}")
                    return []
            else:
                print(f"Yahoo News MCP 실행 실패: {result.stderr}")
                return []
                
        except Exception as e:
            print(f"Yahoo News MCP 호출 실패: {e}")
            return []
    
    async def _get_google_news(self, keyword: str) -> List[Dict[str, Any]]:
        """
        Google News MCP로 뉴스를 가져옵니다.
        """
        
        try:
            print(f"Google News MCP 호출 시도: {keyword}")
            
            # MCP 클라이언트를 통해 Google News MCP와 통신
            # Construct server URL with authentication

            async with streamablehttp_client(url) as (read, write, _):
                async with ClientSession(read, write) as session:
                    # Initialize the connection
                    await session.initialize()
                    
                    # List available tools
                    result = await session.call_tool(
                        "get_news_by_keyword",
                        arguments={
                            "keyword": keyword,
                            "max_results": 3,
                            "period": 3,
                            "summarize": False  # 요약 기능 비활성화
                        }
                    )
                    print(f"Google News MCP 실제 결과: {result}")
                    return result.content if hasattr(result, 'content') else []
                        
        except Exception as e:
            print(f"Google News MCP 호출 실패: {e}")
            return []
    
    async def _get_google_top_news(self) -> List[Dict[str, Any]]:
        """
        Google News MCP로 주요 뉴스를 가져옵니다.
        """
        try:
            print(f"Google Top News MCP 호출 시도")
            
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
                    return result.content if hasattr(result, 'content') else []
                        
        except Exception as e:
            print(f"Google Top News MCP 호출 실패: {e}")
            return []

# 전역 MCP 데이터 서비스 인스턴스
mcp_data_service = MCPDataService()
