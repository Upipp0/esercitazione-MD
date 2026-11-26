"""Pagina 01: che cosa c'e nella struttura di partenza.

   pymol -cq fig_proteina.py -- <complex.gro> <3HTB.pdb> <cartella_img>

Produce due immagini:
  01-proteina.png   la proteina intera e lo zoom sulla cavita
  01-altloc.png     i due conformeri alternativi della Gln102
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(sys.argv[0])))
from pymol import cmd
import comune

gro, pdb, odir = sys.argv[1], sys.argv[2], sys.argv[3]

# ==========================================================================
# 01-proteina.png
# ==========================================================================
comune.scena()
cmd.load(gro, "sys")
cmd.hide("everything")

cmd.show("cartoon", "polymer")
cmd.color("c_proteina", "polymer")
cmd.show("spheres", "resn JZ4")
cmd.color("c_arancio", "resn JZ4 and elem C")
cmd.color("c_rosso", "resn JZ4 and elem O")
cmd.set("sphere_scale", 1.0, "resn JZ4")

# I due residui che la mutagenesi ha cambiato.
mutati = "resi 99+102 and not hydro"
cmd.show("sticks", mutati)
cmd.color("c_blu", "resi 99+102 and elem C")
cmd.set("stick_radius", 0.20, mutati)

# --- pannello A: dove sta il ligando --------------------------------------
# Una superficie semitrasparente dice in un colpo solo quello che servirebbero
# tre frasi a spiegare: il ligando sta dentro, non in superficie.
cmd.set("surface_quality", 1)
cmd.show("surface", "polymer")
cmd.set("transparency", 0.55, "polymer")
cmd.set("surface_color", "grey80", "polymer")
cmd.hide("cartoon")                      # la superficie da sola e piu leggibile
cmd.set("sphere_scale", 1.25, "resn JZ4")
cmd.orient("polymer")
cmd.turn("y", -95)
cmd.turn("z", 10)
cmd.zoom("polymer", -6)
print("oggetti in scena:", cmd.get_names("all"))
a = os.path.join(odir, "_prot_a.png")
comune.rendi(a, 1250, 1250)
cmd.hide("surface")
cmd.show("cartoon", "polymer")
cmd.set("sphere_scale", 1.0, "resn JZ4")

# --- pannello B: la cavita da vicino --------------------------------------
# I residui che rivestono la cavita, in grigio sottile: servono a far vedere
# che la tasca e fatta quasi solo di catene laterali apolari.
tasca = "byres (polymer within 4.5 of resn JZ4) and not resi 99+102"
cmd.show("sticks", f"({tasca}) and not hydro and not name N+C+O")
cmd.color("grey65", f"({tasca}) and elem C")
cmd.set("stick_radius", 0.10, tasca)
cmd.set("cartoon_transparency", 0.80, "polymer")

cmd.show("sticks", "resn JZ4")
cmd.hide("spheres", "resn JZ4")
cmd.set("stick_radius", 0.17, "resn JZ4")

# Il legame a idrogeno che l'esercitazione va a cercare.
cmd.distance("hb", "resn JZ4 and name OAB", "resi 102 and name OE1")
cmd.color("c_acqua", "hb")
cmd.set("dash_radius", 0.055, "hb")
cmd.set("dash_gap", 0.30, "hb")
cmd.hide("labels", "hb")

for sel, testo, dove in (("resi 99 and name CB", "Ala99", (0.0, 2.2, 0.0)),
                         ("resi 102 and name CD", "Gln102", (1.5, 1.8, 0.0)),
                         ("resn JZ4 and name C13", "JZ4", (-1.0, -2.6, 0.0))):
    cmd.label(sel, f'"{testo}"')
    cmd.set("label_position", dove, sel)

cmd.orient("resn JZ4")
cmd.turn("y", 18)
cmd.zoom("resn JZ4", 4.2)
b = os.path.join(odir, "_prot_b.png")
comune.rendi(b, 1250, 1250)

comune.componi(
    [(a, "A. Il ligando e sepolto dentro la proteina"),
     (b, "B. La cavita, da vicino")],
    os.path.join(odir, "01-proteina.png"),
    didascalie=["lisozima T4, 163 residui, in grigio;\n"
                "il ligando (arancione) non tocca il solvente",
                "in blu i due residui mutati per creare la cavita;\n"
                "tratteggio verde: il legame a idrogeno da cercare"],
    didascalia_h=86,
)
os.remove(a)
os.remove(b)

# ==========================================================================
# 01-altloc.png -- i due conformeri alternativi
# ==========================================================================
cmd.delete("all")
comune.scena()
cmd.load(pdb, "xtal")
cmd.hide("everything")
cmd.show("cartoon", "polymer and resi 98-106")
cmd.color("c_proteina", "polymer")
cmd.set("cartoon_transparency", 0.55)

cmd.show("sticks", "resi 102 and not hydro")
cmd.color("c_blu", "resi 102 and alt A and elem C")
cmd.color("c_arancio", "resi 102 and alt B and elem C")
cmd.set("stick_radius", 0.17, "resi 102")

# Le due etichette vanno allontanate a mano: i due atomi NE2 distano meno di
# 2 A e le scritte si sovrapporrebbero.  Ciascuna prende il colore del proprio
# conformero, cosi non serve indovinare quale sia quale.
cmd.label("resi 102 and alt A and name NE2", '"conformero A"')
cmd.set("label_position", (3.2, 2.6, 2.0), "resi 102 and alt A and name NE2")
cmd.set("label_color", "c_blu", "resi 102 and alt A and name NE2")
cmd.label("resi 102 and alt B and name NE2", '"conformero B"')
cmd.set("label_position", (3.2, -2.8, 2.0), "resi 102 and alt B and name NE2")
cmd.set("label_color", "c_arancio", "resi 102 and alt B and name NE2")

cmd.orient("resi 102")
cmd.zoom("resi 102", 1.5)
c = os.path.join(odir, "_alt.png")
comune.rendi(c, 1500, 900)
comune.componi(
    [(c, "La stessa Gln102, modellata in due posizioni")],
    os.path.join(odir, "01-altloc.png"),
    didascalie=["nel cristallo questa catena laterale occupa due posizioni diverse. "
                "Una simulazione\nne vuole una sola: la pulizia della pagina 01 tiene "
                "il conformero A e butta il B."],
    didascalia_h=86,
)
os.remove(c)
