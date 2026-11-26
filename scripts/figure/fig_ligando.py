"""Pagina 03: com'e fatto il ligando, prima e dopo la parametrizzazione.

   pymol -cq fig_ligando.py -- <jz4_crystal.pdb> <jz4.pdb> <cartella_img>

Il primo file e il ligando come esce dal cristallo: dieci atomi pesanti e
nessun idrogeno.  Il secondo e quello che Open Babel e acpype hanno prodotto:
ventidue atomi, pronti per la dinamica.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(sys.argv[0])))
from pymol import cmd
import comune

xtal, pieno, odir = sys.argv[1], sys.argv[2], sys.argv[3]
ANELLO = "name C7+C8+C9+C10+C11+C12"


# --- pannello A: come lo ha visto il cristallografo -----------------------
comune.scena()
cmd.load(xtal, "xtal")
cmd.hide("everything")
cmd.show("sticks", "xtal")
cmd.show("spheres", "xtal")
cmd.set("sphere_scale", 0.26, "xtal")
cmd.color("grey60", "xtal and elem C")
cmd.color("c_rosso", "xtal and elem O")
cmd.set("stick_radius", 0.15, "xtal")
cmd.set("label_size", 25)

# Vista di faccia sull'anello: e il piano che definisce la molecola.
cmd.orient(f"xtal and {ANELLO}")
cmd.turn("z", -25)
cmd.zoom("xtal", 2.8)
vista = cmd.get_view()
comune.etichette_radiali([(f"xtal and name {n}", n) for n in
                   ("C4", "C7", "C8", "C9", "C10", "C11", "C12", "C13", "C14", "OAB")],
                  raggio=2.4, oggetto="xtal")
a = os.path.join(odir, "_lig_a.png")
comune.rendi(a, 1200, 880)

# --- pannello B: dopo gli idrogeni e le cariche ---------------------------
cmd.delete("all")
comune.scena()
cmd.load(pieno, "pieno")
cmd.hide("everything")
cmd.show("sticks", "pieno")
cmd.show("spheres", "pieno")
cmd.set("sphere_scale", 0.22, "pieno")
cmd.set("sphere_scale", 0.15, "pieno and elem H")
cmd.color("grey60", "pieno and elem C")
cmd.color("c_giallo", "pieno and elem H")
cmd.color("c_rosso", "pieno and elem O")
cmd.set("stick_radius", 0.13, "pieno")
cmd.set("label_size", 25)

# I due atomi che faranno il legame a idrogeno della pagina 08.
cmd.color("c_acqua", "pieno and name H11")
cmd.set("sphere_scale", 0.26, "pieno and name H11")

# Stessa vista del pannello A: le due molecole hanno le stesse coordinate,
# quindi il confronto fra i due pannelli e immediato.
cmd.set_view(vista)
cmd.zoom("pieno", 4.6)          # un po' di margine per le due scritte
comune.etichette_radiali([("pieno and name OAB", "OAB  -0.50"),
                          ("pieno and name H11", "H11  +0.42")],
                         raggio=3.0, oggetto="pieno")
b = os.path.join(odir, "_lig_b.png")
comune.rendi(b, 1200, 880)

comune.componi(
    [(a, "A. Come esce dal cristallo"), (b, "B. Dopo Open Babel e acpype")],
    os.path.join(odir, "03-ligando.png"),
    didascalie=[
        "10 atomi pesanti, nessun idrogeno: i raggi X non\n"
        "li vedono.  Questi sono i nomi che ritrovi in\n"
        "jz4_crystal.pdb e in complex.gro",
        "22 atomi.  In giallo i 12 idrogeni aggiunti; in\n"
        "verde l'idrogeno ossidrilico, che porta la carica\n"
        "piu positiva di tutta la molecola",
    ],
    didascalia_h=118,
)
os.remove(a)
os.remove(b)
