"""Render the public operation guides from the reviewed manual sources."""
from html import escape as e


STATES = {'full': '실행 확인', 'partial': '일부 실행 확인', 'unverified': '실행 미확인'}


def icon(path, extra=''):
    return f'<img class="manual-icon {extra}" src="{e(path)}" width="32" height="32" alt="" aria-hidden="true">' if path else ''


def pdf_path(data):
    value = data['downloads']['pdf']
    return value['path'] if isinstance(value, dict) else value


def ppt_path(data):
    value = data['downloads']['pptx']
    return value['path'] if isinstance(value, dict) else value


def actions(product, data, web=True, deck=False):
    links = []
    standalone = product.get('downloads')
    if standalone:
        links.append(f'<a class="button primary" href="{e(standalone["pdf"])}">이 솔루션 PDF 열기 <span aria-hidden="true">↗</span></a>')
        links.append(f'<a class="button" href="{e(standalone["pptx"])}" download>이 솔루션 PPTX ↓</a>')
    if web:
        css = 'button' if standalone else 'button primary'
        links.append(f'<a class="{css}" href="{e(product["manualPage"])}">동작별 웹 매뉴얼 <span aria-hidden="true">→</span></a>')
    if not standalone:
        links.append(f'<a class="button" href="{e(pdf_path(data))}#page={product["chapterPdfPage"]}">PDF 해당 장 열기 <span aria-hidden="true">↗</span></a>')
    links.append(f'<a class="button quiet" href="{e(product["markdown"])}" download>이 솔루션의 Markdown ↓</a>')
    if deck:
        links.append(f'<a class="button quiet" href="{e(pdf_path(data))}#page={product["chapterPdfPage"]}">통합본 해당 장 ↗</a>' if standalone else f'<a class="button quiet" href="{e(ppt_path(data))}" download>통합 매뉴얼 PPTX ↓</a>')
    return '<div class="actions manual-actions">' + ''.join(links) + '</div>'


def manual_strip(product, data):
    first = product['operations'][0]
    stages = ''.join(f'<li><span>{i:02d}</span><strong>{e(op["shortTitle"])}</strong></li>' for i, op in enumerate(product['operations'][:3], 1))
    preview = ''
    if product.get('screenshot'):
        preview = f'<a class="manual-strip-preview" href="{e(product["manualPage"])}" aria-label="{e(product["label"])} 사용 매뉴얼 보기"><img src="{e(product["screenshot"])}" alt="{e(first["shortTitle"])} 실제 실습 화면" loading="lazy"><span>화면을 보며 따라가기 <span aria-hidden="true">↗</span></span></a>'
    return f'''<section class="manual-strip section shell" aria-labelledby="manual-title-{product['id']}"><div class="manual-strip-copy"><p class="eyebrow">FROM OVERVIEW TO HANDS-ON</p><h2 id="manual-title-{product['id']}">{icon(product['icon'])}직접 사용하는 순서</h2><p class="manual-summary">{e(product['subtitle'])}</p><ol class="manual-mini-steps">{stages}</ol><p class="manual-meta">{len(product['operations'])}개 동작 · 실제 캡처 {product['counts']['screenshots']}장 · 전용 문서 {product.get('standalonePages', product['pdfPageEnd']-product['pdfPageStart']+1)}쪽 · 통합본 {product['pdfPageStart']}–{product['pdfPageEnd']}쪽</p>{actions(product, data, deck=True)}<p class="manual-caution">{e(product.get('scopeNote', product['scope']))}</p></div>{preview}</section>'''


