"""Create the current 11-page landscape portfolio from owned local captures.
Uses bundled ReportLab/Pillow/pypdf and embedded OS fonts. No network calls.
"""
import json
import shutil
import struct
from html import escape
from pathlib import Path

from PIL import Image
from pypdf import PdfReader
from reportlab.lib.colors import HexColor, white
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph

ROOT=Path(__file__).resolve().parents[1]
DATA=json.loads((ROOT/'content/projects.json').read_text(encoding='utf-8'))
PROJECTS=DATA['projects']
DATE=DATA['date']
DISPLAY_DATE=DATE.replace('-','.')
OUTPUT=ROOT.parent/f'포트폴리오/산업_소프트웨어_포트폴리오_{DATE}.pdf'
SITE_PDF=ROOT/f'assets/docs/industrial-platform-portfolio-{DATE}.pdf'
SHOTS=ROOT/f'assets/screenshots/{DATE}'
W,H=landscape(A4)
INK,TEAL,PAPER,MUTED,LINE=[HexColor(v) for v in ['#152338','#096c69','#f6f8fa','#627184','#dce3e9']]
PAGE_COUNT=len(PROJECTS)+4


def font(name,path):
    data=path.read_bytes();flags=None
    for i in range(struct.unpack_from('>H',data,4)[0]):
        tag,_,offset,_=struct.unpack_from('>4sIII',data,12+i*16)
        if tag==b'OS/2':flags=struct.unpack_from('>H',data,offset+8)[0]
    if flags not in (0,8):raise ValueError(f'Embedding permission requires review: {path.name}: {flags}')
    pdfmetrics.registerFont(TTFont(name,str(path)))


