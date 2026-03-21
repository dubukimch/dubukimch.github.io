# 스마트팜 통합 솔루션 포트폴리오 웹사이트

이 폴더는 **GitHub Pages에 바로 올릴 수 있는 정적 웹사이트**입니다.  
별도 프레임워크나 빌드 도구 없이 `HTML + CSS + JavaScript`만으로 구성되어 있습니다.

## 포함된 파일

- `index.html` : 포트폴리오 웹페이지
- `presentation.html` : 발표용 웹 프레젠테이션
- `assets/css/` : 스타일 파일
- `assets/js/` : 인터랙션 스크립트
- `assets/images/` : 원본 PDF에서 추출한 슬라이드 이미지
- `assets/docs/smartfarm-portfolio-source.pdf` : 원본 PDF

## 가장 쉬운 배포 방법: GitHub Pages

### 1) 새 저장소 만들기
GitHub에서 새 저장소를 하나 만듭니다.

선택지는 두 가지입니다.

- **사용자 사이트**: `사용자이름.github.io`
- **프로젝트 사이트**: 원하는 저장소 이름 예: `smartfarm-portfolio`

처음이면 `사용자이름.github.io`가 가장 단순합니다.

### 2) 파일 업로드
이 폴더 안의 파일을 전부 저장소 루트에 올립니다.

웹에서 업로드해도 되고, Git으로 올려도 됩니다.

```bash
git init
git add .
git commit -m "Add smart farm portfolio site"
git branch -M main
git remote add origin https://github.com/사용자이름/저장소이름.git
git push -u origin main
```

### 3) GitHub Pages 켜기
저장소에서 다음으로 이동합니다.

- `Settings`
- `Pages`
- `Build and deployment`
- `Source: Deploy from a branch`
- `Branch: main`
- `Folder: /(root)`

저장하면 배포가 시작됩니다.

### 4) 배포 주소 확인
보통 다음 형태입니다.

- 사용자 사이트: `https://사용자이름.github.io`
- 프로젝트 사이트: `https://사용자이름.github.io/저장소이름`

## gist.github.com 이 맞나?

아닙니다.  
**포트폴리오 웹사이트를 공개하려면 일반적으로 `gist.github.com`이 아니라 GitHub 저장소 + GitHub Pages를 사용합니다.**

- **Gist**: 코드 조각, 짧은 예제, 메모 공유용
- **GitHub Pages**: 정적 웹사이트 배포용

즉, HTML/CSS/JS로 만든 포트폴리오를 공개하려면 **repository에 올리고 Pages로 배포**하는 방식이 맞습니다.

## 수정 포인트

### 제목/소개 수정
- `index.html`
- `presentation.html`

위 두 파일 안의 다음 내용을 바꾸면 됩니다.

- 프로젝트 제목
- 지원자 이름
- 소개 문장
- 섹션별 설명

### 이미지 교체
`assets/images/` 안의 파일을 교체하면 됩니다.

현재 파일명 예시:
- `cover.webp`
- `project-background.webp`
- `architecture-software.webp`
- `process-webgl.webp`

같은 이름으로 덮어쓰면 HTML 수정 없이 바뀝니다.

### PDF 교체
원본 PDF를 새 버전으로 바꾸려면:

- `assets/docs/smartfarm-portfolio-source.pdf`

파일만 교체하면 됩니다.

## 추천 작업 순서

1. 먼저 `index.html`을 열어 전체 구조를 확인
2. 제목, 이름, 소개 문구 수정
3. 필요 없는 섹션 삭제 또는 순서 변경
4. 실제 스크린샷으로 이미지 교체
5. `presentation.html`에서 발표용 흐름 정리
6. GitHub 저장소에 업로드
7. GitHub Pages 배포 확인

## 로컬에서 미리 보기

브라우저에서 `index.html`을 바로 열어도 됩니다.  
조금 더 정확하게 보려면 VS Code의 Live Server 같은 로컬 서버를 써도 좋습니다.

## 다음 확장 아이디어

- GitHub 저장소 링크 추가
- 기술 스택 배지 추가
- 자기소개/연락처 섹션 추가
- 프로젝트 데모 영상 링크 추가
- 성능 최적화, 반응형 레이아웃 세부 보정
