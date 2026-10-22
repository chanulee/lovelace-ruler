# Sources and transformations

모듈을 직접 새로 그리지 않고 아래 원본 형상을 복사했다. 모든 좌표·패드 크기·드릴과 내부 거리는 유지하고, 위치와 회전만 바꾼다. XIAO/WROVER는 원본의 실제 전체 랜드 패턴을 포함한다.

| 모듈 | 원본 | 라이선스/고지 |
|---|---|---|
| JST SH · 1.00 mm · 4P | [KiCad official / Connector_JST](https://gitlab.com/kicad/libraries/kicad-footprints/-/blob/master/Connector_JST.pretty/JST_SH_SM04B-SRSS-TB_1x04-1MP_P1.00mm_Horizontal.kicad_mod) | CC-BY-SA-4.0 + library exception |
| JST GH · 1.25 mm · 4P | [KiCad official / Connector_JST](https://gitlab.com/kicad/libraries/kicad-footprints/-/blob/master/Connector_JST.pretty/JST_GH_SM04B-GHS-TB_1x04-1MP_P1.25mm_Horizontal.kicad_mod) | CC-BY-SA-4.0 + library exception |
| JST PH · 2.00 mm · 2P | [KiCad official / Connector_JST](https://gitlab.com/kicad/libraries/kicad-footprints/-/blob/master/Connector_JST.pretty/JST_PH_B2B-PH-K_1x02_P2.00mm_Vertical.kicad_mod) | CC-BY-SA-4.0 + library exception |
| JST PH · 2.00 mm · 8P | [KiCad official / Connector_JST](https://gitlab.com/kicad/libraries/kicad-footprints/-/blob/master/Connector_JST.pretty/JST_PH_B8B-PH-K_1x08_P2.00mm_Vertical.kicad_mod) | CC-BY-SA-4.0 + library exception |
| FPC · 0.50 mm · 8P | [KiCad official / Connector_FFC-FPC](https://gitlab.com/kicad/libraries/kicad-footprints/-/blob/master/Connector_FFC-FPC.pretty/Hirose_FH12-8S-0.5SH_1x08-1MP_P0.50mm_Horizontal.kicad_mod) | CC-BY-SA-4.0 + library exception |
| FPC · 1.00 mm · 8P | [KiCad official / Connector_FFC-FPC](https://gitlab.com/kicad/libraries/kicad-footprints/-/blob/master/Connector_FFC-FPC.pretty/Molex_200528-0080_1x08-1MP_P1.00mm_Horizontal.kicad_mod) | CC-BY-SA-4.0 + library exception |
| USB-C · HRO TYPE-C-31-M-12 | [KiCad official / Connector_USB](https://gitlab.com/kicad/libraries/kicad-footprints/-/blob/master/Connector_USB.pretty/USB_C_Receptacle_HRO_TYPE-C-31-M-12.kicad_mod) | CC-BY-SA-4.0 + library exception |
| QFN · 0.40 mm | [KiCad official / Package_DFN_QFN](https://gitlab.com/kicad/libraries/kicad-footprints/-/blob/master/Package_DFN_QFN.pretty/QFN-24-1EP_3x3mm_P0.4mm_EP1.75x1.6mm.kicad_mod) | CC-BY-SA-4.0 + library exception |
| TQFP-64 · 0.50 mm · ADS1299 | [KiCad official / Package_QFP](https://gitlab.com/kicad/libraries/kicad-footprints/-/blob/master/Package_QFP.pretty/TQFP-64_10x10mm_P0.5mm.kicad_mod) | CC-BY-SA-4.0 + library exception |
| Pin header · 1.27 mm | [KiCad official / Connector_PinHeader_1.27mm](https://gitlab.com/kicad/libraries/kicad-footprints/-/blob/master/Connector_PinHeader_1.27mm.pretty/PinHeader_1x04_P1.27mm_Vertical.kicad_mod) | CC-BY-SA-4.0 + library exception |
| Pin header · 2.54 mm | [KiCad official / Connector_PinHeader_2.54mm](https://gitlab.com/kicad/libraries/kicad-footprints/-/blob/master/Connector_PinHeader_2.54mm.pretty/PinHeader_1x04_P2.54mm_Vertical.kicad_mod) | CC-BY-SA-4.0 + library exception |
| TSSOP · 0.65 mm | [notaroomba/trace](https://github.com/notaroomba/trace) | MIT (upstream README) |
| SOIC · 1.27 mm | [notaroomba/trace](https://github.com/notaroomba/trace) | MIT (upstream README) |
| SOT-23 · 3P | [ICRS PCB Ruler / SOT-23](https://github.com/ben5049/ICRS-PCB-Ruler) | Apache-2.0 |
| QFN-24 · 0.50 mm | [Adafruit PCB Ruler / QFN-24](https://github.com/adafruit/Adafruit-PCB-Ruler) | CC-BY-SA-3.0 |
| 0402 | [notaroomba/trace](https://github.com/notaroomba/trace) | MIT (upstream README) |
| 0603 | [notaroomba/trace](https://github.com/notaroomba/trace) | MIT (upstream README) |
| 0805 | [notaroomba/trace](https://github.com/notaroomba/trace) | MIT (upstream README) |
| M2 · Ø2.2 | [KiCad official / MountingHole](https://gitlab.com/kicad/libraries/kicad-footprints/-/blob/master/MountingHole.pretty/MountingHole_2.2mm_M2_Pad.kicad_mod) | CC-BY-SA-4.0 + library exception |
| M2.5 · Ø2.7 | [KiCad official / MountingHole](https://gitlab.com/kicad/libraries/kicad-footprints/-/blob/master/MountingHole.pretty/MountingHole_2.7mm_M2.5_Pad.kicad_mod) | CC-BY-SA-4.0 + library exception |
| M3 · Ø3.2 | [KiCad official / MountingHole](https://gitlab.com/kicad/libraries/kicad-footprints/-/blob/master/MountingHole.pretty/MountingHole_3.2mm_M3_Pad.kicad_mod) | CC-BY-SA-4.0 + library exception |
| Ø1.5 mm · contact reference | [KiCad official / TestPoint](https://gitlab.com/kicad/libraries/kicad-footprints/-/blob/master/TestPoint.pretty/TestPoint_THTPad_D3.0mm_Drill1.5mm.kicad_mod) | CC-BY-SA-4.0 + library exception |
| Drill · Ø0.5 | [KiCad official / TestPoint](https://gitlab.com/kicad/libraries/kicad-footprints/-/blob/master/TestPoint.pretty/TestPoint_THTPad_D1.0mm_Drill0.5mm.kicad_mod) | CC-BY-SA-4.0 + library exception |
| Drill · Ø0.7 | [KiCad official / TestPoint](https://gitlab.com/kicad/libraries/kicad-footprints/-/blob/master/TestPoint.pretty/TestPoint_THTPad_D1.5mm_Drill0.7mm.kicad_mod) | CC-BY-SA-4.0 + library exception |
| Pogo contacts · 2.54 mm · 5P | [KiCad official / TestPoint](https://gitlab.com/kicad/libraries/kicad-footprints/-/blob/master/TestPoint.pretty/TestPoint_Pad_D1.0mm.kicad_mod) | CC-BY-SA-4.0 + library exception |
| Pad gaps · 0.10 / 0.15 / 0.20 mm | [KiCad official / TestPoint](https://gitlab.com/kicad/libraries/kicad-footprints/-/blob/master/TestPoint.pretty/TestPoint_Pad_D1.0mm.kicad_mod) | CC-BY-SA-4.0 + library exception |
| Via · drill 0.20 / copper 0.40 mm | [notaroomba/trace native via](https://github.com/notaroomba/trace) | MIT (upstream README) |
| XIAO ESP32S3 · 25 copper pads | [Seeed official XIAO footprint](https://wiki.seeedstudio.com/xiao_esp32s3_getting_started/) | Manufacturer source; upstream archive has no explicit license |
| CR2032 · Ø20 body | [KiCad official / Battery](https://gitlab.com/kicad/libraries/kicad-footprints/-/blob/master/Battery.pretty/Battery_Panasonic_CR2032-HFN_Horizontal_CircularHoles.kicad_mod) | CC-BY-SA-4.0 + library exception |
| ESP32-WROVER-E · 39 copper lands | [AS-008 existing footprint / Espressif dimensions](https://www.espressif.com/sites/default/files/documentation/esp32-wrover-e_esp32-wrover-ie_datasheet_en.pdf) | Existing repository design |
| SC-70 / SOT-323 | [notaroomba/trace](https://github.com/notaroomba/trace) | MIT (upstream README) |
| SOT-23-5 | [notaroomba/trace](https://github.com/notaroomba/trace) | MIT (upstream README) |
| SOT-23-6 | [notaroomba/trace](https://github.com/notaroomba/trace) | MIT (upstream README) |
| DFN-6 / .50 | [notaroomba/trace](https://github.com/notaroomba/trace) | MIT (upstream README) |
| DFN-8 / .50 | [notaroomba/trace](https://github.com/notaroomba/trace) | MIT (upstream README) |
| DFN-10 / .50 | [notaroomba/trace](https://github.com/notaroomba/trace) | MIT (upstream README) |
| QFN-16 / .50 | [notaroomba/trace](https://github.com/notaroomba/trace) | MIT (upstream README) |
| QFN-20 / .50 | [notaroomba/trace](https://github.com/notaroomba/trace) | MIT (upstream README) |
| TSSOP-16 / .65 | [notaroomba/trace](https://github.com/notaroomba/trace) | MIT (upstream README) |
| SOD-123 | [notaroomba/trace](https://github.com/notaroomba/trace) | MIT (upstream README) |
| SOD-323 | [notaroomba/trace](https://github.com/notaroomba/trace) | MIT (upstream README) |
| NPN symbol | [notaroomba/trace](https://github.com/notaroomba/trace) | MIT (upstream README) |
| PNP symbol | [notaroomba/trace](https://github.com/notaroomba/trace) | MIT (upstream README) |
| NMOS symbol | [notaroomba/trace](https://github.com/notaroomba/trace) | MIT (upstream README) |
| PMOS symbol | [notaroomba/trace](https://github.com/notaroomba/trace) | MIT (upstream README) |
| C 0402 | [notaroomba/trace](https://github.com/notaroomba/trace) | MIT (upstream README) |
| C 0603 | [notaroomba/trace](https://github.com/notaroomba/trace) | MIT (upstream README) |
| C 0805 | [notaroomba/trace](https://github.com/notaroomba/trace) | MIT (upstream README) |
| L 0402 | [notaroomba/trace](https://github.com/notaroomba/trace) | MIT (upstream README) |
| L 0603 | [notaroomba/trace](https://github.com/notaroomba/trace) | MIT (upstream README) |
| L 0805 | [notaroomba/trace](https://github.com/notaroomba/trace) | MIT (upstream README) |
| Trace widths · 12 / 10 / 8 / 6 mil | [ICRS PCB Ruler / four native width samples](https://github.com/ben5049/ICRS-PCB-Ruler) | Apache-2.0 |
| OSHW gear · generic | [KiCad official / Symbol](https://gitlab.com/kicad/libraries/kicad-footprints/-/blob/master/Symbol.pretty/OSHW-Logo_5.7x6mm_SilkScreen.kicad_mod) | CC-BY-SA-4.0 + library exception |
| Inches · 1/16 · back | [ICRS PCB Ruler / Gauge_6in](https://github.com/ben5049/ICRS-PCB-Ruler) | Apache-2.0 |

## 변환 내용

- ICRS: Apache-2.0, Ben Smith / Imperial College Robotics Society (2023). 보존한 원본은 수정하지 않았다. 155×30→155×25 외형, 검정색, 위치와 라벨을 변경했다. mm 숫자는 cm 숫자를 10배로 표기하고 글자만 .8mm로 줄였다. 눈금 간격은 확대/축소하지 않았다.
- Adafruit: CC-BY-SA-3.0. Eagle QFN-24의 SMD 좌표·크기·회전과 직선 실크를 KiCad로 변환했다. 원본 `license.txt`와 README를 보존했다. 이 기여가 들어간 배치를 공개 재배포할 때 출처·변경 고지와 해당 ShareAlike 조건을 유지해야 한다.
- Trace: TSSOP/SOIC/0402/0603/0805, 실제 .2mm 드릴/.4mm 구리 비아. upstream README가 MIT로 명시하며 별도 LICENSE 파일은 발견하지 못했다. README와 원본 PCB를 보존했다.
- KiCad: 공식 라이브러리의 선택된 파일을 그대로 보존했다. 파일 모음은 CC-BY-SA-4.0과 library exception 문서 포함. 설치된 KiCad 10 라이브러리 스냅샷이며 ORIGIN.json의 SHA-256으로 식별한다.
- 포고: 공식 Ø1.0 SMD 원형 테스트포인트 패드를 복사해 2.54mm 피치로 5개 배열했다. 패드 형상을 새로 설계하지 않았다. 실물 포고 접점 대보기용이고 드릴은 없다.
- 간격: 같은 공식 Ø1.0 원형 패드 쌍을 재배치해 가장 가까운 구리 가장자리 간격 .10/.15/.20mm를 만든다. 평행 트레이스 간격 샘플과는 다르다.
- Seeed XIAO: 제조사 공식 다운로드의 25개 SMD 랜드와 둥근 본체/USB 실크를 그대로 복사했다. 21×17.8mm는 본체 치수이며 USB와 랜드는 바깥으로 나온다. Sense 확장 보드는 제외. 배포 압축파일에 명시적 라이선스는 없으므로 허용 라이선스로 임의 표기하지 않았다.
- CR2032: 공식 Panasonic 배터리 풋프린트의 Ø20mm Fab 원을 뒷면 실크로 가져왔다. 전기 접점이나 홀더 호환성을 의미하지 않는다.
- WROVER-E: 이 저장소 AS-008의 기존 풋프린트를 전체 복사했다. 본체 31.4×18mm, 주변 38개 랜드 + 중앙 접지 랜드, 4개 .3mm 열 비아를 포함한다. AS-008 PCB 자체는 수정하지 않았다.
- OSHW: KiCad 공식 일반 기어 로고를 사용했다. OSHWA 인증 마크/인증번호는 사용하지 않았다.

## 검토만 한 소스

아래 저장소는 참고만 했고 기하·파일을 가져오지 않았다. 이 저장소에 사본을 두지 않는다.

- [Evidlo/uiuc_ruler](https://github.com/Evidlo/uiuc_ruler) (커밋 eda5c1a), [mprosk/ruler](https://github.com/mprosk/ruler) (커밋 15c4305): 명시적 라이선스 없음.
- [headblockhead/ruler](https://github.com/headblockhead/ruler) (커밋 ae08fb0): CERN-OHL-S-2.0. NFC/로고 구성 참고만 했다. 기어는 KiCad 공식 라이브러리에서 가져왔다.

이 문서는 각 기여의 출처 고지이며, 서로 다른 원본 전체를 하나의 새 라이선스로 재지정하지 않는다.

## 밀도 개선 버전의 추가 변환

- Trace의 SC70, SOT23-5/6, DFN6/8/10, QFN16/20, TSSOP16, SOD123/323, R/C/L 0402/0603/0805, NPN/PNP/NMOS/PMOS를 추가로 복사했다. 기호의 글자는 수평으로 정렬했다.
- XIAO와 WROVER 핀 번호는 원본 패드 번호에서 생성한 실크다. GPIO 기능이나 전기 연결을 새로 추정하지 않았다.
- XIAO/WROVER의 실크 외곽선은 실제 구리 랜드 AABB 주변 .22mm를 비우도록 잘랐다. 곡선은 최대 .12mm 길이 현으로 나눠 원본 곡률을 근사했다. 원본 곡선도 Dwgs.User에 남겼다. 패드·드릴·본체 실측 치수는 바꾸지 않았다.
- ICRS 선폭 사다리에서 12/10/8/6mil 네 줄의 원본 구리/마스크 사각형을 그대로 가져와 세로 간격만 줄였다.
- ICRS 인치 눈금은 X축 위치를 그대로 두고 세로 높이를 55%로 줄였다. inch 피치를 축소하지 않았다.
- OSHW 기어는 KiCad 공식 5.7×6mm 실크 버전으로 바꿨다.
