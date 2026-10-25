"""Build the local seven-project portfolio. Never captures or overwrites screenshots."""
import json
import runpy
import shutil
import sys
from html import escape as e
from pathlib import Path
from manual_pages import manual_strip, manual_hub, manual_guide

ROOT = Path(__file__).resolve().parents[1]
DATA = json.loads((ROOT / 'content/projects.json').read_text(encoding='utf-8'))
PROJECTS = DATA['projects']
DATE = DATA['date']
DISPLAY_DATE = DATE.replace('-', '.')
PDF = f'assets/docs/industrial-platform-portfolio-{DATE}.pdf'
SHOTS = f'assets/screenshots/{DATE}'
MIRROR = ROOT.parent / '포트폴리오'
MANUAL_DATE = '2026-10-25'
DESIGN_VERSION = '2026-10-26'
PROJECT_ICONS = {'plc': 'cpu', 'gateway': 'network', 'twin': 'boxes', 'oee': 'gauge', 'data': 'chart', 'assistant': 'message-square', 'assethub': 'waypoints'}
MANUAL_ROOT = ROOT.parent / '솔루션_사용매뉴얼' / '2026-10-24'
GROUPS = [('all', '전체 프로젝트'), ('collect', '수집·연결'), ('operate', '운영·디지털 트윈'), ('analyze', '분석·설명'), ('identity', '자산·의미')]
MANUAL_DATA = {}


def ui_icon(name):
    """Inline the bundled Lucide artwork; decorative icons inherit text color."""
    svg = ' '.join((ROOT / 'assets/icons/lucide' / f'{name}.svg').read_text(encoding='utf-8').split())
    return svg.replace('<svg', '<svg class="ui-icon" aria-hidden="true" focusable="false"', 1)


def brand_mark():
    return '<span class="brand-mark" aria-hidden="true">' + ui_icon('boxes') + '</span>'


def feature_preview():
    twin = next(p for p in PROJECTS if p['id'] == 'twin')
    width, height = image_size(ROOT / SHOTS / 'twin.jpg')
    return f'''<figure class="feature-preview"><div class="feature-topline"><span>{ui_icon('boxes')} TWINFORGE</span><span>SELECTED PROJECT / 03</span></div><a class="feature-image" href="{twin['page']}" aria-label="TwinForge 프로젝트 자세히 보기"><img src="{SHOTS}/twin.jpg" width="{width}" height="{height}" alt="TwinForge의 로컬 가상 공장과 3D 설비 배치 화면" fetchpriority="high"><span class="feature-open">{ui_icon('external-link')}</span></a><figcaption><div><span class="feature-kicker">DIGITAL TWIN / LOCAL SIMULATION</span><strong>데이터에 공간과 맥락을 더하다.</strong></div><a href="{twin['page']}" aria-label="TwinForge 구현과 설계">{ui_icon('chevron-right')}</a></figcaption><p class="feature-scope">직접 구현한 로컬 시뮬레이션 · 실제 공장 데이터와 구분합니다.</p></figure>'''


def manual_downloads():
    links = ''.join(f'<a class="button" href="{path}" download>통합 사용 매뉴얼 {extension.upper()} <span aria-hidden="true">↓</span></a>' for extension, path in MANUAL_DATA.get('downloads', {}).items() if (ROOT / path).is_file())
    return f'<div class="actions manual-downloads" aria-label="솔루션 사용 매뉴얼 다운로드">{links}</div>' if links else ''


def image_size(path):
    """Read JPEG SOF dimensions without installing an image dependency."""
    if path.is_file():
        with path.open('rb') as stream:
            if stream.read(2)==b'\xff\xd8':
                while True:
                    marker=stream.read(1)
                    if not marker:break
                    if marker!=b'\xff':continue
                    marker=stream.read(1)
                    while marker==b'\xff':marker=stream.read(1)
                    if not marker or marker in (b'\xd9',b'\xda'):break
                    length=int.from_bytes(stream.read(2),'big')
                    if length<2:break
                    segment=stream.read(length-2)
                    if marker[0] in (0xc0,0xc1,0xc2,0xc3,0xc5,0xc6,0xc7,0xc9,0xca,0xcb,0xcd,0xce,0xcf):
                        return int.from_bytes(segment[3:5],'big'),int.from_bytes(segment[1:3],'big')
    return 1280,720


