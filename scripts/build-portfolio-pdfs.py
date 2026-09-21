"""Build anonymous, screenshot-led recruiting PDFs from maintained site sources.

Requires reportlab and pypdf; uses Windows Malgun Gothic, or PDF_FONT_DIR.
Uses existing product screenshots; no personal contact details or author metadata.
"""
from pathlib import Path
from html.parser import HTMLParser
from xml.sax.saxutils import escape
import os
from reportlab.pdfgen import canvas
from reportlab import rl_config
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, Image
from PIL import Image as PILImage
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.colors import HexColor, white
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.pagesizes import A4
from pypdf import PdfReader

ROOT = Path(__file__).resolve().parents[1]
rl_config.useA85 = 0
OUT = ROOT / 'assets/docs'
FONT = Path(os.environ.get('PDF_FONT_DIR', 'C:/Windows/Fonts'))
pdfmetrics.registerFont(TTFont('Body', str(FONT / 'malgun.ttf')))
pdfmetrics.registerFont(TTFont('Bold', str(FONT / 'malgunbd.ttf')))
pdfmetrics.registerFontFamily('Body', normal='Body', bold='Bold')
NAVY, TEAL = HexColor('#152c43'), HexColor('#007b83')
ST = {k: ParagraphStyle(k, fontName=f, fontSize=s, leading=l, textColor=NAVY, spaceAfter=a, wordWrap='CJK') for k,f,s,l,a in [
    ('title','Bold',25,33,12), ('sub','Body',11,17,13), ('h','Bold',11,16,7),
    ('body','Body',10,15.5,8), ('small','Body',8.8,13,5), ('label','Bold',8,12,8)]}

class Node:
    def __init__(self, tag='', attrs=()): self.tag, self.attrs, self.children = tag, dict(attrs), []
    def text(self): return ' '.join(''.join(c if isinstance(c,str) else c.text() for c in self.children).split())
    def all(self, tag=None, cls=None):
        found=[]
        for c in self.children:
            if isinstance(c,Node):
                if (tag is None or c.tag==tag) and (cls is None or cls in c.attrs.get('class','').split()): found.append(c)
                found += c.all(tag,cls)
        return found
class Parser(HTMLParser):
    def __init__(self, path):
        super().__init__(); self.root=Node(); self.stack=[self.root]; self.feed(path.read_text(encoding='utf-8'))
    def handle_starttag(self, tag, attrs):
        n=Node(tag,attrs); self.stack[-1].children.append(n)
        if tag not in ['img','br','meta','link','input','hr','source']: self.stack.append(n)
    def handle_endtag(self, tag):
        for i in range(len(self.stack)-1,0,-1):
            if self.stack[i].tag==tag: self.stack=self.stack[:i]; break
    def handle_data(self, data): self.stack[-1].children.append(data)

