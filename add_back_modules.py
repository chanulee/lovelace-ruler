"""Add two back-only modules cut from existing source copper (KiCad Python).

metric-back   The front metric scale (mm x 10 labels) flipped and turned so it
              mirrors the front along the bottom edge. Under the XIAO's bottom
              pad row the 5/10 mm ticks stop 0.2 mm short of the pads; every tick
              keeps its x position and every number its place.
widths-40-18  ICRS trace_widths reduced to its 40/30/24/18 mil rows and labels.

Both keep their source footprint's origin, so a layout places them like the
source. Re-running replaces the two entries. Placement of the trim follows the
layout's XIAO.
"""
import json
from pathlib import Path
import re
import subprocess
import tempfile
import uuid
import xml.etree.ElementTree as ET
import pcbnew as p

R = Path(__file__).resolve().parent
CLI = '/Volumes/KiCad/KiCad/KiCad.app/Contents/MacOS/kicad-cli'
uid = lambda key: str(uuid.uuid5(uuid.NAMESPACE_URL, 'lovelace-ruler-module/' + key))
mm = p.FromMM
CLEAR = .2
keep_alive = []

base = p.LoadBoard(str(R / 'template.kicad_pcb')); keep_alive.append(base)
metadata = [c for c in json.loads((R / 'native-components.json').read_text()) if c['id'] not in (uid('metric-back'), uid('widths-40-18'))]
for fp in list(base.GetFootprints()):
    if fp.m_Uuid.AsString() in (uid('metric-back'), uid('widths-40-18')):
        base.Delete(fp)
by_name = {str(f.GetFPID().GetLibItemName()): f for f in base.GetFootprints()}
layout = json.loads((R / 'silkscreen.json').read_text())


def entry(fp, key, name, side, source, note):
    pos = fp.GetPosition(); box = fp.GetBoundingBox(False, False)
    c = dict(id=fp.m_Uuid.AsString(), name=name, x=p.ToMM(pos.x), y=p.ToMM(pos.y), rotation=0, side=side + '.SilkS',
             both=any(a.GetLayerSet().Contains(p.F_Mask) and a.GetLayerSet().Contains(p.B_Mask) for a in fp.Pads()),
             bounds=[p.ToMM(box.GetX() - pos.x), p.ToMM(box.GetY() - pos.y), p.ToMM(box.GetWidth()), p.ToMM(box.GetHeight())],
             texts=[], drills=[], source=source, note=note)
    for g in fp.GraphicalItems():
        if isinstance(g, p.PCB_TEXT) and g.IsVisible() and g.GetLayer() in (p.F_SilkS, p.B_SilkS):
            c['texts'].append(dict(id=g.m_Uuid.AsString(), text=g.GetText(), x=p.ToMM(g.GetPosition().x - pos.x),
                                   y=p.ToMM(g.GetPosition().y - pos.y), size=p.ToMM(g.GetTextSize().y),
                                   rotation=-g.GetTextAngle().AsDegrees(), side='B' if g.GetLayer() == p.B_SilkS else 'F',
                                   mirror=g.IsMirrored(), align={-1: 'start', 0: 'middle', 1: 'end'}[int(g.GetHorizJustify())],
                                   valign={-1: 'hanging', 0: 'central', 1: 'text-after-edge'}[int(g.GetVertJustify())]))
    fp.SetReference('MOD_' + key.replace('-', '_')); fp.SetValue(name)
    fp.Reference().SetVisible(False); fp.Value().SetVisible(False)
    return c


# metric-back: the recommended front scale, as placed (labels x 10).
front = next(c for c in layout['components'] if c['name'] == 'Metric · 0–155 mm')
source = by_name['Gauge_150mm_Type1_CopperTop']
fp = source.Duplicate(False).Cast(); fp.SetUuid(p.KIID(uid('metric-back')))
labels = {t['id']: t for t in front['texts']}
for g_src, g in zip(source.GraphicalItems(), fp.GraphicalItems()):
    t = labels.get(g_src.m_Uuid.AsString())
    if t and isinstance(g, p.PCB_TEXT):
        g.SetText(t['text']); g.SetTextSize(p.VECTOR2I(mm(t['size']), mm(t['size'])))
        g.SetTextThickness(min(g.GetTextThickness(), mm(t['size'] * .15)))
origin = fp.GetPosition()
fp.Flip(origin, p.FLIP_DIRECTION_LEFT_RIGHT)
fp.Rotate(origin, p.EDA_ANGLE(180, p.DEGREES_T))
# Back scale: origin at (0, 25); the XIAO's lowest pads, in the same frame.
offset = p.VECTOR2I(mm(0) - origin.x, mm(25) - origin.y)
built = p.LoadBoard(str(R / 'lovelace-ruler.kicad_pcb')); keep_alive.append(built)
xiao_id = next(c['id'] for c in layout['components'] if c['name'].startswith('XIAO'))
xiao = next(f for f in built.GetFootprints() if f.m_Uuid.AsString() == xiao_id)
pads = [a.GetBoundingBox() for a in xiao.Pads() if a.IsOnLayer(p.B_Cu)]
lowest = max(b.GetBottom() for b in pads)
row = [b for b in pads if b.GetBottom() > lowest - mm(.5)]
limit = lowest + mm(CLEAR)
shortened = 0
for g in fp.GraphicalItems():
    if isinstance(g, p.PCB_SHAPE) and g.GetLayer() in (p.B_Cu, p.B_Mask) and g.GetShape() == p.SHAPE_T_SEGMENT:
        half = g.GetWidth() // 2
        x = g.GetStart().x + offset.x
        if any(b.GetLeft() - mm(CLEAR) - half < x < b.GetRight() + mm(CLEAR) + half for b in row):
            for getter, setter in ((g.GetStart, g.SetStart), (g.GetEnd, g.SetEnd)):
                point = getter()
                if point.y + offset.y < limit + half:
                    setter(p.VECTOR2I(point.x, limit + half - offset.y)); shortened += 1
    elif isinstance(g, p.PAD) or (isinstance(g, p.PCB_SHAPE) and g.GetLayer() in (p.B_Cu, p.B_Mask)):
        box = g.GetBoundingBox()
        if any(b.GetLeft() - mm(CLEAR) < box.GetRight() + offset.x and box.GetLeft() + offset.x < b.GetRight() + mm(CLEAR) for b in row) and box.GetTop() + offset.y < limit:
            raise SystemExit(f'metric-back: a non-segment tick sits under the XIAO ({g.GetClass()})')
