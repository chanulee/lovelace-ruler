#!/bin/bash
# Bare-board renders (no 3D part models, no solder paste): renders/top.png, bottom.png, angle.png.
set -euo pipefail
cd "$(dirname "$0")"
KICAD=${KICAD:-/Volumes/KiCad/KiCad/KiCad.app/Contents}
PY="$KICAD/Frameworks/Python.framework/Versions/Current/bin/python3"
CLI="$KICAD/MacOS/kicad-cli"
TMP=$(mktemp -d); trap 'rm -rf "$TMP"' EXIT
cp lovelace-ruler.kicad_pro "$TMP/"
"$PY" -c "
import pcbnew as p, sys
b = p.LoadBoard('lovelace-ruler.kicad_pcb')
for f in b.GetFootprints():
    f.Models().clear()
    # No stencil is ordered: show bare ENIG pads, not KiCad's grey paste.
    for a in f.Pads():
        ls = a.GetLayerSet(); ls.RemoveLayer(p.F_Paste); ls.RemoveLayer(p.B_Paste); a.SetLayerSet(ls)
p.SaveBoard(sys.argv[1], b)" "$TMP/lovelace-ruler.kicad_pcb" 2>/dev/null
mkdir -p renders
R=("$CLI" pcb render --quality high --use-board-stackup-colors --background opaque)
"${R[@]}" --side top --width 3200 --height 560 --zoom 2.75 -o renders/top.png "$TMP/lovelace-ruler.kicad_pcb" > /dev/null
"${R[@]}" --side bottom --width 3200 --height 560 --zoom 2.75 -o renders/bottom.png "$TMP/lovelace-ruler.kicad_pcb" > /dev/null
"${R[@]}" --perspective --rotate '-50,0,-20' --zoom 1.9 --width 2400 --height 1100 -o renders/angle.png "$TMP/lovelace-ruler.kicad_pcb" > /dev/null
echo "renders/top.png bottom.png angle.png"
