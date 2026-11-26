#!/usr/bin/env python3
"""Trasforma i file .xvg scritti da GROMACS in una figura e in un riepilogo.

    python3 plot_analysis.py analysis/

Legge quelli che trova in quella cartella e salta gli altri:

    rmsd_backbone.xvg   RMSD dello scheletro proteico      (gmx rms)
    rmsd_jz4.xvg        RMSD del ligando nel tempo         (gmx rms)
    rmsf_residue.xvg    RMSF per residuo                   (gmx rmsf -res)
    hbnum.xvg           legami a idrogeno nel tempo        (gmx hbond -num)
    hbdist.xvg          istogramma delle loro lunghezze    (gmx hbond -dist)
    pocket.txt          residui che delimitano il sito     (facoltativo, gmx select)

Richiede numpy e matplotlib, nient'altro.
"""
import argparse
import os
import sys

import numpy as np
import matplotlib

matplotlib.use("Agg")          # nessuno schermo su un nodo di login
import matplotlib.pyplot as plt

# Colori scelti perche le due curve di RMSD restino distinguibili anche a chi
# non distingue rosso e verde; ogni serie e inoltre etichettata sulla curva
# stessa, cosi niente dipende dal solo colore.
BLUE, ORANGE, AQUA = "#257de0", "#f47230", "#00b894"
INK, MUTED, FAINT = "#191919", "#666666", "#d8d8d8"


def read_xvg(path):
    """Un file .xvg e fatto di colonne di numeri, con commenti '#' e comandi
    '@' per grace.  Non serve sapere altro per leggerlo."""
    rows = []
    with open(path) as fh:
        for line in fh:
            line = line.strip()
            if not line or line[0] in "#@&":
                continue
            try:
                rows.append([float(v) for v in line.split()])
            except ValueError:
                continue
    if not rows:
        raise ValueError(f"{path}: no numeric data")
    return np.array(rows)


def style(ax, xlabel, ylabel, title):
    ax.set_title(title, color=INK, fontsize=11, fontweight="bold", loc="left", pad=8)
    ax.set_xlabel(xlabel, color=MUTED, fontsize=9)
    ax.set_ylabel(ylabel, color=MUTED, fontsize=9)
    ax.tick_params(colors=MUTED, labelsize=8, length=3)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    for side in ("left", "bottom"):
        ax.spines[side].set_color(FAINT)
    ax.grid(axis="y", color=FAINT, linewidth=0.6, alpha=0.8)
    ax.set_axisbelow(True)


def panel_rmsd(ax, d, notes):
    """Due curve su un solo asse: condividono le unita (nm), quindi un asse
    solo e la scelta giusta."""
    drawn = False
    for fname, colour, label in (("rmsd_backbone.xvg", BLUE, "scheletro proteico"),
                                 ("rmsd_jz4.xvg", ORANGE, "ligando JZ4")):
        p = os.path.join(d, fname)
        if not os.path.exists(p):
            continue
        a = read_xvg(p)
        t, r = a[:, 0], a[:, 1]
        ax.plot(t, r, color=colour, linewidth=1.8, label=label)
        # Etichetta diretta in fondo alla curva, cosi l'identita non dipende
        # solo dal quadratino della legenda.
        ax.annotate(label, (t[-1], r[-1]), xytext=(4, 0),
                    textcoords="offset points", color=colour,
                    fontsize=8, va="center", fontweight="bold")
        half = len(r) // 2
        notes.append(f"{label:<20} RMSD  media {r.mean():.3f} nm   "
                     f"seconda meta {r[half:].mean():.3f} +- {r[half:].std():.3f} nm   "
                     f"max {r.max():.3f} nm")
        drawn = True
    if not drawn:
        ax.text(0.5, 0.5, "nessun dato RMSD", ha="center", color=MUTED,
                transform=ax.transAxes)
        return
    style(ax, "tempo (ns)", "RMSD (nm)", "Quanto si e mosso?")
    ax.legend(frameon=False, fontsize=8, labelcolor=MUTED, loc="lower right")
    ax.margins(x=0.22)


def panel_rmsf(ax, d, notes):
    p = os.path.join(d, "rmsf_residue.xvg")
    if not os.path.exists(p):
        ax.text(0.5, 0.5, "nessun dato RMSF", ha="center", color=MUTED,
                transform=ax.transAxes)
        return
    a = read_xvg(p)
    res, f = a[:, 0], a[:, 1]
    ax.plot(res, f, color=BLUE, linewidth=1.4)
    ax.fill_between(res, f, color=BLUE, alpha=0.07)

    pocket = os.path.join(d, "pocket.txt")
    if os.path.exists(pocket):
        want = {int(float(x)) for x in open(pocket).read().split() if x.strip()}
        sel = np.isin(res.astype(int), sorted(want))
        if sel.any():
            ax.plot(res[sel], f[sel], "o", color=AQUA, markersize=5,
                    markeredgecolor="white", markeredgewidth=0.8,
                    label="delimita il sito del ligando", zorder=5)
            ax.legend(frameon=False, fontsize=8, labelcolor=MUTED, loc="upper left")
            notes.append(f"{'residui del sito':<20} RMSF  media {f[sel].mean():.3f} nm "
                         f"contro {f[~sel].mean():.3f} nm per il resto")

    # Etichetta i residui piu mobili: un grafico di 163 valori con ogni numero
    # stampato e illeggibile, quindi solo quelli che vale la pena leggere
    # ricevono un'etichetta, e due picchi sovrapposti ne ricevono una sola.
    labelled = []
    for i in np.argsort(f)[::-1]:
        if len(labelled) >= 5:
            break
        if any(abs(res[i] - res[j]) < 8 for j in labelled):
            continue
        labelled.append(i)
        ax.annotate(f"{int(res[i])}", (res[i], f[i]), xytext=(0, 5),
                    textcoords="offset points", ha="center",
                    fontsize=7.5, color=INK)
    ax.margins(y=0.14)
    style(ax, "numero di residuo", "RMSF (nm)", "Quali parti si muovono di piu?")
    top = np.argsort(f)[-5:][::-1]
    notes.append(f"{'piu mobili':<20} residui " +
                 ", ".join(f"{int(res[i])} ({f[i]:.2f} nm)" for i in top))


