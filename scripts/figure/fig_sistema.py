"""README: l'intero sistema simulato, intero e tagliato a meta.

   pymol -cq fig_sistema.py -- <compatto.gro> <uscita.png>

Il file di ingresso deve essere nella rappresentazione compatta, cioe quella
che si ottiene con

   gmx trjconv -s em.tpr -f solv_ions.gro -o compatto.gro -pbc mol -ur compact -center

altrimenti l'acqua appare sparsa agli angoli della cella triclina invece che
raccolta nella forma del dodecaedro.
"""
import os
import sys

# PyMOL esegue lo script dentro il proprio spazio dei nomi, quindi __file__
# punta a PyMOL e non a questo file: il percorso vero sta in sys.argv[0].
sys.path.insert(0, os.path.dirname(os.path.abspath(sys.argv[0])))
from pymol import cmd
import comune

gro = sys.argv[1]
out = sys.argv[2]
tmp = os.path.dirname(os.path.abspath(out)) or "."

comune.scena()
cmd.load(gro, "sys")
cmd.hide("everything")

cmd.show("cartoon", "polymer")
cmd.color("c_proteina", "polymer")
cmd.show("spheres", "resn JZ4")
cmd.color("c_arancio", "resn JZ4 and elem C")
cmd.set("sphere_scale", 1.0, "resn JZ4")
cmd.show("spheres", "resn NA or resn CL")
cmd.color("c_viola", "resn NA")
cmd.color("c_acqua", "resn CL")
cmd.set("sphere_scale", 0.5, "resn NA or resn CL")
cmd.show("spheres", "resn SOL and name OW")
cmd.color("c_acqua_pale", "resn SOL")
cmd.set("sphere_scale", 0.34, "resn SOL")

cmd.orient("polymer")
cmd.turn("y", 15)
cmd.zoom("all", 1.4)

# --- pannello A: la scatola piena -----------------------------------------
a = os.path.join(tmp, "_sistema_a.png")
comune.rendi(a, 1250, 1250)

# --- pannello B: la stessa scatola, tagliata ------------------------------
# Per tagliare dalla parte dell'osservatore serve sapere quale direzione, nel
# sistema di riferimento del modello, punta verso la telecamera.  La matrice
# che cmd.get_view() restituisce e in ordine per COLONNE, quindi l'asse z
# della telecamera e la terza riga: (V[2], V[5], V[8]).
V = cmd.get_view()
zx, zy, zz = V[2], V[5], V[8]
cx, cy, cz = cmd.centerofmass("polymer")
soglia = zx * cx + zy * cy + zz * cz - 2.0      # un po' oltre la meta

# Il linguaggio di selezione di PyMOL sa fare "x > 10" ma non combinazioni
# lineari delle coordinate.  Si calcola quindi il valore atomo per atomo e lo
# si parcheggia nel fattore B, su cui invece si puo selezionare.
solvente = "resn SOL or resn NA or resn CL"
proiezione = {}
cmd.iterate_state(1, solvente, "proiezione[index] = zx*x + zy*y + zz*z",
                  space={"proiezione": proiezione, "zx": zx, "zy": zy, "zz": zz})
cmd.alter(solvente, "b = proiezione.get(index, -9999)",
          space={"proiezione": proiezione})
cmd.remove(f"({solvente}) and b > {soglia:f}")
print("tolte", len([v for v in proiezione.values() if v > soglia]), "molecole di solvente")
b = os.path.join(tmp, "_sistema_b.png")
comune.rendi(b, 1250, 1250)

comune.componi(
    [(a, "La scatola, piena"), (b, "La stessa scatola, tagliata a meta")],
    out,
    didascalie=["10 226 molecole d'acqua disegnate come punti:\n"
                "prendono la forma del dodecaedro rombico",
                "dentro ci sono la proteina (grigio), il ligando\n"
                "(arancione) e gli ioni Na+ (viola) e Cl- (verde)"],
    didascalia_h=86,
)
os.remove(a)
os.remove(b)