def page(title, content, description, active=''):
    return f'''<!doctype html>
<html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="theme-color" content="#f7f7f2"><title>{e(title)} · dubukimch</title>
<meta name="description" content="{e(description)}"><meta property="og:title" content="{e(title)}"><meta property="og:description" content="{e(description)}"><meta property="og:type" content="website">
<link rel="icon" type="image/svg+xml" href="assets/icons/brand.svg"><link rel="stylesheet" href="assets/css/styles.css?v={DESIGN_VERSION}"><link rel="stylesheet" href="assets/css/manuals.css?v={DESIGN_VERSION}"><script defer src="assets/js/main.js?v={DATE}"></script><script defer src="assets/js/manuals.js?v={MANUAL_DATE}"></script></head>
<body><a class="skip-link" href="#main">본문 바로가기</a>
<header class="site-header"><a class="brand" href="index.html" aria-label="Industrial Systems Portfolio 홈">{brand_mark()}<span class="brand-name">dubukimch<span class="brand-period">.</span><small>Software &amp; industrial systems</small></span></a>
<button class="nav-toggle" type="button" aria-expanded="false" aria-controls="nav" hidden>메뉴 {ui_icon("list")}</button>
<nav id="nav" aria-label="주요 메뉴"><a href="index.html#projects"{' aria-current="page"' if active == 'projects' else ''}>프로젝트 <span>07</span></a><a href="technical.html"{' aria-current="page"' if active == 'architecture' else ''}>아키텍처</a><a href="manuals.html"{' aria-current="page"' if active == 'manuals' else ''}>사용 매뉴얼</a><a href="index.html#evidence">검증 기록</a><a class="nav-cta" href="{PDF}" download>포트폴리오 PDF {ui_icon("file-down")}</a></nav></header>
<main id="main">{content}</main>
<footer class="site-footer"><a class="brand footer-brand" href="index.html">{brand_mark()}<span class="brand-name">dubukimch.<small>생각을 설계하고, 동작으로 증명합니다.</small></span></a><div><a href="index.html#projects">프로젝트</a><a href="technical.html">설계와 검증</a><a href="manuals.html">사용 매뉴얼</a><a href="{PDF}" download>PDF 다운로드 ↗</a></div><p>개인 산업 소프트웨어 포트폴리오 · {DISPLAY_DATE}<span>직접 만든 시스템과 직접 확인한 근거를 담았습니다.</span></p></footer>
<dialog id="lightbox" aria-label="프로젝트 화면 갤러리"><div class="lightbox-toolbar"><span id="gallery-position"></span><button class="lightbox-close" type="button" aria-label="확대 화면 닫기">닫기 <span aria-hidden="true">×</span></button></div><figure><img alt=""><figcaption></figcaption></figure><div class="gallery-controls"><button type="button" data-gallery-step="-1" aria-label="이전 프로젝트 화면">← 이전</button><button type="button" data-gallery-step="1" aria-label="다음 프로젝트 화면">다음 →</button></div></dialog>
</body></html>'''


def diagram():
    return '''<div class="system-map" aria-label="제품별 데이터와 의미의 책임 구조"><div class="map-title"><span>SYSTEM OVERVIEW</span><span class="status-label">7 WORKSPACES</span></div><div class="map-source"><a href="plc-simulation.html"><small>01 / SOURCE</small><strong>PLC Simulation</strong><span>상태 · 카운터</span></a><span class="map-arrow" aria-hidden="true">→</span><a href="iiot-gateway.html"><small>02 / CONNECT</small><strong>IIoT Gateway</strong><span>품질 · 원본 시각</span></a></div><div class="map-branch" aria-hidden="true"><span>↓</span><span>↓</span></div><div class="map-source"><a href="twinforge.html"><small>03 / CONTEXT</small><strong>TwinForge</strong><span>3D · 생산 맥락</span></a><span class="map-arrow" aria-hidden="true">↔</span><a href="oee-analyzer.html"><small>04 / CALCULATE</small><strong>OEEAnalyzer</strong><span>A/P/Q · 계산 근거</span></a></div><div class="map-read"><span>READ & EXPLAIN</span><a href="datanexus-analytics.html">DataNexus ↗</a><a href="industrial-ai-assistant.html">Assistant ↗</a></div><a href="industrial-assethub.html" class="map-identity"><span class="identity-icon" aria-hidden="true">◇</span><div><small>IDENTITY & SEMANTICS</small><strong>Industrial AssetHub</strong><span>공통 식별 · 의미 · 소스 매핑 초안</span></div><span aria-hidden="true">↗</span></a><p class="map-note">제품의 소유권을 나타내는 설계도입니다.<br>연결별 실제 검증 범위는 아래 근거에서 확인할 수 있습니다.</p></div>'''


