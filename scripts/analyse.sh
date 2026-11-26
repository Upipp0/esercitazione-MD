#!/bin/bash
# Tutti i comandi di analisi di guida/08-analisi.md, nell'ordine.
#
#   bash ../scripts/analyse.sh md.tpr md.xtc analysis
#   bash ../scripts/analyse.sh ../reference/md_ref.tpr ../reference/md_ref.xtc ref_analysis
#
# Eseguilo dalla tua cartella run/, con il modulo gromacs caricato.  Sta qui
# perche tu possa rilanciare tutto dopo aver cambiato qualcosa, non per
# sostituire il digitare i comandi almeno una volta e vedere che cosa chiedono.
set -euo pipefail

TPR="${1:-md.tpr}"
XTC="${2:-md.xtc}"
OUT="${3:-analysis}"

command -v gmx >/dev/null || {
    echo "gmx non trovato.  module use /modules && module load gromacs/2026.2" >&2
    exit 1
}
[ -f "$TPR" ] || { echo "file inesistente: $TPR" >&2; exit 1; }
[ -f "$XTC" ] || { echo "file inesistente: $XTC" >&2; exit 1; }
mkdir -p "$OUT"

# Un .tpr che descrive tutta la scatola non si puo usare con una traiettoria
# che contiene solo il soluto: va ridotto, a meno che non lo sia gia.
# pipefail va spento qui: grep -m1 esce al primo risultato e manda un SIGPIPE
# a gmx, che quindi termina con un codice diverso da zero.  Con pipefail e
# set -e lo script morirebbe in silenzio proprio su questa riga.
set +o pipefail
NTPR=$(gmx dump -s "$TPR" 2>/dev/null | grep -m1 -E '^ *natoms' | tr -dc '0-9')
NXTC=$(gmx check -f "$XTC" 2>&1 | sed -n 's/^# Atoms *//p' | tr -dc '0-9')
set -o pipefail
if [ "${NTPR:-0}" != "${NXTC:-0}" ]; then
    echo "== riduco la topologia da $NTPR atomi ai $NXTC della traiettoria"
    [ -f index.ndx ] || { echo "serve index.ndx; vedi la pagina 06 della guida" >&2; exit 1; }
    printf 'Protein_JZ4\n' | gmx convert-tpr -s "$TPR" -n index.ndx -o "$OUT/pl.tpr"
    TPR="$OUT/pl.tpr"
fi

echo "== ricompongo le molecole e tolgo la traslazione d'insieme"
printf 'Protein\nSystem\n' | gmx trjconv -s "$TPR" -f "$XTC" \
       -o "$OUT/traj.xtc" -pbc mol -center

echo "== RMSD dello scheletro proteico"
printf 'Backbone\nBackbone\n' | gmx rms -s "$TPR" -f "$OUT/traj.xtc" \
       -o "$OUT/rmsd_backbone.xvg" -tu ns

echo "== RMSD del ligando, sovrapposto sulla proteina"
printf 'Backbone\nJZ4\n' | gmx rms -s "$TPR" -f "$OUT/traj.xtc" \
       -o "$OUT/rmsd_jz4.xvg" -tu ns

echo "== RMSF per residuo"
printf 'Protein\n' | gmx rmsf -s "$TPR" -f "$OUT/traj.xtc" \
       -o "$OUT/rmsf_residue.xvg" -res

echo "== legami a idrogeno fra ligando e proteina"
gmx hbond -f "$OUT/traj.xtc" -s "$TPR" \
          -r 'resname JZ4' -t 'group Protein' \
          -num "$OUT/hbnum.xvg" -dist "$OUT/hbdist.xvg" -ang "$OUT/hbang.xvg" \
          -o "$OUT/hbond.ndx"

echo "== quali residui delimitano il sito"
gmx select -s "$TPR" -f "$OUT/traj.xtc" \
    -select 'same residue as (group "Protein" and within 0.45 of resname JZ4)' \
    -on "$OUT/pocket.ndx"

# Il file .ndx contiene numeri di atomo; il file di struttura dice a quale
# residuo appartiene ciascuno.  Lo scriviamo perche il grafico dell'RMSF
# possa segnarli.
GRO=complex.gro
[ -f "$GRO" ] || GRO=""
if [ -n "$GRO" ]; then
    python3 -I - "$GRO" "$OUT/pocket.ndx" "$OUT/pocket.txt" <<'PY'
import sys
gro, ndx, out = sys.argv[1:4]
lines = open(gro).read().splitlines()
resid = [int(l[:5]) for l in lines[2:2 + int(lines[1])]]
idx = [int(v) for line in open(ndx) if not line.startswith("[")
       for v in line.split()]
res = sorted({resid[i - 1] for i in idx if 0 < i <= len(resid)})
open(out, "w").write("\n".join(map(str, res)) + "\n")
print(f"   {len(res)} residues: {res}")
PY
fi

echo
echo "fatto.  Adesso disegna:"
echo "    ~/mdvenv/bin/python ../scripts/plot_analysis.py $OUT"
