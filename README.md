# 일정관리 캘린더 (calendar-app)

가벼운 웹 기반 일정관리 캘린더입니다. 서버에 일정을 저장하기 때문에 폰·PC 등 **여러 기기에서 일정이 공유**됩니다. (v0.0.1)

## 특징

- 월간 / 주간 보기
- 일정 색상 6종, 시간 표시
- 서버 공유 저장소 — 기기 공유, 10초 자동 동기화
- JSON 내보내기 / 가져오기
- 다크 테마, 반응형 (모바일 지원)

## 실행 방법

### 방법 1: Python으로 직접 실행 (의존성 없음)

```bash
cd calendar-app
mkdir -p data
DATA_DIR=$PWD/data PORT=3300 python3 server.py
```

http://localhost:3300 접속

### 방법 2: Docker

```bash
docker compose up -d --build
```

http://localhost:3300 접속

### 방법 3: Synology NAS (Container Manager)

1. 폴더 전체를 NAS에 복사 (예: `/volume1/docker/calendar/`)
2. Container Manager → 프로젝트 → 만들기 → 해당 경로 지정
3. `http://NAS-IP:3300` 접속

## API

| Method | Path | 설명 |
|--------|------|------|
| GET | `/` | 캘린더 페이지 |
| GET | `/api/events` | 일정 전체 조회 (JSON 배열) |
| POST | `/api/events` | 일정 전체 저장/대체 (JSON 배열) |

## 일정 형식

```json
{
  "id": "abc123",
  "title": "일정 제목",
  "date": "2026-09-27",
  "time": "09:00",
  "color": "#4f8cff"
}
```

## 라이선스

MIT