def shot(p, detail=False):
    width,height=image_size(ROOT/SHOTS/f'{p["id"]}.jpg')
    return f'''<figure class="product-shot{' detailed' if detail else ''}"><div class="window-bar"><span class="window-dots" aria-hidden="true">● ● ●</span><span>{e(p['name'])}</span><span class="window-local">LOCAL</span></div><button type="button" class="shot" data-lightbox="{SHOTS}/{p['id']}.jpg" data-title="{e(p['label'])}" data-caption="{e(p['caption'])}" aria-label="{e(p['label'])} 화면 확대"><img src="{SHOTS}/{p['id']}.jpg" width="{width}" height="{height}" alt="{e(p['label'])} 로컬 UI 캡처" loading="lazy"><span class="expand-shot" aria-hidden="true">화면 확대 ↗</span></button><figcaption>{e(p['caption'])}</figcaption></figure>'''


def evidence():
    return f'''<div class="evidence-list"><article><span class="evidence-date">2026.10.09</span><div><h3>읽기 흐름을 실제 값으로 확인</h3><p>격리 Docker fixture에서 PLC → Gateway Modbus → Twin OPC UA의 값·Good 품질·원본/수신 시각을 확인했습니다. 통합 검사는 29개 PASS 기록입니다.</p></div><span class="evidence-tag">READ PATH</span></article><article><span class="evidence-date">2026.10.05</span><div><h3>인증과 계산 경계의 회귀</h3><p>실제 MySQL 인증 25개, OEE .NET 35개, Twin .NET 45개 PASS. 서로 다른 fixture의 결과이며 전체 생산 흐름을 뜻하지 않습니다.</p></div><span class="evidence-tag">REGRESSION</span></article><article><span class="evidence-date">{DISPLAY_DATE}</span><div><h3>일곱 작업 공간을 한눈에</h3><p>로컬 UI 캡처와 역할별 설명을 최신 구성으로 정리했습니다. AssetHub는 로컬 초안·온톨로지 구현 단계이며 운영 승인 API와 표준 AAS runtime은 미완료입니다.</p></div><span class="evidence-tag">LOCAL UI</span></article></div><p class="scope-note">{e(DATA['scope'])}</p>'''