def panel_hbnum(ax, d, notes):
    p = os.path.join(d, "hbnum.xvg")
    if not os.path.exists(p):
        ax.text(0.5, 0.5, "nessun dato sui legami", ha="center", color=MUTED,
                transform=ax.transAxes)
        return
    a = read_xvg(p)
    t, n = a[:, 0] / 1000.0, a[:, 1]          # ps -> ns
    # Un conteggio e un intero che salta, quindi va disegnato a gradini e non
    # come una curva continua che passa per valori che non assume mai.
    ax.step(t, n, where="post", color=AQUA, linewidth=1.6)
    ax.axhline(n.mean(), color=MUTED, linewidth=1.0, linestyle=(0, (4, 3)))
    ax.annotate(f"media {n.mean():.2f}", (t[0], n.mean()), xytext=(2, 4),
                textcoords="offset points", ha="left", fontsize=8, color=MUTED,
                bbox=dict(facecolor="white", edgecolor="none", pad=1.0))
    ax.set_ylim(-0.15, max(1.3, n.max() * 1.25))
    ax.set_yticks(range(0, int(max(1, n.max())) + 2))
    style(ax, "tempo (ns)", "legami a idrogeno",
          "Il ligando e tenuto da un legame a idrogeno?")
    occ = 100.0 * (n > 0).sum() / len(n)
    notes.append(f"{'legami a idrogeno':<20} media {n.mean():.2f} per fotogramma   "
                 f"almeno uno nel {occ:.0f}% dei fotogrammi   max {int(n.max())}")


def panel_hbdist(ax, d, notes):
    p = os.path.join(d, "hbdist.xvg")
    if not os.path.exists(p):
        ax.text(0.5, 0.5, "nessun dato sulle lunghezze", ha="center", color=MUTED,
                transform=ax.transAxes)
        return
    a = read_xvg(p)
    r, c = a[:, 0], a[:, 1]
    ax.fill_between(r, c, step="mid", color=AQUA, alpha=0.25)
    ax.step(r, c, where="mid", color=AQUA, linewidth=1.4)
    style(ax, "distanza donatore-accettore (nm)", "conteggio",
          "Quanto e stretto quel legame?")
    # L'istogramma parte da zero, ma sotto ~0,25 nm non si trova mai nulla:
    # mostra solo la parte che contiene dati.
    nz = np.nonzero(c)[0]
    if len(nz):
        ax.set_xlim(max(0.0, r[nz[0]] - 0.015), r[nz[-1]] + 0.015)
    if c.sum() > 0:
        mean = float((r * c).sum() / c.sum())
        ax.axvline(mean, color=MUTED, linewidth=1.0, linestyle=(0, (4, 3)))
        ax.annotate(f"{mean:.3f} nm", (mean, c.max()), xytext=(5, 0),
                    textcoords="offset points", fontsize=8, color=MUTED,
                    va="top", bbox=dict(facecolor="white", edgecolor="none", pad=1.0))
        notes.append(f"{'lunghezza del legame':<20} media {mean:.3f} nm "
                     f"(il raggio di taglio usato era 0.35 nm)")


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("dir", nargs="?", default="analysis",
                    help="cartella con i file .xvg (predefinito: analysis)")
    ap.add_argument("-o", "--out", default=None,
                    help="immagine di uscita (predefinito: <dir>/analysis.png)")
    ap.add_argument("--separate", action="store_true",
                    help="scrivi anche un PNG per ciascun pannello")
    args = ap.parse_args()

    d = args.dir
    if not os.path.isdir(d):
        sys.exit(f"cartella inesistente: {d}")
    out = args.out or os.path.join(d, "analysis.png")

    notes = []
    fig, axes = plt.subplots(2, 2, figsize=(11.0, 7.4))
    fig.patch.set_facecolor("white")
    panel_rmsd(axes[0][0], d, notes)
    panel_rmsf(axes[0][1], d, notes)
    panel_hbnum(axes[1][0], d, notes)
    panel_hbdist(axes[1][1], d, notes)
    fig.suptitle("Lisozima T4 L99A/M102Q + 2-propilfenolo (JZ4)",
                 color=INK, fontsize=12.5, fontweight="bold", x=0.012, ha="left")
    fig.tight_layout(rect=(0, 0, 1, 0.955))
    fig.savefig(out, dpi=150, facecolor="white")
    print(f"scritto {out}")

    if args.separate:
        for name, fn in (("rmsd", panel_rmsd), ("rmsf", panel_rmsf),
                         ("hbnum", panel_hbnum), ("hbdist", panel_hbdist)):
            f1, a1 = plt.subplots(figsize=(6.0, 3.8))
            f1.patch.set_facecolor("white")
            fn(a1, d, [])
            f1.tight_layout()
            p = os.path.join(d, f"{name}.png")
            f1.savefig(p, dpi=150, facecolor="white")
            plt.close(f1)
            print(f"scritto {p}")

    # I numeri dietro la figura, cosi nulla va letto a occhio da un pixel.
    print("\n" + "-" * 72)
    for line in notes:
        print("  " + line)
    print("-" * 72)


if __name__ == "__main__":
    main()
