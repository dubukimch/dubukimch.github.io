# PORTFOLIO CONTENT GUIDE

## 메인 서사

`index.html`은 **현장 신호를 운영 가능한 데이터로 연결한다**는 메시지를 중심으로 다음 순서로 구성했습니다.

1. Hero — PLC → OPC UA → OEE → MES·Digital Twin → Analytics 핵심 메시지
2. Platform — 다섯 제품의 역할과 통합 데이터 흐름
3. Projects — 23개 실제 화면과 프로젝트별 구현 범위
4. Evidence — 제어 Ack, 품질 기반 OEE, DataNexus 독립 관측의 통합 검증
5. Engineering Principles — 정보 모델, 관측성, 안전한 제어, 재현 가능한 검증 원칙

## 이미지와 기능

| 파일 접두사 | 프로젝트 | 설명 |
|---|---|---|
| `plc-01` ~ `plc-05` | PLC Simulation | 대시보드, 노드, 드라이버, 라이브 태그, 데이터 매핑 |
| `gateway-01` ~ `gateway-05` | IIoT Gateway | 채널, 디바이스, OPC UA 태그, 알람, 보안 |
| `twin-01` ~ `twin-04`, `oee-03` | TwinForge | MES, External OEE, 설비, 워크플로, 3D Digital Twin |
| `oee-01` ~ `oee-05` | OEEAnalyzer | 연동 경로, 기간 OEE, 생산 맥락, 데이터 소스, 처리 규칙 |
| `datanexus-01` ~ `datanexus-03` | DataNexus Analytics | 5자 연결 상태, TwinForge 맥락, OEE 권위 결과 |
| `og-industrial-platform.png` | 대표 이미지 | SNS 및 링크 공유용 Open Graph 이미지 |

이미지는 `assets/images/industrial-portfolio/`에 있습니다. 갤러리 이미지를 선택하면 원본 비율의 라이트박스가 열립니다.

## 수정 위치

- 콘텐츠와 이미지 순서: `index.html`
- 색상, 카드, 반응형 레이아웃: `assets/css/styles.css`
- 모바일 메뉴, 애니메이션, 라이트박스: `assets/js/main.js`

## 디자인 기준

- Industrial navy 기반의 어두운 화면
- Cyan은 데이터 흐름, Lime은 정상 상태와 핵심 행동을 표시
- 1240px 데스크톱 레이아웃과 680px 이하 모바일 레이아웃 지원
- 키보드 포커스, reduced-motion, 시맨틱 섹션과 대체 텍스트 적용