def home():
    suite_width,suite_height=image_size(ROOT/SHOTS/'suite.jpg')
    controls=''.join(f'<button type="button" data-filter="{key}" aria-pressed="{str(key == "all").lower()}">{label}</button>' for key,label in GROUPS)
    cards=''.join(f'''<article class="case-card" data-project data-group="{p['group']}" data-search="{e(' '.join([p['label'],p['role'],p['stack'],p['headline']]).lower())}"><div class="case-top"><span class="project-symbol">{ui_icon(PROJECT_ICONS[p['id']])}</span><span class="eyebrow">{e(p['category'].split(" / ",1)[1])}</span><span class="case-number">{i+1:02d}</span></div>{shot(p)}<div class="case-body"><a class="case-title" href="{p['page']}"><h3>{e(p['label'])}</h3>{ui_icon("external-link")}</a><p class="case-headline">{e(p['headline'])}</p><p class="role-label">{e(p['role'])}</p><div class="tags">{''.join('<span>'+e(x)+'</span>' for x in p['stack'].split(' · ')[:3])}</div><div class="case-links"><a class="text-link" href="{p['page']}">프로젝트 자세히 {ui_icon("chevron-right")}</a><a class="case-manual-link" href="manual-{p['id']}.html">{ui_icon("book-open")} 사용 매뉴얼</a></div></div></article>''' for i,p in enumerate(PROJECTS))
    return f'''<section class="hero shell"><div class="hero-copy"><p class="eyebrow"><span class="eyebrow-line"></span> SOFTWARE ENGINEERING PORTFOLIO</p><h1>현장의 데이터가<br><em>쓰이는 순간까지.</em></h1><p class="hero-lead">설비의 신호를 수집하고, 공장을 시각화하고,<br class="desktop-break"> 데이터의 의미를 읽는 소프트웨어를 만듭니다.</p><div class="actions"><a class="button primary" href="#projects">프로젝트 둘러보기 {ui_icon('chevron-right')}</a><a class="button quiet" href="technical.html">전체 설계 보기 {ui_icon('external-link')}</a></div><div class="hero-note">{ui_icon('cpu')}<span>설계부터 구현, 검증까지 직접 만든 7개의 프로젝트</span></div></div><div class="hero-visual">{feature_preview()}</div></section>
<div class="summary-strip shell"><div><strong>07<span> Projects</span></strong><span>서로 다른 역할, 하나의 설계 관점</span></div><div>{ui_icon('network')}<span>수집 · 연결</span></div><div>{ui_icon('boxes')}<span>운영 · 디지털 트윈</span></div><div>{ui_icon('chart')}<span>분석 · 설명</span></div><div>{ui_icon('waypoints')}<span>자산 · 의미</span></div></div>
<section class="section shell" id="projects"><div class="section-head"><div><p class="eyebrow">01 / SELECTED WORK</p><h2>직접 만든 시스템들<span class="heading-count"> / 07</span></h2></div><p>문제에서 출발해, 동작하는 화면으로.<br>각 프로젝트의 구현과 설계 판단을 소개합니다.</p></div><div class="project-tools" hidden><div class="filter-bar" role="group" aria-label="프로젝트 역할 필터">{controls}</div><label class="project-search"><span class="sr-only">프로젝트 검색</span>{ui_icon("search")}<input type="search" id="project-search" placeholder="프로젝트·기술 검색" autocomplete="off"></label></div><p class="result-count" id="project-count" aria-live="polite" hidden>7개 프로젝트</p><div class="cases-grid">{cards}</div><div class="empty-results" hidden><h3>일치하는 프로젝트가 없습니다.</h3><p>다른 이름이나 기술을 검색해 보세요.</p><button class="button" type="button" id="reset-filters">전체 프로젝트 보기</button></div></section>
<section class="integration-section" id="integration"><div class="shell integration-inner"><div><p class="eyebrow">02 / CONNECTED BY DESIGN</p><h2>값은 원본에서.<br>의미는 관계에서.</h2><p>PLC와 Gateway는 신호의 출처를, Twin과 OEE는 생산 맥락과 계산 책임을 지킵니다. DataNexus와 Assistant는 결과를 읽고 설명합니다.</p><a class="text-link" href="technical.html">제품 사이의 계약 살펴보기 →</a></div><div class="integration-notes"><article><span>{ui_icon("network")}</span><div><h3>원본을 보존하는 데이터 경로</h3><p>값과 함께 품질·원본 시각·수신 시각을 읽습니다. 연결되었다는 사실과 유효한 값이 있다는 사실을 구분합니다.</p></div></article><article><span>{ui_icon("gauge")}</span><div><h3>한곳에서 소유하는 계산</h3><p>OEE는 계산 결과를, Twin은 생산 맥락을 소유합니다. 읽기 제품이 효율을 다시 계산하거나 설비를 제어하지 않습니다.</p></div></article><article><span>{ui_icon("waypoints")}</span><div><h3>식별과 의미를 위한 AssetHub</h3><p>공통 ID와 소스 tuple을 로컬 초안에 연결합니다. 기존 실행 경로와 독립적으로 자산·개념·관계를 검토합니다.</p></div></article></div></div></section>
<section class="suite-section shell"><div class="suite-caption"><div><p class="eyebrow">A SHARED LOCAL WORKSPACE</p><h3>일곱 경로의 응답을 한 화면에서.</h3><p>AssetHub 연결 작업 공간에서 고정된 로컬 경로의 HTTP 상태·응답 시간·관측 시각을 확인합니다. 제품 사이 데이터 전송과 업무 흐름의 성공 여부는 별도로 검증합니다.</p></div><a class="button" href="http://127.0.0.1:5189/workbench/suite" data-local-only hidden>로컬 연결 작업 공간 ↗</a></div><figure class="suite-capture"><button type="button" class="shot" data-lightbox="{SHOTS}/suite.jpg" data-title="Industrial Suite" data-caption="고정된 일곱 로컬 경로의 HTTP 응답 관측. 제품 사이 데이터 전송 성공과는 별개입니다." aria-label="일곱 솔루션 연결 작업 공간 화면 확대"><img src="{SHOTS}/suite.jpg" width="{suite_width}" height="{suite_height}" alt="일곱 로컬 경로의 HTTP 관측을 표시한 Industrial Suite" loading="lazy"><span class="expand-shot" aria-hidden="true">화면 확대 ↗</span></button><figcaption>로컬 HTTP 경로의 접근 가능 여부를 관측한 화면입니다. PLC→Gateway→Twin 전송·OEE 계산·Kafka 소비·AssetHub 운영 승인을 뜻하지 않습니다.</figcaption></figure></section>
<section class="section shell" id="evidence"><div class="section-head"><div><p class="eyebrow">03 / ENGINEERING EVIDENCE</p><h2>구현의 뒤에는,<br>확인 가능한 기록.</h2></div><p>검증한 날짜와 경로를 함께 기록합니다.<br>데모·미수신·미완료 상태도 설명에 포함합니다.</p></div>{evidence()}</section>
<section class="closing shell"><div><p class="eyebrow">TAKE A CLOSER LOOK</p><h2>더 깊이 살펴보고 싶다면.</h2></div><div><p>프로젝트의 설계와 검증은 포트폴리오에, 사용 순서는 매뉴얼에 담았습니다.</p><a class="button primary" href="{PDF}" download>포트폴리오 PDF 다운로드 <span aria-hidden="true">↓</span></a>{manual_downloads()}</div></section>'''


