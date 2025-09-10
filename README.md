# 주식 질문 생성 API
키워드를 입력하면 Yahoo Finance MCP와 Google News MCP를 사용하여 실제 시장 데이터와 뉴스를 분석하고, Gemini AI를 통해 주식앱에서 나올법한 질문을 생성하는 API입니다.

## 설치 및 실행

### 1. 의존성 설치
```bash
pip3 install -r requirements.txt
```

### 4. API 키 설정
.env 파일을 root 경로에 추가한다.
```bash
# Gemini API 키 (실제 키로 교체하세요)
GEMINI_API_KEY = "GEMINI_API_KEY"
SMITHERY_API_KEY = "SMITHERY_API_KEY"
```

### 5. 서버 실행
```bash
# 메인 API 서버 시작
python3.11 run.py > api_server.log 2>&1 &
```

### 6. API 테스트
```bash
curl -X POST "http://localhost:8001/questions" \
  -H "Content-Type: application/json" \
  -d '{"keyword": "AAPL"}' \
  --max-time 60
```

## API 엔드포인트

- `POST /questions`: 키워드 기반 주식 질문 생성
- `GET /health`: 서버 상태 확인

## 기능

- **Yahoo Finance MCP**: 실시간 주식 데이터 수집 (주가, 시가총액, 거래량 등) [링크](https://smithery.ai/server/@hwangwoohyun-nav/yahoo-finance-mcp)
- **Google News MCP**: 관련 뉴스 및 주요 뉴스 수집 [링크](https://smithery.ai/server/@jmanek/google-news-trends-mcp)
- **Gemini AI**: 수집된 데이터를 바탕으로 주식앱 스타일의 질문 생성

## API 키 설정

API 키가 설정되지 않으면 기본 질문이 반환됩니다. Gemini API를 사용하려면:

1. [Google AI Studio](https://makersuite.google.com/app/apikey)에서 API 키 발급
2. [smithery](https://smithery.ai/)에서 API 키 발급
3. 환경변수 또는 `.env` 파일에 설정

## 서버 종료

```bash
# 모든 서버 종료
pkill -f "run.py"
```

## 사용법

### 요청 예시
```json
{
  "keyword": "AAPL"
}
```

### 응답 예시
```json
{
  "keyword": "AAPL",
  "questions": [
    "AAPL 주식에 투자하는 것이 좋을까요?",
    "AAPL의 현재 주가 수준은 적정한가요?",
    "AAPL의 장기 투자 전망은 어떤가요?",
    "AAPL 관련 최신 뉴스는 무엇인가요?",
    "AAPL의 경쟁사 대비 우위는 무엇인가요?"
  ]
}
```

## 라이선스

MIT License