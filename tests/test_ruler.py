"""Run with KiCad Python: python3 tests/test_ruler.py."""
import copy
import json
import re
from pathlib import Path
import sys
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from silkscreen_editor import save_layout as shared_save, revision
from unittest.mock import patch
import importlib.util
try:
    import pcbnew as p
except ImportError:
    p=None
if p is not None:
    spec=importlib.util.spec_from_file_location('ruler_silk',ROOT/'silkscreen.py')
    ruler_silk=importlib.util.module_from_spec(spec);spec.loader.exec_module(ruler_silk)
    validate=ruler_silk.validate
    with patch.dict(sys.modules,{'silkscreen':ruler_silk}):
        spec=importlib.util.spec_from_file_location('ruler_build',ROOT/'build.py')
        builder=importlib.util.module_from_spec(spec);spec.loader.exec_module(builder)
    build=builder.build

def save_layout(*args):
    with patch.dict(sys.modules,{'silkscreen':ruler_silk}):
        return shared_save(*args)


@unittest.skipUnless(p is not None,'KiCad Python required')
class RulerTest(unittest.TestCase):
    def setUp(self):
        self.layout=json.loads((ROOT/'silkscreen.json').read_text())

    def test_outline_and_scales(self):
        board=build()
        outline=next(g for g in board.GetDrawings() if g.GetLayer()==p.Edge_Cuts and g.GetShape()==p.SHAPE_T_RECT)
        self.assertEqual((p.ToMM(outline.GetStart().x),p.ToMM(outline.GetStart().y)),(0,0))
        self.assertEqual((p.ToMM(outline.GetEnd().x),p.ToMM(outline.GetEnd().y)),(155,25))
        self.assertFalse(any(g.GetLayer() in (p.F_Cu,p.B_Cu) for g in board.GetDrawings()))

    def test_rejects_invalid_component_identity_position_and_text(self):
        for key,value in [('x',float('nan')),('x',-20),('rotation',400),('id','unknown'),('texts',[])]:
            layout=copy.deepcopy(self.layout);layout['components'][0][key]=value
            with self.subTest(key=key),self.assertRaises(ValueError):validate(layout,155,25)

    def test_board_preserves_imported_geometry(self):
        template=p.LoadBoard(str(ROOT/'template.kicad_pcb'))
        originals={f.m_Uuid.AsString():f for f in template.GetFootprints()}
        keys=json.loads((ROOT/'module-keys.json').read_text())
        layout=self.layout;board=build()
        fps={f.m_Uuid.AsString():f for f in board.GetFootprints()}
        signature=lambda f:sorted((a.GetNumber(),a.GetSize().x,a.GetSize().y,a.GetDrillSize().x,a.GetDrillSize().y) for a in f.Pads())
        for identity,fp in fps.items():
            source=originals[identity]
            self.assertEqual(signature(source),signature(fp))
            old=list(source.Pads());new=list(fp.Pads())
            for i in range(len(old)):
                for j in range(i):
                    self.assertAlmostEqual((old[i].GetPosition()-old[j].GetPosition()).EuclideanNorm(),(new[i].GetPosition()-new[j].GetPosition()).EuclideanNorm(),delta=3)
        self.assertGreaterEqual(len(layout['components']),40)
        # Back scale mirrors the front tick for tick; trace widths keep four ICRS rows.
        for key in ('metric-back','widths-40-18'):
            self.assertTrue(fps[keys[key]].IsFlipped())
        front_x=sorted(round(p.ToMM(g.GetStart().x),3) for g in fps[next(c['id'] for c in layout['components'] if c['name']=='Metric · 0–155 mm')].GraphicalItems() if g.GetLayer()==p.F_Cu and isinstance(g,p.PCB_SHAPE))
        back_x=sorted(round(p.ToMM(g.GetStart().x),3) for g in fps[keys['metric-back']].GraphicalItems() if g.GetLayer()==p.B_Cu and isinstance(g,p.PCB_SHAPE))
        self.assertEqual(front_x,back_x)
        self.assertEqual(fps[keys['xiao']].GetLayer(),p.B_Cu)
        # The circular-pad gaps really measure .10/.15/.20 mm at the copper edges.
        pads=sorted(fps[keys['gaps']].Pads(),key=lambda a:int(a.GetNumber()))
        for i,gap in enumerate((.1,.15,.2)):
            distance=(pads[2*i].GetPosition()-pads[2*i+1].GetPosition()).EuclideanNorm()
            self.assertAlmostEqual(p.ToMM(round(distance))-1,gap,places=6)
        # Saving a moved through-hole module goes to a temporary copy only.
        before=(ROOT/'silkscreen.json').read_bytes()
        with tempfile.TemporaryDirectory() as temp:
            pcb=Path(temp)/'ruler.kicad_pcb';p.SaveBoard(str(pcb),board)
            moved=copy.deepcopy(layout);contact=next(c for c in moved['components'] if c['id']==keys['contact15']);contact['x']+=1
            save_layout(pcb,moved,revision(pcb,Path(temp)/'silkscreen.json'),155,25)
            saved={f.m_Uuid.AsString():f for f in p.LoadBoard(str(pcb)).GetFootprints()}[keys['contact15']]
            self.assertAlmostEqual(p.ToMM(saved.GetPosition().x),contact['x'])
            self.assertEqual([p.ToMM(a.GetDrillSize().x) for a in saved.Pads()],[1.5])
        self.assertEqual(before,(ROOT/'silkscreen.json').read_bytes())

    def test_flipped_copies_build_on_the_back_and_resave_without_duplicates(self):
        known={c['id']:c for c in json.loads((ROOT/'native-components.json').read_text())}
        layout=copy.deepcopy(self.layout)
        metric=next(c for c in layout['components'] if c['name'].startswith('Metric'))
        widths=next(c for c in known.values() if c['name']=='trace_widths')
        x,y,w,h=metric['bounds']
        back=dict(copy.deepcopy(metric),id='11111111-2222-4333-8444-555555555555',copyOf=metric['id'],flip=True,
                  side='B.SilkS',bounds=[-(x+w),y,w,h],x=0,y=25,rotation=180)
        wx,wy,ww,wh=widths['bounds']
        flipped=dict(copy.deepcopy(widths),id='66666666-7777-4888-8999-aaaaaaaaaaaa',copyOf=widths['id'],flip=True,
                     side='B.SilkS',bounds=[-(wx+ww),wy,ww,wh],x=60,y=12.5,rotation=90)
        layout['components']+= [back,flipped]
        validate(layout,155,25)
        reuse=copy.deepcopy(layout);reuse['components'][-1]['id']=widths['id']
        with self.assertRaises(ValueError):validate(reuse,155,25)
        with tempfile.TemporaryDirectory() as temp:
            pcb=Path(temp)/'ruler.kicad_pcb';p.SaveBoard(str(pcb),build())
            for _ in range(2):
                save_layout(pcb,layout,revision(pcb,Path(temp)/'silkscreen.json'),155,25)
            board=p.LoadBoard(str(pcb))
            fps={f.m_Uuid.AsString():f for f in board.GetFootprints()}
            self.assertEqual(len(list(board.GetFootprints())),len(layout['components'])-sum(c['id'] not in fps for c in layout['components']))
            front,rear=fps[metric['id']],fps[back['id']]
            self.assertFalse(front.IsFlipped());self.assertTrue(rear.IsFlipped())
            self.assertEqual(len(list(front.Pads())),len(list(rear.Pads())))
            self.assertAlmostEqual(p.ToMM(rear.GetPosition().y),25);self.assertTrue(fps[flipped['id']].IsFlipped())
            # Its numbers keep the edited text (mm x 10 on this ruler).
            self.assertEqual(sorted(t.GetText() for t in rear.GraphicalItems() if isinstance(t,p.PCB_TEXT)),
                             sorted(t.GetText() for t in front.GraphicalItems() if isinstance(t,p.PCB_TEXT)))
            # The copy's preview is the source art mirrored about the template origin.
            Path(temp,'silkscreen.json').write_text(json.dumps(layout))
            art=ruler_silk.instance_asset(temp,f"{flipped['id']}-B.svg")
            source=(ROOT/'assets'/f"{widths['id']}-F.svg").read_text()
            vx,vy,vw,vh=map(float,re.search(r'viewBox="([^"]+)"',source).group(1).split())
            self.assertIn(f'viewBox="{2*widths["x"]-vx-vw} {vy} {vw} {vh}"',art.decode())
            self.assertIn('scale(-1 1)',art.decode())

    def test_module_lands_match_the_actual_manufacturer_files(self):
        board=build()
        fps={f.m_Uuid.AsString():f for f in board.GetFootprints()}
        keys=json.loads((ROOT/'module-keys.json').read_text())
        for key,directory,name,count in [
            ('xiao',ROOT/'upstream/Seeed','XIAO-ESP32-S3-SMD',25),
            ('wrover',ROOT/'upstream/AS-008','ESP32-WROVER-E',52),
        ]:
            source=p.FootprintLoad(str(directory),name);actual=fps[keys[key]]
            pads=list(actual.Pads());original=list(source.Pads())
            self.assertEqual(len(pads),count)
            self.assertEqual(sorted((a.GetNumber(),a.GetSize().x,a.GetSize().y,a.GetDrillSize().x,a.GetDrillSize().y) for a in pads),sorted((a.GetNumber(),a.GetSize().x,a.GetSize().y,a.GetDrillSize().x,a.GetDrillSize().y) for a in original))
            self.assertGreater(sum(a.GetLayerSet().Contains(p.B_Cu) and a.GetLayerSet().Contains(p.B_Mask) for a in pads),20)
            # KiCad reorders pads on serialization; compare unique pin identities, not iterator order.
            unique={a.GetNumber():a for a in original if sum(b.GetNumber()==a.GetNumber() for b in original)==1}
            targets={a.GetNumber():a for a in pads if a.GetNumber() in unique}
            for first,a in unique.items():
                for second,b in unique.items():
                    self.assertAlmostEqual((a.GetPosition()-b.GetPosition()).EuclideanNorm(),(targets[first].GetPosition()-targets[second].GetPosition()).EuclideanNorm(),delta=3)
            distances=lambda values:sorted((a.GetPosition()-b.GetPosition()).EuclideanNorm() for i,a in enumerate(values) for b in values[:i])
            for before,after in zip(distances(original),distances(pads)):self.assertAlmostEqual(before,after,delta=3)

    def test_move_rotate_delete_text_svg_save_and_repeat_without_duplicates(self):
        with tempfile.TemporaryDirectory() as temp:
            pcb=Path(temp)/'ruler.kicad_pcb';p.SaveBoard(str(pcb),build())
            target=next(c for c in self.layout['components'] if 'MountingHole_3.2' in c['name'])
            target.update(x=target['x']-1,rotation=15)
            removed=next(c for c in self.layout['components'] if c['name']=='SOIC · 1.27 mm')
            self.layout['components'].remove(removed)
            trace=next(c for c in self.layout['components'] if c['name'].startswith('Trace widths · 12'))
            trace['texts'][0]['text']='EDIT'
            self.layout['items'].append(dict(id='custom-text',kind='text',side='F.SilkS',text='CUSTOM',x=60,y=12,size=1,thickness=.15,rotation=0))
            self.layout['items'].append(dict(id='custom-svg',kind='svg',side='B.SilkS',svg='<svg/>',x=25,y=12,width=4,height=2,rotation=90,rectangles=[[0,0,.2,1]]))
            rev=revision(pcb,Path(temp)/'silkscreen.json')
            newrev=save_layout(pcb,self.layout,rev,155,25)
            saved=p.LoadBoard(str(pcb));fps={f.m_Uuid.AsString():f for f in saved.GetFootprints()}
            self.assertNotIn(removed['id'],fps)
            self.assertAlmostEqual(p.ToMM(fps[target['id']].GetPosition().x),target['x'])
            self.assertTrue(any(isinstance(g,p.PCB_TEXT) and g.GetText()=='EDIT' for g in fps[trace['id']].GraphicalItems()))
            self.assertTrue(any(isinstance(g,p.PCB_TEXT) and g.GetText()=='CUSTOM' for g in saved.GetDrawings()))
            count=(len(fps),len(list(saved.GetDrawings())))
            save_layout(pcb,self.layout,newrev,155,25)
            twice=p.LoadBoard(str(pcb))
            self.assertEqual(count,(len(list(twice.GetFootprints())),len(list(twice.GetDrawings()))))
            self.assertEqual(json.loads((Path(temp)/'silkscreen.json').read_text()),self.layout)
            with self.assertRaises(ValueError):save_layout(pcb,self.layout,rev,155,25)

if __name__=='__main__':unittest.main()
