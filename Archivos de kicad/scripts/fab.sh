#!/bin/bash
# uso: fab.sh <dir_rev> <nombre>   -> genera fabricacion JLCPCB en <dir_rev>/fab
set -e
CLI="/c/Program Files/KiCad/9.0/bin/kicad-cli.exe"; cd "$1"; N="$2"; mkdir -p fab/gerber
"$CLI" pcb export gerbers --layers "F.Cu,In1.Cu,In2.Cu,B.Cu,F.Paste,B.Paste,F.Silkscreen,B.Silkscreen,F.Mask,B.Mask,Edge.Cuts" --subtract-soldermask --use-drill-file-origin -o fab/gerber/ "$N.kicad_pcb" >/dev/null
"$CLI" pcb export drill --format excellon --excellon-separate-th --generate-map --map-format pdf -o fab/gerber/ "$N.kicad_pcb" >/dev/null
"$CLI" pcb export pos --side front --format csv --units mm --exclude-dnp -o "fab/${N}_CPL_top.csv" "$N.kicad_pcb" >/dev/null
"$CLI" sch export bom --fields "Reference,Value,Footprint,MPN,BOM_Cat,\${QUANTITY}" --group-by "Value,Footprint,MPN" --exclude-dnp -o "fab/${N}_BOM.csv" "$N.kicad_sch" >/dev/null
"$CLI" pcb export step --subst-models --force -o "fab/${N}.step" "$N.kicad_pcb" >/dev/null 2>&1 || echo "STEP: aviso (modelos 3D faltantes)"
"$CLI" pcb render --side top --quality high --background opaque --width 1600 --height 1300 -o "fab/${N}_3D_top.png" "$N.kicad_pcb" >/dev/null 2>&1 || true
"$CLI" pcb render --side top --rotate "-40,0,25" --perspective --quality high --background opaque --width 1600 --height 1200 -o "fab/${N}_3D_iso.png" "$N.kicad_pcb" >/dev/null 2>&1 || true
"$CLI" sch export pdf -o "fab/${N}_esquematico.pdf" "$N.kicad_sch" >/dev/null
(cd fab/gerber && rm -f ../"${N}_gerbers.zip" && powershell -NoProfile -Command "Compress-Archive -Path * -DestinationPath ..\${N}_gerbers.zip -Force")
ls -la fab fab/gerber | grep -v "^total"
