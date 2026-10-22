"""Import source geometry for the two ruler proposals; no footprints are drawn by hand.
Run with KiCad Python. Existing ICRS layout is preserved; proposal layouts are generated separately.
"""
import copy
import json
import math
from pathlib import Path
import shutil
import subprocess
import tempfile
import uuid
import xml.etree.ElementTree as ET
import pcbnew as p

R=Path(__file__).resolve().parent
LIB=Path('/Volumes/KiCad/KiCad/KiCad.app/Contents/SharedSupport/footprints')
pt=lambda x,y:p.VECTOR2I(p.FromMM(x),p.FromMM(y))
uid=lambda key:str(uuid.uuid5(uuid.NAMESPACE_URL,'lovelace-ruler-module/'+key))
boards=[]
owned_sources=[]
for name in ('template.kicad_pcb','native-components.json'):
 target=R/(name.replace('.kicad_pcb','-icrs.kicad_pcb').replace('.json','-icrs.json'))
 if not target.exists():shutil.copy2(R/name,target)
base=p.LoadBoard(str(R/'template-icrs.kicad_pcb'));boards.append(base)
old=json.loads((R/'native-components-icrs.json').read_text())
for c in old:c.setdefault('source',dict(name='ICRS PCB Ruler',url='https://github.com/ben5049/ICRS-PCB-Ruler',license='Apache-2.0'))
metadata=old[:];added=[];by_key={}

def preserve_repo(owner,folder,files):
 source=Path('/tmp')/folder;dest=R/'upstream'/owner;dest.mkdir(exist_ok=True)
 for filename in files:
  path=source/filename
  if path.exists():(dest/filename).parent.mkdir(parents=True,exist_ok=True);shutil.copy2(path,dest/filename)
 commit=subprocess.check_output(['git','-C',str(source),'rev-parse','HEAD'],text=True).strip()
 (dest/'ORIGIN.json').write_text(json.dumps(dict(url='https://github.com/'+owner.replace('__','/'),commit=commit),indent=2)+'\n')
 return dest,commit

trace_dir,trace_rev=preserve_repo('notaroomba__trace','ruler-reference-notaroomba',['README.md','hardware/trace.kicad_pcb'])
ada_dir,ada_rev=preserve_repo('adafruit__Adafruit-PCB-Ruler','ruler-reference-adafruit',['README.md','license.txt','Adafruit PCB Reference Ruler.brd'])
# Reviewed but not used (see SOURCES.md): headblockhead/ruler, Evidlo/uiuc_ruler, mprosk/ruler.
# Their files are not redistributed here.
trace=p.LoadBoard(str(trace_dir/'hardware/trace.kicad_pcb'));boards.append(trace)
trace_fps={str(f.GetFPID().GetLibItemName()):f for f in trace.GetFootprints()}


def official(library,name):
 source=LIB/(library+'.pretty')/(name+'.kicad_mod')
 if not source.exists():raise FileNotFoundError(source)
 dest=R/'upstream/official-kicad'/(library+'.pretty');dest.mkdir(parents=True,exist_ok=True);shutil.copy2(source,dest/source.name)
 fp=p.FootprintLoad(str(dest),name);owned_sources.append(fp)
 return fp,dict(name='KiCad official / '+library,url='https://gitlab.com/kicad/libraries/kicad-footprints/-/blob/master/'+library+'.pretty/'+name+'.kicad_mod',license='CC-BY-SA-4.0 + library exception',path=str((dest/source.name).relative_to(R)))


def source_trace(name):
 return trace_fps[name].Duplicate(False).Cast(),dict(name='notaroomba/trace',url='https://github.com/notaroomba/trace',license='MIT (upstream README)',revision=trace_rev,path='hardware/trace.kicad_pcb',originalUuid=trace_fps[name].m_Uuid.AsString())


def front_clone(fp):
 if fp.GetLayer()==p.B_Cu:fp.Flip(fp.GetPosition(),True)
 return fp


