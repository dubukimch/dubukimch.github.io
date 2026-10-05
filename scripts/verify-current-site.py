"""Check authored local links/assets/anchors and PDF identity; never fetch externals."""
from html.parser import HTMLParser
from pathlib import Path
import hashlib
import json
from urllib.parse import urlsplit, unquote, urljoin
from urllib.request import build_opener, ProxyHandler, Request
from urllib.error import HTTPError

ROOT=Path(__file__).resolve().parents[1]
BASE='http://127.0.0.1:4174/'


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
                assert path in documents and unquote(parts.fragment) in documents[path].ids, 'Missing anchor '+link
                anchors+=1
            urls.add(urljoin(BASE,path)+(('?' + parts.query) if parts.query else ''))
    for url in sorted(urls):
        with opener.open(url,timeout=5) as response:
            assert response.status==200,url
            assert response.headers['X-Content-Type-Options']=='nosniff'
            if urlsplit(url).path.endswith('.pdf'):assert response.read(5)==b'%PDF-'
    for method in ['GET','HEAD']:
        try:
            opener.open(Request(BASE+'.git/config',method=method),timeout=5)
        except HTTPError as error:
            assert error.code==404
        else:
            raise AssertionError('Hidden git configuration must not be served')
    pdf=ROOT/'assets/docs/industrial-platform-portfolio-2026-10-05.pdf'
    original=ROOT.parent/'포트폴리오/산업_소프트웨어_포트폴리오_2026-10-05.pdf'
    digest=hashlib.sha256(pdf.read_bytes()).hexdigest()
    assert digest==hashlib.sha256(original.read_bytes()).hexdigest()
    result={'status':'PASS','html_pages':len(documents),'local_resources':len(urls),'anchors':anchors,
            'external_links_not_fetched':len(external),'pdf_sha256':digest,'hidden_git_path':'404',
            'scope':'Static local links/assets/anchors and PDF identity; browser behavior checked separately'}
    (ROOT/'.local-preview/link-result.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    print(json.dumps(result,ensure_ascii=False))


if __name__=='__main__':main()
