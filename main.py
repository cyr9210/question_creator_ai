from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any
import uvicorn
import google.generativeai as genai
import os
from mcp_data_service import mcp_data_service

# 로컬 설정 파일 import (있는 경우에만)
try:
    from config_local import GEMINI_API_KEY as LOCAL_GEMINI_KEY, SMITHERY_API_KEY as LOCAL_SMITHERY_KEY
    # 로컬 API 키가 있으면 환경변수에 설정
    if LOCAL_GEMINI_KEY and LOCAL_GEMINI_KEY != "your_actual_api_key_here":
        os.environ["GEMINI_API_KEY"] = LOCAL_GEMINI_KEY
    if LOCAL_SMITHERY_KEY and LOCAL_SMITHERY_KEY != "your_smithery_api_key_here":
        os.environ["SMITHERY_API_KEY"] = LOCAL_SMITHERY_KEY
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
당신은 주식 투자 앱의 AI 어시스턴트입니다. 
사용자가 "{keyword}"라는 키워드를 입력했을 때, 아래 실제 데이터를 바탕으로 주식앱에서 나올법한 실용적인 질문 5개를 생성해주세요.

=== 실제 수집된 데이터 ===
주식 정보: {mcp_data.get('stock_info', {})}
Yahoo 뉴스: {mcp_data.get('yahoo_news', [])}
Google 뉴스: {mcp_data.get('google_news', [])}
주요 뉴스: {mcp_data.get('top_news', [])}

질문은 다음과 같은 특징을 가져야 합니다:
- 위 실제 데이터를 참고하여 구체적인 질문 생성
- 투자자들이 실제로 궁금해할 만한 내용
- 주식앱에서 자주 나오는 질문 스타일
- 한국어로 작성

각 질문을 한 줄씩 작성해주세요.
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
