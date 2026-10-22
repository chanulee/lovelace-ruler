#!/bin/bash
# Order files: Gerbers, drills, DRC report and a ZIP for JLCPCB.
# 2 layers, 1.6 mm, black mask, white silk, ENIG.
set -euo pipefail
cd "$(dirname "$0")"
KICAD=${KICAD:-/Volumes/KiCad/KiCad/KiCad.app/Contents}
CLI="$KICAD/MacOS/kicad-cli"
OUT=release
rm -rf "$OUT" && mkdir -p "$OUT" reports
"$CLI" pcb export gerbers -o "$OUT/" lovelace-ruler.kicad_pcb \
    --layers F.Cu,B.Cu,F.Mask,B.Mask,F.Silkscreen,B.Silkscreen,Edge.Cuts > /dev/null
"$CLI" pcb export drill --excellon-separate-th -o "$OUT/" lovelace-ruler.kicad_pcb > /dev/null
# Report only: a ruler has intentional rule exceptions (README, "제작 전 남은 항목").
"$CLI" pcb drc --format json -o reports/drc.json lovelace-ruler.kicad_pcb | grep Found || true
(cd "$OUT" && rm -f ../lovelace-ruler-gerbers.zip && zip -q ../lovelace-ruler-gerbers.zip ./*)
echo "Order files: lovelace-ruler-gerbers.zip"
