# Industrial Systems Portfolio

여섯 산업 소프트웨어 프로젝트의 역할, 설계 판단, 현재 화면과 실제 검증 범위를 소개하는 정적 포트폴리오다. 현재판은 **2026-10-05** 기준이다. 로컬 검증을 실제 설비 또는 여섯 출처의 전체 데이터 통합 성공으로 표현하지 않는다.

## 구성

- `index.html`: 여섯 역할, 프로젝트 카드와 검증 근거
- PLC / Gateway / OEE / Twin / DataNexus / Assistant: 프로젝트별 상세 페이지
- `technical.html`: 역할 경계, 검증과 미완료 범위, 비용·라이선스 기준
- `presentation.html`: 현재 제출용 PDF 안내
- `assets/docs/industrial-platform-portfolio-2026-10-05.pdf`: 10쪽 PDF. 상위 `포트폴리오` 폴더의 현재판과 동일
- `content/projects.json`: 웹과 PDF에서 공유하는 콘텐츠 원본
- `assets/images/current-2026-10-05/`: 직접 실행하여 캡처한 여섯 프로젝트 화면
- `작업진행현황/`: 검증 결과, 수정 사항과 다음 작업 프롬프트

기존 화면, PDF와 이전 생성 스크립트는 이력 보존을 위해 유지한다. 현재 페이지는 새 PDF와 새 화면만 참조한다. `scripts/build-portfolio-pdfs.py`와 기존 캡처 스크립트는 현재판 재생성 도구가 아니다.

## 로컬 실행과 검사

저장소 루트에서 실행한다. Python 표준 라이브러리만 사용하며 외부 API와 연결하지 않는다.

```powershell
python scripts/serve-local.py
```

`http://127.0.0.1:4174/`에서 확인한다. 루프백에만 바인딩하며 `.git` 등 숨김 경로는 GET/HEAD 모두 404다. 미리보기 보안 헤더는 GitHub Pages 배포에 자동 적용되지 않는다.

다른 터미널에서 확인하거나 종료한다.

```powershell
python scripts/verify-current-site.py
node --check assets/js/main.js
python scripts/serve-local.py --stop
```

검사는 9개 HTML, 18개 로컬 리소스, 34개 앵커와 PDF 사본의 SHA256 일치를 확인한다. 외부 링크 9개는 요청하지 않는다. 모바일 메뉴, 확대 화면, 320/390px 모바일과 기본 데스크톱 레이아웃은 브라우저에서 별도로 확인했다.

## 콘텐츠 재생성

```powershell
python scripts/build-current-site.py
python scripts/build-current-pdf.py
```

웹 생성에는 Python 표준 라이브러리만 필요하다. PDF 생성은 기존 ReportLab, Pillow, pypdf와 Windows `C:/Windows/Fonts/malgun.ttf`, `malgunbd.ttf`를 사용한다. 이번에는 Codex에 포함된 기존 Python 런타임을 사용했으며 새 패키지를 설치하지 않았다. 글꼴 임베딩 플래그가 허용된 값(0 또는 8)이 아니면 중단한다. 글꼴 파일 자체를 사이트에 복사하지 않는다. 재생성 후 PDF 모든 페이지를 렌더링하여 한글·표·이미지 비율·페이지 경계를 육안 확인해야 한다.

정적 HTML/CSS/JS이므로 GitHub Pages는 별도 npm 빌드 없이 제공할 수 있다. 저장소 커밋과 GitHub 원격 반영은 별도 상태이며, 원격 인증이 확보되지 않은 상태를 배포 완료로 표현하지 않는다.

## 검증 범위와 제약

2026-10-05 재검증: Docker HTTP/WebSocket 30개, 실제 일회성 MySQL 인증 25개, OEE .NET 35개, TwinForge .NET 45개 PASS. Assistant는 Fake/Mock만 시험했다. 여섯 출처 전체 통합, 정상 Timescale/Redis 경로, 실장비 제어 및 실제 LLM 응답은 검증하지 않았다.

새 유료 서비스, CDN, 외부 폰트, 스톡 이미지, 라이브러리 다운로드 및 외부 LLM API를 사용하지 않았다. 기존 제품 의존성의 원문 라이선스 검토 필요 197행은 여전히 후속 과제이며, 전체 배포 권리를 승인했다는 의미가 아니다.
