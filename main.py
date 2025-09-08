from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any
import uvicorn
import google.generativeai as genai
import os
from mcp_data_service import mcp_data_service

# 로컬 설정 파일 import (있는 경우에만)
try:
    from config_local import GEMINI_API_KEY as LOCAL_GEMINI_KEY
    # 로컬 API 키가 있으면 환경변수에 설정
    if LOCAL_GEMINI_KEY and LOCAL_GEMINI_KEY != "your_actual_api_key_here":
        os.environ["GEMINI_API_KEY"] = LOCAL_GEMINI_KEY
except ImportError:
    pass  # config_local.py가 없으면 환경변수만 사용

app = FastAPI(
    title="주식 질문 생성 API",
    description="키워드를 입력하면 주식앱에서 나올법한 질문을 생성하는 API",
    version="1.0.0"
)

class KeywordRequest(BaseModel):
    keyword: str

class QuestionResponse(BaseModel):
    keyword: str
    questions: List[str]  # 주식앱에서 나올법한 질문들

@app.get("/")
async def root():
    return {"message": "주식 질문 생성 API에 오신 것을 환영합니다!"}

async def generate_stock_questions(keyword: str) -> List[str]:
    """
    MCP 데이터를 기반으로 Gemini를 사용하여 주식앱에서 나올법한 질문을 생성합니다.
    """
    try:
        # 1. MCP를 통해 실제 데이터 수집
        mcp_data = await mcp_data_service.get_comprehensive_data(keyword)
        
        # 2. Gemini API 키 확인
        api_key = os.getenv("GEMINI_API_KEY")
        
        if not api_key:
            print("❌ GEMINI_API_KEY가 설정되지 않았습니다.")

        if not api_key:
            # API 키가 없으면 기본 질문 반환
            return [
                f"{keyword} 주식에 투자하는 것이 좋을까요?",
                f"{keyword}의 현재 주가 수준은 적정한가요?",
                f"{keyword}의 장기 투자 전망은 어떤가요?",
                f"{keyword} 관련 최신 뉴스는 무엇인가요?",
                f"{keyword}의 경쟁사 대비 우위는 무엇인가요?"
            ]
        
        # 3. Gemini 클라이언트 초기화
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        # 4. MCP 데이터를 기반으로 프롬프트 생성
        prompt = f"""
당신은 카카오페이증권에서 운영하는 AI 어시스턴트입니다. 
당신의 핵심 임무는 실시간으로 수집된 데이터를 기반으로, 사용자들이 가장 궁금해할 만한 핵심 질문을 생성하여 투자 결정에 도움을 주는 것입니다. 
---

## #2. 지시사항

사용자가 입력한 `{keyword}`와 아래 `#4. 입력 데이터`에 제공된 실시간 데이터를 종합적으로 분석하여, **주식 투자자들이 앱에서 즉시 클릭하고 싶을 만한 실용적인 질문 5개를 생성**하세요.

생성될 질문은 아래 3가지 카테고리를 균형 있게 포함해야 합니다.

*   **카테고리 1: 시황/경제 (Market/Economy):** 금리, 환율, 유가, FOMC, CPI 등 거시 경제 지표와 관련된 질문
*   **카테고리 2: 종목/산업 (Stock/Industry):** 특정 종목의 주가 변동, 실적 발표, 신기술, 산업 동향 등과 관련된 질문
*   **카테고리 3: 개념/용어 (Concept/Term):** 데이터에 등장하는 중요한 투자 용어 또는 경제 현상에 대한 설명 요청 질문

---

## #3. 사고 과정

다음 5단계의 사고 과정을 반드시 따르세요.

*   **1단계: 핵심 정보 식별**
    *   먼저, 사용자가 입력한 `{keyword}`의 의미를 파악합니다.
    *   그다음, 실시간 데이터 전체를 훑어보며 가장 중요하고 반복적으로 언급되는 주제, 종목명, 경제 이벤트, 수치(예: 실적, 금리) 등을 식별합니다.

*   **2단계: 정보 간 연관성 분석**
    *   `{keyword}`와 1단계에서 식별된 핵심 정보들 간의 관계를 분석합니다.
    *   예를 들어, `{keyword}`가 '엔비디아'라면, 엔비디아의 주가 정보(`stock_info`), 실적 관련 뉴스(`top_news`), 그리고 경쟁사 동향(`google_news`)을 연결하여 전체적인 맥락을 구성합니다. 만약 `{keyword}`가 '금리인하'라면, 연준 관련 뉴스, 채권 시장 데이터, 수혜 예상 업종 뉴스 등을 연결합니다.

*   **3단계: 카테고리별 질문 초안 생성**
    *   분석된 연관성을 바탕으로 위에서 정의된 3가지 카테고리(시황/경제, 종목/산업, 개념/용어)에 맞춰 각각 2~3개의 질문 초안을 만듭니다. 이 단계에서는 품질보다 아이디어의 양에 집중합니다.
    *   예시
        *   (시황) "오늘 FOMC 발표 이후 시장 반응은 어때?"
        *   (종목) "엔비디아 주가 급등, AI 칩 수요 때문이야?"
        *   (개념) "어닝 서프라이즈가 정확히 무슨 뜻이야?"

*   **4단계: 질문 고도화 및 스타일 적용**
    *   초안으로 만들어진 질문들을 투자자의 입장에서 더 매력적이고 구체적으로 다듬습니다.
    *   주식 앱 사용자에게 친근하게 다가갈 수 있는 어투를 사용합니다. (예: **"~궁금하지 않아?"**, **"~핵심만 알려줘"**, **"~어떻게 될까?"**, **"~이유가 뭐야?"**)
    *   데이터에 있는 구체적인 사실(숫자, 이벤트명)을 포함하여 질문의 신뢰도를 높입니다. (예: "엔비디아 **2분기 실적 발표**, 핵심만 알려줘")

*   **5단계: 최종 5개 질문 선정 (Select Final 5 Questions)**
    *   고도화된 질문들 중에서 가장 실용적이고, 시의성이 높으며, 카테고리 배분이 적절한 최종 5개의 질문을 선정합니다.

---

## #4. 입력 데이터

### Keyword
```
{keyword}
```

### Real-time Data (MCP)

stock_info: {mcp_data.get('stock_info', {})}
yahoo_news: {mcp_data.get('yahoo_news', [])}
google_news: {mcp_data.get('google_news', [])}
top_news: {mcp_data.get('top_news', [])}

---

## #5. 제약 조건 및 출력

*   **반드시** `#4. 입력데이터`에 제공된 데이터의 내용에 근거하여 질문을 생성해야 합니다.
*   **반드시** 한국어로 작성해야 합니다.
*   **반드시** 총 5개의 질문만 생성해야 합니다.
*   각 질문은 줄바꿈으로 구분하여 한 줄에 하나씩 작성해주세요.
*   질문 목록 외에 다른 부가 설명이나 서론, 결론을 포함하지 마세요.
*   **출력 예시:**
    ```
    오늘 연준의 금리 결정, 시장에 미칠 영향 궁금하지 않아?
    엔비디아 실적 발표, 핵심만 빠르게 알려줘.
    요즘 자주 보이는 'CBR'이 대체 무슨 뜻이야?
    삼성전자 주가, 반도체 업황 개선 기대감 때문일까?
    금리 인하가 되면 우리 증시에 뭐가 좋아?
"""
        
        # 5. Gemini API 호출
        response = model.generate_content(prompt)
        content = response.text
        
        # 6. 질문 파싱
        questions = [line.strip() for line in content.split('\n') if line.strip()]
        
        return questions[:5]  # 최대 5개
        
    except Exception as e:
        print(f"Gemini 질문 생성 실패: {e}")
        # 오류 시 기본 질문 반환
        return [
            f"{keyword} 주식에 투자하는 것이 좋을까요?",
            f"{keyword}의 현재 주가 수준은 적정한가요?",
            f"{keyword}의 장기 투자 전망은 어떤가요?",
            f"{keyword} 관련 최신 뉴스는 무엇인가요?",
            f"{keyword}의 경쟁사 대비 우위는 무엇인가요?"
        ]

@app.post("/questions", response_model=QuestionResponse)
async def generate_questions(keyword_request: KeywordRequest):
    """
    키워드를 기반으로 주식앱에서 나올법한 질문을 생성합니다.
    """
    try:
        keyword = keyword_request.keyword.upper()
        
        # LLM을 통한 질문 생성
        questions = await generate_stock_questions(keyword)
        
        return QuestionResponse(
            keyword=keyword,
            questions=questions
        )
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"질문 생성 중 오류가 발생했습니다: {str(e)}")

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "market-analysis-api"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
