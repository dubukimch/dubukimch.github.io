"""Check authored local links/assets/anchors and PDF identity; never fetch externals."""
from html.parser import HTMLParser
from pathlib import Path
import argparse
import hashlib
import json
import re
from urllib.parse import urlsplit, unquote, urljoin
from urllib.request import build_opener, ProxyHandler, Request
from urllib.error import HTTPError

ROOT=Path(__file__).resolve().parents[1]


class Document(HTMLParser):
    def __init__(self,path):
        super().__init__();self.links=[];self.ids=set();self.h1=0;self.feed(path.read_text(encoding='utf-8-sig'))

    def handle_starttag(self,tag,attrs):
        values=dict(attrs)
        if values.get('id'):self.ids.add(values['id'])
        if tag=='h1':self.h1+=1
        for attribute in ['href','src','data-lightbox']:
            if values.get(attribute):self.links.append(values[attribute])


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--port',type=int,default=5190)
    args=parser.parse_args()
    base=f'http://127.0.0.1:{args.port}/'
    data=json.loads((ROOT/'content/projects.json').read_text(encoding='utf-8'))
    guide_data=json.loads((ROOT/'content/manuals.json').read_text(encoding='utf-8'))
    publication=json.loads((ROOT/guide_data['publication']).read_text(encoding='utf-8')) if guide_data.get('publication') else None
    publication_entries=[publication['integrated'],*publication['solutions']] if publication else []
    pdf_limits={entry['pdf']['path']:entry['slides'] for entry in publication_entries} if publication else {guide_data['downloads']['pdf']:guide_data['stats']['pdfPages']}
    date=data['date']
    assert len(data['projects'])==7,'Seven project records are required'
    assert len({p['id'] for p in data['projects']})==7,'Duplicate project identity'
    documents={p.name:Document(p) for p in ROOT.glob('*.html')}
    opener=build_opener(ProxyHandler({}))
    urls=set();anchors=0;external=set()
    for name,document in documents.items():
        assert document.h1==1, name+' must have one h1'
        for link in document.links:
            parts=urlsplit(link)
            if parts.scheme or parts.netloc:
                external.add(link);continue
            path=unquote(parts.path) or name
            target=(ROOT/path).resolve()
            assert target.is_relative_to(ROOT), 'Link outside site root'
            assert target.is_file(), name+': missing '+path
            if parts.fragment:
                if path.endswith('.pdf'):
                    assert re.fullmatch(r'page=[1-9]\d*', parts.fragment), 'Invalid PDF page link '+link
                    assert path in pdf_limits and int(parts.fragment.split('=')[1]) <= pdf_limits[path], 'PDF page out of range '+link
                else:
                    assert path in documents and unquote(parts.fragment) in documents[path].ids, 'Missing anchor '+link
                anchors+=1
            urls.add(urljoin(base,path)+(('?' + parts.query) if parts.query else ''))
    for alias in (publication or {}).get('legacyDownloads', {}).values():
        urls.add(urljoin(base,alias))
    for url in sorted(urls):
        with opener.open(url,timeout=5) as response:
            assert response.status==200,url
            assert response.headers['X-Content-Type-Options']=='nosniff'
            if urlsplit(url).path.endswith('.pdf'):assert response.read(5)==b'%PDF-'
            if urlsplit(url).path.endswith('.pptx'):assert response.read(2)==b'PK'
            while response.read(1024*1024):
                pass
    for method in ['GET','HEAD']:
        try:
            opener.open(Request(base+'.git/config',method=method),timeout=5)
        except HTTPError as error:
            assert error.code==404
        else:
            raise AssertionError('Hidden git configuration must not be served')
    pdf=ROOT/f'assets/docs/industrial-platform-portfolio-{date}.pdf'
    mirror=ROOT.parent/'포트폴리오'
    original=mirror/f'산업_소프트웨어_포트폴리오_{date}.pdf'
    digest=hashlib.sha256(pdf.read_bytes()).hexdigest()
    assert digest==hashlib.sha256(original.read_bytes()).hexdigest()
    assets=['assets/css/styles.css','assets/js/main.js',str(pdf.relative_to(ROOT))]
    assets += [f'assets/screenshots/{date}/{p["id"]}.jpg' for p in data['projects']]
    assets += [f'assets/screenshots/{date}/suite.jpg']
    manuals=[ROOT/entry[extension]['path'] for entry in publication_entries for extension in ('pdf','pptx')] if publication else [ROOT/path for path in guide_data['downloads'].values()]
    for manual in manuals:
        assert manual.is_file() and manual.suffix in ('.pdf','.pptx')
        assets.append(manual.relative_to(ROOT).as_posix())
    for relative in guide_data['downloads'].values():
        for page in ['index.html','presentation.html']:
            assert relative in documents[page].links, 'Integrated manual download missing: '+page
    if publication:
        for extension, relative in publication['legacyDownloads'].items():
            assert hashlib.sha256((ROOT/relative).read_bytes()).hexdigest()==publication['integrated'][extension]['sha256'], 'Legacy manual URL serves stale bytes'
            assets.append(relative)
    assets=sorted((set(assets)|{unquote(urlsplit(url).path.lstrip('/')) for url in urls})-set(documents))
    for name in list(documents)+assets:
        assert hashlib.sha256((ROOT/name).read_bytes()).digest()==hashlib.sha256((mirror/name).read_bytes()).digest(),'Stale portfolio mirror: '+name
    manifest=json.loads((ROOT/'content/screenshots.json').read_text(encoding='utf-8'))
    assert {s['id'] for s in manifest['screenshots']}=={p['id'] for p in data['projects']}
    result={'status':'PASS','html_pages':len(documents),'local_resources':len(urls),'anchors':anchors,
            'external_links_not_fetched':len(external),'pdf_sha256':digest,'hidden_git_path':'404',
            'projects':len(data['projects']),'mirror_files':len(documents)+len(assets),
            'manual_downloads':len(manuals),
            'legacy_download_aliases':len((publication or {}).get('legacyDownloads', {})),
            'scope':'Static local links/assets/HTML and PDF anchors, manual captures and site-mirror identity; browser rendering not verified in this run'}
    stage=ROOT/'.local-preview';stage.mkdir(exist_ok=True)
    (stage/'link-result.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    print(json.dumps(result,ensure_ascii=False))


if __name__=='__main__':main()