def manual_hub(data):
    rows = []
    for i, product in enumerate(data['products'], 1):
        search = e(' '.join([product['label'], product['subtitle'], *[op['shortTitle'] for op in product['operations']]]).lower())
        rows.append(f'''<article class="manual-catalog-item" data-manual-search="{search}"><div class="manual-catalog-number">{i:02d}</div><div class="manual-catalog-copy"><p class="eyebrow">{icon(product['icon'])}{e(product['label'])}</p><h2><a href="{e(product['manualPage'])}">{e(product['title'])}<span aria-hidden="true"> ↗</span></a></h2><p class="manual-summary">{e(product['subtitle'])}</p><p class="manual-meta">{len(product['operations'])}개 동작 · 캡처 {product['counts']['screenshots']}장 · 전용 문서 {product.get('standalonePages', product['pdfPageEnd']-product['pdfPageStart']+1)}쪽 · 통합본 {product['pdfPageStart']}–{product['pdfPageEnd']}쪽</p>{actions(product, data)}</div><a class="manual-catalog-preview" href="{e(product['manualPage'])}" aria-label="{e(product['label'])} 사용 절차 보기"><img src="{e(product['screenshot'])}" alt="{e(product['label'])} 로컬 실습 화면" loading="lazy"></a></article>''')
    return f'''<section class="manual-intro shell"><p class="eyebrow">THE OPERATION LIBRARY / {e(data['date'].replace('-', '.'))}</p><h1>화면을 보며,<br><em>한 단계씩 직접.</em></h1><p class="detail-lead">처음 실행하는 순간부터 결과를 확인할 때까지. 일곱 솔루션의 사용 순서를 실제 화면과 함께 안내합니다.</p><div class="manual-stats"><span><strong>07</strong>솔루션</span><span><strong>41</strong>동작 안내</span><span><strong>38</strong>실제 캡처</span><span><strong>{data['stats']['pdfPages']}</strong>통합 PDF 쪽</span></div><div class="actions manual-actions"><a class="button primary" href="{e(pdf_path(data))}" download>통합 매뉴얼 PDF ↓</a><a class="button" href="{e(ppt_path(data))}" download>통합 매뉴얼 PPTX ↓</a><a class="button quiet" href="index.html#projects">프로젝트 설명 보기 →</a></div><p class="scope-note">로컬 실습을 기록한 사용 안내입니다. 각 동작에 실행 확인 범위와 미연결·미확인 상태를 함께 표시했습니다.</p></section><section class="manual-hub shell"><div class="manual-search-tools" hidden><label for="manual-search">솔루션 또는 동작 찾기</label><input id="manual-search" type="search" placeholder="예: CSV, 태그, 설비, 온도" autocomplete="off"><span id="manual-search-count" role="status" aria-live="polite">7개 솔루션</span></div><div class="manual-catalog">{''.join(rows)}</div><p class="manual-empty" hidden>일치하는 안내가 없습니다. 다른 솔루션명이나 동작을 검색해 주세요.</p></section><section class="section shell manual-files"><p class="eyebrow">FILES FOR PRACTICE</p><h2>같은 자료로 시작하는 실습</h2><p>교육용 입력 파일과 실습에서 실제로 저장한 결과입니다. 실제 설비 생산 데이터와 구분해 사용합니다.</p>{sample_links(data)}<p class="manual-meta">아이콘: Lucide · <a href="assets/icons/lucide/LICENSE-Lucide.txt">라이선스</a> · <a href="assets/icons/lucide/SOURCES.md">출처</a></p></section>'''


def sample_links(data, product=None):
    samples = product.get('samples', []) if product else data.get('samples', [])
    if not samples and product is None:
        unique = {}
        for item in data['products']:
            for sample in item.get('samples', []):
                unique[sample['path']] = sample
        samples = list(unique.values())
    if not samples:
        return ''
    return '<ul class="manual-file-grid">' + ''.join(f'<li><a href="{e(item["path"])}" download>{e(item["label"])} <span aria-hidden="true">↓</span></a></li>' for item in samples) + '</ul>'