TECH=Parser(ROOT/'technical.html').root
PROJECTS=[
 ('plc','PLC Simulation','plc-simulation.html','이기종 장비를 동일한 통신·운영 모델로 연결',
  '제조사마다 다른 주소·데이터 형식·접속 설정을 공통 드라이버 계약으로 묶고, 실제 장비 없이 상위 시스템의 수집과 제어 흐름을 재현하는 개발 기반을 구성했습니다.',
  '드라이버 추상화 · 프로토콜 변환 · 명령/피드백 분리 · 실시간 모니터링',
  'Start·Stop·Reset은 sequence와 Ack를 대조하고 SpeedSetpoint 1.8 m/s에 대한 PLC 소유 SpeedPV 추종을 확인하는 통합 시나리오로 검증합니다. 명령 레지스터 이외 FC6/FC16 쓰기를 거부하는 경계를 포함합니다.'),
 ('gateway','IIoT Gateway','iiot-gateway.html','현장 주소를 품질 정보가 있는 표준 데이터로 전환',
  '장비별 수집 로직을 상위 서비스에서 반복 구현하지 않도록 Channel·Device·Tag 설정과 공통 캐시를 중심으로 OPC UA, 알람, 이력을 연결했습니다.',
  '설정 모델 · Scan Rate 수집 · OPC UA 정보 모델 · 알람/이력 · 이중화',
  'Total·Reject·State·Epoch 네 생산 경로의 Good 품질과 Source Timestamp를 통합 경로에서 대조합니다. 읽기 실패를 Bad로 표시하고 cache miss를 0으로 저장하지 않아 결측과 정상값을 구분합니다.'),
 ('oee','OEEAnalyzer','oee-analyzer.html','생산 지표에 계산 근거와 신뢰도를 함께 제공',
  '누적 생산 카운터만으로 가동률을 단정하지 않고 설비 상태, 품질, 이벤트 시각과 MES 작업 맥락을 결합해 기간 A/P/Q/OEE를 계산하는 분석 경계를 구성했습니다.',
  '이벤트 계약 · Kafka 수집 · 기간 계산 · 멱등 맥락 저장 · 권한 분리',
  '동일 epoch·source·mapping의 Good 표본만 증가분 계산에 사용합니다. 부분 coverage, 지연 표본, 분모 부재와 비율 위반을 상태·사유·revision으로 드러내 결과를 추적할 수 있게 했습니다.'),
 ('twinforge','TwinForge','twinforge.html','MES 작업 맥락과 실시간 설비 상태를 운영 화면에 통합',
  '장비 시뮬레이션, OPC UA 외부 데이터, 작업지시와 3D 장면이 서로 다른 값을 표시하지 않도록 공통 장비 상태와 이벤트 전달 경로를 구성했습니다.',
  '장비 모델 · SignalR 상태 동기화 · MES 맥락 · External OEE · 3D 시각화',
  '작업지시 context와 실제 표본의 시작 경계를 맞춘 뒤 External OEE를 조회합니다. 자체 MES 지표와 외부 분석 결과를 구분하며, 외부 모드에서 내부 시뮬레이션이 수신 값을 덮어쓰지 않도록 처리했습니다.'),
 ('datanexus','DataNexus Analytics','datanexus-analytics.html','원본 표본과 분석 결과를 독립 경로에서 교차 관측',
  '통합 화면의 숫자만으로 연결 상태를 판단하지 않도록 Kafka 원본 표본과 OEEAnalyzer의 권위 있는 Window를 읽기 전용 경로로 결합했습니다.',
  '독립 consumer · 검증 후 commit · 데이터 계보 · DLQ · 읽기 전용 분석',
  '기존 기술 문서에 Release 빌드 경고·오류 0, 단위 테스트 14/14와 5자 통합 runner 통과가 기록되어 있습니다. 수용 기준은 Kafka/OEE API 연결, sample/window 존재, coverage 1.0과 rejected 0입니다.'),
]

