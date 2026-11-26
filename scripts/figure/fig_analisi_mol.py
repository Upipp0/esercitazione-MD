"""Pagina 08: i pannelli molecolari dell'analisi.

   pymol -cq fig_analisi_mol.py -- <primo.pdb> <ultimo.pdb> <rmsf_residue.xvg> <cartella_img>

Produce:
  _an_rmsd.png     primo e ultimo fotogramma sovrapposti
  _an_rmsf.png     la proteina ingrossata dove si muove di piu
  08-contatti.png  che cosa tiene fermo il ligando
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(sys.argv[0])))
from pymol import cmd
import comune

primo, ultimo, rmsf_xvg, odir = sys.argv[1:5]

# ==========================================================================
# _an_rmsd.png -- che cosa misura l'RMSD
# ==========================================================================
comune.scena()
cmd.load(primo, "primo")
cmd.load(ultimo, "ultimo")
cmd.hide("everything")

# La sovrapposizione e il cuore dell'RMSD: senza, si misurerebbe solo il
# fatto che la proteina ha traslato e ruotato.
cmd.align("ultimo and name CA", "primo and name CA")

for og, col in (("primo", "c_proteina"), ("ultimo", "c_blu")):
    cmd.show("cartoon", f"{og} and polymer")
    cmd.color(col, f"{og} and polymer")
    cmd.show("sticks", f"{og} and resn JZ4 and not hydro")
cmd.color("grey70", "primo and resn JZ4 and elem C")
cmd.color("c_arancio", "ultimo and resn JZ4 and elem C")
cmd.set("stick_radius", 0.17, "resn JZ4")
# il ligando e minuscolo rispetto alla proteina: a sfere si vede
cmd.show("spheres", "resn JZ4")
cmd.set("sphere_scale", 0.55, "resn JZ4")
cmd.set("cartoon_transparency", 0.35, "primo")

cmd.orient("primo and polymer")
cmd.turn("y", -95)
cmd.zoom("primo and polymer", 1.5)
comune.rendi(os.path.join(odir, "_an_rmsd.png"), 1150, 1050)

# ==========================================================================
# _an_rmsf.png -- dove si muove
# ==========================================================================
cmd.delete("all")
comune.scena()
cmd.load(ultimo, "prot")
cmd.hide("everything")

# L'RMSF per residuo finisce nel fattore B, e il "putty" lo trasforma in
# spessore: il nastro si gonfia dove la proteina si muove di piu.
rmsf = {}
for riga in open(rmsf_xvg):
    riga = riga.strip()
    if not riga or riga[0] in "#@&":
        continue
    try:
        res, val = riga.split()[:2]
        rmsf[int(float(res))] = float(val)
    except ValueError:
        continue
print("letti", len(rmsf), "residui dal file RMSF")

cmd.alter("prot and polymer", "b = rmsf.get(int(resi), 0.0)", space={"rmsf": rmsf})
cmd.show("cartoon", "prot and polymer")
cmd.cartoon("putty", "prot and polymer")
cmd.set("cartoon_putty_scale_min", 0.5)
cmd.set("cartoon_putty_scale_max", 3.5)
cmd.set("cartoon_putty_radius", 0.35)
cmd.set("cartoon_putty_transform", 0)
cmd.spectrum("b", "blue_white_orange", "prot and polymer and name CA")
cmd.show("spheres", "prot and resn JZ4")
cmd.color("c_acqua", "prot and resn JZ4")
cmd.set("sphere_scale", 0.8, "prot and resn JZ4")

cmd.orient("prot and polymer")
cmd.turn("y", -95)
cmd.zoom("prot and polymer", 1.5)
comune.rendi(os.path.join(odir, "_an_rmsf.png"), 1150, 1050)

# ==========================================================================
# 08-contatti.png -- che cosa tiene fermo il ligando
# ==========================================================================
cmd.delete("all")
comune.scena()
cmd.load(ultimo, "f")
cmd.hide("everything")

tasca = "byres (polymer within 4.5 of resn JZ4)"
cmd.show("sticks", f"({tasca}) and not hydro")
cmd.color("grey72", f"({tasca}) and elem C")
cmd.set("stick_radius", 0.10, tasca)
cmd.show("cartoon", "polymer")
cmd.set("cartoon_transparency", 0.88)
cmd.color("c_proteina", "polymer")

cmd.show("sticks", "resn JZ4")
cmd.color("c_arancio", "resn JZ4 and elem C")
cmd.color("c_rosso", "resn JZ4 and elem O")
cmd.set("stick_radius", 0.18, "resn JZ4")

# I due residui che accettano il legame a idrogeno: in blu, come nella
# pagina 01, e piu spessi del resto della tasca.
cmd.color("c_blu", "resi 99+102 and elem C")
cmd.set("stick_radius", 0.17, "resi 99+102")

for n, sel in enumerate(("resi 102 and name OE1", "resi 99 and name O")):
    if cmd.count_atoms(sel):
        cmd.distance(f"hb{n}", "resn JZ4 and name OAB", sel)
        cmd.color("c_acqua", f"hb{n}")
        cmd.set("dash_radius", 0.06, f"hb{n}")
        cmd.set("dash_gap", 0.26, f"hb{n}")
        cmd.hide("labels", f"hb{n}")

# I contatti idrofobici: carbonio contro carbonio sotto 4 A, con nessuno dei
# due attaccato a un azoto o a un ossigeno.  Sono loro a seppellire il
# ligando, e sono molti piu dei legami a idrogeno.
lig_c = "resn JZ4 and elem C and not (neighbor elem O)"
prot_c = f"({tasca}) and elem C and not (neighbor (elem N+O))"
cmd.select("vicini", f"({prot_c}) within 4.0 of ({lig_c})")
coppie = cmd.find_pairs(lig_c, "vicini", cutoff=4.0)

conteggio, visti = {}, set()
for n, ((o1, i1), (o2, i2)) in enumerate(coppie):
    if i2 in visti:
        continue
    visti.add(i2)
    cmd.distance(f"ph{n}", f"index {i1}", f"index {i2}")
    cmd.color("grey35", f"ph{n}")
    cmd.set("dash_radius", 0.040, f"ph{n}")
    cmd.set("dash_gap", 0.38, f"ph{n}")
    cmd.hide("labels", f"ph{n}")
    for a in cmd.get_model(f"index {i2}").atom:
        conteggio[(a.resn, a.resi)] = conteggio.get((a.resn, a.resi), 0) + 1
print("contatti idrofobici disegnati:", len(visti), "su", len(conteggio), "residui")

# Etichette solo dove servono: i due accettori del legame a idrogeno piu i
# due residui idrofobici che toccano il ligando in piu punti.  La tasca ha
# quattordici residui, ma quattordici nomi su un'immagine larga venti
# angstrom non si leggono: gli altri restano grigi e senza nome.
primi = sorted(conteggio.items(), key=lambda kv: -kv[1])[:2]
da_etichettare = [("resi 102 and name CD", "Gln102"), ("resi 99 and name CB", "Ala99")]
for (resn, resi), _ in primi:
    if resi in ("99", "102"):
        continue
    sel = f"resi {resi} and name CB"
    if cmd.count_atoms(sel):
        da_etichettare.append((sel, f"{resn.capitalize()}{resi}"))
cmd.set("label_size", 22)
comune.etichette_radiali(da_etichettare, raggio=5.0, oggetto="resn JZ4",
                         minima=3.0, per_carattere=0.55, altezza=2.6)

cmd.orient("resn JZ4")
cmd.turn("y", 25)
cmd.zoom("resn JZ4", 6.5)
m = os.path.join(odir, "_contatti.png")
comune.rendi(m, 1700, 1250)
comune.componi(
    [(m, "Che cosa tiene fermo il ligando")],
    os.path.join(odir, "08-contatti.png"),
    didascalie=[
        "Tratteggio verde: i legami a idrogeno che gmx hbond conta, dall'ossidrile del ligando\n"
        "a Gln102 e ad Ala99.  Tratteggio grigio sottile: i contatti idrofobici, carbonio contro\n"
        "carbonio sotto 4 A.  Sono questi, non il legame a idrogeno, a fare la maggior parte del\n"
        "lavoro: il legame a idrogeno c'e solo in sei fotogrammi su dieci, i contatti ci sono sempre.",
    ],
    didascalia_h=150,
)
os.remove(m)
