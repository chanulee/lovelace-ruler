"""Reset the working template/layout from the preserved upstream source (KiCad Python)."""
import json, subprocess, tempfile, re
from pathlib import Path
import pcbnew as p
R=Path(__file__).resolve().parent
U=R/'upstream/ICRS-PCB-Ruler'
b=p.LoadBoard(str(U/'Ruler_KiCad/Ruler_KiCad.kicad_pcb'))
pt=lambda x,y:p.VECTOR2I(p.FromMM(x),p.FromMM(y))
for f in b.GetFootprints():
 name=str(f.GetFPID().GetLibItemName())
 f.Move(pt(-75,-85))
 if name=='Gauge_6in':f.Move(pt(0,-5))
 elif name!='Gauge_150mm_Type1_CopperTop':f.Move(pt(0,-2.5))
 # Logos are artwork: scale only their shapes, never gauge pads or hole geometry.
 if name in ('ICRS_20mm','ICRS_28mm','Alert 40mm'):
  center=f.GetPosition()
  for g in f.GraphicalItems():
   if isinstance(g,p.PCB_SHAPE):
    g.Move(-center);g.Scale(.78);g.Move(center)
for g in b.GetDrawings():
 g.Move(pt(-75,-85))
 if isinstance(g,p.PCB_SHAPE) and g.GetShape()==p.SHAPE_T_RECT and g.GetLayer() in (p.Edge_Cuts,p.F_Cu,p.B_Cu):
  g.SetEnd(pt(155,25))
 elif isinstance(g,p.PCB_SHAPE) and g.GetLayer()==p.Edge_Cuts:
  g.Move(pt(0,-.5 if p.ToMM(g.GetPosition().y)<15 else -4.5))
 else:
  pos=g.GetPosition();g.Move(pt(0,-p.ToMM(pos.y)/6))
b.GetTitleBlock().SetTitle('Lovelace Ruler — derived from ICRS PCB Ruler')
b.SetFileName(str(R/'template.kicad_pcb'))
p.SaveBoard(str(R/'template.kicad_pcb'),b)
# Actual KiCad stackup colour, as well as the web preview colour.
f=R/'template.kicad_pcb';f.write_text(f.read_text().replace('"Blue"','"Black"'))
b=p.LoadBoard(str(f))
components=[];items=[]
# Give the source's otherwise anonymous footprints meaningful editor labels.
for fp in b.GetFootprints():
 name=str(fp.GetFPID().GetLibItemName());pos=fp.GetPosition()
 box=fp.GetBoundingBox(False,False)
 c=dict(id=fp.m_Uuid.AsString(),name=name,x=p.ToMM(pos.x),y=p.ToMM(pos.y),rotation=0,
        side='F.SilkS' if any(g.GetLayer() in (p.F_SilkS,p.F_Mask) and (not isinstance(g,p.PCB_TEXT) or g.IsVisible()) for g in fp.GraphicalItems()) or any(a.GetLayerSet().Contains(p.F_Mask) for a in fp.Pads()) else 'B.SilkS',both=any(a.GetLayerSet().Contains(p.F_Mask) and a.GetLayerSet().Contains(p.B_Mask) for a in fp.Pads()),
        bounds=[p.ToMM(box.GetX()-pos.x),p.ToMM(box.GetY()-pos.y),p.ToMM(box.GetWidth()),p.ToMM(box.GetHeight())],
        drills=[[p.ToMM(a.GetPosition().x-pos.x),p.ToMM(a.GetPosition().y-pos.y),p.ToMM(a.GetDrillSize().x)] for a in fp.Pads() if a.GetDrillSize().x>0],
        texts=[dict(id=g.m_Uuid.AsString(),text=g.GetText(),x=p.ToMM(g.GetPosition().x-pos.x),y=p.ToMM(g.GetPosition().y-pos.y),size=p.ToMM(g.GetTextSize().y),rotation=-g.GetTextAngle().AsDegrees(),side='B' if g.GetLayer()==p.B_SilkS else 'F',mirror=g.IsMirrored(),align={-1:'start',0:'middle',1:'end'}[int(g.GetHorizJustify())],valign={-1:'hanging',0:'central',1:'text-after-edge'}[int(g.GetVertJustify())]) for g in fp.GraphicalItems() if isinstance(g,p.PCB_TEXT) and g.IsVisible() and g.GetLayer() in (p.F_SilkS,p.B_SilkS)])
 components.append(c)
