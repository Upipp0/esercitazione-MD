"""Le formule della guida, composte con LaTeX e salvate come immagini.

   python3 fig_formule.py <cartella_img>

Perche non scriverle direttamente in Markdown: GitHub interpreta una riga che
comincia con "+" come un elenco puntato, e una formula lunga spezzata su piu
righe perde proprio i segni "+".  Comporla con LaTeX risolve il problema e in
piu permette di colorare i termini, cosi la formula e la spiegazione che la
segue parlano la stessa lingua.
"""
import os
import shutil
import subprocess
import sys
import tempfile

odir = sys.argv[1]

PREAMBOLO = r"""
\documentclass[preview,border=10pt,varwidth=26cm]{standalone}
\usepackage{amsmath,amssymb}
\usepackage[dvipsnames]{xcolor}
\definecolor{legati}{HTML}{257DE0}
\definecolor{nonlegati}{HTML}{F47230}
\definecolor{inchiostro}{HTML}{191919}
\begin{document}
\color{inchiostro}
"""

FORMULE = {
    "formula-newton": r"""
\[
\Large
\mathbf{F}_i \;=\; -\nabla_i V(\mathbf{r}_1 \dots \mathbf{r}_N),
\qquad
m_i \ddot{\mathbf{r}}_i \;=\; \mathbf{F}_i
\]
""",
    "formula-campo-di-forze": r"""
\[
\large
\begin{aligned}
V \;=\;&
\underbrace{
  \textcolor{legati}{
  \sum_{\text{legami}} \tfrac{1}{2} k_b (r-r_0)^2
  \;+\; \sum_{\text{angoli}} \tfrac{1}{2} k_\theta (\theta-\theta_0)^2
  \;+\; \sum_{\text{diedri}} \tfrac{k_\phi}{2}\bigl[1+\cos(n\phi-\delta)\bigr]}
}_{\textcolor{legati}{\text{termini legati: tengono insieme la molecola}}}
\\[3.2ex]
+\;&
\underbrace{
  \textcolor{nonlegati}{
  \sum_{i<j} 4\epsilon_{ij}\Bigl[\bigl(\tfrac{\sigma_{ij}}{r_{ij}}\bigr)^{12}
  - \bigl(\tfrac{\sigma_{ij}}{r_{ij}}\bigr)^{6}\Bigr]
  \;+\; \sum_{i<j} \dfrac{q_i q_j}{4\pi\epsilon_0 r_{ij}}}
}_{\textcolor{nonlegati}{\text{termini non legati: tutto il resto}}}
\end{aligned}
\]
""",
    "formula-rmsd": r"""
\[
\Large
\mathrm{RMSD}(t) \;=\;
\sqrt{\frac{1}{N}\sum_{i=1}^{N}\bigl|\mathbf{r}_i(t)-\mathbf{r}_i^{\,\text{rif}}\bigr|^{2}}
\]
""",
    "formula-rmsf": r"""
\[
\Large
\mathrm{RMSF}_i \;=\;
\sqrt{\bigl\langle\,\bigl|\mathbf{r}_i(t)-\langle\mathbf{r}_i\rangle\bigr|^{2}\,\bigr\rangle_t}
\]
""",
    "formula-lennard-jones": r"""
\[
\Large
V_{\mathrm{LJ}} \;\propto\; \Bigl(\frac{\sigma}{r}\Bigr)^{12}
\]
""",
    "formula-discesa": r"""
\[
\Large
\mathbf{r}_{n+1} \;=\; \mathbf{r}_n
  + \frac{\mathbf{F}_n}{\max|\mathbf{F}_n|}\, h_n
\]
""",
}

def ritaglia(path, margine=26):
    """Toglie il bianco attorno alla formula.

    varwidth fissa la larghezza della pagina, non quella della formula:
    senza questo passaggio le immagini avrebbero margini enormi e diversi
    l'una dall'altra.
    """
    from PIL import Image, ImageChops

    im = Image.open(path).convert("RGB")
    sfondo = Image.new("RGB", im.size, (255, 255, 255))
    box = ImageChops.difference(im, sfondo).getbbox()
    if box is None:
        return
    x0, y0, x1, y1 = box
    im = im.crop((max(0, x0 - margine), max(0, y0 - margine),
                  min(im.width, x1 + margine), min(im.height, y1 + margine)))
    im.save(path)


if shutil.which("pdflatex") is None or shutil.which("pdftocairo") is None:
    sys.exit("servono pdflatex e pdftocairo (poppler-utils)")

for nome, corpo in FORMULE.items():
    with tempfile.TemporaryDirectory() as d:
        tex = os.path.join(d, "f.tex")
        open(tex, "w").write(PREAMBOLO + corpo + "\n\\end{document}\n")
        r = subprocess.run(["pdflatex", "-interaction=nonstopmode", "-halt-on-error",
                            "-output-directory", d, tex],
                           capture_output=True, text=True)
        if r.returncode != 0:
            print(f"ERRORE in {nome}:")
            print("\n".join(r.stdout.splitlines()[-18:]))
            continue
        subprocess.run(["pdftocairo", "-png", "-r", "260", "-singlefile",
                        os.path.join(d, "f.pdf"), os.path.join(odir, nome)],
                       check=True)
        ritaglia(os.path.join(odir, nome + ".png"))
        print("scritto", os.path.join(odir, nome + ".png"))
