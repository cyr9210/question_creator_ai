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
NAVER_CLIENT_ID = "clientId",
NAVER_CLIENT_SECRET = "secret"
```

### 5. 서버 실행
```bash
# 메인 API 서버 시작
pip3 run.py > api_server.log 2>&1 &
```

### 6. API 테스트
```bash
curl -X POST "http://localhost:8002/questions" \
  -H "Content-Type: application/json" \
  -d '{
    "keyword": "애플",
    "user_data": "{\"user_id\": \"user_0001_1757652986\", \"characteristics\": [{\"characteristic\": \"자산포트폴리오정보\", \"value\": {\"총자산\": 50000000, \"예수금\": 10000000, \"주식평가금액\": 40000000, \"총평가손익\": 5000000, \"보유종목\": [{\"종목명\": \"삼성전자\", \"수량\": 500, \"평균매수가\": 75000, \"화폐\": \"KRW\"}, {\"종목명\": \"SK하이닉스\", \"수량\": 100, \"평균매수가\": 130000, \"화폐\": \"KRW\"}]}, \"description\": \"소액투자자\", \"confidence\": 0.82, \"generated_at\": \"2025-09-12T13:56:26.525708\"}, {\"characteristic\": \"거래행태정보\", \"value\": {\"월평균매매횟수\": 5, \"최근거래일\": \"2025-01-12\", \"평균보유기간\": \"중기(3-6개월)\", \"거래패턴\": \"중기투자형\"}, \"description\": \"중 기투자형\", \"confidence\": 0.89, \"generated_at\": \"2025-09-12T13:56:26.525740\"}, {\"characteristic\": \"서비스내행동정보\", \"value\": {\"콘텐츠소비\": {\"뉴스조회(월)\": 200, \"공시조회(월)\": 100}, \"투자정보조회\": {\"재무제표조회(월)\": 80, \"배당정보조회(월)\": 40}, \"커뮤니티활동\": {\"조회(일)\": 50}, \"관심종목수\": 100}, \"description\": \"고급사용자\", \"confidence\": 0.83, \"generated_at\": \"2025-09-12T13:56:26.525753\"}, {\"characteristic\": \"투자경험수준\", \"value\": \"고급자 (7-15년)\", \"description\": \"풍부한 투자 경험과 전문 지식을 가진 고급자\", \"confidence\": 0.74, \"generated_at\": \"2025-09-12T13:56:26.525764\"}, {\"characteristic\": \"투자성향\", \"value\": \"성장추구형\", \"description\": \"장기적 성장을 추구하는 성향\", \"confidence\": 0.91, \"generated_at\": \"2025-09-12T13:56:26.525775\"}, {\"characteristic\": \"관심섹터\", \"value\": \"유틸리티주 (전력, 가스, 수도)\", \"description\": \"공공 서비스를 제공하는 섹터\", \"confidence\": 0.81, \"generated_at\": \"2025-09-12T13:56:26.525786\"}, {\"characteristic\": \"투자금액규모\", \"value\": \"초고액투자자 (5억원 이상)\", \"description\": \"5억원 이상 투자하는 고액 투자자\", \"confidence\": 0.62, \"generated_at\": \"2025-09-12T13:56:26.525796\"}]}"
  }'
```

## API 엔드포인트

- `POST /questions`: 키워드 기반 주식 질문 생성
- `GET /health`: 서버 상태 확인

## 기능

- **Gemini AI**: 수집된 데이터를 바탕으로 주식앱 스타일의 질문 생성
- **Naver Search**: naver 검색 MCP [링크](https://smithery.ai/server/@isnow890/naver-search-mcp)

## API 키 설정

API 키가 설정되지 않으면 기본 질문이 반환됩니다. Gemini API를 사용하려면:

1. [Google AI Studio](https://makersuite.google.com/app/apikey)에서 API 키 발급
2. [smithery](https://smithery.ai/)에서 API 키 발급
3. Naver api key 생성
4. 환경변수 또는 `.env` 파일에 설정

## 서버 종료

```bash
# 모든 서버 종료
pkill -f "run.py"
```

## 사용법

### 요청 예시
```json
{
	"keyword": "에이다",
	"question_count": 10,
	"user_data": {
		"user_id": "user_0001_1757652986",
		"characteristics": [
			{
				"characteristic": "자산포트폴리오정보",
				"value": {
					"총자산": 50000000,
					"예수금": 10000000,
					"주식평가금액": 40000000,
					"총평가손익": 5000000,
					"보유종목": [
						{
							"종목명": "삼성전자",
							"수량": 500,
							"평균매수가": 75000,
							"화폐": "KRW"
						},
						{
							"종목명": "SK하이닉스",
							"수량": 100,
							"평균매수가": 130000,
							"화폐": "KRW"
						}
					]
				},
				"description": "소액투자자",
				"confidence": 0.82,
				"generated_at": "2025-09-12T13:56:26.525708"
			},
			{
				"characteristic": "거래행태정보",
				"value": {
					"월평균매매횟수": 5,
					"최근거래일": "2025-01-12",
					"평균보유기간": "중기(3-6개월)",
					"거래패턴": "중기투자형"
				},
				"description": "중기투자형",
				"confidence": 0.89,
				"generated_at": "2025-09-12T13:56:26.525740"
			},
			{
				"characteristic": "서비스내행동정보",
				"value": {
					"콘텐츠소비": {
						"뉴스조회(월)": 200,
						"공시조회(월)": 100
					},
					"투자정보조회": {
						"재무제표조회(월)": 80,
						"배당정보조회(월)": 40
					},
					"커뮤니티활동": {
						"조회(일)": 50
					},
					"관심종목수": 100
				},
				"description": "고급사용자",
				"confidence": 0.83,
				"generated_at": "2025-09-12T13:56:26.525753"
			},
			{
				"characteristic": "투자경험수준",
				"value": "고급자 (7-15년)",
				"description": "풍부한 투자 경험과 전문 지식을 가진 고급자",
				"confidence": 0.74,
				"generated_at": "2025-09-12T13:56:26.525764"
			},
			{
				"characteristic": "투자성향",
				"value": "성장추구형",
				"description": "장기적 성장을 추구하는 성향",
				"confidence": 0.91,
				"generated_at": "2025-09-12T13:56:26.525775"
			},
			{
				"characteristic": "관심섹터",
				"value": "유틸리티주 (전력, 가스, 수도)",
				"description": "공공 서비스를 제공하는 섹터",
				"confidence": 0.81,
				"generated_at": "2025-09-12T13:56:26.525786"
			},
			{
				"characteristic": "투자금액규모",
				"value": "초고액투자자 (5억원 이상)",
				"description": "5억원 이상 투자하는 고액 투자자",
				"confidence": 0.62,
				"generated_at": "2025-09-12T13:56:26.525796"
			}
		]
	}
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