"""Pagina 08: RMSD e RMSF, il concetto accanto al risultato.

   python3 fig_analisi.py <cartella_analisi> <cartella_img>

Si aspetta di trovare in <cartella_img> i pannelli molecolari prodotti da
fig_analisi_mol.py (_an_rmsd.png e _an_rmsf.png).
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import grafici as g
import matplotlib.pyplot as plt
import numpy as np

andir, odir = sys.argv[1], sys.argv[2]

# ==========================================================================
# 08-rmsd.png
# ==========================================================================
fig, ax = plt.subplots(figsize=(6.4, 5.4))
for nome, colore, etichetta in (("rmsd_backbone.xvg", g.BLU, "scheletro proteico"),
                                ("rmsd_jz4.xvg", g.ARANCIO, "ligando JZ4")):
    p = os.path.join(andir, nome)
    if not os.path.exists(p):
        continue
    d = g.leggi_xvg(p)
    ax.plot(d[:, 0], d[:, 1], color=colore, linewidth=1.8, label=etichetta)
    # le due curve finiscono quasi alla stessa altezza: le scritte dirette
    # vanno scostate a mano, altrimenti si sovrappongono
    dy = 11 if colore == g.ARANCIO else -11
    ax.annotate(etichetta, (d[-1, 0], d[-1, 1]), xytext=(6, dy),
                textcoords="offset points", color=colore, fontsize=9.5,
                va="center", fontweight="bold")
g.stile(ax, "tempo (ns)", "RMSD (nm)")
ax.legend(frameon=False, fontsize=9.5, labelcolor=g.ATTENUATO, loc="lower right")
ax.margins(x=0.20)
grafico = os.path.join(odir, "_rmsd_plot.png")
g.salva(fig, grafico)

g.affianca(
    [(os.path.join(odir, "_an_rmsd.png"), "A. Che cosa misura"),
     (grafico, "B. Che cosa viene fuori")],
    os.path.join(odir, "08-rmsd.png"),
    didascalia=(
        "A: il primo fotogramma (grigio) e l'ultimo (blu), sovrapposti sugli atomi CA.  L'RMSD e la distanza media\n"
        "fra atomi corrispondenti DOPO la sovrapposizione: senza, misurerebbe solo il fatto che la proteina si e spostata.\n"
        "B: una curva piatta vuol dire che la struttura tiene.  Il ligando (arancione) oscilla di piu della proteina perche\n"
        "e una molecola piccola in una tasca, non perche se ne stia andando."),
    didascalia_h=130,
)
os.remove(grafico)

# ==========================================================================
# 08-rmsf.png
# ==========================================================================
fig, ax = plt.subplots(figsize=(6.4, 5.4))
d = g.leggi_xvg(os.path.join(andir, "rmsf_residue.xvg"))
res, f = d[:, 0], d[:, 1]
ax.plot(res, f, color=g.BLU, linewidth=1.5)
ax.fill_between(res, f, color=g.BLU, alpha=0.08)

tasca = os.path.join(andir, "pocket.txt")
if os.path.exists(tasca):
    voluti = {int(float(x)) for x in open(tasca).read().split() if x.strip()}
    sel = np.isin(res.astype(int), sorted(voluti))
    ax.plot(res[sel], f[sel], "o", color=g.ACQUA, markersize=5,
            markeredgecolor="white", markeredgewidth=0.8, zorder=5,
            label="residui della tasca")
    ax.legend(frameon=False, fontsize=9.5, labelcolor=g.ATTENUATO, loc="upper left")

etichettati = []
for i in np.argsort(f)[::-1]:
    if len(etichettati) >= 4:
        break
    if any(abs(res[i] - res[j]) < 10 for j in etichettati):
        continue
    etichettati.append(i)
    ax.annotate(f"{int(res[i])}", (res[i], f[i]), xytext=(0, 6),
                textcoords="offset points", ha="center", fontsize=9,
                color=g.INCHIOSTRO)
ax.margins(y=0.16)
g.stile(ax, "numero di residuo", "RMSF (nm)")
ax.set_ylim(bottom=0)
grafico = os.path.join(odir, "_rmsf_plot.png")
g.salva(fig, grafico)

g.affianca(
    [(os.path.join(odir, "_an_rmsf.png"), "A. Lo stesso dato sulla struttura"),
     (grafico, "B. Lo stesso dato in grafico")],
    os.path.join(odir, "08-rmsf.png"),
    didascalia=(
        "A: il nastro e ingrossato e colorato dove l'RMSF e alto (arancione) e sottile dove e basso (blu).  Il ligando\n"
        "e la sfera verde.  B: lo stesso numero, residuo per residuo.  I picchi sono le estremita della catena e le anse\n"
        "in superficie; il minimo e il nucleo idrofobico, che e anche dove sta la tasca.  I residui che rivestono il sito\n"
        "(punti verdi) stanno quasi tutti sotto la media: una tasca sepolta e piu rigida del resto della proteina."),
    didascalia_h=130,
)
os.remove(grafico)
