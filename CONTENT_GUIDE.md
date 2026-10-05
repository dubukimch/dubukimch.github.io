# Portfolio Content Guide — 2026-10-05

현재 원본은 `content/projects.json`이다. 여섯 프로젝트의 역할, 문제, 해결 방식, 설계 판단, 확인한 동작, 화면 캡션과 남은 개선 범위를 수정하고 `scripts/build-current-site.py`로 HTML을 재생성한다. PDF는 같은 원본을 사용하되 검증 표와 제약 설명도 `scripts/build-current-pdf.py`에서 함께 확인한다.

## 역할 경계

| 프로젝트 | 소유하는 역할 |
|---|---|
| PLC Simulation | 원본 상태·생산 카운터·명령 Ack |
| IIoT Gateway | 수집·품질·원본 시각·namespace·라우팅 |
| OEEAnalyzer | 기간 A/P/Q/OEE·coverage·revision 계산 |
| TwinForge | 3D·워크플로·MES 생산 맥락 |
| DataNexus Analytics | 읽기 전용 탐색·비교·보고서 |
| Industrial AI Assistant | 읽기 전용 근거 조회·출처 설명 |

OEE를 다른 프로젝트에서 재계산하거나 Assistant/DataNexus에 설비 명령 권한을 추가하지 않는다. Twin External의 결측을 무작위 값으로 대체하지 않는다.

## 현재 화면과 디자인

`assets/images/current-2026-10-05/{plc,gateway,oee,twin,data,assistant}.jpg`는 직접 실행한 로컬 UI 캡처다. Data 화면은 합성 CSV 네 행을 사용한다. OEE 로그인, Twin 미연결 Preview Mode, Assistant 테스트 안내를 실데이터 성공으로 설명하지 않는다. 확대는 원본 비율을 보존하고 캡션을 표시한다.

밝은 종이색 바탕, 짙은 녹색 강조, 여백과 타이포그래피 중심 레이아웃을 사용한다. 시스템 글꼴만 참조한다. 데스크톱 두 열, 760px 이하 단일 열, 모바일 메뉴와 역할 카드가 기본이다. 긴 역할 문자열은 줄바꿈한다. 표는 컨테이너 안에서만 가로 스크롤한다.

- 디자인: `assets/css/styles.css`
- 모바일 메뉴, Escape 키 닫기, 이미지 확대와 포커스 복귀: `assets/js/main.js`
- 템플릿과 페이지 구조: `scripts/build-current-site.py`
- PDF 배치와 임베딩 검사: `scripts/build-current-pdf.py`

본문 바로가기, 시맨틱 HTML, 단일 h1, 이미지 설명, 키보드 포커스, reduced-motion을 유지한다. 새 애니메이션이나 외부 라이브러리는 필요성을 먼저 검토한다.

## 근거를 표현하는 기준

숫자에는 날짜와 범위를 함께 기록한다. Docker 30 PASS와 MySQL 25 PASS는 다른 fixture다. OEE 35/Twin 45 테스트와 브라우저 검사도 구분한다. 전체 통합, 실제 AI, 실장비 또는 라이선스 전체 승인으로 확대 해석하지 않는다.

로컬 링크 검사와 UI 확인, PDF 전 페이지 렌더링을 함께 수행한다. 외부 GitHub/공식 문서 9개는 링크 검사에서 요청하지 않는다. 기존 PDF/자산은 보존 자료로 유지하며 현재 페이지에서 사용하지 않는다.
