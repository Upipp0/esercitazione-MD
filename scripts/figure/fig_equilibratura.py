"""Pagina 06: che cosa controlli dopo NVT e dopo NPT.

   python3 fig_equilibratura.py <nvt_T.xvg> <npt_rho.xvg> <uscita.png>

I due grafici che dicono se l'equilibratura e riuscita.  Sono disegnati
insieme di proposito: la temperatura si assesta in pochi picosecondi e
fluttua molto, la densita si assesta piu lentamente e fluttua pochissimo.
Sono due comportamenti diversi e vanno letti in modo diverso.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import grafici as g
import matplotlib.pyplot as plt
import numpy as np

t_xvg, rho_xvg, uscita = sys.argv[1], sys.argv[2], sys.argv[3]

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11.6, 4.3))

# --- NVT: la temperatura ---------------------------------------------------
d = g.leggi_xvg(t_xvg)
t, T = d[:, 0], d[:, 1]
ax1.plot(t, T, color=g.BLU, linewidth=1.3)
ax1.axhline(300, color=g.ATTENUATO, linewidth=1.1, linestyle=(0, (5, 4)))
ax1.annotate("300 K, il valore chiesto al termostato", (t[-1], 300),
             xytext=(-6, 9), textcoords="offset points", ha="right",
             fontsize=9.5, color=g.ATTENUATO)
g.stile(ax1, "tempo (ps)", "temperatura (K)",
        "NVT: la temperatura arriva subito")
ax1.annotate(f"media {T.mean():.1f} K\nscarto {T.std():.1f} K",
             (0.03, 0.06), xycoords="axes fraction", fontsize=10,
             color=g.INCHIOSTRO,
             bbox=dict(facecolor="white", edgecolor=g.TENUE, pad=5))

# --- NPT: la densita -------------------------------------------------------
d = g.leggi_xvg(rho_xvg)
t, r = d[:, 0], d[:, 1]
ax2.plot(t, r, color=g.ACQUA, linewidth=1.3)
meta = len(r) // 2
ax2.axhline(r[meta:].mean(), color=g.ATTENUATO, linewidth=1.1,
            linestyle=(0, (5, 4)))
g.stile(ax2, "tempo (ps)", "densita (kg/m$^3$)",
        "NPT: la densita si assesta e resta piatta")
ax2.annotate(f"media {r[meta:].mean():.0f} kg/m$^3$\nscarto {r[meta:].std():.1f}",
             (0.03, 0.06), xycoords="axes fraction", fontsize=10,
             color=g.INCHIOSTRO,
             bbox=dict(facecolor="white", edgecolor=g.TENUE, pad=5))
ax2.annotate("acqua pura a 300 K: 997", (t[-1], 997), xytext=(-6, -16),
             textcoords="offset points", ha="right", fontsize=9.5,
             color=g.ATTENUATO)
ax2.axhline(997, color=g.TENUE, linewidth=1.0)

fig.suptitle("I due controlli dell'equilibratura", x=0.012, ha="left",
             color=g.INCHIOSTRO, fontsize=13.5, fontweight="bold")
fig.tight_layout(rect=(0, 0, 1, 0.94))
g.salva(fig, uscita)
