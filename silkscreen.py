"""Editable ICRS native objects plus custom SVG/text, using the shared editor."""
import importlib.util
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parent
# Board-level silk text/SVG shared with the LOVELACE AS boards (audiostream-esp32).
spec = importlib.util.spec_from_file_location('shared_silk', ROOT / 'shared_silkscreen.py')
shared = importlib.util.module_from_spec(spec)
spec.loader.exec_module(shared)
LAYOUT_FILE = 'silkscreen.json'


def registry():
    return {c['id']: c for c in json.loads((ROOT/'native-components.json').read_text())}


def source_of(c):
    """Catalog id behind a placed module; copies carry it in 'copyOf'."""
    return c.get('copyOf', c.get('id'))


def placed_bounds(c, known):
    x, y, w, h = known[source_of(c)]['bounds']
    return [-(x + w), y, w, h] if c.get('flip') else [x, y, w, h]


def validate(layout, width, height):
    shared.validate(layout, width, height)
    known = registry()
    components = layout.get('components')
    if not isinstance(components, list) or len(components) > 2 * len(known):
        raise ValueError('원본 요소 목록을 확인하세요.')
    ids = set()
    for c in components:
        if not isinstance(c, dict) or source_of(c) not in known or c.get('id') in ids:
            raise ValueError('원본 요소 ID가 잘못되었거나 중복되었습니다.')
        if 'copyOf' in c and (not isinstance(c['id'], str) or not c['id'] or c['id'] in known):
            raise ValueError('복사한 요소에는 새 ID가 필요합니다.')
        if not isinstance(c.get('flip', False), bool) or (c.get('flip') and 'copyOf' not in c and c['id'] not in known):
            raise ValueError('뒤집기 값을 확인하세요.')
        ids.add(c['id'])
        for key in ('x', 'y', 'rotation'):
            shared.number(c.get(key))
        if abs(c['rotation']) > 360:
            raise ValueError('회전은 -360~360도 범위입니다.')
        # The source edge scales intentionally touch the physical board edge.
        x,y,w,h=placed_bounds(c,known);a=math.radians(c['rotation'])
        for u,v in ((x,y),(x+w,y),(x+w,y+h),(x,y+h)):
            px=c['x']+u*math.cos(a)-v*math.sin(a)
            py=c['y']+u*math.sin(a)+v*math.cos(a)
            if not -.6 <= px <= width+.6 or not -.6 <= py <= height+.6:
                raise ValueError(f"{known[source_of(c)]['name']}: 요소가 기판 밖으로 나갑니다.")
        texts=c.get('texts',[])
        expected={t['id'] for t in known[source_of(c)]['texts']}
        if not isinstance(texts,list) or any(not isinstance(t,dict) for t in texts) or {t.get('id') for t in texts}!=expected or len(texts)!=len(expected):
            raise ValueError('원본 구성 텍스트 목록을 확인하세요.')
        if any(not isinstance(t.get('text'),str) or len(t['text'])>120 or any(ord(ch)<32 for ch in t['text']) for t in texts):
            raise ValueError('구성 텍스트는 한 줄당 최대 120자입니다.')
        for t in texts:
            shared.number(t.get('size'))
            if not .3 <= t['size'] <= 10:raise ValueError('구성 텍스트 크기를 확인하세요.')
    return layout


def read_layout(board, directory, width, height):
    return validate(json.loads((Path(directory)/LAYOUT_FILE).read_text()),width,height)


