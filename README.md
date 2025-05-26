# 인터파크 자동 예매 프로그램

## 개발 인원

## 디렉토리 구조

```
interpark_auto_ticketing/
├── main.py
│
├── presentation/                 # GUI
│   └── gui_app.py
│
├── application/                  # Use Case
│   ├── reserve_usecase.py
│   └── schedule_runner.py
│
├── domain/                       # 비즈니스 로직
│   ├── performance.py
│   ├── seat.py
│   └── reservation_request.py
│
├── infrastructure/               # 외부 로직
│   ├── crawler/
│   │   ├── interpark_crawler.py
│   │   └── parser.py
│   ├── automation/
│   │   └── selenium_bot.py
│   └── config/
│       ├── settings.py
│       └── secrets.json
│
├── utils/                        # 유틸리티
│   └── logger.py
│
└── requirements.txt
```

## 라이브러리 선정

### 1. 브라우저 자동화 처리

- Selenium : 안정성
- Playwright : 가장 빠름
- Puppeteer

속도가 중요하므로 **`Playwright`** 선정

### 2. GUI 라이브러리

- Tkinter : 단순함, UI 구림, 반응형과 스타일 제어 어려움
- PyQt : UI 이쁨, 설치 무거움, 상용 라이선스 유의

가격을 아끼기 위해 **`Tkinter`** 선정

## 개발 방법

- python3.13
- tkinter

```bash
# 0. tkinter 설치(맥북) / 윈도우는 사이트에서..
brew install python-tk
```

```bash
# 1. 가상환경 설정
python3.13 -m venv venv

# MacOS
source venv/bin/activate

# Windows
.\venv\Scripts\activate
```

```bash
# 2. 환경 설정
pip install -r requirements.txt
```

```bash
# 3. 실행
python main.py
```

## 빌드 방법

```bash
pyinstaller --onefile --windowed main.py
```
