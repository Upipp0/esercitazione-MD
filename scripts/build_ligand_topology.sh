#!/bin/bash
# Come sono stati prodotti input/jz4.itp, input/jz4_atomtypes.itp,
# input/jz4.gro e input/posre_jz4.itp.  NON serve eseguirlo per
# l'esercitazione: i file sono gia in input/.  Sta qui perche la provenienza
# dei parametri del ligando non sia un mistero, e perche tu possa ripetere la
# procedura con un ligando diverso.
#
#   bash build_ligand_topology.sh jz4_crystal.pdb outdir
#
# Richiede acpype e Open Babel, nessuno dei due installato a livello di
# sistema su Bombina.  Entrambi si installano con pip:
#
#   python3 -m venv ~/ligvenv
#   ~/ligvenv/bin/pip install acpype openbabel-wheel
#
# acpype porta con se la propria copia di antechamber, quindi non c'e nessun
# AmberTools da installare a parte.
set -euo pipefail

PDB="${1:?usage: build_ligand_topology.sh <ligand.pdb> <outdir>}"
OUT="${2:?usage: build_ligand_topology.sh <ligand.pdb> <outdir>}"
VENV="${VENV:-$HOME/ligvenv}"
NAME="${NAME:-JZ4}"
CHARGE="${CHARGE:-0}"
RESNR="${RESNR:-164}"        # il numero di residuo che il ligando prende in complex.gro
OFFSET="${OFFSET:-2614}"     # quanti atomi di proteina deve seguire

PDB="$(readlink -f "$PDB")"
mkdir -p "$OUT"; cd "$OUT"
cp "$PDB" ligand_noh.pdb

# 1. Una struttura cristallografica non ha idrogeni.  Aggiungili, e scrivi in
#    mol2 perche gli ordini di legame aromatici sopravvivano: ad antechamber
#    serve sapere che l'anello e aromatico per tipizzarlo come 'ca' e non come
#    singoli e doppi alternati.
"$VENV/bin/obabel" -ipdb ligand_noh.pdb -omol2 -O ligand_h.mol2 -h

# 2. Tipi atomici GAFF2 e cariche parziali AM1-BCC.
#    -n e la CARICA FORMALE NETTA della molecola.  Sbagliarla e il modo piu
#    comune di produrre una topologia dall'aria plausibile e del tutto
#    sbagliata.
"$VENV/bin/acpype" -i ligand_h.mol2 -b "$NAME" -n "$CHARGE" -a gaff2 -c bcc -f

ACP="$NAME.acpype/${NAME}_GMX.itp"

# 3. Estrai il blocco [ atomtypes ] dal file della molecola.  GROMACS esige
#    che ogni tipo atomico sia dichiarato prima del primo [ moleculetype ]
#    della topologia assemblata, e il blocco del ligando viene per forza dopo
#    quello della proteina.
awk '/^\[ *atomtypes *\]/ {a=1} /^\[ *moleculetype *\]/ {a=0} a' "$ACP" > atomtypes_raw.itp
awk '/^\[ *moleculetype *\]/ {m=1} m' "$ACP" > "$(echo "$NAME" | tr A-Z a-z).itp"

# 4. Aggiungi la colonna del numero atomico che acpype omette.  Senza, gli
#    atomi non hanno elemento e gmx hbond riporta che una molecola con un
#    gruppo ossidrilico non ha donatori ne accettori.  Si deduce dalla massa.
#
#    LC_ALL=C conta: con una localizzazione italiana (o tedesca, o francese)
#    awk formatta e legge i numeri con la virgola, e ogni confronto di massa
#    qui fallirebbe in silenzio.
LC_ALL=C awk '
    /^ *;name/ { print ";name  bond_type  at.num    mass     charge  ptype   sigma         epsilon"; next }
    /^ *[;[]/ || NF < 7 { print; next }
    { m = $3 + 0; n = 0
      if      (m > 0.9  && m < 1.2)  n = 1
      else if (m > 11.9 && m < 12.2) n = 6
      else if (m > 13.9 && m < 14.2) n = 7
      else if (m > 15.9 && m < 16.2) n = 8
      else if (m > 18.9 && m < 19.1) n = 9
      else if (m > 22.9 && m < 23.1) n = 11
      else if (m > 30.9 && m < 31.1) n = 15
      else if (m > 31.9 && m < 32.3) n = 16
      else if (m > 35.3 && m < 35.6) n = 17
      if (n == 0)
          printf("; ATTENZIONE: elemento di %s non deducibile dalla massa %s -- metti at.num a mano\n", $1, $3)
      rest = ""
      for (i = 4; i <= NF; i++) rest = rest " " $i
      printf " %-7s %-9s %3d  %10s%s\n", $1, $2, n, $3, rest }
   ' atomtypes_raw.itp > "$(echo "$NAME" | tr A-Z a-z)_atomtypes.itp"

# 5. Vincoli posizionali sugli atomi pesanti, che acpype elenca per primi.
#    Servono solo durante l'equilibratura.
NHEAVY=$(awk '/^\[ *atoms *\]/{a=1;next} /^\[/{a=0} a && NF>7 && $8+0 > 2.0 {n++} END{print n}' \
         "$(echo "$NAME" | tr A-Z a-z).itp")
{ printf '; Vincoli posizionali del ligando: i %d atomi pesanti.\n' "$NHEAVY"
  printf '; Si accendono con -DPOSRES_LIG al momento di grompp.\n'
  printf '[ position_restraints ]\n'
  printf ';  ai  funz        fcx        fcy        fcz\n'
  for i in $(seq 1 "$NHEAVY"); do printf '%5d    1       1000       1000       1000\n' "$i"; done
} > "posre_$(echo "$NAME" | tr A-Z a-z).itp"

# 6. Rinumera le coordinate perche si possano incollare subito dopo quelle
#    della proteina.
NAT=$(sed -n 2p "$NAME.acpype/${NAME}_GMX.gro" | tr -d ' ')
{ printf 'ligando con gli idrogeni, numerato per seguire una proteina di %d atomi\n' "$OFFSET"
  printf '%5d\n' "$NAT"
  awk -v r="$RESNR" -v n="$NAME" -v o="$OFFSET" '
      NR > 2 && NR <= 2 + '"$NAT"' {
          printf "%5d%-5s%5s%5d%s\n", r, n, substr($0,11,5), o + NR - 2, substr($0,21) }
      ' "$NAME.acpype/${NAME}_GMX.gro"
  printf '%10.5f%10.5f%10.5f\n' 5 5 5
} > "$(echo "$NAME" | tr A-Z a-z).gro"

echo
echo "scritti in $PWD:"
ls -la *.itp *.gro | grep -v acpype