SCREENS = {
 'plc': [('plc-04-live-tags.png','실시간 태그 모니터','명령 태그의 Write와 PLC 소유 피드백의 Read-only를 구분하고 값·품질·시각을 함께 표시합니다.'),('plc-03-driver-config.png','드라이버 구성','모델·프로파일·통신 옵션을 하나의 설정 흐름으로 묶어 이기종 장비 연결을 구성합니다.'),('plc-05-data-mapping.png','업무 의미 기반 매핑','프로토콜 주소를 별칭과 표준 경로로 변환하고 누락 매핑을 점검합니다.')],
 'gateway': [('gateway-03-tags.png','OPC UA 태그 구성','PLC 주소·데이터 형식·접근 권한을 표준 태그로 정의하고 생산 신호를 상위 서비스에 제공합니다.'),('gateway-02-device.png','디바이스 연결 설정','Channel 아래의 Device에 PLC 종류와 연결 옵션을 지정해 드라이버 실행 구성을 만듭니다.'),('gateway-04-alarm.png','알람 조건 구성','수집 태그에 임계값과 심각도를 연결해 실시간 값에서 운영 이벤트를 파생합니다.')],
 'oee': [('oee-01-integration-overview.png','연동 경로와 기간 OEE','Gateway 계측과 TwinForge 맥락이 분석 Window로 이어지는 경로, 상태와 coverage를 함께 보여줍니다.'),('oee-02-live-oee.png','기간 계산 원장','A/P/Q/OEE와 생산·불량 증가분, coverage, revision을 같은 행에서 대조합니다.'),('oee-04-data-sources.png','범용 데이터 소스 설정','OPC UA 연결과 태그 매핑을 관리하는 UI입니다. Docker External 4신호 binding과는 별도 설정 경로입니다.')],
 'twinforge': [('twin-04-3d-factory.png','3D Digital Twin','설비의 공간 배치와 상태를 같은 장비 모델에 연결해 운영자가 위치와 텔레메트리를 함께 확인합니다.'),('twin-01-mes-dashboard.png','MES 작업지시','작업지시별 진행률, 양품·불량·WIP와 스테이션 상태를 표시해 생산 맥락을 제공합니다.'),('twin-03-workflow.png','워크플로 실행 모델','노드 연결과 실행 상태를 시각화합니다. 이 화면의 Run은 브라우저 Store 기반 실행 시뮬레이션입니다.')],
 'datanexus': [('datanexus-01-integration.png','다섯 시스템 독립 관측','Kafka 생산 표본과 OEEAnalyzer 계산 결과를 읽기 전용 경로에서 모아 연결 상태와 품질을 대조합니다.'),('datanexus-03-oee-evidence.png','원천 OEE 결과 대조','OEEAnalyzer의 Window와 ledger를 확인하는 근거 화면입니다. DataNexus가 지표를 재계산한 화면이 아닙니다.'),('datanexus-02-twinforge-context.png','생산 맥락 대조','TwinForge의 External OEE와 작업 맥락을 확인하는 근거 화면입니다. 촬영 시점이 달라 다른 화면과 수치가 다를 수 있습니다.')],
}

def p(text, style='body'): return Paragraph(escape(text), ST[style])
def screenshot(item, height=287):
    filename,title,caption=item
    path=ROOT/'assets/images/industrial-portfolio'/filename
    with PILImage.open(path) as source: w,h=source.size
    scale=min(511/w,height/h)
    im=Image(str(path),width=w*scale,height=h*scale,hAlign='CENTER')
    return [KeepTogether([im,Spacer(1,5),p(title+' | '+caption,'small'),Spacer(1,7)])]
def section(title, text): return [p(title,'h'),p(text)]
def table(rows, widths):
    t=Table([[p(v,'small') for v in row] for row in rows],colWidths=widths,hAlign='LEFT')
    t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),HexColor('#e6f0f3')),('VALIGN',(0,0),(-1,-1),'TOP'),('LEFTPADDING',(0,0),(-1,-1),10),('RIGHTPADDING',(0,0),(-1,-1),10),('TOPPADDING',(0,0),(-1,-1),9),('BOTTOMPADDING',(0,0),(-1,-1),7),('LINEBELOW',(0,0),(-1,-1),.4,HexColor('#d9e3e8'))]))
    return t
def header(label, title, subtitle): return [p(label,'label'),p(title,'title'),p(subtitle,'sub')]
def page(c, doc):
    c.setStrokeColor(TEAL); c.setLineWidth(2); c.line(42,805,553,805)
    c.setFont('Body',7); c.setFillColor(NAVY)
    c.drawString(42,818,'INDUSTRIAL DATA PLATFORM / PROJECT PORTFOLIO')
    c.drawString(42,25,'프로젝트 구현 기록  |  공개 문서 기반  |  2026.09')
    c.drawRightString(553,25,f'{doc.page}')
class AnonymousCanvas(canvas.Canvas):
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs); self.setAuthor(''); self.setCreator('Portfolio PDF Builder')
def build(name, story, expected):
    doc=SimpleDocTemplate(str(OUT/name),pagesize=A4,rightMargin=42,leftMargin=42,topMargin=52,bottomMargin=43,title=name.removesuffix('.pdf'),author='')
    doc.build(story,onFirstPage=page,onLaterPages=page,canvasmaker=AnonymousCanvas)
    reader=PdfReader(OUT/name)
    if len(reader.pages)!=expected: raise RuntimeError(f'{name}: expected {expected}, got {len(reader.pages)} pages')
    print(name, 'pages=',len(reader.pages),'characters=',[len(x.extract_text()) for x in reader.pages])

