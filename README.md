# Industrial Systems Portfolio

일곱 산업 소프트웨어의 화면, 역할과 설계 판단을 소개하는 정적 포트폴리오다. 제품 소개와 포트폴리오 PDF는 **2026-10-23**, 통합·솔루션별 사용 매뉴얼은 **2026-10-25 이미지 호환성 복구판**이다. 공개 주소는 `https://dubukimch.github.io/`다.

## 현재 원본

- `content/projects.json`: 일곱 제품의 문제·구현·역할·검증 범위와 남은 개선
- `content/screenshots.json`: 로컬 캡처 경로·엔드포인트·설명 manifest
- `assets/screenshots/2026-10-23/`: 직접 실행한 로컬 UI 7개
- `assets/css/styles.css`, `assets/js/main.js`: 반응형 디자인·검색·역할 필터·키보드 갤러리
- `scripts/build-current-site.py`: 홈·상세 7개·아키텍처·문서 안내·매뉴얼 모음·솔루션별 웹 매뉴얼 7개, 총 18페이지 생성
- `scripts/build-current-pdf.py`: 같은 원본으로 가로형 A4 11쪽 PDF 생성
- `assets/docs/industrial-platform-portfolio-2026-10-23.pdf`: 현재 제출본
- `assets/docs/manuals/`: 통합 PDF·PPTX와 `solutions/`의 솔루션별 PDF·PPTX 14개, 총 16개 문서. 예전 2026-10-24 통합 URL도 복구판 바이트로 연결한다.
- `content/manual-publication.json`: 16개 문서의 SHA·파일 크기·슬라이드 수·솔루션별 실제 동작 페이지와 새 캡처 근거
- `content/manuals.json`, `content/manual-assets.json`: 41개 동작과 PDF 페이지·원본 캡처·공개 자산 SHA 기록
- `manuals.html`, `manual-*.html`: 검색 가능한 매뉴얼 모음과 실제 캡처 38장을 담은 솔루션별 안내
- `scripts/sync-manual-content.py`, `scripts/manual_pages.py`: 확정된 매뉴얼의 공개 자산 동기화와 웹 렌더링
- `assets/css/manuals.css`, `assets/js/manuals.js`: 반응형 읽기 화면·동작 목차·매뉴얼 검색

정적 페이지는 설비나 AI 서비스에 접속하지 않는다. 제품별 로컬 작업 공간 링크는 loopback에서 미리 볼 때만 표시한다. 필터·검색은 브라우저에서만 처리하며 사용자 입력을 외부로 보내지 않는다. JavaScript가 없으면 모든 프로젝트와 내비게이션을 볼 수 있다.

## 로컬 실행과 확인

저장소 루트에서 실행한다. 정적 서버는 Python 표준 라이브러리만 필요하며, 문서 검증에는 기존 번들 런타임의 pypdf·Pillow를 사용한다.

```powershell
python scripts/serve-local.py --port 5190
```

미리보기는 `http://127.0.0.1:5190/`다. 서버는 loopback에 바인딩하고 숨김 경로를 GET/HEAD 모두 404로 처리한다. 미리보기 보안 헤더가 GitHub Pages에 자동 적용되는 것은 아니다.

```powershell
python scripts/verify-current-site.py --port 5190
python scripts/verify-manual-site.py
node --check assets/js/main.js
node --check assets/js/manuals.js
python scripts/serve-local.py --port 5190 --stop
```

검사는 로컬 링크·리소스·앵커, 7개 캡처 manifest, 제출 PDF와 사이트 PDF의 SHA256, 상위 `포트폴리오` 미러의 HTML/CSS/JS/이미지/PDF 일치를 확인한다. 외부 GitHub와 로컬 제품 링크는 요청하지 않는다. 검색·필터·갤러리·모바일 메뉴와 반응형 레이아웃은 브라우저에서 별도로 확인한다.

## 재생성

```powershell
python scripts/build-current-site.py
python scripts/build-current-pdf.py
python scripts/build-current-site.py
```

사이트 생성기는 기존 캡처를 덮어쓰지 않는다. `assets/screenshots/{date}/{id}.jpg`와 `suite.jpg`를 준비한 뒤 실행한다. PDF 생성기는 현재 프로젝트 7개 캡처가 모두 준비되지 않으면 중단하며 과거 이미지를 새 캡처로 복사하지 않는다. 마지막 사이트 생성은 현재 PDF·캡처까지 상위 `포트폴리오` 폴더에 동기화한다. 과거 자산과 PDF는 이력으로 보존한다.

