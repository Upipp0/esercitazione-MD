"""Pagina 02: i quattro tipi di termine che compongono una topologia.

   pymol -cq fig_topologia.py -- <complex.gro> <cartella_img>

Tutti e quattro i termini sono mostrati sulla stessa catena propilica del
ligando - C12-C13-C14-C4 - perche quattro atomi legati in fila sono il minimo
che serve a definire un diedro, e usare sempre lo stesso frammento rende
evidente che le quattro sezioni della topologia parlano degli stessi atomi.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(sys.argv[0])))
from pymol import cmd
import comune

gro, odir = sys.argv[1], sys.argv[2]
A1, A2, A3, A4 = "C12", "C13", "C14", "C4"


def atomo(nome):
    return f"resn JZ4 and name {nome}"


comune.scena()
cmd.load(gro, "sys")
cmd.hide("everything")

# Solo il ligando, e solo la parte che serve: il resto distrae.
cmd.show("sticks", "resn JZ4")
cmd.color("grey70", "resn JZ4 and elem C")
cmd.color("white", "resn JZ4 and elem H")
cmd.set("stick_radius", 0.13, "resn JZ4")
cmd.set("stick_h_scale", 1.0)

# I quattro atomi protagonisti, evidenziati e nominati una volta per tutte.
quattro = " or ".join(atomo(n) for n in (A1, A2, A3, A4))
cmd.show("spheres", quattro)
cmd.set("sphere_scale", 0.22, quattro)
cmd.color("c_blu", quattro)
for n, dove in ((A1, (-1.6, 1.3, 0)), (A2, (-0.6, -1.8, 0)),
                (A3, (0.9, 1.5, 0)), (A4, (1.8, -1.4, 0))):
    cmd.label(atomo(n), f'"{n}"')
    cmd.set("label_position", dove, atomo(n))
cmd.set("label_size", 26)

cmd.orient("resn JZ4")
cmd.turn("x", -28)
cmd.turn("y", 12)
cmd.zoom("resn JZ4", 0.3)
vista = cmd.get_view()

pannelli = []
TERMINI = [
    ("legame", "[ bonds ]", [(A1, A2)], "distance"),
    ("angolo", "[ angles ]", [(A1, A2, A3)], "angle"),
    ("diedro", "[ dihedrals ]", [(A1, A2, A3, A4)], "dihedral"),
    ("coppia 1-4", "[ pairs ]", [(A1, A4)], "distance"),
]

cmd.set("angle_size", 1.4)
cmd.set("dihedral_size", 1.4)

for k, (nome, sezione, gruppi, tipo) in enumerate(TERMINI):
    cmd.delete("misura")
    cmd.set_view(vista)
    # ripristina il legame: il pannello precedente puo averlo ingrossato
    cmd.set_bond("stick_radius", 0.13, atomo(A1), atomo(A2))
    cmd.set_bond("stick_color", "default", atomo(A1), atomo(A2))
    sel = [atomo(a) for a in gruppi[0]]

    if nome == "legame":
        # Una linea tratteggiata fra due atomi legati sparirebbe dentro il
        # bastoncino: il legame si evidenzia ingrossandolo e colorandolo.
        cmd.set_bond("stick_radius", 0.30, sel[0], sel[1])
        cmd.set_bond("stick_color", "c_arancio", sel[0], sel[1])
    elif tipo == "angle":
        cmd.angle("misura", sel[0], sel[1], sel[2])
    elif tipo == "dihedral":
        cmd.dihedral("misura", sel[0], sel[1], sel[2], sel[3])
    else:
        cmd.distance("misura", sel[0], sel[1])

    if "misura" in cmd.get_names("objects"):
        cmd.color("c_acqua" if nome == "coppia 1-4" else "c_arancio", "misura")
        cmd.set("dash_radius", 0.09, "misura")
        cmd.set("dash_gap", 0.25 if nome == "coppia 1-4" else 0.0, "misura")
        cmd.hide("labels", "misura")

    p = os.path.join(odir, f"_topo_{k}.png")
    comune.rendi(p, 1050, 690)
    pannelli.append((p, f"{nome}   {sezione}"))

comune.componi(
    pannelli,
    os.path.join(odir, "02-termini.png"),
    colonne=2,
    didascalie=[
        "due atomi legati: una molla fra C12 e C13",
        "tre atomi in fila: l'ampiezza C12-C13-C14",
        "quattro atomi: la rotazione attorno al legame C13-C14",
        "primo e quarto atomo: si vedono, ma a forza ridotta",
    ],
    didascalia_h=46,
)
for p, _ in pannelli:
    os.remove(p)