def overview(technical=False):
    s=header('ENGINEERING PORTFOLIO / '+('TECHNICAL DETAILS' if technical else 'PROJECT EXPERIENCE'), ('산업 데이터 플랫폼 · 기술 문서' if technical else '산업 데이터 플랫폼 · 포트폴리오'), '현장 신호의 수집부터 생산 분석, MES·3D 운영과 독립 관측까지')
    s+=section('프로젝트 개요','다섯 프로젝트를 연결해 생산 명령과 실제 피드백, 원본 데이터의 품질, 작업 맥락과 계산 결과를 추적하는 산업 데이터 플랫폼을 구성했습니다. 단순 화면 소개보다 서비스 간 데이터 계약과 장애·품질 처리 기준을 중심으로 구현 내용을 정리했습니다.')
    s.append(table([['프로젝트 / 핵심 영역','구현 내용과 다음 단계 연결']]+[[x[1],x[3]] for x in PROJECTS],[143,368]))
    s.append(Spacer(1,14))
    s+=section('전체 연동 흐름','PLC 생산 신호 → Gateway OPC UA → OEEAnalyzer 기간 분석 → TwinForge 운영 화면. TwinForge의 작업지시 맥락은 OEEAnalyzer 계산 경계를 제공하며, DataNexus는 Kafka 표본과 OEE API 결과를 별도 경로로 읽습니다.')
    s+=section('핵심 엔지니어링 역량','① 프로토콜별 구현을 공통 계약으로 추상화  ② 품질·시각·출처를 포함한 데이터 모델 설계  ③ 실시간 UI와 서버 상태 동기화  ④ 명령 쓰기와 관측 권한 분리  ⑤ 통합 시나리오와 수용 기준을 통한 검증')
    s+=section('기술 구성','OPC UA · Modbus · MQTT · Kafka · MySQL · TimescaleDB · SignalR · React · Zustand · Three.js · Docker. 각 기술의 사용 위치와 처리 책임은 프로젝트별 설명에 연결했습니다.')
    s+=section('문서의 범위','현재 저장소의 프로젝트 설명과 기존 검증 기록을 기반으로 작성했습니다. 개인 식별정보, 연락처, 소속, 학력은 수록하지 않았습니다. 참여 기간·직책·기여율 및 상용 성과 수치는 확인 자료가 없어 기재하지 않았습니다. 검증 기록은 이번 문서 편집에서 재실행한 결과가 아닙니다.')
    return s

