# Industrial Data Platform Portfolio

가상 PLC → OPC UA Gateway → MES / 3D Digital Twin으로 이어지는 산업 데이터 플랫폼 포트폴리오입니다. GitHub Pages에서 별도 빌드 없이 실행되는 HTML/CSS/JavaScript 정적 사이트입니다.

## 포트폴리오 구성

- `index.html`: 통합 포트폴리오 메인 페이지
- `assets/css/styles.css`: 메인 페이지 디자인과 반응형 레이아웃
- `assets/js/main.js`: 메뉴, 등장 효과, 현재 섹션 표시, 이미지 라이트박스
- `assets/images/industrial-portfolio/`: 3개 프로젝트 주요 화면 14장과 OG 이미지

## 로컬 실행

```powershell
python -m http.server 4174
```

브라우저에서 `http://127.0.0.1:4174/`를 엽니다. 정적 파일이므로 GitHub Pages 저장소 루트에 그대로 배포할 수 있습니다.

## 프로젝트

1. **PLC Simulation** — Modbus TCP 기반 가상 데이터 소스, 라이브 태그와 메모리 매핑
2. **IIoT Gateway** — OPC UA Data Access, Alarms & Conditions, 보안과 클라이언트 연동
3. **TwinForge** — MES 대시보드, 생산 워크플로, Three.js 기반 3D Digital Twin

공개 사이트에는 전화번호와 주소 등 개인정보를 포함하지 않습니다.
