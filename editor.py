#!/usr/bin/env python3
"""Open the ruler in the repository's SVG/text editor."""
import os
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent
os.execv(sys.executable, [sys.executable, str(ROOT / 'tools/silkscreen_editor.py'),
                         '--board', str(ROOT / 'lovelace-ruler.kicad_pcb'),
                         '--port', '8766', *sys.argv[1:]])
