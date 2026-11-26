"""Impostazioni condivise da tutte le immagini molecolari della guida.

Un solo schema di colori in tutta l'esercitazione, cosi lo stesso oggetto ha
sempre lo stesso colore: la proteina e grigia, il ligando arancione, i due
residui mutati blu, i legami a idrogeno verde acqua.

I colori vengono dalla stessa tavolozza della figura di analisi, scelta per
restare leggibile anche a chi non distingue rosso e verde.
"""
from pymol import cmd

BLU, ARANCIO, ACQUA = "#257de0", "#f47230", "#00b894"
GIALLO, VIOLA, ROSSO = "#f2a600", "#6a4ce2", "#ec4647"


def tavolozza():
    cmd.set_color("c_blu", _rgb(BLU))
    cmd.set_color("c_arancio", _rgb(ARANCIO))
    cmd.set_color("c_acqua", _rgb(ACQUA))
    cmd.set_color("c_giallo", _rgb(GIALLO))
    cmd.set_color("c_viola", _rgb(VIOLA))
    cmd.set_color("c_rosso", _rgb(ROSSO))
    cmd.set_color("c_proteina", [0.78, 0.78, 0.80])
    cmd.set_color("c_acqua_pale", [0.72, 0.82, 0.92])


def _rgb(h):
    h = h.lstrip("#")
    return [int(h[i:i + 2], 16) / 255.0 for i in (0, 2, 4)]


def scena(sfondo="white"):
    """Le impostazioni di resa usate da ogni figura."""
    tavolozza()
    cmd.bg_color(sfondo)
    cmd.set("ray_opaque_background", 1)
    cmd.set("antialias", 2)
    cmd.set("ray_trace_mode", 0)
    cmd.set("ray_shadows", 0)
    cmd.set("specular", 0.15)
    cmd.set("ambient", 0.22)
    cmd.set("direct", 0.55)
    cmd.set("reflect", 0.25)
    cmd.set("depth_cue", 0)
    cmd.set("ray_trace_fog", 0)
    cmd.set("orthoscopic", 1)
    cmd.set("cartoon_transparency", 0.0)
    cmd.set("stick_radius", 0.14)
    cmd.set("dash_gap", 0.28)
    cmd.set("dash_radius", 0.045)
    cmd.set("label_size", 20)
    cmd.set("label_color", "black")
    cmd.set("label_outline_color", "white")
    cmd.set("label_font_id", 7)
    cmd.set("cartoon_oval_length", 0.9)
    cmd.set("cartoon_rect_length", 1.2)


def rendi(path, larghezza=1800, altezza=1350):
    cmd.ray(larghezza, altezza)
    cmd.png(path, dpi=200)
    print("scritto", path)


# --------------------------------------------------------------------------
# Composizione di piu pannelli in una sola figura.
# Serve PIL, che PyMOL porta gia con se.
# --------------------------------------------------------------------------
GRASSETTO = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
NORMALE = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
INCHIOSTRO = (25, 25, 25)
ATTENUATO = (102, 102, 102)


def componi(pannelli, uscita, colonne=None, titolo_h=52, didascalia_h=0,
            margine=18, didascalie=None):
    """Affianca i PNG di `pannelli` = [(percorso, etichetta), ...].

    Ogni pannello riceve la sua etichetta sopra; `didascalie` aggiunge una
    riga piu piccola sotto ciascuno.
    """
    from PIL import Image, ImageDraw, ImageFont

    imgs = [Image.open(p).convert("RGB") for p, _ in pannelli]
    etichette = [e for _, e in pannelli]
    colonne = colonne or len(imgs)
    righe = (len(imgs) + colonne - 1) // colonne

    w = max(i.width for i in imgs)
    h = max(i.height for i in imgs)
    cella_h = titolo_h + h + didascalia_h
    W = colonne * w + (colonne + 1) * margine
    H = righe * cella_h + (righe + 1) * margine

    tela = Image.new("RGB", (W, H), "white")
    d = ImageDraw.Draw(tela)
    f_tit = ImageFont.truetype(GRASSETTO, 34)
    f_cap = ImageFont.truetype(NORMALE, 26)

    for k, im in enumerate(imgs):
        r, c = divmod(k, colonne)
        x = margine + c * (w + margine)
        y = margine + r * (cella_h + margine)
        if etichette[k]:
            d.text((x + 6, y + 6), etichette[k], font=f_tit, fill=INCHIOSTRO)
        tela.paste(im, (x + (w - im.width) // 2, y + titolo_h))
        if didascalie and didascalie[k]:
            d.text((x + 6, y + titolo_h + h + 6), didascalie[k],
                   font=f_cap, fill=ATTENUATO)

    tela.save(uscita)
    print("composto", uscita, tela.size)


def etichette_radiali(coppie, raggio=2.6, oggetto="all", minima=2.2,
                      per_carattere=0.62, altezza=2.0):
    """Mette ogni etichetta spingendola verso l'esterno della molecola,
    scostandola se la sua scritta finisce sopra una gia messa.

    Le posizioni delle etichette in PyMOL sono scostamenti sullo SCHERMO, non
    nello spazio del modello: per sapere dove sta "fuori" serve la matrice
    della vista.  cmd.get_view() la restituisce in ordine per COLONNE, quindi
    la prima riga e (V[0], V[3], V[6]) e la seconda (V[1], V[4], V[7]).

    Il controllo di sovrapposizione e fra RETTANGOLI, non fra punti: una
    scritta come "Gln102" e larga sei caratteri e due etichette i cui punti
    di ancoraggio distano 4 A si sovrappongono lo stesso.
    """
    import math

    V = cmd.get_view()

    def schermo(p):
        return (V[0] * p[0] + V[3] * p[1] + V[6] * p[2],
                V[1] * p[0] + V[4] * p[1] + V[7] * p[2])

    c = schermo(cmd.centerofmass(oggetto))
    messe = []          # (x, y, mezza_larghezza)
    for sel, testo in coppie:
        try:
            p = schermo(cmd.get_atom_coords(sel))
        except Exception:
            continue
        mezza = max(minima, len(testo) * per_carattere) / 2.0
        dx, dy = p[0] - c[0], p[1] - c[1]
        n = math.hypot(dx, dy) or 1.0
        base = math.atan2(dy, dx)
        scelta = None
        for giro in (0, 25, -25, 50, -50, 80, -80, 110, -110, 145, -145, 180):
            for r in (raggio, raggio * 1.35, raggio * 1.75):
                th = base + math.radians(giro)
                q = (p[0] + r * math.cos(th), p[1] + r * math.sin(th))
                libero = all(abs(q[0] - mx) > mezza + mw or abs(q[1] - my) > altezza
                             for mx, my, mw in messe)
                if libero:
                    scelta = (th, r, q)
                    break
            if scelta:
                break
        if scelta is None:
            th, r = base, raggio * 1.75
            q = (p[0] + r * math.cos(th), p[1] + r * math.sin(th))
        else:
            th, r, q = scelta
        messe.append((q[0], q[1], mezza))
        cmd.label(sel, f'"{testo}"')
        cmd.set("label_position", (r * math.cos(th), r * math.sin(th), 2.0), sel)
