"""Stile condiviso dai grafici e dagli schemi della guida.

Gli stessi colori delle immagini molecolari, cosi una curva blu e sempre la
stessa cosa di un atomo blu.  Richiede numpy e matplotlib.
"""
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

BLU, ARANCIO, ACQUA = "#257de0", "#f47230", "#00b894"
GIALLO, VIOLA, ROSSO = "#f2a600", "#6a4ce2", "#ec4647"
INCHIOSTRO, ATTENUATO, TENUE = "#191919", "#666666", "#d8d8d8"


def leggi_xvg(path):
    """Un .xvg e fatto di colonne di numeri, con commenti '#' e comandi '@'."""
    righe = []
    for l in open(path):
        l = l.strip()
        if not l or l[0] in "#@&":
            continue
        try:
            righe.append([float(v) for v in l.split()])
        except ValueError:
            continue
    return np.array(righe)


def stile(ax, xlabel="", ylabel="", titolo="", griglia="y"):
    if titolo:
        ax.set_title(titolo, color=INCHIOSTRO, fontsize=12.5,
                     fontweight="bold", loc="left", pad=10)
    ax.set_xlabel(xlabel, color=ATTENUATO, fontsize=10.5)
    ax.set_ylabel(ylabel, color=ATTENUATO, fontsize=10.5)
    ax.tick_params(colors=ATTENUATO, labelsize=9.5, length=3)
    for lato in ("top", "right"):
        ax.spines[lato].set_visible(False)
    for lato in ("left", "bottom"):
        ax.spines[lato].set_color(TENUE)
    if griglia:
        ax.grid(axis=griglia, color=TENUE, linewidth=0.7, alpha=0.9)
    ax.set_axisbelow(True)


def pulisci(ax):
    """Toglie assi e cornice: per gli schemi, dove i numeri non servono."""
    ax.set_xticks([])
    ax.set_yticks([])
    for lato in ("top", "right", "bottom", "left"):
        ax.spines[lato].set_visible(False)


def salva(fig, path, dpi=165):
    fig.savefig(path, dpi=dpi, facecolor="white", bbox_inches="tight")
    plt.close(fig)
    print("scritto", path)


GRASSETTO = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
NORMALE = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"


def affianca(pannelli, uscita, didascalia="", titolo_h=50, didascalia_h=0,
             margine=18):
    """Affianca immagini gia pronte: [(percorso, etichetta), ...].

    Come comune.componi, ma senza PyMOL: serve negli script che girano col
    python di sistema.
    """
    from PIL import Image, ImageDraw, ImageFont

    imgs = [Image.open(p).convert("RGB") for p, _ in pannelli]
    h = max(i.height for i in imgs)
    larghezze = [int(i.width * h / i.height) for i in imgs]
    imgs = [i.resize((w, h), Image.LANCZOS) for i, w in zip(imgs, larghezze)]

    W = sum(larghezze) + (len(imgs) + 1) * margine
    H = titolo_h + h + didascalia_h + 2 * margine
    tela = Image.new("RGB", (W, H), "white")
    d = ImageDraw.Draw(tela)
    f_t = ImageFont.truetype(GRASSETTO, 32)
    f_c = ImageFont.truetype(NORMALE, 25)

    x = margine
    for (p, etichetta), im in zip(pannelli, imgs):
        if etichetta:
            d.text((x + 6, margine + 4), etichetta, font=f_t, fill=(25, 25, 25))
        tela.paste(im, (x, margine + titolo_h))
        x += im.width + margine
    if didascalia:
        d.text((margine + 6, margine + titolo_h + h + 8), didascalia,
               font=f_c, fill=(102, 102, 102))
    tela.save(uscita)
    print("composto", uscita, tela.size)
