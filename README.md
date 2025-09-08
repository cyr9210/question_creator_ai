# 주식 질문 생성 API
키워드를 입력하면 Yahoo Finance MCP와 Google News MCP를 사용하여 실제 시장 데이터와 뉴스를 분석하고, Gemini AI를 통해 주식앱에서 나올법한 질문을 생성하는 API입니다.

## 설치 및 실행

### 1. 의존성 설치
```bash
pip3 install -r requirements.txt
```

### 2. NLTK 데이터 설치 (Google News MCP용)
```bash
python3.11 -c "import nltk; nltk.download('punkt_tab')"
```

### 3. Playwright 브라우저 설치 (Google News MCP용)
```bash
playwright install
```

### 4. API 키 설정
/config_local.py
```bash
"""
로컬 환경 설정 파일
이 파일은 .gitignore에 포함되어 Git에 업로드되지 않습니다.
"""

# Gemini API 키 (실제 키로 교체하세요)
GEMINI_API_KEY = "GEMINI_API_KEY"

# 서버 설정
HOST = "0.0.0.0"
PORT = 8001
DEBUG = True
LOG_LEVEL = "info"
```

### 5. 서버 실행
```bash
# Yahoo Finance MCP 서버 시작
cd yahoo-finance-mcp && python3.11 server.py > yahoo_finance_mcp.log 2>&1 &

# Google News MCP 서버 시작
cd .. && python3.11 -m google_news_trends_mcp > google_news_mcp.log 2>&1 &

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

- **Yahoo Finance MCP**: 실시간 주식 데이터 수집 (주가, 시가총액, 거래량 등)
- **Google News MCP**: 관련 뉴스 및 주요 뉴스 수집
- **Gemini AI**: 수집된 데이터를 바탕으로 주식앱 스타일의 질문 생성

## API 키 설정

API 키가 설정되지 않으면 기본 질문이 반환됩니다. Gemini API를 사용하려면:

1. [Google AI Studio](https://makersuite.google.com/app/apikey)에서 API 키 발급
2. 환경변수 또는 `config_local.py` 파일에 설정

## 보안

- `config_local.py` 파일은 `.gitignore`에 포함되어 Git에 업로드되지 않습니다
- API 키는 절대 공개 저장소에 업로드하지 마세요

## 서버 종료

```bash
# 모든 서버 종료
pkill -f "run.py"
pkill -f "google_news_trends_mcp"
pkill -f "yahoo-finance-mcp"
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