def detail(p, index):
    features=''.join('<li>'+e(x)+'</li>' for x in p['features'])
    decisions=''.join('<li>'+e(x)+'</li>' for x in p['decisions'])
    next_project=PROJECTS[(index+1)%len(PROJECTS)]
    return f'''<section class="detail-hero shell"><a class="back-link" href="index.html#projects">← 전체 프로젝트</a><p class="eyebrow">{ui_icon(PROJECT_ICONS[p["id"]])} PROJECT {index+1:02d} / {e(p['category'].split(' / ',1)[1])}</p><h1>{e(p['label'])}</h1><p class="detail-lead">{e(p['headline'])}</p><div class="tags">{''.join('<span>'+e(x)+'</span>' for x in p['stack'].split(' · '))}</div></section><section class="detail-layout shell"><div class="detail-visual">{shot(p,True)}<div class="detail-role"><span>THIS PRODUCT OWNS</span><strong>{e(p['role'])}</strong></div></div><div class="detail-copy"><section><p class="eyebrow">THE PROBLEM</p><h2>해결하려는 과제</h2><p>{e(p['problem'])}</p></section><section><p class="eyebrow">THE WORKSPACE</p><h2>구현한 작업 공간</h2><p>{e(p['solution'])}</p><ul>{features}</ul></section><section><p class="eyebrow">DESIGN DECISIONS</p><h2>설계에서 지킨 것</h2><ul>{decisions}</ul></section></div></section><section class="section shell"><div class="verification-grid"><article><span class="eyebrow">EVIDENCE & SCOPE</span><h2>확인된 동작</h2><p>{e(p['verified'])}</p></article><article><span class="eyebrow">NEXT ITERATION</span><h2>다음 개선 범위</h2><p>{e(p['improvement'])}</p></article></div><p class="scope-note">{e(DATA['scope'])}</p><div class="actions detail-actions"><a class="button primary" href="https://github.com/dubukimch/{p['name']}">GitHub 소스 ↗</a><a class="button" href="technical.html">전체 연결 구조</a><a class="button" href="{e(p['endpoint'])}" data-local-only hidden>로컬 작업 공간 열기 ↗</a></div></section><section class="next-project shell"><span class="eyebrow">NEXT PROJECT</span><a href="{next_project['page']}">{e(next_project['label'])}<span aria-hidden="true">→</span></a></section>'''