기존 상세 절차 원문과 38개 원본 캡처는 상위 `솔루션_사용매뉴얼/2026-10-24`에 동결 보존한다. 새 문서와 재촬영의 정식 원본은 `솔루션_사용매뉴얼/2026-10-25/publication-manifest.json`이다. 사이트 생성기는 이 manifest의 16개 문서 해시를 확인해 ASCII 다운로드 경로로 복사하며, `captureOverrides`의 실제 새 캡처와 실행 근거를 웹 안내·공개 Markdown에 반영한다. 원문 절차나 과거 증거 파일은 변경하지 않는다. 원본 폴더가 없는 공개 체크아웃에서는 함께 제공된 `content/manuals.json`과 공개 자산으로 재생성한다. 임시 검수본은 `python scripts/build-current-site.py --publication-manifest <manifest 경로>`로 지정할 수 있다.

각 제품 상세 페이지의 ‘직접 사용하는 순서’에서 **해당 솔루션의 PDF·PPTX**를 먼저 제공하고, 웹 매뉴얼·Markdown·통합본 해당 장도 연결한다. 웹의 각 동작은 솔루션 전용 PDF의 정확한 로컬 페이지로 이동하며 통합본 페이지도 함께 안내한다. 통합본 장 시작은 PLC 6 / Gateway 12 / Twin 17 / OEE 24 / Data 31 / Assistant 37 / AssetHub 45쪽이다. 사이트와 상위 `포트폴리오` 미러의 모든 문서는 동일하다.

복구판은 잘못된 SVG 대체 이미지에 의존하지 않고 실제 PNG 아이콘을 PPTX에 내장한다. 검증기는 8개 PPTX의 모든 래스터 이미지 디코딩, 8개 PDF의 페이지 수, 문서 해시와 동작별 페이지를 검사한다. DataNexus의 파일 수집·그리드·보고서는 대비 보정 후 2026-10-25 다시 촬영했다. 보고서 생성·Preview·Copy MD·Download .md와 복사/저장 내용 일치를 확인했으며 실제 저장 파일도 실습 자료에 포함한다. OEE 인증 이후 3개 절차는 미실행 상태로 유지한다.

웹 생성에는 Python 표준 라이브러리, PDF에는 기존 ReportLab·Pillow·pypdf와 `C:/Windows/Fonts/malgun.ttf`, `malgunbd.ttf`를 사용한다. OS/2 임베딩 플래그가 허용값 0 또는 8일 때만 글꼴을 부분 임베딩한다. 글꼴 파일 자체를 사이트에 복사하지 않는다. PDF는 전 페이지를 렌더링해 시각 확인한다. 새 패키지·외부 폰트·외부 AI API가 필요하지 않다.

## 검증 근거의 날짜와 범위

- **2026-10-23**: AssetHub 기반·Host 75개, Assistant C# 52개와 결정적 채팅 smoke PASS. 현재 Assistant는 PLC/Twin HTTP adapter를 구성하고 나머지 네 출처를 Mock으로 유지한다. 답변·지식·음성은 Fake다. Suite는 일곱 고정 로컬 경로의 HTTP 응답을 관측하며 데이터 전송 성공과 구분한다.
- **2026-10-09**: 격리 Docker fixture 29개 PASS, Assistant C# 계약 51개 PASS. PLC → Gateway Modbus → Twin OPC UA의 값·품질·원본/수신 시각과 다섯 제품의 제한된 로그 → Fake 답변 출처를 확인했다.
- **2026-10-05**: 실제 MySQL 인증 25개, OEE .NET 35개, Twin .NET 45개 PASS. 각기 다른 fixture의 과거 검증 기록이다.
- **현재 화면**: 일곱 로컬 UI의 캡처와 역할 설명. 화면에서 확인한 서비스 상태와 과거 통합 검증을 혼합하지 않는다.

OEE sample/context가 없는 NoData와 DataNexus Kafka 미연결은 전체 생산 흐름 성공을 의미하지 않는다. AssetHub는 로컬 자산·의미·관계 초안 구현 단계이며 운영 승인 API·원장·표준 AAS runtime·외부 Assistant 연동은 미완료다. 실장비·실제 외부 LLM 답변 품질·표준 적합성·운영 배포 승인은 별도 범위다.

GitHub 원격 반영이나 게시 완료는 로컬 파일 생성과 별개다. 기존 `capture-industrial-portfolio.mjs`, `build-portfolio-pdfs.py`와 2026-10-05 자산은 보존 자료이며 현재판 재생성 도구가 아니다.
