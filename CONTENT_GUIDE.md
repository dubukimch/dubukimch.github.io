# Portfolio Content Guide - 2026-10-24

현재 원본은 `content/projects.json`이다. 날짜와 일곱 제품의 문제·구현·책임·설계 판단·근거·캡션·남은 개선을 여기서 수정한다. 사이트·PDF 생성기는 같은 원본을 사용한다.

사용 절차는 확정된 사용 매뉴얼을 `scripts/sync-manual-content.py`로 공개용 `content/manuals.json`에 동기화한다. 생성 JSON을 임의로 고쳐 원본과 다른 실행 결과를 만들지 않는다. `scripts/manual_pages.py`가 7개 프로젝트 상세의 첨부 영역, `manuals.html` 모음과 `manual-*.html` 안내를 렌더링한다. PDF는 해당 실제 페이지로 연결하고 통합 PPTX·개별 Markdown·관련 실습 파일도 제공한다.

## 역할 경계

| 제품 | 소유하는 역할 |
|---|---|
| PLC Simulation | 원본 상태·생산 카운터·명령 Ack |
| IIoT Gateway | 수집·품질·원본 시각·라우팅 |
| TwinForge | 3D·워크플로·MES 생산 맥락 |
| OEEAnalyzer | 기간 A/P/Q/OEE·coverage·revision |
| DataNexus Analytics | 읽기 전용 탐색·비교·보고서 |
| Industrial Assistant | 읽기 전용 조회·근거·출처 설명 |
| Industrial AssetHub | 공통 자산 식별·의미·소스 매핑 초안 |

AssetHub는 기존 실행 경로의 필수 의존성을 추가하지 않는다. 로컬 검토를 운영 승인으로, 개념 매칭 순위를 확률로, AAS 설계를 표준 적합성 확인으로 설명하지 않는다. OEE 계산을 다른 제품에서 중복하거나 읽기 제품에 설비 명령 책임을 추가하지 않는다.

## 화면과 디자인

기본 화면은 `assets/screenshots/2026-10-23/{plc,gateway,twin,oee,data,assistant,assethub}.jpg`와 HTTP 관측 작업 공간 `suite.jpg`다. OEE의 홈 카드·상세 대표는 `content/oee-screens.json`의 2026-09-16 통합 분석 캡처를 사용하고, 상세에 같은 날의 실제 동작 화면과 10월 로그인 화면을 함께 제공한다. `content/screenshots.json`은 대표 파일·실제 이미지 크기·캡처 엔드포인트·설명과 OEE 갤러리의 개별 날짜를 제공한다. 사이트 생성기는 캡처를 덮어쓰지 않는다. 새로운 캡처가 없으면 과거 화면을 새 날짜 폴더로 복사하지 않는다.

웹 디자인은 따뜻한 오프화이트 배경, 짙은 녹색 제목, 세이지 강조와 충분한 여백을 사용한다. 홈은 TwinForge의 실제 로컬 화면을 대표 이미지로 배치하고, 프로젝트별 Lucide 선형 아이콘과 일관된 링크를 제공한다. 2026-10-27부터 자체 호스팅 Pretendard Variable과 여유 있는 제목 자간·완화한 굵기를 사용한다. 글꼴 원본·OFL 라이선스·출처는 `assets/fonts/pretendard/`에 보관한다. 웹 디자인 개정일은 기존 캡처·PDF의 근거 날짜를 변경하지 않는다. 데스크톱 두 열 프로젝트 갤러리, 모바일 한 열, 역할 필터·검색·빈 상태·키보드 이미지 갤러리를 제공한다. 확대와 PDF 이미지는 원본 비율을 유지한다.

- 디자인: `assets/css/styles.css`
- 메뉴·필터·검색·갤러리·포커스 복귀: `assets/js/main.js`
- HTML 템플릿·연결 구조·미러: `scripts/build-current-site.py`
- 11쪽 가로형 PDF·글꼴 임베딩 검사: `scripts/build-current-pdf.py`
- 링크·앵커·캡처 manifest·미러·PDF 일치: `scripts/verify-current-site.py`
- 매뉴얼 디자인·검색·동작 목차: `assets/css/manuals.css`, `assets/js/manuals.js`
- 41개 절차·38개 캡처·검증 상태·PDF 페이지·MD 링크·아이콘 출처: `scripts/verify-manual-site.py`

본문 바로가기, 시맨틱 구조, 단일 h1, 검색 레이블, 필터 aria-pressed, 검색 결과 aria-live, Escape 닫기와 포커스 복귀, reduced-motion을 유지한다. JavaScript가 없어도 모든 프로젝트가 표시되어야 한다. 로컬 제품 링크는 loopback 미리보기에서만 표시한다.

## 근거 표현

근거에는 날짜와 범위를 함께 쓴다. 10월 9일 격리 통합 29개, Assistant C# 계약 51개와 10월 5일 MySQL 25개/OEE 35개/Twin 45개는 서로 다른 실행이다. 새 UI 화면을 과거 테스트의 재실행으로 표현하지 않는다.

PLC/Gateway/Twin의 실제 시뮬레이터 읽기 값과 품질 확인을 OEE 정상 생산 계산·Kafka 통합·실장비 검증으로 확대하지 않는다. OEE NoData, Kafka 미연결, Fake/Mock, AssetHub 로컬 초안과 미완료 승인 API를 그대로 설명한다.

재생성 후 로컬 링크 검사와 브라우저 동작·반응형 확인, PDF 전 페이지 렌더링을 수행한다. 과거 자산은 보존하되 현재 페이지가 현재 캡처와 PDF만 참조하도록 한다.
