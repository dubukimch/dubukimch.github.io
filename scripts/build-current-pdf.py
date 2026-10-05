"""Create one reviewed 10-page Korean portfolio; copy the same PDF to the site.
Uses existing bundled ReportLab/Pillow/pypdf and OS fonts with embedding checks.
No software installation, font redistribution, external request or AI inference.
"""
import json
import shutil
import struct
from pathlib import Path
from html import escape

from PIL import Image
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.colors import HexColor, white
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Paragraph
from pypdf import PdfReader

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT.parent / '포트폴리오/산업_소프트웨어_포트폴리오_2026-10-05.pdf'
DATA = json.loads((ROOT/'content/projects.json').read_text(encoding='utf-8'))
PROJECTS = DATA['projects']
W,H = A4
INK,TEAL,PAPER,MUTED,LINE = [HexColor(x) for x in ['#17211f','#145d50','#f5f4ef','#59645f','#d9ded7']]


def font(name, path):
    data = path.read_bytes()
    flags = None
    for i in range(struct.unpack_from('>H',data,4)[0]):
        tag, _, offset, _ = struct.unpack_from('>4sIII',data,12+i*16)
        if tag == b'OS/2':
            flags = struct.unpack_from('>H',data,offset+8)[0]
    # Only installable or editable embedding; refuse restricted/no-subset/bitmap flags.
    if flags not in (0,8):
        raise ValueError(f'Font embedding permission requires review: {path.name}: {flags}')
    pdfmetrics.registerFont(TTFont(name,str(path)))


