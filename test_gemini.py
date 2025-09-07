#!/usr/bin/env python3
"""
Gemini API 테스트 스크립트
"""

import asyncio
import os
import google.generativeai as genai

async def test_gemini():
    """Gemini API 테스트"""
    try:
        # API 키 확인
        api_key = os.getenv("GEMINI_API_KEY")
        print(f"API 키 설정됨: {'Yes' if api_key else 'No'}")
        
        if not api_key:
            print("❌ GEMINI_API_KEY가 설정되지 않았습니다.")
            return
        
        # Gemini 클라이언트 초기화
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-pro')
        
        # 테스트 프롬프트
        prompt = """
당신은 주식 투자 앱의 AI 어시스턴트입니다. 
사용자가 "AAPL"라는 키워드를 입력했을 때, 주식앱에서 나올법한 실용적인 질문 3개를 생성해주세요.

각 질문을 한 줄씩 작성해주세요.
"""
        
        print("🔄 Gemini API 호출 중...")
        
        # Gemini API 호출
        response = model.generate_content(prompt)
        content = response.text
        
        print("✅ Gemini API 호출 성공!")
        print("\n📝 생성된 질문들:")
        print("-" * 50)
        
        # 질문 파싱
        questions = [line.strip() for line in content.split('\n') if line.strip()]
        for i, question in enumerate(questions[:3], 1):
            print(f"{i}. {question}")
        
        print("-" * 50)
        
    except Exception as e:
        print(f"❌ 오류 발생: {e}")

if __name__ == "__main__":
    asyncio.run(test_gemini())
