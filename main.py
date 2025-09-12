from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any
import asyncio
import uvicorn
from fastmcp import Client
from urllib.parse import urlencode
from dotenv import load_dotenv
import os
from datetime import datetime, timedelta
load_dotenv()
from google import genai
from langchain.output_parsers import PydanticOutputParser
from fastapi.middleware.cors import CORSMiddleware

smithery_key = os.getenv("SMITHERY_API_KEY")

# google_news_base_url = "https://server.smithery.ai/@jmanek/google-news-trends-mcp/mcp"
# params = {"api_key": smithery_key}
# google_news_url = f"{google_news_base_url}?{urlencode(params)}"


naver_news_base_url = "https://server.smithery.ai/@isnow890/naver-search-mcp/mcp"
params = {"api_key": smithery_key}
naver_news_url = f"{naver_news_base_url}?{urlencode(params)}"

# yahoo_base_url = "https://server.smithery.ai/@hwangwoohyun-nav/yahoo-finance-mcp/mcp"
# params = {"api_key": smithery_key}
# yahoo_url= f"{yahoo_base_url}?{urlencode(params)}"

# yahoo_client = Client(yahoo_url)
# google_client = Client(google_news_url)
naver_client = Client(naver_news_url)
internal_client = Client("mcp_main.py")
gemini_client = genai.Client()

app = FastAPI(
    title="주식 질문 생성 API",
    description="키워드를 입력하면 주식앱에서 나올법한 질문을 생성하는 API",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 모든 도메인에서 접근 허용
    allow_credentials=True,
    allow_methods=["*"],  # 모든 HTTP 메서드 허용
    allow_headers=["*"],  # 모든 헤더 허용
)

class KeywordRequest(BaseModel):
    keyword: str
    user_data: dict = None

class QuestionResponse(BaseModel):
    keyword: str
    questions: List[str]  # 주식앱에서 나올법한 질문들

@app.get("/")
async def root():
    return {"message": "주식 질문 생성 API에 오신 것을 환영합니다!"}

@app.post("/questions", response_model=QuestionResponse)
async def generate_questions(keyword_request: KeywordRequest):
    
    """
    키워드를 기반으로 주식앱에서 나올법한 질문을 생성합니다.
    """
    try:
        keyword = keyword_request.keyword.upper()
        user_data = keyword_request.user_data
        
        # LLM을 통한 질문 생성
        questions = await generate_stock_questions(keyword, user_data, datetime.now())
        
        return QuestionResponse(
            keyword=keyword,
            questions=questions
        )
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"질문 생성 중 오류가 발생했습니다: {str(e)}")

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "market-analysis-api"}

