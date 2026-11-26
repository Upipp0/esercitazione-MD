"""Pagina 07: come avanza l'integratore, e che cosa fa nstlist.

   python3 fig_integrazione.py <cartella_img>

Due schemi:
  07-integrazione.png  il salto della rana, e perche il passo non puo crescere
  07-nstlist.png       la lista dei vicini e il suo margine
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import grafici as g
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Circle, FancyArrowPatch

odir = sys.argv[1]

# ==========================================================================
# 07-integrazione.png
# ==========================================================================
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12.0, 4.4))

# --- a sinistra: lo schema del salto della rana ---------------------------
g.pulisci(ax1)
ax1.set_xlim(-0.6, 4.6)
ax1.set_ylim(-1.5, 1.75)
ax1.set_title("Il salto della rana", color=g.INCHIOSTRO, fontsize=12.5,
              fontweight="bold", loc="left", pad=10)

ax1.plot([-0.2, 4.4], [0, 0], color=g.TENUE, linewidth=1.4, zorder=1)
for k in range(5):
    ax1.plot([k], [0], marker="|", color=g.TENUE, markersize=14)

# posizioni sui passi interi, velocita sui mezzi passi
for k in range(5):
    ax1.plot(k, 0.62, "o", color=g.BLU, markersize=11, zorder=3)
    ax1.text(k, 0.95, f"$x_{{{k}}}$", ha="center", fontsize=12.5, color=g.BLU)
for k in range(4):
    ax1.plot(k + 0.5, -0.62, "o", color=g.ARANCIO, markersize=11, zorder=3)
    ax1.text(k + 0.5, -1.08, f"$v_{{{k}+\\frac{{1}}{{2}}}}$", ha="center",
             fontsize=11.5, color=g.ARANCIO)

for k in range(4):
    ax1.add_patch(FancyArrowPatch((k, 0.5), (k + 0.5, -0.5),
                                  arrowstyle="-|>", mutation_scale=13,
                                  color=g.ATTENUATO, linewidth=1.1,
                                  connectionstyle="arc3,rad=0.25", zorder=2))
    ax1.add_patch(FancyArrowPatch((k + 0.5, -0.5), (k + 1, 0.5),
                                  arrowstyle="-|>", mutation_scale=13,
                                  color=g.ATTENUATO, linewidth=1.1,
                                  connectionstyle="arc3,rad=0.25", zorder=2))

ax1.text(2.0, 1.45, "la forza aggiorna la velocita,\nla velocita aggiorna la posizione",
         ha="center", fontsize=10.5, color=g.ATTENUATO)
ax1.text(2.0, -1.42, "posizioni e velocita non sono mai allo stesso istante:\n"
                     "si scavalcano, da qui il nome",
         ha="center", fontsize=10, color=g.ATTENUATO)

# --- a destra: perche il passo e limitato ---------------------------------
# Il controllo vero non e "la curva sembra brutta" ma "l'energia totale si
# conserva".  Un oscillatore armonico integrato col salto della rana conserva
# l'energia finche dt < 2/omega; oltre, cresce in modo geometrico.  I numeri
# qui sotto escono dall'integrazione vera, non da un disegno.
omega = 1.0
limite = 2.0 / omega
for frazione, colore, etichetta in (
        (0.20, g.ACQUA, f"dt = {0.20:.2f} x limite"),
        (0.70, g.BLU, f"dt = {0.70:.2f} x limite"),
        (1.03, g.ROSSO, f"dt = {1.03:.2f} x limite  (instabile)")):
    dt = frazione * limite
    n = int(30.0 / dt)
    x, v = 1.0, 0.0
    tt, ee = [], []
    for k in range(n):
        v += -omega ** 2 * x * dt
        x += v * dt
        tt.append(k * dt)
        ee.append(0.5 * v ** 2 + 0.5 * omega ** 2 * x ** 2)
        if ee[-1] > 1e12:
            break
    ax2.semilogy(tt, ee, color=colore, linewidth=1.9, label=etichetta)

ax2.set_xlim(0, 30)
ax2.set_ylim(1e-1, 1e12)
g.stile(ax2, "tempo (unita arbitrarie)", "energia totale",
        "Il passo si giudica dall'energia")
ax2.legend(frameon=False, fontsize=9.5, labelcolor=g.ATTENUATO, loc="upper left")
ax2.annotate("L'energia totale deve restare costante.  Sopra il limite cresce\n"
             "di un fattore fisso a ogni passo: in poche centinaia di passi la\n"
             "simulazione e finita.  Il moto piu veloce del sistema e la\n"
             "vibrazione X-H, ed e lei a fissare il limite: congelarla con\n"
             "constraints = h-bonds e cio che porta il passo da 0,5 fs a 2 fs.",
             (0.97, 0.05), xycoords="axes fraction", ha="right", va="bottom",
             fontsize=9.5, color=g.ATTENUATO)

fig.tight_layout()
g.salva(fig, os.path.join(odir, "07-integrazione.png"))

# ==========================================================================
# 07-nstlist.png
# ==========================================================================
rng = np.random.default_rng(7)
fig, assi = plt.subplots(1, 2, figsize=(11.2, 5.0))
R_TAGLIO, R_LISTA = 1.0, 1.18

punti = rng.uniform(-1.75, 1.75, size=(150, 2))
punti = punti[np.linalg.norm(punti, axis=1) > 0.18][:110]
spostamento = rng.normal(0, 0.085, size=punti.shape)

for ax, pos, titolo in ((assi[0], punti, "quando la lista viene costruita"),
                        (assi[1], punti + spostamento,
                         "nstlist passi dopo, prima di rifarla")):
    g.pulisci(ax)
    ax.set_aspect("equal")
    ax.set_xlim(-1.85, 1.85)
    ax.set_ylim(-1.85, 1.85)
    ax.set_title(titolo, color=g.INCHIOSTRO, fontsize=12,
                 fontweight="bold", loc="left", pad=10)

    ax.add_patch(Circle((0, 0), R_LISTA, facecolor=g.ACQUA, alpha=0.10,
                        edgecolor=g.ACQUA, linewidth=1.6, linestyle=(0, (5, 4))))
    ax.add_patch(Circle((0, 0), R_TAGLIO, facecolor=g.BLU, alpha=0.10,
                        edgecolor=g.BLU, linewidth=1.8))

    d = np.linalg.norm(pos, axis=1)
    dentro = d <= R_TAGLIO
    margine = (d > R_TAGLIO) & (d <= R_LISTA)
    fuori = d > R_LISTA
    ax.plot(pos[fuori, 0], pos[fuori, 1], "o", color=g.TENUE, markersize=5.5)
    ax.plot(pos[margine, 0], pos[margine, 1], "o", color=g.ACQUA, markersize=6.5)
    ax.plot(pos[dentro, 0], pos[dentro, 1], "o", color=g.BLU, markersize=6.5)
    ax.plot(0, 0, "o", color=g.ARANCIO, markersize=12)

assi[0].annotate("$r_{taglio}$", (0.72, 0.72), fontsize=12, color=g.BLU)
assi[0].annotate("$r_{lista}$", (-1.5, 1.15), fontsize=12, color=g.ACQUA)

fig.suptitle("La lista dei vicini, e perche ha un margine",
             x=0.012, ha="left", color=g.INCHIOSTRO, fontsize=13.5,
             fontweight="bold")
fig.text(0.012, 0.015,
         "In blu gli atomi entro il raggio di taglio, in verde quelli nel margine, in grigio quelli "
         "ignorati.\nFra una ricostruzione e l'altra gli atomi si muovono: senza margine, qualcuno "
         "entrerebbe nel raggio\ndi taglio senza essere nella lista, e la sua forza andrebbe persa. "
         "GROMACS dimensiona il margine da solo,\na partire da verlet-buffer-tolerance; alzare "
         "nstlist allarga il margine, non peggiora l'accuratezza.",
         fontsize=10, color=g.ATTENUATO, va="bottom")
fig.tight_layout(rect=(0, 0.17, 1, 0.95))
g.salva(fig, os.path.join(odir, "07-nstlist.png"))
