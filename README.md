# Industrial Data Platform Portfolio

TwinForge의 제한된 명령 → OPC UA Gateway → PLC Ack·feedback과 생산 근거 → OEEAnalyzer → TwinForge 운영 화면으로 이어지는 산업 데이터 플랫폼 포트폴리오입니다. GitHub Pages에서 별도 빌드 없이 실행되는 HTML/CSS/JavaScript 정적 사이트입니다.

## 포트폴리오 구성

- `index.html`: 통합 포트폴리오 메인 페이지
- `technical.html`: 네 프로젝트의 런타임 구조와 전체 데이터 흐름을 설명하는 통합 기술 문서
- `plc-simulation.html`: PLC Simulation 5개 화면의 사용자 조작과 처리 결과
- `iiot-gateway.html`: IIoT Gateway 5개 설정 화면의 입력·저장·런타임 동작
- `twinforge.html`: TwinForge 5개 화면의 MES·External OEE·설비·워크플로·3D 제어 흐름
- `oee-analyzer.html`: OEEAnalyzer 5개 화면의 연동 경로·기간 OEE·데이터 소스·처리 규칙
- `assets/docs/industrial-platform-technical-document.pdf`: 인쇄와 제출용 통합 기술 문서 PDF
- `assets/docs/industrial-products-feature-guide.pdf`: 제품별 화면을 묶은 기능 포트폴리오 PDF
- `assets/css/styles.css`: 메인 페이지 디자인과 반응형 레이아웃
- `assets/js/main.js`: 메뉴, 등장 효과, 현재 섹션 표시, 이미지 라이트박스
- `assets/images/industrial-portfolio/`: 네 프로젝트 주요 화면과 OG 이미지
- `scripts/capture-industrial-portfolio.mjs`: 실행 중인 로컬 4자 시스템에서 최신 화면을 다시 캡처하는 Playwright 스크립트

## 로컬 실행

```powershell
python -m http.server 4174
```

브라우저에서 `http://127.0.0.1:4174/`를 엽니다. 정적 파일이므로 GitHub Pages 저장소 루트에 그대로 배포할 수 있습니다.

## 프로젝트

1. **PLC Simulation** — Modbus TCP 기반 가상 데이터 소스, 라이브 태그와 메모리 매핑
2. **IIoT Gateway** — OPC UA Data Access, Alarms & Conditions, 보안과 클라이언트 연동
3. **TwinForge** — MES 대시보드, 생산 워크플로, Three.js 기반 3D Digital Twin
4. **OEEAnalyzer** — 생산 근거와 MES 맥락을 결합한 기간 A/P/Q/OEE, coverage와 revision

## 최신 화면 다시 캡처

PLC Simulation `5088`, Gateway ConfigUI `5279`, TwinForge `18081`, OEEAnalyzer UI `18083`이 실행 중이어야 합니다. Playwright가 설치된 Node.js 환경에서 다음 변수를 지정하고 실행합니다.

```powershell
$env:PORTFOLIO_OEE_PASSWORD = '<local demo password>'
node .\scripts\capture-industrial-portfolio.mjs
```

환경에 따라 `PORTFOLIO_PLAYWRIGHT_MODULE`, `PORTFOLIO_CHROMIUM_PATH`와 각 `PORTFOLIO_*_URL`을 지정할 수 있습니다. 스크립트는 실제 태그·Ack·OEE context가 화면에 표시된 뒤 이미지를 저장하므로 빈 로딩 화면을 결과로 남기지 않습니다.

공개 사이트에는 전화번호와 주소 등 개인정보를 포함하지 않습니다.