def operation_section(product, op, data):
    state = op['evidenceState']
    stages = ''.join(f'<li>{icon(stage.get("icon", ""))}<div><strong>{e(stage["label"])}</strong><p>{e(stage["detail"])}</p></div></li>' for stage in op['stages'])
    evidence = ''
    if op.get('screenshot'):
        meta = op.get('evidence') or {}
        stamp = str(meta.get('capturedAtUtc') or '')
        caption = e(meta.get('observed') or op.get('resultShort') or op['expected'])
        evidence = f'''<figure class="manual-evidence"><button type="button" class="shot" data-lightbox="{e(op['screenshot'])}" data-title="{e(op['shortTitle'])}" data-caption="{caption}" aria-label="{e(op['shortTitle'])} 캡처 확대"><img src="{e(op['screenshot'])}" alt="{e(op['shortTitle'])} 실제 조작 결과" width="{op.get('screenshotWidth', 1280)}" height="{op.get('screenshotHeight', 720)}" loading="lazy"><span class="expand-shot" aria-hidden="true">원본 화면 확대 ↗</span></button><figcaption>{caption}<span class="manual-capture-date">캡처 {e(stamp)} UTC</span></figcaption></figure>'''
    else:
        evidence = f'''<div class="manual-unverified">{icon('assets/icons/lucide/alert-triangle.svg')}<strong>현재 환경에서 실행하지 못한 절차입니다.</strong><p>실제 성공 화면은 아직 없습니다. 아래 순서와 시작 조건을 확인한 뒤 로컬 서비스 복구 후 실행합니다.</p></div>'''
    steps = ''.join(f'<li>{e(item)}</li>' for item in op['steps'])
    trouble = ''.join(f'<li>{e(item)}</li>' for item in op.get('troubleshooting', []))
    capture_note = f'<p class="manual-caution">{e(op["captureNote"])}</p>' if op.get('captureNote') else ''
    legacy_note = f'<p class="manual-caution">{e(op["legacyEvidenceNote"])}</p>' if op.get('legacyEvidenceNote') else ''
    caution = f'<p class="manual-caution">{e(op["cautionShort"])}</p>' if op.get('cautionShort') else ''
    dedicated = f'<a class="text-link" href="{e(op["standalonePdfUrl"])}">전용 PDF {op["standalonePdfPage"]}쪽에서 같은 동작 보기 ↗</a>' if op.get('standalonePdfUrl') else ''
    return f'''<section class="manual-operation" id="{e(op['id'])}" data-operation="{e(op['id'])}" data-evidence-state="{state}"><div class="manual-operation-heading"><span class="manual-step-number">{op['order']:02d}</span><h2>{e(op['shortTitle'])}</h2><span class="manual-state manual-state-{state}">{STATES[state]}</span></div><p class="manual-operation-goal">{e(op['oneLineGoal'])}</p><ol class="manual-stages">{stages}</ol>{evidence}<div class="manual-expected"><strong>{'복구 후 확인할 결과' if state == 'unverified' else '결과 확인'}</strong><p>{e(op['resultShort'])}</p></div>{caution}{capture_note}<details class="manual-details"><summary>전체 조작 단계와 문제 해결</summary>{legacy_note}<h3>{e(op['title'])}</h3><p>{e(op['goal'])}</p><ol>{steps}</ol><h3>기대 결과</h3><p>{e(op['expected'])}</p>{'<h3>문제가 생기면</h3><ul>'+trouble+'</ul>' if trouble else ''}</details><div class="actions">{dedicated}<a class="text-link" href="{e(pdf_path(data))}#page={op['pdfPage']}">통합본 {op['pdfPage']}쪽 ↗</a></div></section>'''


def manual_guide(product, data):
    toc = ''.join(f'<li><a href="#{e(op["id"])}"><span>{op["order"]:02d}</span>{e(op["shortTitle"])}</a></li>' for op in product['operations'])
    prereqs = ''.join(f'<li>{e(item)}</li>' for item in product.get('prerequisites', []))
    sections = ''.join(operation_section(product, op, data) for op in product['operations'])
    return f'''<section class="manual-guide-hero shell"><div class="manual-breadcrumb"><a href="manuals.html">사용 매뉴얼</a><span aria-hidden="true">/</span><a href="{e(product['portfolioPage'])}">{e(product['label'])} 소개</a></div><p class="eyebrow">{icon(product['icon'])} {e(product['label'])} / OPERATION GUIDE</p><h1>{e(product['title'])}</h1><p class="detail-lead">{e(product['subtitle'])}</p><p class="manual-meta">{len(product['operations'])}개 동작 · 실제 캡처 {product['counts']['screenshots']}장 · {e(data['date'].replace('-', '.'))} 개정</p>{actions(product, data, web=False)}<p class="scope-note">{e(product.get('scopeNote', product['scope']))}</p></section><div class="manual-layout shell"><aside class="manual-toc"><nav aria-label="이 솔루션의 동작 목차"><p class="eyebrow">이 페이지에서</p><ol><li><a href="#before-start">시작하기 전에</a></li>{toc}</ol><a class="text-link" href="manuals.html">전체 매뉴얼 →</a></nav></aside><div class="manual-body"><section class="manual-operation" id="before-start"><p class="eyebrow">BEFORE YOU START</p><h2>시작하기 전에</h2><ul class="manual-prerequisites">{prereqs}</ul>{sample_links(data, product)}<p class="manual-caution">{e(product['scope'])}</p></section>{sections}<section class="manual-files"><h2>설명과 자료 이어 보기</h2><div class="actions manual-actions"><a class="button primary" href="{e(product['portfolioPage'])}">이 솔루션의 구현과 설계 →</a><a class="button" href="{e(ppt_path(data))}" download>통합 매뉴얼 PPTX ↓</a><a class="button quiet" href="{e(product['pdfUrl'])}">통합본 해당 장 ↗</a><a class="button quiet" href="manuals.html">다른 솔루션 매뉴얼 →</a></div></section></div></div>'''