for g in b.GetDrawings():
 if isinstance(g,p.PCB_TEXT):
  back=g.GetLayer()==p.B_SilkS
  items.append(dict(id=g.m_Uuid.AsString(),nativeId=g.m_Uuid.AsString(),kind='text',side='B.SilkS' if back else 'F.SilkS',
     text=g.GetText(),x=155-p.ToMM(g.GetPosition().x) if back else p.ToMM(g.GetPosition().x),y=p.ToMM(g.GetPosition().y),
     align={-1:'start',0:'middle',1:'end'}[int(g.GetHorizJustify())],valign={-1:'hanging',0:'central',1:'text-after-edge'}[int(g.GetVertJustify())],size=p.ToMM(g.GetTextSize().y),thickness=p.ToMM(g.GetTextThickness()),rotation=g.GetTextAngle().AsDegrees()*(1 if back else -1)))
 elif isinstance(g,p.PCB_SHAPE):
  if g.GetLayer() in (p.F_Cu,p.B_Cu) or (g.GetLayer()==p.Edge_Cuts and g.GetShape()==p.SHAPE_T_RECT):continue
  box=g.GetBoundingBox();pos=g.GetPosition()
  label=('AWG hole Ø'+str(round(p.ToMM(g.GetRadius())*2,3))) if g.GetLayer()==p.Edge_Cuts else 'Reference frame / '+g.GetLayerName()
  components.append(dict(id=g.m_Uuid.AsString(),name=label,x=p.ToMM(pos.x),y=p.ToMM(pos.y),rotation=0,
    side='B.SilkS' if g.GetLayer()==p.B_SilkS else 'F.SilkS',both=g.GetLayer()==p.Edge_Cuts,
    bounds=[p.ToMM(box.GetX()-pos.x),p.ToMM(box.GetY()-pos.y),p.ToMM(box.GetWidth()),p.ToMM(box.GetHeight())],drills=[[0,0,p.ToMM(g.GetRadius())*2]] if g.GetLayer()==p.Edge_Cuts else [],texts=[]))
(R/'native-components.json').write_text(json.dumps(components,ensure_ascii=False,indent=2)+'\n')
(R/'silkscreen.json').write_text(json.dumps(dict(version=1,items=items,components=components),ensure_ascii=False,indent=2)+'\n')
# Render faithful native footprint/shape previews; board-level text stays individually editable.
assets=R/'assets';assets.mkdir(exist_ok=True)
cli='/Volumes/KiCad/KiCad/KiCad.app/Contents/MacOS/kicad-cli'
objects={o.m_Uuid.AsString():o for o in [*b.GetFootprints(),*b.GetDrawings()]}
isolated_boards=[]
for index,c in enumerate(components):
 for side in ('F','B') if c['both'] else (c['side'][0],):
  isolated=p.LoadBoard(str(R/'template.kicad_pcb'));isolated_boards.append(isolated)
  obj=None
  for candidate in [*isolated.GetFootprints(),*isolated.GetDrawings()]:
   if candidate.m_Uuid.AsString()==c['id']:obj=candidate
   else:isolated.Delete(candidate)
  if isinstance(obj,p.FOOTPRINT):
   for graphic in list(obj.GraphicalItems()):
    if isinstance(graphic,p.PCB_TEXT):graphic.SetLayer(p.Dwgs_User)
  with tempfile.TemporaryDirectory() as temp:
   pcb=Path(temp)/'item.kicad_pcb';svg=Path(temp)/'item.svg'
   p.SaveBoard(str(pcb),isolated)
   subprocess.run([cli,'pcb','export','svg','--layers',f'{side}.Mask,{side}.SilkS,Edge.Cuts','--mode-single','--page-size-mode','0','--exclude-drawing-sheet','-o',str(svg),str(pcb)],check=True,capture_output=True)
   data=svg.read_text()
   # Keep native coordinates but crop to the component box in physical front coordinates.
   x,y,w,h=c['bounds'];view=f'{c["x"]+x} {c["y"]+y} {w} {h}'
   data=re.sub(r'viewBox="[^"]*"',f'viewBox="{view}"',data,count=1)
   data=re.sub(r'(stroke|fill):\s*(?:#[0-9a-fA-F]{3,8}|rgb\([^)]*\))',r'\1:#dfbf77',data)
   if 'ICRS_' in c['name'] or c['name']=='Alert 40mm' or c['name'].startswith('Reference frame'):data=data.replace('#dfbf77','#ffffff')
   (assets/f'{c["id"]}-{side}.svg').write_text(data)
 print('preview',index+1,len(components),flush=True)
(R/'upstream/ICRS-PCB-Ruler/ORIGIN.json').write_text(json.dumps(dict(url='https://github.com/ben5049/ICRS-PCB-Ruler',commit='bbd91fe08e0448bfdac4fd1e471ed0cc8afc96d2',source='Ruler_KiCad',license='Apache-2.0'),indent=2)+'\n')