base.Add(fp)
metric = entry(fp, 'metric-back', 'Metric · 0–155 mm · back', 'B',
               dict(name='ICRS PCB Ruler / Gauge_150mm_Type1_CopperTop', url='https://github.com/ben5049/ICRS-PCB-Ruler', license='Apache-2.0'),
               f'앞면 mm 눈금을 뒤집어 아래 가장자리에 대칭으로 둔 것입니다. XIAO 아래 패드 열 밑에서만 5/10 mm 눈금 {shortened}개 끝을 패드에서 {CLEAR} mm 떨어지게 줄이고 숫자는 앞면과 같은 자리입니다.')
print('metric-back: shortened', shortened, 'tick ends')

# widths-40-18: the four widest ICRS rows with their mil labels.
source = by_name['trace_widths']
fp = source.Duplicate(False).Cast(); fp.SetUuid(p.KIID(uid('widths-40-18')))
for g in list(fp.GraphicalItems()):
    rel = p.ToMM(g.GetPosition().y - fp.GetPosition().y)
    if isinstance(g, p.PCB_TEXT):
        if g.GetText() not in ('40', '30', '24', '18'):
            fp.Remove(g)
    elif isinstance(g, p.PCB_SHAPE) and g.GetLayer() in (p.F_Cu, p.F_Mask):
        if rel > 8:
            fp.Remove(g)
    else:
        fp.Remove(g)
fp.Flip(fp.GetPosition(), p.FLIP_DIRECTION_LEFT_RIGHT)
base.Add(fp)
widths = entry(fp, 'widths-40-18', 'Trace widths · 40 / 30 / 24 / 18 mil', 'B',
               dict(name='ICRS PCB Ruler / trace_widths', url='https://github.com/ben5049/ICRS-PCB-Ruler', license='Apache-2.0'),
               '원본 구리 도형의 40/30/24/18 mil 네 줄과 mil 숫자만 남겼습니다. 실제 폭은 1.016/.762/.6096/.4572 mm입니다.')
print('widths-40-18:', sum(1 for g in fp.GraphicalItems() if isinstance(g, p.PCB_SHAPE)), 'shapes,', [t['text'] for t in widths['texts']])

p.SaveBoard(str(R / 'template.kicad_pcb'), base)
metadata += [metric, widths]
(R / 'native-components.json').write_text(json.dumps(metadata, ensure_ascii=False, indent=2) + '\n')
keys = json.loads((R / 'module-keys.json').read_text()); keys.update({'metric-back': metric['id'], 'widths-40-18': widths['id']})
(R / 'module-keys.json').write_text(json.dumps(keys, indent=2) + '\n')

# Previews, as import_modules.py makes them.
for c in (metric, widths):
    isolated = p.LoadBoard(str(R / 'template.kicad_pcb')); keep_alive.append(isolated); selected = None
    for candidate in [*isolated.GetFootprints(), *isolated.GetDrawings(), *isolated.GetTracks()]:
        if candidate.m_Uuid.AsString() == c['id']: selected = candidate
        else: isolated.Delete(candidate)
    for graphic in selected.GraphicalItems():
        if isinstance(graphic, p.PCB_TEXT): graphic.SetLayer(p.Dwgs_User)
    with tempfile.TemporaryDirectory() as temp:
        pcb = Path(temp) / 'item.kicad_pcb'; svg = Path(temp) / 'item.svg'; p.SaveBoard(str(pcb), isolated)
        subprocess.run([CLI, 'pcb', 'export', 'svg', '--layers', 'B.Mask,B.SilkS,Edge.Cuts', '--mode-single', '--page-size-mode', '0',
                        '--exclude-drawing-sheet', '-o', str(svg), str(pcb)], capture_output=True, check=True, timeout=30)
        doc = ET.fromstring(svg.read_text()); x, y, w, h = c['bounds']; doc.set('viewBox', f'{c["x"] + x} {c["y"] + y} {w} {h}')
        for element in doc.iter():
            style = element.get('style')
            if style:
                style = re.sub(r'(stroke|fill):\s*(#[0-9a-fA-F]{6})',
                               lambda m: m.group(1) + (':#ffffff' if m.group(2).upper() in ('#F2EDA1', '#E8B2A7', '#FFFFFF') else ':#dfbf77'), style)
                element.set('style', style.replace('fill-opacity:0.4000', 'fill-opacity:1.0000'))
        (R / 'assets' / f'{c["id"]}-B.svg').write_text(ET.tostring(doc, encoding='unicode'))
print('Saved template, catalog and previews')
