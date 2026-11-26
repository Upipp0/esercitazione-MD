"""Pagina 04: la scatola, le condizioni al contorno periodiche, il solvente.

   pymol -cq fig_pbc.py -- <box.gro> <compatto.gro> <cartella_img>

Produce due immagini:
  04-scatola.png   la scatola vuota e la stessa riempita d'acqua
  04-pbc.png       la stessa scatola ripetuta: non c'e nessun bordo
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(sys.argv[0])))
from pymol import cmd
import comune

box, compatto, odir = sys.argv[1], sys.argv[2], sys.argv[3]


def soluto():
    cmd.show("cartoon", "polymer")
    cmd.color("c_proteina", "polymer")
    cmd.show("spheres", "resn JZ4")
    cmd.color("c_arancio", "resn JZ4 and elem C")
    cmd.set("sphere_scale", 1.0, "resn JZ4")


# ==========================================================================
# 04-scatola.png
# ==========================================================================
# La vista si fissa sul sistema solvatato, che e il piu grande: applicata poi
# alla scatola vuota fa vedere quanto spazio l'acqua andra a occupare.
comune.scena()
cmd.load(compatto, "piena")
cmd.hide("everything")
soluto()
cmd.show("spheres", "resn SOL and name OW")
cmd.color("c_acqua_pale", "resn SOL")
cmd.set("sphere_scale", 0.34, "resn SOL")
cmd.show("spheres", "resn NA or resn CL")
cmd.color("c_viola", "resn NA")
cmd.color("c_acqua", "resn CL")
cmd.set("sphere_scale", 0.5, "resn NA or resn CL")
cmd.orient("polymer")
cmd.turn("y", 15)
cmd.zoom("piena", 3.0)
vista = cmd.get_view()
b = os.path.join(odir, "_box_b.png")
comune.rendi(b, 1250, 1100)

cmd.delete("all")
comune.scena()
# cell_color va impostato PRIMA di mostrare la cella: il colore viene fissato
# quando l'oggetto grafico e costruito, non dopo.
cmd.set_color("c_cella", [0.42, 0.42, 0.45])
cmd.set("cell_color", "c_cella")
cmd.load(box, "vuota")
cmd.hide("everything")
soluto()
cmd.show("cell")
cmd.set_view(vista)
a = os.path.join(odir, "_box_a.png")
comune.rendi(a, 1250, 1100)

comune.componi(
    [(a, "A. Dopo gmx editconf"), (b, "B. Dopo gmx solvate e gmx genion")],
    os.path.join(odir, "04-scatola.png"),
    didascalie=[
        "2 636 atomi: proteina e ligando, al centro della scatola\n"
        "vuota.  Le linee sono la cella come la memorizza GROMACS,\n"
        "cioe triclina: non e questa la sua forma vera",
        "33 382 atomi.  Riempita d'acqua, la stessa cella mostra la\n"
        "forma che ha davvero: un dodecaedro rombico, il solido piu\n"
        "vicino a una sfera fra quelli che riempiono lo spazio",
    ],
    didascalia_h=118,
)
os.remove(a)
os.remove(b)

# ==========================================================================
# 04-pbc.png -- la stessa immagine, affiancata a se stessa
# ==========================================================================
# Non serve calcolare nulla: la periodicita vuol dire esattamente che la
# scatola e la sua copia sono la stessa cosa.  Ripetere l'immagine e quindi
# una rappresentazione onesta, e rende evidente che un atomo sul bordo ha
# vicini anche "fuori".
cmd.delete("all")
comune.scena()
cmd.load(compatto, "piena")
cmd.hide("everything")
soluto()
cmd.show("spheres", "resn SOL and name OW")
cmd.color("c_acqua_pale", "resn SOL")
cmd.set("sphere_scale", 0.34, "resn SOL")
cmd.set_view(vista)
cmd.zoom("all", 0.2)
t = os.path.join(odir, "_pbc_tile.png")
comune.rendi(t, 560, 560)

from PIL import Image, ImageDraw, ImageEnhance, ImageFont

cella = Image.open(t).convert("RGB")
w, h = cella.size
pallida = ImageEnhance.Brightness(ImageEnhance.Color(cella).enhance(0.35)).enhance(1.18)

tela = Image.new("RGB", (3 * w, 3 * h), "white")
for r in range(3):
    for c in range(3):
        tela.paste(cella if (r, c) == (1, 1) else pallida, (c * w, r * h))
d = ImageDraw.Draw(tela)
d.rectangle([w, h, 2 * w - 1, 2 * h - 1], outline=(37, 125, 224), width=5)
f = ImageFont.truetype(comune.GRASSETTO, 30)
d.text((w + 14, h + 10), "la scatola che simuli", font=f, fill=(37, 125, 224))
f2 = ImageFont.truetype(comune.NORMALE, 27)
d.text((16, 12), "tutte le altre sono la stessa scatola, non copie indipendenti",
       font=f2, fill=comune.ATTENUATO)
tela.save(t)

comune.componi(
    [(t, "Condizioni al contorno periodiche")],
    os.path.join(odir, "04-pbc.png"),
    didascalie=[
        "Un atomo che esce da una faccia rientra da quella opposta.  Non esiste un bordo, quindi\n"
        "nessuna molecola d'acqua si trova mai su una superficie: e questo che rende il sistema\n"
        "un liquido e non una goccia.  In cambio la proteina non deve mai arrivare a vedere la\n"
        "propria immagine, ed e per questo che editconf lascia 1,0 nm di margine.",
    ],
    didascalia_h=150,
)
os.remove(t)
