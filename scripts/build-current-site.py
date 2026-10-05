"""Build a dependency-free portfolio from reviewed content and owned screenshots."""
import json
from html import escape as e
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[1]
DATA = json.loads((ROOT / 'content/projects.json').read_text(encoding='utf-8'))
PROJECTS = DATA['projects']
PDF = 'assets/docs/industrial-platform-portfolio-2026-10-05.pdf'
SHOTS = 'assets/images/current-2026-10-05'


def page(title, content, description):
    return f'''<!doctype html>
<html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="theme-color" content="#f5f4ef"><title>{e(title) if title == 'Industrial Systems Portfolio' else e(title) + ' · Industrial Systems Portfolio'}</title>
<meta name="description" content="{e(description)}"><meta property="og:title" content="{e(title)}">
<meta property="og:description" content="{e(description)}"><meta property="og:type" content="website">
<link rel="stylesheet" href="assets/css/styles.css?v=20261005"><script defer src="assets/js/main.js?v=20261005"></script></head>
<body><a class="skip-link" href="#main">본문 바로가기</a>
<header class="site-header"><a class="brand" href="index.html"><span class="brand-mark">IP</span><span>Industrial<br><b>Systems Portfolio</b></span></a>
<button class="nav-toggle" type="button" aria-expanded="false" aria-controls="nav" hidden>메뉴</button>
<nav id="nav" aria-label="주요 메뉴"><a href="index.html#projects">Projects <span>06</span></a><a href="technical.html">Architecture</a><a href="index.html#evidence">Verification</a><a class="nav-cta" href="{PDF}" download>Portfolio PDF ↗</a></nav></header>
<main id="main">{content}</main>
<footer class="site-footer"><div><b>Industrial Systems Portfolio</b><p>개인 프로젝트 / 비상업 포트폴리오 · 2026.10.05</p></div><div><a href="index.html">홈</a><a href="technical.html">설계와 검증</a><a href="{PDF}" download>PDF 다운로드</a></div><p class="footer-note">확인된 동작과 남은 범위를 함께 기록합니다. 공개 페이지는 정적 문서이며 실제 설비·AI 서비스와 연결하지 않습니다.</p></footer>
<dialog id="lightbox" aria-label="프로젝트 화면 확대"><button class="lightbox-close" aria-label="확대 화면 닫기">닫기 ×</button><figure><img alt=""><figcaption></figcaption></figure></dialog>
</body></html>'''


def flow():
    nodes = ''.join(f'<a class="flow-node" href="{p["page"]}"><span>0{i+1} / {e(p["category"].split(" / ")[0])}</span><b>{e(p["label"])}</b><small>{e(p["role"])}</small></a>' for i,p in enumerate(PROJECTS))
    return '<div class="flow-grid" aria-label="여섯 프로젝트의 역할">'+nodes+'</div>'


def shot(p, detailed=False):
    return f'''<figure class="product-shot{' detailed' if detailed else ''}"><button class="shot" data-lightbox="{SHOTS}/{p['id']}.jpg" data-caption="{e(p['caption'])}" aria-label="{e(p['label'])} 화면 확대"><img src="{SHOTS}/{p['id']}.jpg" width="1123" height="1244" alt="{e(p['label'])} 현재 로컬 화면" loading="lazy"></button><figcaption>{e(p['caption'])}</figcaption></figure>'''


def evidence():
    rows=[('Docker HTTP / WebSocket','30 PASS','6개 저장소 · 웹 응답 · BlazorPack · CORS · Fake/Mock API'),
          ('MySQL authentication','25 PASS','Bootstrap · 실제 로그인 · Admin/Viewer · 계정 보존 · 정리'),
          ('OEE .NET tests','35 PASS','보안 초기화 · 계산 관련 회귀 · 손상된 암호 해시 거부'),
          ('TwinForge .NET tests','45 PASS','두 로컬 OPC UA 서버 · namespace · quality · 재연결 fixture')]
    table=''.join(f'<tr><th scope="row">{a}</th><td><span class="pass">{b}</span></td><td>{c}</td></tr>' for a,b,c in rows)
    return f'''<div class="table-scroll"><table class="evidence-table"><caption>2026-10-05 재실행한 검증 결과</caption><thead><tr><th scope="col">검증 경로</th><th scope="col">결과</th><th scope="col">확인 범위</th></tr></thead><tbody>{table}</tbody></table></div><p class="scope-note">{e(DATA['scope'])}</p>'''


