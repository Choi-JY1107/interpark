# 인터파크 자동 티켓팅 시스템

인터파크 티켓 예매를 자동화하는 프로그램입니다. Clean Architecture 패턴을 적용하여 설계되었습니다.

## 주요 기능

- **자동 대기열 진입**: 지정된 시간에 자동으로 대기열에 진입
- **캡차 자동 해결**: OCR을 이용한 보안문자 자동 입력
- **스마트 좌석 선택**: 
  - 일반 모드: 무대에서 가까운 좌석부터 선택
  - 작은 포도알 모드: 최대 4개 좌석을 포도알 형태로 선택
  - 큰 포도알 모드: 최대 2개 좌석을 포도알 형태로 선택
- **좌석 충돌 자동 처리**: "이미 선택된 좌석" 팝업 자동 처리 및 재시도

## 프로젝트 구조

```
interpark-auto-ticketing/
├── domain/                 # 비즈니스 로직 (엔티티, 리포지토리, 유스케이스)
│   ├── entities/          # 도메인 엔티티
│   ├── repositories/      # 리포지토리 인터페이스
│   └── use_cases/         # 비즈니스 유스케이스
├── infrastructure/         # 외부 시스템 연동
│   ├── web_driver/        # Selenium WebDriver 관리
│   ├── ocr/               # OCR 캡차 해결
│   └── interpark/         # 인터파크 특화 구현
├── application/            # 애플리케이션 서비스
│   ├── services/          # 비즈니스 서비스
│   └── dtos/              # 데이터 전송 객체
├── presentation/           # UI 레이어
│   ├── views/             # GUI 뷰
│   └── controllers/       # 컨트롤러
└── config/                # 설정 관리
```

## 아키텍처 특징

- **Clean Architecture**: 비즈니스 로직과 인프라 분리
- **의존성 역전**: 도메인이 인프라에 의존하지 않음
- **테스트 가능**: 각 레이어 독립적으로 테스트 가능
- **확장 가능**: 다른 티켓팅 사이트 지원 추가 용이

## 설치 방법

### 1. Python 환경 설정

```bash
# 가상환경 생성
python3 -m venv venv

# MacOS/Linux
source venv/bin/activate

# Windows
.\venv\Scripts\activate
```

### 2. 패키지 설치

```bash
pip install -r requirements.txt
```

### 3. 추가 소프트웨어 설치

**Tesseract OCR 설치 (캡차 인식용)**

```bash
# macOS
brew install tesseract

# Windows
# https://github.com/UB-Mannheim/tesseract/wiki 에서 설치

# Ubuntu/Debian
sudo apt-get install tesseract-ocr
```

**Chrome 브라우저**
- Chrome 브라우저가 설치되어 있어야 합니다
- selenium이 자동으로 ChromeDriver를 관리합니다

## 사용 방법

```bash
python main.py
```

1. **공연 정보 입력**
   - 공연명과 URL 입력
   - 날짜와 시간 선택
   - 대기 시작 시간 설정

2. **좌석 설정**
   - 좌석 선택 방식 선택 (일반/작은 포도알/큰 포도알)
   - 선택 방향 설정 (오른쪽부터/왼쪽부터)
   - 좌석 수 지정

3. **시작 버튼 클릭**
   - 지정된 시간에 자동으로 티켓팅 시작
   - 좌석 선택까지 자동 진행

## 빌드 방법

실행 파일로 빌드:

```bash
pyinstaller --onefile --windowed main.py
```

빌드된 파일은 `dist/` 폴더에 생성됩니다.

## 주의사항

- 본 프로그램은 교육 목적으로 제작되었습니다
- 서비스 이용약관을 준수하여 사용하세요
- 과도한 사용은 계정 제재를 받을 수 있습니다