async def generate_stock_questions(keyword: str, user_data: str, current_date: datetime) -> List[str]:
    async with naver_client, internal_client:
        """
        MCP 데이터를 기반으로 Gemini를 사용하여 주식앱에서 나올법한 질문을 생성합니다.
        """ 
        
        parser = PydanticOutputParser(pydantic_object=QuestionResponse)
        format_instructions = parser.get_format_instructions()

        # 4. MCP 데이터를 기반으로 프롬프트 생성
        prompt1= f"""
## #1. 페르소나
당신은 카카오페이증권에서 운영하는 AI 어시스턴트입니다. 
당신의 핵심 임무는 고객의 투자 수준과 관심사를 파악하여, 실시간으로 수집된 데이터를 기반으로 개인화된 핵심 질문을 생성하여 투자 결정에 도움을 주는 것입니다. 
---

## #2. 지시사항

고객이 입력한 `{keyword}`와 고객 정보(`{user_data}`), 그리고 `{current_date}` 기준의 실시간 데이터를 종합적으로 분석하여, **해당 고객이 앱에서 즉시 클릭하고 싶을 만한 개인화된 질문 5개를 생성**하세요.

생성될 질문은 아래 3가지 카테고리를 균형 있게 포함해야 합니다.

*   **카테고리 1: 시황/경제 (Market/Economy):** 금리, 환율, 유가, FOMC, CPI 등 거시 경제 지표와 관련된 질문
*   **카테고리 2: 종목/산업 (Stock/Industry):** 특정 종목의 주가 변동, 실적 발표, 신기술, 산업 동향 등과 관련된 질문
*   **카테고리 3: 개념/용어 (Concept/Term):** 데이터에 등장하는 중요한 투자 용어 또는 경제 현상에 대한 설명 요청 질문

---

## #3. 사고 과정

다음 6단계의 사고 과정을 반드시 따르세요.

*   **1단계: 고객 수준 및 관심사 파악**
    *   `{user_data}`를 분석하여 고객의 투자 경험 수준, 보유 포트폴리오, 거래 패턴, 관심 업종/종목 등을 파악합니다.
    *   고객이 초보자인지, 중급자인지, 고급자인지 판단하고, 그에 맞는 질문의 난이도와 깊이를 결정합니다.
    *   고객의 보유 종목이나 관심 업종과 `{keyword}`의 연관성을 분석합니다.

*   **2단계: 핵심 정보 식별**
    *   먼저, 고객이 입력한 `{keyword}`의 의미를 파악합니다.
    *   `{current_date}` 기준으로 실시간 데이터 전체를 훑어보며 가장 중요하고 반복적으로 언급되는 주제, 종목명, 경제 이벤트, 수치(예: 실적, 금리) 등을 식별합니다.

*   **3단계: 정보 간 연관성 분석**
    *   `{keyword}`, 고객 정보, 그리고 2단계에서 식별된 핵심 정보들 간의 관계를 분석합니다.
    *   예를 들어, `{keyword}`가 '엔비디아'이고 고객이 AI 관련 종목을 보유하고 있다면, 엔비디아의 주가 정보(`stock_info`), 실적 관련 뉴스(`top_news`), 그리고 고객의 포트폴리오에 미치는 영향을 연결하여 분석합니다.

*   **4단계: 고객 수준별 질문 초안 생성**
    *   분석된 연관성과 고객 수준을 바탕으로 위에서 정의된 3가지 카테고리(시황/경제, 종목/산업, 개념/용어)에 맞춰 각각 2~3개의 질문 초안을 만듭니다.
    *   고객의 수준에 따라 질문의 복잡도와 전문성을 조절합니다:
        *   **초보자**: 기본적인 개념 설명과 단순한 시장 동향 질문
        *   **중급자**: 구체적인 분석과 전략적 관점의 질문
        *   **고급자**: 심화된 분석과 전문적인 투자 전략 질문
    *   예시
        *   (초보자-시황) "오늘 FOMC 발표가 뭔지, 주식에 어떤 영향이 있을까?"
        *   (중급자-종목) "엔비디아 주가 급등, AI 칩 수요 증가가 실적에 미치는 영향은?"
        *   (고급자-개념) "어닝 서프라이즈의 통계적 유의성과 포트폴리오 리밸런싱 전략은?"

*   **5단계: 질문 고도화 및 개인화**
    *   초안으로 만들어진 질문들을 고객의 수준과 관심사에 맞게 개인화하여 다듬습니다.
    *   고객의 보유 종목이나 관심 업종을 언급하여 관련성을 높입니다.
    *   주식 앱 고객들에게 친근하게 다가갈 수 있는 어투를 사용합니다. (예: **"~궁금하지 않아?"**, **"~핵심만 알려줘"**, **"~어떻게 될까?"**, **"~이유가 뭐야?"**)
    *   `{current_date}` 기준의 구체적인 사실(숫자, 이벤트명)을 포함하여 질문의 신뢰도와 시의성을 높입니다.

*   **6단계: 최종 5개 질문 선정 (Select Final 5 Questions)**
    *   개인화된 질문들 중에서 고객의 수준에 가장 적합하고, 시의성이 높으며, 카테고리 배분이 적절한 최종 5개의 질문을 선정합니다.

—

## #4. 입력 데이터

### Keyword
```
{keyword}
```

### User Info
```
{user_data}
```

### Current Date
```
{current_date}
```

## 출력
{format_instructions}
"""
        
        response = await gemini_client.aio.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt1,
                config=genai.types.GenerateContentConfig(
                    temperature=0,
                    tools=[naver_client.session, internal_client.session],
                ),
            )
            
        # 5. Gemini API 호출
        content = response.text
        parsed_response = parser.parse(content)
        # 6. 질문 파싱

        return parsed_response.questions[:5]

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
