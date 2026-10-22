#!/usr/bin/env python3
"""Build lovelace-ruler.kicad_pcb from template.kicad_pcb and silkscreen.json (KiCad Python)."""
import json
from pathlib import Path
import pcbnew as p
from silkscreen import apply_layout

ROOT = Path(__file__).resolve().parent
W, H = 155, 25


def build(directory=ROOT):
    directory = Path(directory)
    board = p.LoadBoard(str(ROOT / 'template.kicad_pcb'))
    apply_layout(board, json.loads((directory / 'silkscreen.json').read_text()), W, H)
    return board


if __name__ == '__main__':
    p.SaveBoard(str(ROOT / 'lovelace-ruler.kicad_pcb'), build())
    print('Built lovelace-ruler.kicad_pcb')