def main():
    for p in PROJECTS:
        if not (SHOTS/f'{p["id"]}.jpg').is_file():
            raise FileNotFoundError(f'Fresh local capture required: {SHOTS/p["id"]}.jpg')
    font('Body',Path('C:/Windows/Fonts/malgun.ttf'))
    font('Bold',Path('C:/Windows/Fonts/malgunbd.ttf'))
    pdfmetrics.registerFontFamily('Body',normal='Body',bold='Bold')
    staging=ROOT/'.local-preview';staging.mkdir(exist_ok=True)
    temporary=staging/'current-portfolio.pdf'
    c=canvas.Canvas(str(temporary),pagesize=(W,H),pageCompression=1)
    c.setTitle(f'Industrial Systems Portfolio - Seven Projects - {DATE}')
    c.setAuthor('')
    c.setSubject('Local industrial software workspaces, ownership and evidence')

    def text(value,x,y,size=10,color=INK,bold=False):
        c.setFillColor(color);c.setFont('Bold' if bold else 'Body',size);c.drawString(x,y,value)

    def para(value,x,top,width,size=9,color=MUTED,bold=False,leading=None,min_bottom=51):
        style=ParagraphStyle('local',fontName='Bold' if bold else 'Body',fontSize=size,leading=leading or size*1.6,textColor=color,wordWrap='CJK')
        p=Paragraph(escape(value).replace('\n','<br/>'),style);_,height=p.wrap(width,H)
        if top-height<min_bottom:raise ValueError('Text overflow: '+value[:70])
        p.drawOn(c,x,top-height);return top-height

    def box(x,y,width,height,color=PAPER,radius=8):
        c.setFillColor(color);c.setStrokeColor(LINE);c.roundRect(x,y,width,height,radius,stroke=1,fill=1)

    def frame(number,label):
        c.setFillColor(white);c.rect(0,0,W,H,fill=1,stroke=0)
        text('INDUSTRIAL SYSTEMS / PORTFOLIO',43,H-30,7,TEAL,True)
        text(label,43,H-48,8,MUTED)
        c.setStrokeColor(LINE);c.line(43,37,W-43,37)
        text(f'{DISPLAY_DATE} / LOCAL WORKSPACES & EVIDENCE',43,23,6.5,MUTED)
        text(f'{number:02d} / {PAGE_COUNT:02d}',W-85,23,7,MUTED)

    # Cover.
    c.setFillColor(INK);c.rect(0,0,W,H,fill=1,stroke=0)
    text('INDEPENDENT ENGINEERING / 2026',45,H-43,9,HexColor('#9ed3c8'),True)
    text('현장과 데이터를,',44,445,37,white,True)
    text('하나의 흐름으로.',44,389,37,white,True)
    para('신호를 만들고, 연결하고, 해석하는\n일곱 개의 산업 소프트웨어 포트폴리오',47,343,425,13,HexColor('#bfd0da'),leading=22)
    text('07',W-218,391,89,HexColor('#9ed3c8'),True)
    text('CONNECTED WORKSPACES',W-218,366,8,HexColor('#bfd0da'),True)
    c.setStrokeColor(HexColor('#3b4b5f'));c.line(46,252,W-46,252)
    names=['PLC Simulation · IIoT Gateway','TwinForge · OEEAnalyzer','DataNexus · Industrial Assistant','Industrial AssetHub']
    for i,name in enumerate(names):text(name,47,222-i*24,10,HexColor('#d4dfe5'))
    para('직접 캡처한 로컬 화면, 제품별 책임과 설계 판단,\n확인한 읽기 경로와 아직 남아 있는 구현 범위를 담았습니다.',W-350,228,302,10,HexColor('#a9becb'),leading=18)
    text(DISPLAY_DATE,47,57,11,white,True)
    text('github.com/dubukimch',W-207,57,8,HexColor('#bfd0da'))
    c.linkURL('https://github.com/dubukimch',(W-210,48,W-45,72),relative=0)
    c.showPage()

    # Architecture. The seven boxes express ownership, not live service status.
    frame(2,'ARCHITECTURE / OWNERSHIP')
    text('서로 다른 역할, 연결되는 작업 경험',43,510,26,INK,True)
    para('기존 여섯 제품의 실행 책임에 공통 자산 식별·의미 작업 공간을 더했습니다.',44,489,W-88,10)
    for i,p in enumerate(PROJECTS):
        col,row=i%4,i//4;x=43+col*192;y=296-row*133
        box(x,y,180,116)
        text(p['category'].split(' / ')[0]+' / '+p['group'].upper(),x+13,y+94,7,TEAL,True)
        para(p['label'],x+13,y+79,153,12,INK,True,leading=18)
        para(p['role'],x+13,y+43,153,8,MUTED,leading=13)
    para('원본과 계산의 경계\nPLC → Gateway → Twin 읽기는 확인했습니다. OEE sample/context와 Kafka를 포함한 전체 생산 흐름은 추가 검증이 필요합니다.',624,274,174,8.5,MUTED,leading=14)
    para('AssetHub는 로컬 자산·개념·소스 매핑 초안입니다. 기존 실행 경로의 필수 의존성이 아니며 승인 API·운영 원장·표준 AAS runtime은 미완료입니다.',44,132,W-88,9,TEAL,leading=15)
    para('값과 함께 quality, 원본·수신 시각과 명시적 binding을 보존합니다. 미수신 값을 임의 수치로 대체하지 않습니다.',44,87,W-88,8.5,MUTED)
    c.showPage()

    # Product pages. Images retain their full native aspect ratio.
    for number,p in enumerate(PROJECTS,3):
        frame(number,p['category'])
        text(p['label'],43,509,25,INK,True)
        para(p['headline'],44,488,W-88,10,MUTED)
        path=SHOTS/f'{p["id"]}.jpg'
        with Image.open(path) as image:iw,ih=image.size
        x,y,bw,bh=43,153,468,314
        box(x,y,bw,bh,HexColor('#edf2f6'))
        scale=min((bw-8)/iw,(bh-8)/ih);dw,dh=iw*scale,ih*scale
        c.drawImage(str(path),x+(bw-dw)/2,y+(bh-dh)/2,dw,dh,mask='auto')
        para(p['caption'],44,141,466,7.4,MUTED,leading=11,min_bottom=100)
        top=465
        copy_x=536
        copy_width=W-copy_x-60
        assert copy_x+copy_width<=W-60
        for heading,body in [('소유하는 역할',p['role']),('문제와 구현',p['problem']+' '+p['solution']),('확인된 근거',p['verified'])]:
            top=para(heading,copy_x,top,copy_width,9,TEAL,True,leading=13)-6
            top=para(body,copy_x,top,copy_width,8.5,MUTED,leading=13.3,min_bottom=102)-15
        para('다음 개선 / '+p['improvement'],44,85,W-88,8,MUTED,leading=12)
        c.linkURL('https://github.com/dubukimch/'+p['name'],(43,499,510,530),relative=0)
        c.showPage()

    # Evidence, explicitly dated.
    frame(PAGE_COUNT-1,'EVIDENCE / REPRODUCIBLE SCOPE')
    text('확인한 경로를, 날짜와 함께',43,510,26,INK,True)
    para('과거 fixture의 통과 수와 현재 UI 캡처는 서로 다른 근거입니다.',44,488,W-88,10)
    items=[
        ('2026.10.09','READ PATH / 29 PASS','PLC → Gateway Modbus → Twin OPC UA','격리 Docker fixture에서 실제 시뮬레이터 값, Good 품질과 원본·수신 시각을 확인했습니다. PLC 중단 시 Bad 품질 전이도 확인했습니다.'),
        (DISPLAY_DATE,'CURRENT REGRESSION','AssetHub 75 · Assistant 52 · smoke','AssetHub 기반·Host 75개와 Assistant C# 52개, 결정적 채팅 smoke를 확인했습니다. PLC/Twin HTTP 소스 설정과 다른 네 출처의 Mock, Fake 생성 방식을 구분합니다.'),
        ('2026.10.05','REGRESSION / DATED','MySQL 25 · OEE 35 · Twin 45','실제 MySQL 인증과 권한, OEE .NET, Twin의 두 로컬 OPC UA 서버를 포함한 회귀입니다. 각각의 fixture이며 통과 수를 전체 운영 통합으로 확대하지 않습니다.'),
        (DISPLAY_DATE,'LOCAL UI / 7 PRODUCTS','현재 작업 공간과 공통 식별','일곱 로컬 UI 화면과 제품별 설명을 최신화했습니다. AssetHub는 자산·의미·관계의 로컬 초안이며 운영 승인과 표준 적합성은 미완료입니다.')]
    for i,(date,label,title,body) in enumerate(items):
        top=451-i*84
        c.setStrokeColor(LINE);c.line(43,top+2,W-43,top+2)
        text(date,44,top-18,8,MUTED)
        text(label,44,top-35,6.5,TEAL,True)
        text(title,205,top-19,12,INK,True)
        para(body,205,top-32,W-250,8.5,MUTED,leading=13)
    para(DATA['scope'],44,91,W-88,8,TEAL,leading=13)
    c.showPage()

    # Delivery and next work.
    frame(PAGE_COUNT,'DELIVERY / NEXT ITERATION')
    text('구현한 것과, 다음에 연결할 것',43,510,26,INK,True)
    columns=[
        ('데이터 경로','정상 OEE sample/context와 Timescale/Redis 경로, DataNexus Kafka, 지연·중복·결측 회귀를 확대합니다. 연결 상태와 실제 관측값을 분리하는 원칙을 유지합니다.'),
        ('자산과 의미','AssetHub의 운영 인증·승인 API·원장, 승인된 knowledge release와 소스 매핑 소비 계약을 단계적으로 구현합니다. 로컬 검토를 운영 승인으로 표현하지 않습니다.'),
        ('조회와 운영','명시적 논리 자산 매핑, provenance·staleness, 상류 권한 오류와 일시적 장애의 재시도 정책을 검증합니다. 읽기 경계와 제어 책임을 보존합니다.'),
        ('화면과 접근성','일곱 제품의 작업 구조를 명확하게 다듬고 검색·필터·상태 안내·반응형 화면을 개선합니다. 포트폴리오는 역할 필터와 검색, 키보드 갤러리와 원본 비율 확대를 제공합니다.')]
    for i,(heading,body) in enumerate(columns):
        col,row=i%2,i//2;x=43+col*389;top=459-row*139
        box(x,top-120,367,120)
        text(heading,x+17,top-25,13,TEAL,True)
        para(body,x+17,top-42,333,9,MUTED,leading=15)
    para('제작과 실행',44,171,W-88,11,INK,True)
    para('자체 HTML/CSS/JavaScript와 직접 캡처한 로컬 UI, 기존 ReportLab/Pillow/pypdf를 사용했습니다. 외부 AI API·새 유료 서비스·외부 폰트·새 의존성을 추가하지 않았습니다. 맑은 고딕의 임베딩 허용 플래그를 확인해 문서에 부분 임베딩하며 글꼴 파일 자체는 배포하지 않습니다.',44,151,W-88,8.5,MUTED,leading=14)
    para('운영 인증·표준 적합성·의존성 및 native 자산의 배포 조건은 별도 검토 대상입니다. 이 포트폴리오는 로컬 결과이며 GitHub 원격 게시나 제품 운영 배포 승인을 의미하지 않습니다.',44,92,W-88,8,MUTED,leading=13)
    c.showPage();c.save()
    reader=PdfReader(temporary)
    assert len(reader.pages)==PAGE_COUNT
    text_all='\n'.join(p.extract_text() or '' for p in reader.pages)
    for p in PROJECTS:assert p['label'] in text_all
    assert '\ufffd' not in text_all
    OUTPUT.parent.mkdir(exist_ok=True);SITE_PDF.parent.mkdir(parents=True,exist_ok=True)
    shutil.copyfile(temporary,OUTPUT);shutil.copyfile(temporary,SITE_PDF)
    mirror_pdf=ROOT.parent/'포트폴리오'/f'assets/docs/industrial-platform-portfolio-{DATE}.pdf'
    mirror_pdf.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(temporary,mirror_pdf)
    print(f'Created {PAGE_COUNT} landscape pages / {OUTPUT.stat().st_size:,} bytes; identical portfolio/site copies. Render before delivery.')


if __name__=='__main__':main()