def architecture():
    rows=''.join(f'<tr><th scope="row"><a href="{p["page"]}">{e(p["label"])}</a></th><td>{e(p["role"])}</td><td>{e(p["decisions"][0])}</td></tr>' for p in PROJECTS)
    return f'''<section class="detail-hero shell"><p class="eyebrow">ARCHITECTURE / OWNERSHIP / EVIDENCE</p><h1>연결은 명확하게.<br><em>책임은 분명하게.</em></h1><p class="detail-lead">원본 신호, 계산 결과와 자산의 의미를 구분합니다. 각 제품의 책임이 선명할수록 통합의 근거도 읽기 쉬워집니다.</p></section><section class="architecture-overview shell">{diagram()}<div class="detail-copy"><section><p class="eyebrow">DATA PLANE</p><h2>값과 생산 맥락의 흐름</h2><p>PLC → Gateway → Twin 읽기 값은 격리 fixture로 확인했습니다. OEE sample/context와 DataNexus Kafka 경로를 포함한 전체 생산 흐름은 추가 검증이 필요합니다.</p></section><section><p class="eyebrow">IDENTITY & SEMANTICS</p><h2>원본을 대체하지 않는 공통 식별</h2><p>AssetHub는 자산 ID, 개념과 소스 매핑 초안을 다룹니다. Gateway 수집·PLC 실행·OEE 계산·Twin 생산 맥락의 책임은 유지합니다. 현재 로컬 작업 공간이며 승인 API와 운영 원장은 미완료입니다.</p></section><section><p class="eyebrow">READING CONTRACT</p><h2>결측도 데이터의 일부</h2><p>quality, 원본·수신 시각, sourceMode와 명시적 binding을 보존합니다. 미수신을 0이나 임의 값으로 채우지 않고, 연결과 실제 관측을 별도로 표시합니다.</p></section></div></section><section class="section shell"><p class="eyebrow">PRODUCT RESPONSIBILITIES</p><h2>제품마다 하나의 소유권</h2><div class="table-scroll"><table><caption class="sr-only">일곱 프로젝트의 책임과 설계 원칙</caption><thead><tr><th scope="col">프로젝트</th><th scope="col">소유하는 역할</th><th scope="col">설계 원칙</th></tr></thead><tbody>{rows}</tbody></table></div></section><section class="section shell"><p class="eyebrow">REPRODUCIBLE EVIDENCE</p><h2>확인한 연결과 남은 경계</h2>{evidence()}<div class="verification-grid"><article><h3>실행과 데이터의 경계</h3><p>격리 시뮬레이터·빈 DB fixture·로컬 초안을 사용합니다. OEE NoData, Kafka 미연결, Fake 생성기와 실제 읽기 출처를 구분합니다. 실장비 명령은 이 포트폴리오의 검증 경로에 포함하지 않습니다.</p></article><article><h3>제작과 공개의 범위</h3><p>자체 HTML/CSS/JavaScript와 직접 캡처한 화면을 사용합니다. 외부 AI API·새 유료 서비스·외부 폰트가 필요하지 않습니다. 로컬 검증과 GitHub 원격 게시 상태는 별개입니다.</p></article></div></section><section class="section shell delivery-note"><p class="eyebrow">DELIVERY NOTES</p><h2>구현 다음에 남은 검토</h2><p>운영 인증·승인된 자산 매핑 소비 계약·정상 OEE 시계열 경로·재연결과 지연 회귀가 남아 있습니다. 전체 의존성·native 자산·NOTICE의 배포 조건도 별도 검토 대상입니다. 로컬 UI와 이 문서는 제품의 운영 배포 승인이나 AAS 표준 적합성 판정을 선언하지 않습니다.</p><a class="button" href="{PDF}" download>전체 포트폴리오 PDF ↓</a></section>'''


