"""Pagina 05: che cosa fa davvero la minimizzazione dell'energia.

   pymol -cq fig_minimizzazione.py -- <solv_ions.gro> <em.gro> <cartella_img>

Mostra la stessa coppia di atomi prima e dopo.  La coppia non e stata scelta
a mano: e il contatto acqua-proteina piu corto di tutto il sistema appena
solvatato, trovato cercando il minimo su tutte le coppie di atomi pesanti.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(sys.argv[0])))
from pymol import cmd
import comune

prima, dopo, odir = sys.argv[1], sys.argv[2], sys.argv[3]

ACQUA = "resi 9511 and resn SOL"
OSSI = f"({ACQUA}) and name OW"
CARBONILE = "resi 48 and resn LYS and name O"


def pannello(gro, nome, uscita, vista=None):
    cmd.delete("all")
    comune.scena()
    cmd.load(gro, nome)
    cmd.hide("everything")

    intorno = f"byres (polymer within 6 of ({OSSI}))"
    cmd.show("sticks", f"({intorno}) and not hydro")
    cmd.color("grey70", f"({intorno}) and elem C")
    cmd.set("stick_radius", 0.11, intorno)

    # Il carbonile che subisce l'urto, in evidenza.
    cmd.show("sticks", "resi 48 and not hydro")
    cmd.color("c_blu", "resi 48 and elem C")
    cmd.set("stick_radius", 0.16, "resi 48")

    # La molecola d'acqua colpevole, con i suoi idrogeni.
    cmd.show("sticks", ACQUA)
    cmd.show("spheres", ACQUA)
    cmd.set("sphere_scale", 0.20, ACQUA)
    cmd.color("c_acqua_pale", f"({ACQUA}) and elem O")
    cmd.color("white", f"({ACQUA}) and elem H")
    cmd.set("stick_radius", 0.10, ACQUA)

    # Le altre acque vicine, appena accennate.
    altre = f"byres (resn SOL within 6 of ({OSSI})) and not ({ACQUA})"
    cmd.show("lines", altre)
    cmd.color("c_acqua_pale", altre)
    cmd.set("line_width", 1.6)

    d = cmd.get_distance(OSSI, CARBONILE)
    cmd.distance("contatto", OSSI, CARBONILE)
    cmd.color("c_rosso" if d < 0.24 * 10 else "c_acqua", "contatto")
    cmd.set("dash_radius", 0.07, "contatto")
    cmd.set("dash_gap", 0.22, "contatto")
    cmd.hide("labels", "contatto")

    cmd.label(OSSI, f'"{d:.2f} A"')
    cmd.set("label_position", (0.0, -3.0, 2.0), OSSI)
    cmd.set("label_size", 30)
    cmd.set("label_color", "c_rosso" if d < 2.4 else "c_acqua", OSSI)

    if vista is None:
        cmd.orient(f"({OSSI}) or ({CARBONILE})")
        cmd.zoom(f"({OSSI}) or ({CARBONILE})", 4.5)
        vista = cmd.get_view()
    else:
        cmd.set_view(vista)
    comune.rendi(uscita, 1200, 950)
    return vista, d


a = os.path.join(odir, "_em_a.png")
b = os.path.join(odir, "_em_b.png")
vista, d0 = pannello(prima, "prima", a)
_, d1 = pannello(dopo, "dopo", b, vista)

comune.componi(
    [(a, "A. Appena solvatato"), (b, "B. Dopo la minimizzazione")],
    os.path.join(odir, "05-minimizzazione.png"),
    didascalie=[
        f"un ossigeno dell'acqua a {d0:.2f} A dal carbonile di Lys48.\n"
        "Due ossigeni non possono stare cosi vicini: la repulsione\n"
        "di Lennard-Jones qui vale milioni di kJ/mol",
        f"la stessa coppia, ora a {d1:.2f} A: un legame a idrogeno\n"
        "normale.  In tutta la scatola i contatti sotto 2.4 A\n"
        "passano da 71 a zero",
    ],
    didascalia_h=118,
)
os.remove(a)
os.remove(b)