def register(key,name,fp,source,side='F',note='',outline=False):
 print('Register',key,flush=True)
 fp.SetParent(base)
 fp.SetUuid(p.KIID(uid(key)))
 fp.Reference().SetVisible(False);fp.Value().SetVisible(False)
 for pad in fp.Pads():pad.SetNetCode(0)
 if side=='B' and fp.GetLayer()!=p.B_Cu:fp.Flip(fp.GetPosition(),True)
 elif side=='F' and fp.GetLayer()!=p.F_Cu:fp.Flip(fp.GetPosition(),True)
 # Center the imported object while retaining all internal distances.
 box=fp.GetBoundingBox(False,False)
 center=p.VECTOR2I(box.GetX()+box.GetWidth()//2,box.GetY()+box.GetHeight()//2)
 fp.Move(pt(77.5,12.5)-center)
 pos=fp.GetPosition();box=fp.GetBoundingBox(False,False)
 c=dict(id=fp.m_Uuid.AsString(),name=name,x=p.ToMM(pos.x),y=p.ToMM(pos.y),rotation=0,side=side+'.SilkS',both=any(a.GetLayerSet().Contains(p.F_Mask) and a.GetLayerSet().Contains(p.B_Mask) for a in fp.Pads()),bounds=[p.ToMM(box.GetX()-pos.x),p.ToMM(box.GetY()-pos.y),p.ToMM(box.GetWidth()),p.ToMM(box.GetHeight())],texts=[],drills=[[p.ToMM(a.GetPosition().x-pos.x),p.ToMM(a.GetPosition().y-pos.y),p.ToMM(a.GetDrillSize().x)] for a in fp.Pads() if a.GetDrillSize().x>0],source=source,note=note)
 # Only visible silk text is exposed; no hidden reference/value fields.
 for g in fp.GraphicalItems():
  if isinstance(g,p.PCB_TEXT) and g.IsVisible() and g.GetLayer() in (p.F_SilkS,p.B_SilkS):
   c['texts'].append(dict(id=g.m_Uuid.AsString(),text=g.GetText(),x=p.ToMM(g.GetPosition().x-pos.x),y=p.ToMM(g.GetPosition().y-pos.y),size=p.ToMM(g.GetTextSize().y),rotation=-g.GetTextAngle().AsDegrees(),side='B' if g.GetLayer()==p.B_SilkS else 'F',mirror=g.IsMirrored(),align={-1:'start',0:'middle',1:'end'}[int(g.GetHorizJustify())],valign={-1:'hanging',0:'central',1:'text-after-edge'}[int(g.GetVertJustify())]))
 fp.SetReference('MOD_'+key.replace('-','_'));fp.SetValue(name)
 base.Add(fp);metadata.append(c);added.append(c);by_key[key]=c
 return c

# Connector geometry: copied from official library files, not approximated by pin pitch.
for key,label,lib,name in [
 ('jst-sh','JST SH · 1.00 mm · 4P','Connector_JST','JST_SH_SM04B-SRSS-TB_1x04-1MP_P1.00mm_Horizontal'),
 ('jst-gh','JST GH · 1.25 mm · 4P','Connector_JST','JST_GH_SM04B-GHS-TB_1x04-1MP_P1.25mm_Horizontal'),
 ('jst-ph2','JST PH · 2.00 mm · 2P','Connector_JST','JST_PH_B2B-PH-K_1x02_P2.00mm_Vertical'),
 ('jst-ph8','JST PH · 2.00 mm · 8P','Connector_JST','JST_PH_B8B-PH-K_1x08_P2.00mm_Vertical'),
 ('fpc05','FPC · 0.50 mm · 8P','Connector_FFC-FPC','Hirose_FH12-8S-0.5SH_1x08-1MP_P0.50mm_Horizontal'),
 ('fpc10','FPC · 1.00 mm · 8P','Connector_FFC-FPC','Molex_200528-0080_1x08-1MP_P1.00mm_Horizontal'),
 ('usbc','USB-C · HRO TYPE-C-31-M-12','Connector_USB','USB_C_Receptacle_HRO_TYPE-C-31-M-12'),
 ('qfn04','QFN · 0.40 mm','Package_DFN_QFN','QFN-24-1EP_3x3mm_P0.4mm_EP1.75x1.6mm'),
 ('ads1299','TQFP-64 · 0.50 mm · ADS1299','Package_QFP','TQFP-64_10x10mm_P0.5mm'),
 ('header127','Pin header · 1.27 mm','Connector_PinHeader_1.27mm','PinHeader_1x04_P1.27mm_Vertical'),
 ('header254','Pin header · 2.54 mm','Connector_PinHeader_2.54mm','PinHeader_1x04_P2.54mm_Vertical'),
]:
 fp,src=official(lib,name)
 register(key,label,fp,src,note='실물 크기·피치 참고용입니다. 커넥터끼리의 호환성이나 핀 배열을 보증하지 않습니다.' if key.startswith('jst') else '')
for key,name,label in [('tssop','TSSOP-8_4.4x3mm_P0.65mm','TSSOP · 0.65 mm'),('soic','SOIC-8_3.9x4.9mm_P1.27mm','SOIC · 1.27 mm')]:
 fp,src=source_trace(name);front_clone(fp);register(key,label,fp,src)
fp=next(f for f in base.GetFootprints() if str(f.GetFPID().GetLibItemName())=='SOT-23').Duplicate(False).Cast();front_clone(fp)
register('sot23','SOT-23 · 3P',fp,dict(name='ICRS PCB Ruler / SOT-23',url='https://github.com/ben5049/ICRS-PCB-Ruler',license='Apache-2.0'))
# Copy Adafruit's original Eagle SMD coordinates and straight outline segments for QFN-24.
xml=ET.parse(ada_dir/'Adafruit PCB Reference Ruler.brd').getroot()
package=next(q for q in xml.findall('.//packages/package') if q.get('name')=='QFN-24')
fp=p.FOOTPRINT(base)
for e in package.findall('smd'):
 a=p.PAD(fp);a.SetNumber(e.get('name'));a.SetAttribute(p.PAD_ATTRIB_SMD);a.SetShape(p.PAD_SHAPE_RECT);a.SetSize(pt(float(e.get('dx')),float(e.get('dy'))));a.SetPosition(pt(float(e.get('x')),-float(e.get('y'))));a.SetOrientationDegrees(float(e.get('rot','R0').lstrip('R')));layers=p.LSET();layers.AddLayer(p.F_Cu);layers.AddLayer(p.F_Mask);a.SetLayerSet(layers);fp.Add(a)
for e in package.findall('wire'):
 if e.get('layer')!='21':continue
 if float(e.get('curve','0')):raise ValueError('Unexpected Eagle arc in QFN module')
 g=p.PCB_SHAPE(fp);g.SetShape(p.SHAPE_T_SEGMENT);g.SetStart(pt(float(e.get('x1')),-float(e.get('y1'))));g.SetEnd(pt(float(e.get('x2')),-float(e.get('y2'))));g.SetWidth(p.FromMM(float(e.get('width'))));g.SetLayer(p.F_SilkS);fp.Add(g)
register('qfn05','QFN-24 · 0.50 mm',fp,dict(name='Adafruit PCB Ruler / QFN-24',url='https://github.com/adafruit/Adafruit-PCB-Ruler',license='CC-BY-SA-3.0',revision=ada_rev,path='Adafruit PCB Reference Ruler.brd',package='QFN-24'),note='Eagle 원본 패드 좌표·크기를 변환했습니다. ADS1299는 이 QFN이 아니라 별도의 TQFP-64 샘플입니다.')
# Source SMD examples on the back.
for size in ('0402','0603','0805'):
 name=next(n for n in trace_fps if n.startswith('R_'+size+'_'))
 fp,src=source_trace(name);front_clone(fp);register('r'+size,size,fp,src,side='B')
for key,lib,name in [('m2','MountingHole','MountingHole_2.2mm_M2_Pad'),('m25','MountingHole','MountingHole_2.7mm_M2.5_Pad'),('m3','MountingHole','MountingHole_3.2mm_M3_Pad'),('contact15','TestPoint','TestPoint_THTPad_D3.0mm_Drill1.5mm'),('drill05','TestPoint','TestPoint_THTPad_D1.0mm_Drill0.5mm'),('drill07','TestPoint','TestPoint_THTPad_D1.5mm_Drill0.7mm')]:
 fp,src=official(lib,name);register(key,dict(m2='M2 · Ø2.2',m25='M2.5 · Ø2.7',m3='M3 · Ø3.2',contact15='Ø1.5 mm · contact reference',drill05='Drill · Ø0.5',drill07='Drill · Ø0.7')[key],fp,src,side='B',note='1.5 mm는 접점 지름 참고입니다. touch-proof 커넥터의 패널 장착 홀 또는 스냅 호환성 게이지가 아닙니다.' if key=='contact15' else '')
# Pogo row is an assembly of copied official test pads, with the requested 2.54 mm spacing.
pad_fp,src=official('TestPoint','TestPoint_Pad_D1.0mm');fp=p.FOOTPRINT(base)
source_pad=next(iter(pad_fp.Pads()))
for i in range(5):
 a=source_pad.Duplicate().Cast();a.SetPosition(pt(i*2.54,0));a.SetNumber(str(i+1));fp.Add(a)
register('pogo','Pogo contacts · 2.54 mm · 5P',fp,src,side='B',note='공식 Ø1.0 mm SMD 테스트 패드를 복사하여 2.54 mm 간격으로 배치했습니다. 홀은 없습니다.')
# Spacing references pair copies of the official round pad; the circle diameter is unchanged.
fp=p.FOOTPRINT(base)
for i,gap in enumerate((.1,.15,.2)):
 for row in range(2):
  a=source_pad.Duplicate().Cast();a.SetPosition(pt(i*3,row*(1+gap)));a.SetNumber(str(i*2+row+1));fp.Add(a)
register('gaps','Pad gaps · 0.10 / 0.15 / 0.20 mm',fp,src,side='B',note='공식 Ø1.0 mm 패드를 쌍으로 복사해 가장 가까운 구리 가장자리 간격을 표시합니다. 평행 트레이스 간격 게이지가 아닙니다.')
# Preserve the exact trace project's drilled via as a native via object.
via=next(t for t in trace.GetTracks() if isinstance(t,p.PCB_VIA)).Duplicate().Cast();via.SetParent(base);via.SetUuid(p.KIID(uid('via02')));via.SetNetCode(0);via.SetPosition(pt(77.5,12.5));base.Add(via)
c=dict(id=uid('via02'),name='Via · drill 0.20 / copper 0.40 mm',x=77.5,y=12.5,rotation=0,side='B.SilkS',both=True,bounds=[-.2,-.2,.4,.4],texts=[],drills=[[0,0,.2]],source=dict(name='notaroomba/trace native via',url='https://github.com/notaroomba/trace',license='MIT (upstream README)',revision=trace_rev),note='Trace 원본의 실제 비아를 복사했습니다. 공칭 드릴 치수와 완성 홀 치수는 다를 수 있습니다.')
metadata.append(c);added.append(c);by_key['via02']=c
def clip_body_silk(fp):
 # Trim source outlines around their real copper lands; never change the lands themselves.
 boxes=[]
 for pad in fp.Pads():
  if not pad.GetLayerSet().Contains(p.F_Mask):continue
  b=pad.GetBoundingBox();margin=p.FromMM(.22)
  boxes.append((b.GetX()-margin,b.GetY()-margin,b.GetRight()+margin,b.GetBottom()+margin))
 def line(a,b,width):
  dx,dy=b[0]-a[0],b[1]-a[1];intervals=[(0.,1.)]
  for left,top,right,bottom in boxes:
   low,high=0.,1.
   for origin,delta,minimum,maximum in ((a[0],dx,left,right),(a[1],dy,top,bottom)):
    if delta==0:
     if not minimum<=origin<=maximum:low,high=1,0;break
    else:
     t1,t2=sorted(((minimum-origin)/delta,(maximum-origin)/delta));low=max(low,t1);high=min(high,t2)
   if low<=high:
    next_parts=[]
    for start,end in intervals:
     if high<=start or low>=end:next_parts.append((start,end))
     else:
      if start<low:next_parts.append((start,low))
      if high<end:next_parts.append((high,end))
    intervals=next_parts
  for start,end in intervals:
   if math.hypot(dx,dy)*(end-start)<p.FromMM(.08):continue
   shape=p.PCB_SHAPE(fp);shape.SetShape(p.SHAPE_T_SEGMENT);shape.SetLayer(p.F_SilkS);shape.SetWidth(width)
   shape.SetStart(p.VECTOR2I(round(a[0]+dx*start),round(a[1]+dy*start)));shape.SetEnd(p.VECTOR2I(round(a[0]+dx*end),round(a[1]+dy*end)));fp.Add(shape)
 for g in list(fp.GraphicalItems()):
  if not isinstance(g,p.PCB_SHAPE) or g.GetLayer()!=p.F_SilkS:continue
  kind=g.GetShape();start=g.GetStart();end=g.GetEnd();parts=[]
  if kind==p.SHAPE_T_SEGMENT:parts=[((start.x,start.y),(end.x,end.y))]
  elif kind==p.SHAPE_T_RECT:
   x,y,u,v=start.x,start.y,end.x,end.y;parts=[((x,y),(u,y)),((u,y),(u,v)),((u,v),(x,v)),((x,v),(x,y))]
  elif kind==p.SHAPE_T_ARC:
   center=g.GetCenter();start=g.GetStart();middle=g.GetArcMid();end=g.GetEnd();radius=math.hypot(start.x-center.x,start.y-center.y)
   angle=lambda q:math.atan2(q.y-center.y,q.x-center.x)
   first=angle(start);sweep=(angle(end)-first)%(2*math.pi)
   if (angle(middle)-first)%(2*math.pi)>sweep:sweep-=2*math.pi
   count=max(1,math.ceil(abs(sweep)*radius/p.FromMM(.12)))
   points=[(center.x+radius*math.cos(first+sweep*i/count),center.y+radius*math.sin(first+sweep*i/count)) for i in range(count+1)]
   parts=list(zip(points,points[1:]))
  else:continue
  g.SetLayer(p.Dwgs_User)
  for a,b in parts:line(a,b,g.GetWidth())

def pad_numbers(fp, maximum, inset, size):
 # Labels use the source pad numbers and sit just inside the two peripheral pad rows.
 box=fp.GetBoundingBox(False,False);cy=box.GetY()+box.GetHeight()/2
 for pad in fp.Pads():
  if not pad.GetNumber().isdigit() or not 1<=int(pad.GetNumber())<=maximum:continue
  at=pad.GetPosition();g=p.PCB_TEXT(fp);g.SetText(pad.GetNumber());g.SetLayer(p.F_SilkS)
  local_inset=1.9 if maximum==14 and pad.GetNumber() in ('3','4') else inset
  g.SetPosition(p.VECTOR2I(at.x,at.y+p.FromMM(local_inset if at.y<cy else -local_inset)))
  g.SetTextSize(pt(size,size));g.SetTextThickness(p.FromMM(.12));fp.Add(g)

# Full manufacturer's footprint: all 25 copper/mask lands, rounded outline and USB shell.
xiao_src=Path('/tmp/seeed-xiao-footprints/New_XIAO_Series_Footprints/XIAO-ESP32-S3-SMD.kicad_mod')
xiao_dest=R/'upstream/Seeed';xiao_dest.mkdir(exist_ok=True);shutil.copy2(xiao_src,xiao_dest/xiao_src.name)
fp=p.FootprintLoad(str(xiao_dest),xiao_src.stem);owned_sources.append(fp);fp.SetParent(base)
# User.2 is a 0.001mm assembly illustration, not printable silk. Keep it on its source layer.
for g in list(fp.GraphicalItems()):
 if isinstance(g,p.PCB_SHAPE) and g.GetLayer()==p.F_Fab and g.GetShape()==p.SHAPE_T_CIRCLE:
  clone=g.Duplicate().Cast();clone.SetLayer(p.F_SilkS);fp.Add(clone)
fp.Rotate(fp.GetPosition(),p.EDA_ANGLE(90,p.DEGREES_T))
clip_body_silk(fp)
pad_numbers(fp,14,2.3,.7)
register('xiao','XIAO ESP32S3 · 25 copper pads',fp,dict(name='Seeed official XIAO footprint',url='https://wiki.seeedstudio.com/xiao_esp32s3_getting_started/',license='Manufacturer source; upstream archive has no explicit license',path=str((xiao_dest/xiao_src.name).relative_to(R))),side='B',note='공식 25개 SMD 패드의 좌표·크기, 둥근 본체와 USB 돌출부를 보존했습니다. 21 × 17.8 mm는 본체 크기이며 패드와 USB가 이보다 바깥으로 나옵니다.')
# Copy only the official CR2032 20 mm body circle.
original,src=official('Battery','Battery_Panasonic_CR2032-HFN_Horizontal_CircularHoles');fp=p.FOOTPRINT(base)
for g in original.GraphicalItems():
 if isinstance(g,p.PCB_SHAPE) and g.GetShape()==p.SHAPE_T_CIRCLE and g.GetLayer()==p.F_Fab and abs(p.ToMM(g.GetRadius())-10)<.01:
  clone=g.Duplicate().Cast();clone.SetLayer(p.F_SilkS);fp.Add(clone)
register('cr2032','CR2032 · Ø20 body',fp,src,side='B')
# AS-008's actual module family is more useful than a coin cell for the recommended version.
wrover_path=R/'upstream/AS-008/ESP32-WROVER-E.kicad_mod'
wrover_dest=R/'upstream/AS-008';wrover_dest.mkdir(exist_ok=True);shutil.copy2(wrover_path,wrover_dest/wrover_path.name)
fp=p.FootprintLoad(str(wrover_dest),'ESP32-WROVER-E');owned_sources.append(fp);fp.SetParent(base)
src=dict(name='AS-008 existing footprint / Espressif dimensions',url='https://www.espressif.com/sites/default/files/documentation/esp32-wrover-e_esp32-wrover-ie_datasheet_en.pdf',license='Existing repository design',path='hardware/lovelace-as-008/lib/LOVELACE.pretty/ESP32-WROVER-E.kicad_mod')
for g in list(fp.GraphicalItems()):
 if isinstance(g,p.PCB_SHAPE) and g.GetLayer()==p.F_Fab:
  clone=g.Duplicate().Cast();clone.SetLayer(p.F_SilkS);fp.Add(clone)
fp.Rotate(fp.GetPosition(),p.EDA_ANGLE(90,p.DEGREES_T))
clip_body_silk(fp)
pad_numbers(fp,38,1.3,.65)
register('wrover','ESP32-WROVER-E · 39 copper lands',fp,src,side='B',note='기존 AS-008 풋프린트의 주변 38개 패드·중앙 접지 패드·4개 열 비아와 본체/안테나 구역을 복사했습니다. 안테나 keepout 배치 규칙을 대체하지 않습니다.')
# More compact comparison modules copied directly from Trace, matching the reference rulers' density.
for key,name,label,side in [
 ('sc70','SOT-323_SC-70','SC-70 / SOT-323','F'),
 ('sot235','SOT-23-5','SOT-23-5','F'),('sot236','SOT-23-6','SOT-23-6','F'),
 ('dfn6','DFN-6-1EP_2x2mm_P0.5mm_EP0.6x1.37mm','DFN-6 / .50','F'),
 ('dfn8','DFN-8-1EP_3x3mm_P0.5mm_EP1.66x2.38mm','DFN-8 / .50','F'),
 ('dfn10','DFN-10-1EP_3x3mm_P0.5mm_EP1.65x2.38mm','DFN-10 / .50','F'),
 ('qfn16','QFN-16-1EP_3x3mm_P0.5mm_EP1.7x1.7mm','QFN-16 / .50','F'),
 ('qfn20','QFN-20-1EP_3.5x3.5mm_P0.5mm_EP2x2mm','QFN-20 / .50','F'),
 ('tssop16','TSSOP-16_4.4x5mm_P0.65mm','TSSOP-16 / .65','F'),
 ('sod123','D_SOD-123','SOD-123','B'),('sod323','D_SOD-323','SOD-323','B'),
 ('npn','NPN-SYMB','NPN symbol','B'),('pnp','PNP-SYMB','PNP symbol','B'),
 ('nmos','NMOS-SYMB','NMOS symbol','B'),('pmos','PMOS-SYMB','PMOS symbol','B'),
 ('c0402','C_0402_1005Metric','C 0402','B'),('c0603','C_0603_1608Metric','C 0603','B'),('c0805','C_0805_2012Metric','C 0805','B'),
 ('l0402','L_0402_1005Metric','L 0402','B'),('l0603','L_0603_1608Metric','L 0603','B'),('l0805','L_0805_2012Metric','L 0805','B')]:
 fp,src=source_trace(name);front_clone(fp)
 if key in ('npn','pnp','nmos','pmos'):
  for g in fp.GraphicalItems():
   if isinstance(g,p.PCB_TEXT):g.SetTextAngle(p.EDA_ANGLE(0,p.DEGREES_T));g.SetTextSize(pt(.8,.8));g.SetTextThickness(p.FromMM(.12))
 register(key,label,fp,src,side=side)
# Four native ICRS copper width samples, with original mil labels; only row spacing changes.
original=next(f for f in base.GetFootprints() if str(f.GetFPID().GetLibItemName())=='trace_widths')
fp=p.FOOTPRINT(base)
for g in original.GraphicalItems():
 rel=p.ToMM(g.GetPosition().y-original.GetPosition().y)
 if isinstance(g,p.PCB_SHAPE) and g.GetLayer() in (p.F_Cu,p.F_Mask) and rel>8:
  row=round((rel-8.845)/2.045);clone=g.Duplicate().Cast();clone.Move(-original.GetPosition());clone.Move(pt(0,row*1.6-(9+row*2)));fp.Add(clone)
 elif isinstance(g,p.PCB_TEXT) and g.GetText() in ('12','10','8','6'):
  row=('12','10','8','6').index(g.GetText());clone=g.Duplicate().Cast();clone.Move(-original.GetPosition());clone.Move(pt(0,row*1.6-(9+row*2)));clone.SetTextSize(pt(.8,.8));clone.SetTextThickness(p.FromMM(.12));fp.Add(clone)
register('widths4','Trace widths · 12 / 10 / 8 / 6 mil',fp,dict(name='ICRS PCB Ruler / four native width samples',url='https://github.com/ben5049/ICRS-PCB-Ruler',license='Apache-2.0'),note='원본 구리 도형의 폭과 길이를 유지하고 네 행의 간격만 줄였습니다. 실제 폭은 .3048/.254/.2032/.1524 mm입니다.')
# Generic OSHW gear from the official library, not the OSHWA certification mark.
fp,src=official('Symbol','OSHW-Logo_5.7x6mm_SilkScreen');register('oshw','OSHW gear · generic',fp,src,side='B',note='OSHW 정의에 맞춰 설계 소스와 라이선스를 공개하는 프로젝트용 일반 로고입니다. OSHWA 인증 마크가 아닙니다.')
# Reuse the original inch scale on the back. Flip and rotate the source; never rescale it.
original=next(f for f in base.GetFootprints() if str(f.GetFPID().GetLibItemName())=='Gauge_6in')
fp=original.Duplicate(False).Cast();fp.Flip(fp.GetPosition(),False);fp.Rotate(fp.GetPosition(),p.EDA_ANGLE(180,p.DEGREES_T))
# Compact the tick HEIGHT only; x coordinates and the 25.4mm inch pitch stay unchanged.
anchor=fp.GetPosition().y
for g in fp.GraphicalItems():
 if isinstance(g,p.PCB_SHAPE) and g.GetShape()==p.SHAPE_T_SEGMENT:
  for getter,setter in ((g.GetStart,g.SetStart),(g.GetEnd,g.SetEnd)):
   point=getter();setter(p.VECTOR2I(point.x,round(anchor+(point.y-anchor)*.55)))
 elif isinstance(g,p.PCB_TEXT):
  point=g.GetPosition();g.SetPosition(p.VECTOR2I(point.x,round(anchor+(point.y-anchor)*.55)));g.SetTextSize(pt(.8,.8));g.SetTextThickness(p.FromMM(.12))
register('inch-back','Inches · 1/16 · back',fp,dict(name='ICRS PCB Ruler / Gauge_6in',url='https://github.com/ben5049/ICRS-PCB-Ruler',license='Apache-2.0'),side='B')
# Base includes copied source copper; functional NFC circuitry is intentionally not added.
p.SaveBoard(str(R/'template.kicad_pcb'),base)
(R/'native-components.json').write_text(json.dumps(metadata,ensure_ascii=False,indent=2)+'\n')
(R/'module-keys.json').write_text(json.dumps({k:v['id'] for k,v in by_key.items()},indent=2)+'\n')
# Isolate one source object at a time for faithful vector previews. Keep boards alive (KiCad SWIG ownership).
cli='/Volumes/KiCad/KiCad/KiCad.app/Contents/MacOS/kicad-cli';assets=R/'assets'
for index,c in enumerate(added):
 for side in ('F','B') if c['both'] else (c['side'][0],):
  isolated=p.LoadBoard(str(R/'template.kicad_pcb'));boards.append(isolated);selected=None
  for candidate in [*isolated.GetFootprints(),*isolated.GetDrawings(),*isolated.GetTracks()]:
   if candidate.m_Uuid.AsString()==c['id']:selected=candidate
   else:isolated.Delete(candidate)
  if isinstance(selected,p.FOOTPRINT):
   for graphic in selected.GraphicalItems():
    if isinstance(graphic,p.PCB_TEXT):graphic.SetLayer(p.Dwgs_User)
  with tempfile.TemporaryDirectory() as temp:
   pcb=Path(temp)/'item.kicad_pcb';svg=Path(temp)/'item.svg';p.SaveBoard(str(pcb),isolated)
   subprocess.run([cli,'pcb','export','svg','--layers',f'{side}.Mask,{side}.SilkS,Edge.Cuts','--mode-single','--page-size-mode','0','--exclude-drawing-sheet','-o',str(svg),str(pcb)],capture_output=True,check=True,timeout=30)
   doc=ET.fromstring(svg.read_text());x,y,w,h=c['bounds'];doc.set('viewBox',f'{c["x"]+x} {c["y"]+y} {w} {h}')
   import re
   # KiCad SVG preserves per-layer color. Resolve it before replacing with the preview colors.
   for element in doc.iter():
    style=element.get('style')
    if style:
     def color(match):
      value=match.group(2).upper()
      return match.group(1)+(':#ffffff' if value in ('#F2EDA1','#E8B2A7','#FFFFFF') else ':#dfbf77')
     style=re.sub(r'(stroke|fill):\s*(#[0-9a-fA-F]{6})',color,style)
     style=style.replace('fill-opacity:0.4000','fill-opacity:1.0000')
     element.set('style',style)
   (assets/f'{c["id"]}-{side}.svg').write_text(ET.tostring(doc,encoding='unicode'))
 print('Imported preview',index+1,len(added),flush=True)