def build():
    global MANUAL_DATA
    saved_manuals = json.loads((ROOT/'content/manuals.json').read_text(encoding='utf-8')) if (ROOT/'content/manuals.json').is_file() else {}
    explicit_publication = any(argument.startswith('--publication-manifest') for argument in sys.argv[1:])
    official_publication = ROOT.parent/'솔루션_사용매뉴얼'/MANUAL_DATE/'publication-manifest.json'
    can_refresh = official_publication.is_file() or explicit_publication or saved_manuals.get('schemaVersion', 0) < 2
    if (MANUAL_ROOT/'data/manual-manifest.json').is_file() and can_refresh:
        runpy.run_path(str(ROOT/'scripts/sync-manual-content.py'), run_name='__main__')
    elif not (ROOT/'content/manuals.json').is_file():
        raise FileNotFoundError('Provide the reviewed manual source or the published content/manuals.json and assets.')
    MANUAL_DATA = json.loads((ROOT/'content/manuals.json').read_text(encoding='utf-8'))
    guides = {product['id']: product for product in MANUAL_DATA['products']}
    (ROOT/SHOTS).mkdir(parents=True,exist_ok=True)
    home_html = home()
    pages={'index.html':page('산업 소프트웨어 포트폴리오',home_html,'일곱 산업 소프트웨어의 구현, 연결 구조, 실제 화면과 동작별 사용 매뉴얼','projects'), 'technical.html':page('Architecture & Evidence',architecture(),'일곱 프로젝트의 책임 경계, 자산 의미와 실제 읽기 경로의 검증','architecture')}
    for index,p in enumerate(PROJECTS):
        detail_html = detail(p,index)
        marker = '<section class="section shell"><div class="verification-grid">'
        assert detail_html.count(marker) == 1, 'Project guide must precede verification section'
        detail_html = detail_html.replace(marker, manual_strip(guides[p['id']], MANUAL_DATA) + marker, 1)
        pages[p['page']]=page(p['label'],detail_html,p['headline']+' · '+p['role'])
    pages['manuals.html'] = page('솔루션 사용 매뉴얼', manual_hub(MANUAL_DATA), '일곱 산업 솔루션의 41개 동작과 38개 실제 화면, PDF·PPTX·Markdown 사용 안내', 'manuals')
    for guide in MANUAL_DATA['products']:
        pages[guide['manualPage']] = page(guide['title'], manual_guide(guide, MANUAL_DATA), guide['subtitle']+' · 동작별 캡처와 사용 순서', 'manuals')
    presentation=f'''<section class="document-hero shell"><p class="eyebrow">PORTFOLIO / {DISPLAY_DATE}</p><h1>구현한 시스템.<br><em>연결한 경험.</em></h1><p class="detail-lead">일곱 프로젝트의 문제, 화면, 설계 판단과 검증 범위를 정리한 현재 포트폴리오입니다.</p><div class="actions"><a class="button primary" href="{PDF}">PDF 열기 ↗</a><a class="button" href="{PDF}" download>다운로드 ↓</a><a class="button quiet" href="index.html#projects">프로젝트 둘러보기 →</a></div>{manual_downloads()}<p class="scope-note">{e(DATA['scope'])}</p></section>'''
    pages['presentation.html']=page('Portfolio document',presentation,'일곱 산업 소프트웨어 포트폴리오 PDF')
    for filename,html in pages.items():
        (ROOT/filename).write_text(html,encoding='utf-8')
    manifest={'date':DATE,'capture_format':'Native browser JPEG; dimensions recorded from each available image','screenshots':[{'id':p['id'],'file':f'{SHOTS}/{p["id"]}.jpg','size':image_size(ROOT/SHOTS/f'{p["id"]}.jpg') if (ROOT/SHOTS/f'{p["id"]}.jpg').is_file() else None,'endpoint':p['endpoint'],'caption':p['caption']} for p in PROJECTS], 'integration_capture':{'file':f'{SHOTS}/suite.jpg','size':image_size(ROOT/SHOTS/'suite.jpg') if (ROOT/SHOTS/'suite.jpg').is_file() else None,'endpoint':'http://127.0.0.1:5189/workbench/suite','caption':'고정된 일곱 로컬 경로의 HTTP 응답 관측. 제품 사이 데이터 전송 성공과는 별개입니다.'}}
    (ROOT/'content/screenshots.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    MIRROR.mkdir(exist_ok=True)
    for filename in pages:
        shutil.copyfile(ROOT/filename,MIRROR/filename)
    for path in ['assets/css/styles.css','assets/js/main.js','assets/icons/brand.svg',PDF,f'{SHOTS}/suite.jpg']+[f'{SHOTS}/{p["id"]}.jpg' for p in PROJECTS]:
        if (ROOT/path).is_file():
            target=MIRROR/path;target.parent.mkdir(parents=True,exist_ok=True)
            shutil.copyfile(ROOT/path,target)
    guide_assets = [ROOT/'assets/css/manuals.css', ROOT/'assets/js/manuals.js', ROOT/'content/manuals.json', ROOT/'content/manual-assets.json']
    if (ROOT/'content/manual-publication.json').is_file():
        guide_assets.append(ROOT/'content/manual-publication.json')
    for folder in ['assets/docs/manuals', 'assets/icons/lucide', 'assets/screenshots/manuals']:
        guide_assets.extend(path for path in (ROOT/folder).rglob('*') if path.is_file())
    for source in guide_assets:
        target = MIRROR/source.relative_to(ROOT)
        target.parent.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(source,target)
    print(f'Built {len(pages)} pages for {len(PROJECTS)} projects; mirrored available assets. Screenshots are never overwritten.')


if __name__=='__main__':
    build()