def build():
    dest=ROOT/SHOTS
    dest.mkdir(parents=True,exist_ok=True)
    source=ROOT.parent/'포트폴리오/screenshots/2026-10-05'
    for p in PROJECTS:
        shutil.copyfile(source/(p['id']+'.jpg'),dest/(p['id']+'.jpg'))
    cards=''.join(f'''<article class="case-card" id="{p['id']}"><div class="case-head"><span class="eyebrow">0{i+1} / {e(p['category'])}</span><a class="case-title" href="{p['page']}">{e(p['label'])}<span aria-hidden="true">↗</span></a><p>{e(p['headline'])}</p></div>{shot(p)}<div class="case-body"><p class="role-label">{e(p['role'])}</p><p>{e(p['solution'])}</p><div class="tags">{''.join('<span>'+e(x)+'</span>' for x in p['stack'].split(' · '))}</div><a class="text-link" href="{p['page']}">문제 · 설계 · 검증 살펴보기 →</a></div></article>''' for i,p in enumerate(PROJECTS))
    home=f'''<section class="hero"><div class="hero-copy"><p class="eyebrow">INDUSTRIAL SOFTWARE / SIX PROJECTS</p><h1>현장 데이터에서<br><em>근거 있는 판단까지.</em></h1><p class="hero-lead">신호를 만들고, 연결하고, 계산하고, 이해하는 여섯 개의 작업 공간. 각 제품이 맡는 역할과 실제로 확인한 동작을 한곳에 정리했습니다.</p><div class="actions"><a class="button primary" href="#projects">프로젝트 탐색 ↗</a><a class="button" href="{PDF}" download>10쪽 포트폴리오 PDF ↓</a></div><p class="edition">VERIFIED 2026.10.05 <span>로컬 검증 / 외부 AI 호출 없음</span></p></div><aside class="hero-map"><div class="map-heading"><span>01 — SYSTEM OWNERSHIP</span><span class="status-dot">6 WORKSPACES</span></div>{flow()}<p class="map-note">PLC → Gateway → OEE · Twin은 생산 맥락 제공<br>DataNexus와 Assistant는 권위 결과를 읽고 설명합니다.</p></aside></section>
<section class="stat-strip" aria-label="검증 요약"><div><strong>06</strong><span>독립 프로젝트</span></div><div><strong>30</strong><span>HTTP / WebSocket PASS</span></div><div><strong>25</strong><span>실제 MySQL 인증 PASS</span></div><div><strong>80</strong><span>OEE / Twin .NET PASS</span></div></section>
<section class="section" id="projects"><div class="section-head"><div><p class="eyebrow">02 — SELECTED PROJECTS</p><h2>역할은 분명하게.<br>화면은 연결되게.</h2></div><p>현재 로컬 화면과 함께 해결 과제, 구현 선택, 검증 결과를 설명합니다. 각 화면의 데모·미수신 상태도 그대로 표시합니다.</p></div><div class="cases-grid">{cards}</div></section>
<section class="section evidence" id="evidence"><div class="section-head"><div><p class="eyebrow">03 — VERIFICATION</p><h2>수치보다 먼저,<br>검증의 범위.</h2></div><p>성공한 검사와 검증하지 않은 경로를 구분합니다. 테스트가 생성한 컨테이너와 DB 볼륨은 정리했습니다.</p></div>{evidence()}<div class="verification-grid"><article><h3>브라우저에서 확인</h3><p>PLC 가상 입력→출력, DataNexus CSV 4행→SVG→그리드 추가, Gateway 채널 폼, OEE 인증 화면, Twin 3D 미리보기·미수신 표시, Assistant 조회 전용·빈 키 보호.</p></article><article><h3>남아 있는 검증</h3><p>6개 출처의 실제 데이터 통합, 정상 시계열 DB 경로, 제어 UUID/TTL 감사, 대용량·동시 import, 전체 자산·의존성 배포 조건 검토.</p></article></div></section>
<section class="section closing"><p class="eyebrow">04 — ENGINEERING APPROACH</p><h2>계산의 소유권을 지키고,<br>데이터의 출처를 남깁니다.</h2><p>구현 범위와 근거를 담은 설계 문서 및 제출용 PDF로 프로젝트를 더 자세히 확인할 수 있습니다.</p><div class="actions"><a class="button primary" href="technical.html">아키텍처와 검증 기준 ↗</a><a class="button" href="{PDF}" download>PDF 다운로드 ↓</a></div></section>'''
    (ROOT/'index.html').write_text(page('Industrial Systems Portfolio',home,'여섯 산업 소프트웨어 프로젝트의 역할, 현재 화면, 로컬 검증 근거를 담은 포트폴리오'),encoding='utf-8')
    for i,p in enumerate(PROJECTS):
        bullets=''.join('<li>'+e(x)+'</li>' for x in p['decisions'])
        features=''.join('<li>'+e(x)+'</li>' for x in p['features'])
        detail=f'''<section class="detail-hero"><a class="text-link" href="index.html#projects">← 전체 프로젝트</a><p class="eyebrow">PROJECT 0{i+1} / {e(p['category'])}</p><h1>{e(p['label'])}</h1><p class="detail-lead">{e(p['headline'])}</p><div class="tags"><span>{e(p['role'])}</span><span>{e(p['stack'])}</span></div></section><section class="section detail-grid">{shot(p,True)}<div class="detail-copy"><section><p class="eyebrow">THE PROBLEM</p><h2>해결하려는 과제</h2><p>{e(p['problem'])}</p></section><section><p class="eyebrow">IMPLEMENTATION</p><h2>구현한 작업 공간</h2><p>{e(p['solution'])}</p><ul>{features}</ul></section><section><p class="eyebrow">DESIGN DECISIONS</p><h2>설계 판단</h2><ul>{bullets}</ul></section></div></section><section class="section verification-grid"><article><span class="pass">VERIFIED / 2026.10.05</span><h2>확인된 동작</h2><p>{e(p['verified'])}</p></article><article><span class="eyebrow">NEXT ITERATION</span><h2>추가 개선 범위</h2><p>{e(p['improvement'])}</p></article></section><section class="section compact"><p class="scope-note">{e(DATA['scope'])}</p><div class="actions"><a class="button primary" href="technical.html">전체 설계·검증 보기</a><a class="button" href="https://github.com/dubukimch/{p['name']}">GitHub 소스 ↗</a><a class="button" href="{PDF}" download>포트폴리오 PDF ↓</a></div></section>'''
        (ROOT/p['page']).write_text(page(p['label'],detail,p['headline']+' · '+p['role']),encoding='utf-8')
    responsibilities=''.join(f'<tr><th scope="row">{e(p["label"])}</th><td>{e(p["role"])}</td><td>{e(p["decisions"][0])}</td></tr>' for p in PROJECTS)
    architecture=f'''<section class="detail-hero"><p class="eyebrow">ARCHITECTURE / VERIFICATION</p><h1>역할의 경계와<br><em>검증의 근거.</em></h1><p class="detail-lead">신호의 원본, 계산의 권위, 읽기·설명의 책임을 나눕니다. 아래 연결은 설계된 데이터 경로이며 전체 통합 실행 성공을 뜻하지 않습니다.</p></section><section class="section compact">{flow()}<div class="table-scroll"><table class="evidence-table"><caption>책임과 소유권</caption><thead><tr><th>프로젝트</th><th>소유 범위</th><th>설계 원칙</th></tr></thead><tbody>{responsibilities}</tbody></table></div></section><section class="section"><p class="eyebrow">REPRODUCIBLE LOCAL CHECKS</p><h2>2026.10.05 동작 검사</h2>{evidence()}<div class="verification-grid"><article><h3>격리 실행</h3><p>임의 Docker 프로젝트·내부 네트워크·loopback 공개 포트·자격 증명 없는 테스트 설정을 사용합니다. 실제 사용자 DB/설비를 재사용하지 않습니다.</p></article><article><h3>계정과 권한</h3><p>OEE 기본 Bootstrap 비활성, 명시적 관리자 생성, Viewer 쓰기 거부, 비활성·손상 해시 거부, 재시작 후 계정 보존을 실제 MySQL에서 검사했습니다.</p></article></div></section><section class="section"><p class="eyebrow">COST / LICENSE / REMAINING WORK</p><h2>무료 실행과 검토 범위</h2><div class="verification-grid"><article><h3>사용한 재료</h3><p>자체 작성 HTML/CSS/JS·도식과 직접 캡처한 로컬 UI를 사용합니다. 새 npm·NuGet·AI 의존성, 외부 LLM API, 유료 서비스, 웹 폰트 다운로드를 추가하지 않았습니다.</p><p>PDF는 기존 ReportLab/Pillow/pypdf와 Windows 맑은 고딕의 editable embedding 플래그를 확인해 만들었습니다. 글꼴 파일을 사이트에 복사하지 않습니다.</p></article><article><h3>배포 전 검토</h3><p>Gateway/Twin OPC UA는 원문 MIT 버전으로 전환했습니다. 전체 1195개 메타데이터 행 중 원문 검토 필요 197행은 미완료이며 SNI.runtime 독자 조건, native 구성 요소·자산·NOTICE도 별도 검토 대상입니다.</p><p>사이트와 PDF는 바이너리/컨테이너 배포 승인을 선언하지 않습니다. GitHub 원격 반영도 인증·권한 확보 전에는 완료로 표시하지 않습니다.</p></article></div><div class="reference-links"><a href="https://opcfoundation.org/license/mit.html">OPC Foundation MIT 조건 ↗</a><a href="https://www.mysql.com/products/community/">MySQL Community ↗</a><a href="https://learn.microsoft.com/en-us/typography/fonts/font-faq">Windows 글꼴 문서 임베딩 조건 ↗</a></div></section>'''
    (ROOT/'technical.html').write_text(page('Architecture & Verification',architecture,'여섯 프로젝트의 책임 경계와 2026-10-05 실제 로컬 검증 범위'),encoding='utf-8')
    presentation=f'<section class="detail-hero"><p class="eyebrow">PORTFOLIO / CURRENT EDITION</p><h1>여섯 프로젝트를<br>한 문서로.</h1><p class="detail-lead">2026.10.05 검증과 현재 로컬 화면을 포함한 10쪽 포트폴리오입니다.</p><div class="actions"><a class="button primary" href="{PDF}">PDF 열기 ↗</a><a class="button" href="index.html">프로젝트 둘러보기</a></div></section>'
    (ROOT/'presentation.html').write_text(page('Portfolio document',presentation,'검증된 여섯 프로젝트의 현재 포트폴리오 PDF'),encoding='utf-8')
    print('Built 9 static pages, 6 current owned screenshots; no package/download/API calls.')


if __name__=='__main__':
    build()