def main():
    font('Body',Path('C:/Windows/Fonts/malgun.ttf'))
    font('Bold',Path('C:/Windows/Fonts/malgunbd.ttf'))
    pdfmetrics.registerFontFamily('Body',normal='Body',bold='Bold')
    OUTPUT.parent.mkdir(parents=True,exist_ok=True)
    c = canvas.Canvas(str(OUTPUT),pagesize=A4,pageCompression=1)
    c.setTitle('Industrial Systems Portfolio - Six Projects - 2026-10-05')
    c.setAuthor('')
    c.setSubject('Verified local industrial software portfolio; scope and limitations included')

    def text(value,x,y,size=10,color=INK,bold=False):
        c.setFillColor(color);c.setFont('Bold' if bold else 'Body',size)
        c.drawString(x,y,value)

    def para(value,x,top,width,size=10,color=INK,bold=False,leading=None,min_bottom=64):
        style=ParagraphStyle('local',fontName='Bold' if bold else 'Body',fontSize=size,
                             leading=leading or size*1.6,textColor=color,wordWrap='CJK')
        p=Paragraph(escape(value).replace('\n','<br/>'),style)
        _,height=p.wrap(width,H)
        if top-height < min_bottom:
            raise ValueError('Text would overflow page: '+value[:50])
        p.drawOn(c,x,top-height)
        return top-height

    def box(x,y,w,h,color=PAPER):
        c.setFillColor(color);c.setStrokeColor(LINE)
        c.roundRect(x,y,w,h,10,fill=1,stroke=1)

    def frame(number,label):
        c.setFillColor(white);c.rect(0,0,W,H,fill=1,stroke=0)
        text('INDUSTRIAL SYSTEMS / PORTFOLIO',38,H-35,8,TEAL,True)
        text(label,38,H-61,9,MUTED)
        c.setStrokeColor(LINE);c.line(38,54,W-38,54)
        text('2026.10.05 · LOCAL VERIFICATION',38,36,7,MUTED)
        text(f'{number:02d} / 10',W-83,36,8,MUTED)

    # 01: cover
    c.setFillColor(INK);c.rect(0,0,W,H,fill=1,stroke=0)
    text('INDUSTRIAL SOFTWARE / SIX PROJECTS',42,783,10,HexColor('#ddedb6'),True)
    text('현장 데이터에서',42,701,38,white,True)
    text('근거 있는 판단까지.',42,646,38,white,True)
    para('PLC · IIoT Gateway · OEEAnalyzer\nTwinForge · DataNexus · Industrial Assistant',43,598,W-86,13,HexColor('#d5ddd6'),leading=22)
    para('역할의 경계, 구현한 작업 공간, 확인된 동작을 담은\n개인 산업 소프트웨어 포트폴리오',43,516,W-86,12,HexColor('#a9b9b0'))
    for i,(value,label) in enumerate([('06','독립 프로젝트'),('30','HTTP / WebSocket PASS'),('25','MySQL 인증 PASS')]):
        x=43+i*172
        c.setFillColor(HexColor('#23342d'));c.roundRect(x,330,160,107,10,fill=1,stroke=0)
        text(value,x+16,390,31,HexColor('#ddedb6'),True)
        para(label,x+16,368,133,8,white)
    para('실장비·전체 6개 출처 데이터 통합·외부 AI 품질은 이번 검증 범위에 포함하지 않습니다. 데모, 미수신, Fake/Mock 화면을 구분해 제시합니다.',43,264,W-86,10,HexColor('#b7c7bf'))
    text('VERIFIED 2026.10.05',43,86,11,white,True)
    text('github.com/dubukimch',43,61,9,HexColor('#a9b9b0'))
    c.linkURL('https://github.com/dubukimch',(42,52,245,76),relative=0)
    c.showPage()

    # 02: ownership and proposed paths
    frame(2,'SYSTEM ARCHITECTURE')
    text('여섯 제품, 분명한 소유권',38,735,24,INK,True)
    para('아래 연결은 설계된 경로입니다. 전체 통합 실행 성공을 의미하지 않습니다.',38,710,W-76,10,MUTED)
    for i,p in enumerate(PROJECTS):
        col,row=i%3,i//3;x=38+col*178;y=500-row*147
        box(x,y,163,130)
        text(f'0{i+1} / {p["category"].split(" / ")[0]}',x+13,y+108,8,TEAL,True)
        para(p['label'],x+13,y+93,137,12,bold=True)
        role=p['role'].replace('기간 A/P/Q/OEE·coverage·revision 계산','기간 A/P/Q/OEE 계산\ncoverage · revision')
        para(role,x+13,y+53,137,9,MUTED)
    para('계측: PLC → Gateway → OEEAnalyzer\n생산 맥락: TwinForge → OEEAnalyzer\n조회·설명: OEE 권위 결과 → TwinForge / DataNexus / Assistant',38,316,W-76,11,TEAL,bold=True,leading=22)
    para('설계 원칙',38,224,W-76,13,bold=True)
    para('원본 상태와 계산 결과의 책임을 나누고 OEE 재계산을 중복하지 않습니다. 데이터가 없으면 0이나 임의 값 대신 결측·미수신 상태를 보여줍니다. 조회 adapter와 제어 경계를 분리하고 출처·품질·원본 시각을 보존하는 방향으로 발전시킵니다.',38,194,W-76,10,MUTED)
    para('다음 계약 검증',38,126,W-76,11,bold=True)
    para('schemaVersion, 원본 시각, quality, 중복·지연·결측에 대한 6개 출처의 실제 읽기 경로를 후속 fixture로 검증합니다.',38,102,W-76,9,MUTED)
    c.showPage()

    # 03-08: product case studies
    for number,p in enumerate(PROJECTS,3):
        frame(number,p['category'])
        text(p['label'],38,735,24,INK,True)
        para(p['headline'],38,713,W-76,11,MUTED)
        path=ROOT/'assets/images/current-2026-10-05'/f'{p["id"]}.jpg'
        with Image.open(path) as image:
            iw,ih=image.size
        scale=min(310/iw,340/ih);dw,dh=iw*scale,ih*scale
        box(38,337,310,350,HexColor('#e9eddf'))
        c.drawImage(str(path),38+(310-dw)/2,342+(340-dh)/2,dw,dh)
        top=683
        for heading,body in [('소유하는 역할',p['role']),('해결하려는 과제',p['problem']),('구현과 설계',p['solution'])]:
            top=para(heading,367,top,190,10,TEAL,True)-8
            top=para(body,367,top,190,9,MUTED,leading=14)-15
        para('주요 기술\n'+p['stack'],367,top,190,8,MUTED,leading=13)
        para(p['caption'],38,323,W-76,8,MUTED,leading=12)
        para('구현: '+' · '.join(p['features']),38,282,W-76,8.7,MUTED,leading=13)
        para('확인된 동작',38,236,W-76,12,TEAL,True)
        para(p['verified'],38,214,W-76,10,leading=15)
        para('다음 개선',38,146,W-76,11,bold=True)
        para(p['improvement'],38,125,W-76,9,MUTED,leading=14)
        c.linkURL('https://github.com/dubukimch/'+p['name'],(38,724,W-38,759),relative=0)
        c.showPage()

    # 09: verification evidence
    frame(9,'VERIFICATION / 2026.10.05')
    text('동작 검사는 범위와 함께',38,735,24,INK,True)
    top=700
    for title,result,body in [
        ('Docker HTTP / WebSocket','30 PASS','6개 저장소 / 8개 서비스. 웹 응답, health, BlazorPack 호출 바인딩, OEE 401/400/503와 CORS, Assistant Fake/Mock·CSP·키·세션·길이 경계.'),
        ('실제 MySQL 인증','25 PASS','기본 Bootstrap 비활성, 명시적 관리자, Admin/Viewer, 잘못된 암호·토큰·비활성·손상 해시 거부, 기존 계정/해시 보존, 생성한 볼륨·컨테이너 정리.'),
        ('OEE .NET 회귀','35 PASS','기존 보안 초기화와 회귀 검사를 재실행. 손상된 저장 해시의 500 오류를 수정하고 정상 기존 해시 및 Unicode 암호를 보존.'),
        ('TwinForge .NET / OPC UA','45 PASS','실제 두 로컬 OPC UA 서버를 포함한 namespace·quality·재연결 fixture. MIT 버전 전환 후 API 호환성과 2048비트 최소 인증서 키 조건 검증.')]:
        box(38,top-111,W-76,111)
        text(title,52,top-24,12,INK,True)
        text(result,W-126,top-24,10,TEAL,True)
        para(body,52,top-44,W-104,9,MUTED,leading=14)
        top-=129
    para('브라우저 확인',38,180,W-76,12,TEAL,True)
    para('PLC 가상 RUN/X0 입력/모터 ON, DataNexus CSV 4행/SVG/그리드 추가, Gateway 채널 폼, OEE 로그인 UI, Twin 3D 미리보기·미수신·제어 비활성, Assistant 조회 전용·빈 키 보호를 확인했습니다.',38,158,W-76,9,MUTED,leading=14)
    para('전체 서비스의 정상 데이터 연동·실장비·외부 LLM 성능·운영 배포 준비를 판정한 검사가 아닙니다.',38,92,W-76,9,TEAL,True,leading=14)
    c.showPage()

    # 10: cost/license/remaining work
    frame(10,'DELIVERY / BOUNDARIES')
    text('완성도는 근거와 남은 일로',38,735,24,INK,True)
    top=697
    for heading,body in [
        ('무료 실행과 재료','새 유료 서비스, 외부 LLM API, 모델 다운로드, 클라우드 자원, npm/NuGet 의존성을 추가하지 않았습니다. 정적 사이트·도식은 자체 작성하고 현재 로컬 UI를 직접 캡처했습니다.'),
        ('라이선스 확인과 한계','Gateway/Twin의 구형 OPC UA를 실제 원문이 MIT인 1.5.378.145로 전환했습니다. 전체 메타데이터 1195행 중 원문 검토 대상 197행은 남아 있으며 SNI.runtime의 독자 조건, native 구성 요소·자산·NOTICE는 별도 검토가 필요합니다. 이 PDF는 앱 바이너리/컨테이너 배포 승인을 선언하지 않습니다.'),
        ('PDF 글꼴과 제작 도구','기존 ReportLab/Pillow/pypdf를 사용했습니다. Windows 맑은 고딕 두 파일의 OS/2 fsType=8(editable embedding)을 확인한 뒤 문서에 부분 임베딩했습니다. 글꼴 파일을 웹이나 저장소에 복사하지 않았습니다.'),
        ('다음 개발 우선순위','6개 출처 읽기 통합과 원본 시각·품질·중복·지연·결측, Gateway 비명령 노드 Write 거부, Twin UUID/TTL/ACK 감사, 정상 시계열 DB, Data 대용량·동시 import, Assistant provenance를 확대 검증합니다.'),
        ('공개와 제출 상태','현재 PDF와 정적 사이트는 로컬에서 검증합니다. GitHub 원격 업로드는 기존 저장소 인증·권한 확보가 필요하며 게시 완료로 표시하지 않습니다. 화면과 문서에는 사용자 계정 비밀값·AI 키·운영 데이터가 없습니다.')]:
        top=para(heading,38,top,W-76,12,TEAL,True)-8
        top=para(body,38,top,W-76,9.5,MUTED,leading=15)-21
    links=[('OPC Foundation MIT','https://opcfoundation.org/license/mit.html'),
           ('MySQL Community','https://www.mysql.com/products/community/'),
           ('Windows font embedding','https://learn.microsoft.com/en-us/typography/fonts/font-faq')]
    top=para('공식 사용 조건 / 클릭 가능한 근거',38,top,W-76,10,bold=True)-8
    for label,url in links:
        text(label+' ↗',38,top-10,8,TEAL)
        c.linkURL(url,(38,top-15,340,top+3),relative=0)
        top-=20
    c.showPage();c.save()
    reader=PdfReader(OUTPUT)
    assert len(reader.pages)==10
    text_all='\n'.join(p.extract_text() or '' for p in reader.pages)
    for p in PROJECTS:
        assert p['label'] in text_all
    assert '\ufffd' not in text_all
    site_pdf=ROOT/'assets/docs/industrial-platform-portfolio-2026-10-05.pdf'
    site_pdf.parent.mkdir(parents=True,exist_ok=True)
    shutil.copyfile(OUTPUT,site_pdf)
    print(f'Created 10 pages / {OUTPUT.stat().st_size:,} bytes; identical site copy. Render all pages before delivery.')


if __name__=='__main__':
    main()
