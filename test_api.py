#!/usr/bin/env python3
"""
API 테스트 스크립트
"""

import asyncio
import aiohttp
import json

async def test_api():
    """API 테스트 함수"""
    
    base_url = "http://localhost:8000"
    
    async with aiohttp.ClientSession() as session:
        # 1. 헬스 체크 테스트
        print("=== 헬스 체크 테스트 ===")
        try:
            async with session.get(f"{base_url}/health") as response:
                if response.status == 200:
                    result = await response.json()
                    print(f"✅ 헬스 체크 성공: {result}")
                else:
                    print(f"❌ 헬스 체크 실패: {response.status}")
        except Exception as e:
            print(f"❌ 헬스 체크 오류: {e}")
        
        print("\n" + "="*50 + "\n")
        
        # 2. 시황 분석 테스트
        print("=== 시황 분석 테스트 ===")
        test_data = {
            "keyword": "엔비디아",
            "period": "1mo"
        }
        
        try:
            async with session.post(
                f"{base_url}/analyze",
                json=test_data,
                headers={"Content-Type": "application/json"}
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    print(f"✅ 시황 분석 성공!")
                    print(f"키워드: {result['keyword']}")
                    print(f"시황 분석: {result['market_analysis']}")
                    print(f"시황 관련 질문 수: {len(result['market_questions'])}")
                    print(f"뉴스 관련 질문 수: {len(result['news_questions'])}")
                    print(f"추천사항 수: {len(result['recommendations'])}")
                    
                    print("\n--- 시황 관련 질문들 ---")
                    for i, question in enumerate(result['market_questions'], 1):
                        print(f"{i}. {question}")
                    
                    print("\n--- 뉴스 관련 질문들 ---")
                    for i, question in enumerate(result['news_questions'], 1):
                        print(f"{i}. {question}")
                    
                    print("\n--- 추천사항들 ---")
                    for i, rec in enumerate(result['recommendations'], 1):
                        print(f"{i}. {rec}")
                        
                else:
                    error_text = await response.text()
                    print(f"❌ 시황 분석 실패: {response.status}")
                    print(f"오류 내용: {error_text}")
        except Exception as e:
            print(f"❌ 시황 분석 오류: {e}")

if __name__ == "__main__":
    print("API 테스트를 시작합니다...")
    print("서버가 실행 중인지 확인하세요: python main.py")
    print()
    
    asyncio.run(test_api())