def main():
    feature=overview()
    technical=overview(True)
    for i,(key,name,file,tagline,problem,scope,evidence) in enumerate(PROJECTS,1):
        sec=next(x for x in TECH.all('section') if x.attrs.get('id')==key)
        articles=sec.all('div','doc-grid')[0].all('article')
        feature += [PageBreak()]+header(f'PROJECT {i:02d} / IMPLEMENTATION & VALUE',name,tagline)
        feature += screenshot(SCREENS[key][0])
        feature += section('해결 과제',problem)+section('구현 범위',scope)
        feature += section('핵심 설계', ' '.join(a.all('p')[0].text() for a in articles[:2]))
        feature += section('검증 근거와 구현 가치',evidence)
        boundaries={'plc':'통신 시뮬레이터와 Docker 연동을 통한 검증입니다. 모든 제조사 실장비의 호환성이나 현장 도입 실적을 의미하지 않습니다.', 'gateway':'일부 설정 화면은 인메모리 구성 모드에서 촬영한 기록입니다. 설정 UI의 표시와 실제 영속 저장·장애 전환의 검증 범위를 구분합니다.', 'oee':'범용 Data Sources 및 3태그 Logic Builder와 Docker External 4신호 binding은 별도 경로입니다. 데이터가 부족한 기간을 정상 OEE로 채우지 않습니다.', 'twinforge':'워크플로 Run은 브라우저 Store 기반 실행 시뮬레이션입니다. External OEE는 실제 API 결과이며, 3D 장면이나 워크플로 데모를 현장 자동화 운영 실적으로 표현하지 않습니다.', 'datanexus':'OEE를 재계산하거나 생산 제어에 참여하지 않습니다. 기존 테스트 수치는 당시 기록이며, 운영 규모나 장기 안정성을 보장하는 성능 수치로 사용하지 않습니다.'}
        feature += [PageBreak()]+header(f'PROJECT {i:02d} / SCREEN EVIDENCE',name+' · 상세 화면','설정과 실행 결과를 연결하는 실제 UI')
        feature += screenshot(SCREENS[key][1],225)+screenshot(SCREENS[key][2],225)
        feature += section('적용 범위와 해석',boundaries[key])
        feature += [p(f'상세 근거: {file} / technical.html#{key}','small')]
        technical += [PageBreak()]+header(f'PROJECT {i:02d} / TECHNICAL CONTRACT',name,tagline)
        technical += screenshot(SCREENS[key][0],280)
        technical += [table([['처리 단계','구현 방식과 동작']]+[[a.all('h3')[0].text(),a.all('p')[0].text()] for a in articles],[132,379])]
        technical += [PageBreak()]+header(f'PROJECT {i:02d} / DATA & FAILURE HANDLING',name+' · 처리 상세','데이터 계약과 오류 처리 기준')
        technical += screenshot(SCREENS[key][1],230)
        details=sec.all('div','doc-detail')[0]
        for n in details.children:
            if not isinstance(n,Node): continue
            if n.tag=='h3': technical.append(p(n.text(),'h'))
            elif n.tag=='p': technical.append(p(n.text()))
            elif n.tag=='ol':
                for j,li in enumerate(n.all('li'),1): technical.append(p(f'{j}. {li.text()}'))
        technical += section('구현 범위의 경계',boundaries[key])
    technical += [PageBreak()]+header('INTEGRATION / REVIEW CHECKLIST','통합 검증과 설계 판단','명령이 성공했다는 응답과 실제 상태가 바뀌었다는 근거를 분리합니다.')
    technical.append(table([['단계','확인 대상','판단 기준'],['제어','Command Type / Sequence / Ack','명령 sequence와 PLC Ack·feedback 대조'],['계측','Total / Reject / State / Epoch','네 노드 품질·시각·매핑 일치'],['맥락','작업지시 / 설비 / UTC 구간','동일 설비 키, 표본 경계와 context version'],['분석','A/P/Q/OEE / coverage / revision','결측·분모 부재·지연을 상태와 사유로 설명'],['소비','TwinForge / DataNexus','같은 Window 출처, 상태와 계산 근거 대조']],[62,184,265]))
    technical.append(Spacer(1,16))
    for h,t in [('장애 격리','PLC 드라이버 실패가 다른 폴링을 중단하지 않도록 하고, Gateway는 수집 실패를 Bad 품질로 전달합니다. DataNexus 장애가 생산 제어나 OEE 계산 경로를 중단하지 않도록 소비자를 분리했습니다.'),('데이터 신뢰성','캐시 누락을 0으로 저장하거나 부분 관측을 정상 OEE로 대체하지 않습니다. Source Timestamp, 품질, epoch, mapping version과 revision을 남겨 값이 만들어진 조건을 확인할 수 있도록 했습니다.'),('권한과 소유권','PLC 상태·생산 카운터는 PLC가 소유하고 외부에는 제한된 명령만 허용합니다. OEE API는 설비 claim과 기능별 scope를 검사하며 DataNexus는 조회 권한만 사용합니다.'),('검증 기록의 해석','기존 통합 기록은 Start·Stop·Reset, 1.8 m/s 설정값 추종, Good 생산 신호, context·coverage와 독립 소비 경로를 대상으로 합니다. 이번 작업은 문서 재구성으로, 서비스 빌드·단위 테스트·Docker 통합 검증을 새로 수행한 것은 아닙니다.'),('근거 문서','technical.html 및 PLC Simulation, IIoT Gateway, OEEAnalyzer, TwinForge, DataNexus의 개별 HTML 설명을 사용했습니다. 코드 단위의 추가 심사에서는 각 구현 저장소의 테스트와 통합 runner 실행 기록을 함께 확인할 수 있습니다.')]: technical+=section(h,t)
    build('industrial-products-feature-guide.pdf',feature,11)
    build('industrial-platform-technical-document.pdf',technical,12)
if __name__=='__main__': main()
