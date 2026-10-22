# Notices

**Board design** (`*.kicad_pcb`, `*.kicad_pro`, templates, `silkscreen.json`, `native-components*.json`,
`assets/`, `renders/`, Gerbers): © 2026 Chanwoo Lee, [CC BY-SA 4.0](LICENSE).
**Scripts and tools** (`*.py`, `*.sh`, `tools/`, `tests/`): [MIT](LICENSE-MIT).

The design contains third-party geometry. Each keeps its own terms; see [SOURCES.md](SOURCES.md)
for the per-module list and the changes made.

| Source | Used for | Terms | Copy kept |
|---|---|---|---|
| [ICRS PCB Ruler](https://github.com/ben5049/ICRS-PCB-Ruler), Ben Smith / Imperial College Robotics Society, 2023 | outline and scales, trace widths, M2–M4 holes | Apache-2.0 | `upstream/ICRS-PCB-Ruler/LICENSE` |
| [KiCad official footprints](https://gitlab.com/kicad/libraries/kicad-footprints) | connectors, packages, holes, test points, OSHW gear | CC-BY-SA-4.0 with the KiCad library exception | `upstream/official-kicad/LICENSE.md` |
| [Adafruit PCB Reference Ruler](https://github.com/adafruit/Adafruit-PCB-Ruler) | QFN-24 0.5 mm | CC-BY-SA-3.0 (the reason the design is ShareAlike) | `upstream/adafruit__Adafruit-PCB-Ruler/license.txt` |
| [notaroomba/trace](https://github.com/notaroomba/trace) | SOT/DFN/QFN/TSSOP/SOD, R/C/L, via, transistor symbols | MIT, as stated in its README (no LICENSE file upstream) | `upstream/notaroomba__trace/README.md` |
| [Seeed Studio XIAO ESP32S3](https://wiki.seeedstudio.com/xiao_esp32s3_getting_started/) | XIAO footprint (25 pads, body outline) | Manufacturer download; **no explicit licence** — not covered by this repository's licences | `upstream/Seeed/` |
| LOVELACE AS-008 ([audiostream-esp32](https://github.com/chanulee/audiostream-esp32)) | ESP32-WROVER-E land pattern | same author | `upstream/AS-008/` |

"ICRS", the Imperial College Robotics Society name and logo, "OSHW" and "Seeed"/"XIAO" are names or marks
of their owners; the licences above cover copyright, not trademarks. The OSHW gear here is the generic
logo, not an OSHWA certification mark.