def apply_layout(board, layout, width, height):
    import pcbnew as p
    validate(layout,width,height)
    sources=[p.LoadBoard(str(ROOT/'template.kicad_pcb'))]
    native={o.m_Uuid.AsString():o for o in [*sources[0].GetFootprints(),*sources[0].GetDrawings(),*sources[0].GetTracks()]}
    controlled=registry()
    # Every footprint on a ruler board comes from the template, copies included.
    for obj in [*board.GetFootprints(),*board.GetDrawings(),*board.GetTracks()]:
        if obj.m_Uuid.AsString() in controlled or isinstance(obj,p.FOOTPRINT):
            board.Delete(obj)
    shared.apply_layout(board,dict(version=1,items=[i for i in layout['items'] if not i.get('nativeId')]),width,height)
    if layout.get('sourceCopper') is False:
        # ICRS uses full-board copper artwork; retain only the imported measuring modules here.
        for obj in list(board.GetDrawings()):
            if obj.GetLayer() in (p.F_Cu,p.B_Cu):board.Delete(obj)
    used=set()
    for c in layout['components']:
        src=source_of(c)
        if src in used:
            # A second copy of the same source needs its own untouched object.
            sources.append(p.LoadBoard(str(ROOT/'template.kicad_pcb')))
            obj=next(o for o in [*sources[-1].GetFootprints(),*sources[-1].GetDrawings(),*sources[-1].GetTracks()] if o.m_Uuid.AsString()==src)
        else:
            obj=native[src]
        used.add(src)
        for g in obj.GraphicalItems() if isinstance(obj,p.FOOTPRINT) else []:
            for t in c['texts']:
                if g.m_Uuid.AsString()==t['id']:
                    g.SetText(t['text'])
                    if g.GetTextSize().y!=p.FromMM(t['size']):
                        g.SetTextThickness(min(g.GetTextThickness(),p.FromMM(t['size']*.15)))
                    g.SetTextSize(p.VECTOR2I(p.FromMM(t['size']),p.FromMM(t['size'])))
        origin=obj.GetPosition()
        if c.get('flip'):
            if not isinstance(obj,p.FOOTPRINT):
                raise ValueError(f"{controlled[src]['name']}: 풋프린트만 다른 면으로 옮길 수 있습니다.")
            obj.Flip(origin,p.FLIP_DIRECTION_LEFT_RIGHT)
        obj.Rotate(origin,p.EDA_ANGLE(-c['rotation'],p.DEGREES_T))
        obj.Move(p.VECTOR2I(p.FromMM(c['x'])-origin.x,p.FromMM(c['y'])-origin.y))
        clone=(obj.Duplicate(False) if isinstance(obj,p.FOOTPRINT) else obj.Duplicate()).Cast();clone.SetUuid(p.KIID(c['id']));board.Add(clone)
    for item in layout['items']:
        if not item.get('nativeId'):
            continue
        original=native.get(item['nativeId'])
        if not isinstance(original,p.PCB_TEXT):
            raise ValueError('원본 텍스트 ID를 확인하세요.')
        clone=original.Duplicate().Cast()
        clone.SetUuid(p.KIID(item['id']))
        back=item['side']=='B.SilkS'
        clone.SetText(item['text']);clone.SetLayer(p.B_SilkS if back else p.F_SilkS)
        clone.SetMirrored(back)
        clone.SetPosition(p.VECTOR2I(p.FromMM(width-item['x'] if back else item['x']),p.FromMM(item['y'])))
        clone.SetTextSize(p.VECTOR2I(p.FromMM(item['size']),p.FromMM(item['size'])))
        clone.SetTextThickness(p.FromMM(item['thickness']))
        clone.SetTextAngle(p.EDA_ANGLE(item['rotation']*(1 if back else -1),p.DEGREES_T))
        board.Add(clone)


def instance_asset(directory, name):
    """Preview art for a copied or flipped module: the source's own file,
    mirrored about its template origin when it changed face."""
    import re
    import xml.etree.ElementTree as ET
    match=re.fullmatch(r'([0-9a-f-]{36})-([FB])\.svg',name)
    path=Path(directory)/LAYOUT_FILE
    if not match or not path.exists():
        return None
    c=next((c for c in json.loads(path.read_text()).get('components',[]) if c.get('id')==match[1] and 'copyOf' in c),None)
    if c is None:
        return None
    side=match[2]
    if c.get('flip'):
        side='F' if side=='B' else 'B'
    asset=ROOT/'assets'/f"{c['copyOf']}-{side}.svg"
    if not asset.is_file():
        return None
    if not c.get('flip'):
        return asset.read_bytes()
    ET.register_namespace('','http://www.w3.org/2000/svg')
    root=ET.fromstring(asset.read_bytes())
    vx,vy,vw,vh=map(float,root.get('viewBox').split())
    tx=registry()[c['copyOf']]['x']
    group=ET.Element('{http://www.w3.org/2000/svg}g',transform=f'translate({2*tx} 0) scale(-1 1)')
    for child in list(root):
        if not child.tag.endswith(('}title','}desc')):
            group.append(child)
        root.remove(child)
    root.append(group)
    root.set('viewBox',f'{2*tx-vx-vw} {vy} {vw} {vh}')
    return ET.tostring(root)
