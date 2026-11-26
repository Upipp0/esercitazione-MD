#!/bin/bash
# Tutto quello che sta nelle pagine 01-06 della guida, senza fermarsi a
# spiegarlo.
#
#   cd ~/esercitazione-MD/run
#   bash ../scripts/catch_up.sh
#
# Usalo SOLO per rimetterti in pari se qualcosa e andato storto e l'aula e
# andata avanti: finisce dove comincia la pagina 07, con npt.gro pronto.
# L'esercizio e percorrere la guida a mano; questa e la rete di sicurezza.
#
# Non sovrascrive un lavoro gia iniziato: lancialo in una cartella vuota.
set -euo pipefail

NT="${NT:-2}"                       # thread; lascia 2 su una macchina condivisa
IN="$(cd "$(dirname "$0")/../input" && pwd)"
MDP="$(cd "$(dirname "$0")/../mdp" && pwd)"

command -v gmx >/dev/null || {
    echo "gmx non trovato.  module use /modules && module load gromacs/2026.2" >&2
    exit 1
}
for f in complex.gro topol.top npt.gro; do
    [ -e "$f" ] && { echo "$f e gia qui -- lancia questo script in una cartella vuota" >&2; exit 1; }
done

echo "== pagina 01: separo la struttura cristallografica"
cp "$IN/3HTB.pdb" .
awk '/^ATOM/ && substr($0,22,1)=="A" && (substr($0,17,1)==" " || substr($0,17,1)=="A") {
       print substr($0,1,16) " " substr($0,18) } END {print "END"}' 3HTB.pdb > protein.pdb
awk '/^HETATM/ && substr($0,18,3)=="JZ4" {
       print substr($0,1,16) " " substr($0,18) } END {print "END"}' 3HTB.pdb > jz4_crystal.pdb

echo "== pagina 02: topologia della proteina"
gmx pdb2gmx -f protein.pdb -o protein_processed.gro -p topol.top -i posre.itp \
            -ff amber99sb-ildn -water tip3p

echo "== pagina 03: inserisco il ligando"
cp "$IN/jz4_atomtypes.itp" "$IN/jz4.itp" "$IN/posre_jz4.itp" .
python3 -I - <<'PY'
t = open("topol.top").read()
ff = '#include "amber99sb-ildn.ff/forcefield.itp"\n'
assert t.count(ff) == 1
t = t.replace(ff, ff + '\n; Tipi atomici del ligando -- devono precedere ogni [ moleculetype ]\n'
                       '#include "jz4_atomtypes.itp"\n')
w = '; Include water topology\n'
assert t.count(w) == 1
t = t.replace(w, '; Il ligando\n#include "jz4.itp"\n\n'
                 '#ifdef POSRES_LIG\n#include "posre_jz4.itp"\n#endif\n\n' + w)
m = 'Protein_chain_A     1\n'
assert t.count(m) == 1
t = t.replace(m, m + 'JZ4                 1\n')
open("topol.top", "w").write(t)
PY

NP=$(sed -n 2p protein_processed.gro | tr -d ' ')
{ head -2 protein_processed.gro
  sed -n "3,$((NP + 2))p" protein_processed.gro
  grep 'JZ4' "$IN/jz4.gro"
  tail -1 protein_processed.gro
} > complex.gro
sed -i "2s/.*/ $((NP + 22))/" complex.gro
echo "   complex.gro: $((NP + 22)) atomi"

echo "== pagina 04: scatola, acqua, ioni"
gmx editconf -f complex.gro -o box.gro -c -d 1.0 -bt dodecahedron
gmx solvate  -cp box.gro -cs spc216.gro -o solv.gro -p topol.top
gmx grompp   -f "$MDP/ions.mdp" -c solv.gro -p topol.top -o ions.tpr -maxwarn 1
echo SOL | gmx genion -s ions.tpr -o solv_ions.gro -p topol.top \
                      -pname NA -nname CL -neutral -conc 0.15

echo "== pagina 05: minimizzazione dell'energia"
gmx grompp -f "$MDP/em.mdp" -c solv_ions.gro -p topol.top -o em.tpr
gmx mdrun -deffnm em -nt "$NT"

echo "== pagina 06: gruppi di indice, NVT, NPT"
printf '1 | 13\nname 21 Protein_JZ4\nq\n' | gmx make_ndx -f solv_ions.gro -o index.ndx
gmx grompp -f "$MDP/nvt.mdp" -c em.gro  -r em.gro  -p topol.top -n index.ndx -o nvt.tpr
gmx mdrun -deffnm nvt -nt "$NT"
gmx grompp -f "$MDP/npt.mdp" -c nvt.gro -r nvt.gro -t nvt.cpt -p topol.top -n index.ndx -o npt.tpr
gmx mdrun -deffnm npt -nt "$NT"

echo
echo "Equilibrato.  Prosegui da guida/07-produzione-e-prestazioni.md:"
echo "    gmx grompp -f ../mdp/md.mdp -c npt.gro -t npt.cpt -p topol.top -n index.ndx -o md.tpr"
echo "    gmx mdrun -deffnm md -nt $NT"
