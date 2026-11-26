# 04 — Scatola, acqua e ioni

**Tempo: 20 minuti.** Tre comandi e un'idea importante.

---

## Perché serve una scatola

Hai 2636 atomi. Supponi di circondarli semplicemente d'acqua e di simulare
quella goccia. Una goccia abbastanza grande da coprire questa proteina ha una
frazione enorme di molecole in superficie, e una molecola d'acqua in superficie
si trova in un ambiente completamente diverso da una nel bulk: ha vicini da un
lato solo, viene tirata verso l'interno, si orienta. La tua proteina passerebbe
la simulazione accanto a un'interfaccia con il vuoto che nella provetta non
esiste.

La soluzione standard sono le **condizioni al contorno periodiche** (PBC).
Si dichiara che la scatola riempie lo spazio ripetendosi all'infinito nelle tre
direzioni. Un atomo che esce dalla faccia destra rientra da quella sinistra.
Non ci sono superfici, perché non c'è un bordo: ogni molecola d'acqua ha un
insieme completo di vicini.

```
   ┌─────┬─────┬─────┐
   │ ·o· │ ·o· │ ·o· │     la stessa scatola, ripetuta.  Un atomo sul bordo
   ├─────┼─────┼─────┤     destro è vicino di uno sul bordo sinistro della
   │ ·o· │ ·O· │ ·o· │     copia accanto -- cioè di se stesso.
   ├─────┼─────┼─────┤
   │ ·o· │ ·o· │ ·o· │
   └─────┴─────┴─────┘
```

Non hai ottenuto qualcosa per niente. Il sistema è ora **infinito e
perfettamente periodico**, cosa che le soluzioni vere non sono. Ne seguono
subito due conseguenze.

**La convenzione dell'immagine minima.** Ogni atomo interagisce con la copia
più vicina di ogni altro atomo, e con una sola copia. Perché questo sia ben
definito, il raggio di taglio oltre il quale le interazioni sono ignorate deve
essere **minore di metà della dimensione più piccola della scatola**. Il nostro
raggio sarà 1,0 nm, quindi la scatola deve misurare almeno 2,0 nm. Ne misurerà
7,8.

**La proteina non deve vedere se stessa.** Se la scatola è troppo stretta, la
proteina interagisce con la propria immagine periodica, che è l'equivalente
simulativo di un cristallo anziché di una soluzione. La garanzia abituale è
almeno 1,0 nm d'acqua fra la proteina e la faccia della scatola — cioè 2,0 nm
fra una proteina e la sua copia più vicina. È ciò che significa `-d 1.0` qui
sotto. (Nemmeno questo è perfetto: la periodicità sopprime i moti con
lunghezza d'onda maggiore della scatola. Per una proteina ripiegata su qualche
nanosecondo è una preoccupazione minore.)

---

## Definire la scatola

```bash
gmx editconf -f complex.gro -o box.gro -c -d 1.0 -bt dodecahedron
```

| opzione | |
|---|---|
| `-c` | metti il soluto al centro della scatola |
| `-d 1.0` | lascia almeno 1,0 nm fra il soluto e ogni faccia |
| `-bt dodecahedron` | la forma della scatola |

```
    system size :  4.069  4.192  5.073 (nm)
    diameter    :  5.849               (nm)
new box vectors :  7.849  7.849  7.849 (nm)
new box volume  : 341.95               (nm^3)
```

### Perché un dodecaedro rombico e non un cubo

Una proteina globulare è grosso modo una sfera. Un cubo che lasci a una sfera
1 nm di margine in ogni direzione spreca gli otto spigoli in acqua che non fa
nulla se non costarti tempo.

Un **dodecaedro rombico** è la forma di cella che più si avvicina a una sfera
pur continuando a riempire lo spazio. A parità di distanza minima fra immagini
ha il **71 % del volume del cubo** — qui 342 nm³ invece di 484. Simulerai circa
4500 molecole d'acqua in meno a parità esatta di fisica, cioè quasi un 30 % di
risparmio su ogni passo della simulazione.

È la decisione sulle prestazioni che costa meno in tutta l'esercitazione, ed è
presa prima che sia stato eseguito un solo passo di dinamica.

> GROMACS memorizza internamente un dodecaedro come cella triclina — per questo
> i "box vectors" stampati sembrano un cubo. Non allarmarti se una struttura
> che estrarrai più avanti sembra deformata: `gmx trjconv -pbc mol` la rimette
> a posto per la visualizzazione (pagina 08).

---

## Aggiungere l'acqua

```bash
gmx solvate -cp box.gro -cs spc216.gro -o solv.gro -p topol.top
```

| opzione | |
|---|---|
| `-cp` | il soluto, nella sua scatola |
| `-cs` | il solvente con cui riempire. `spc216.gro` è un cubetto pre-equilibrato di 216 molecole d'acqua distribuito con GROMACS; viene impilato e ritagliato per riempire la scatola |
| `-p` | **la topologia, che viene modificata sul posto** |

```
Adding line for 10294 solvent molecules with resname (SOL) to topology file
```

Controlla che cosa ha fatto:

```bash
tail -5 topol.top
```

```
[ molecules ]
; Compound        #mols
Protein_chain_A     1
JZ4                 1
SOL             10294
```

`gmx solvate` ha aggiunto per te una riga a `[ molecules ]`. È l'unico punto in
cui un programma GROMACS modifica la tua topologia senza che glielo si chieda,
ed è il motivo per cui il file si passa con `-p`.

> `spc216.gro` è una scatola di acqua SPC, ma il *modello* usato è quello che
> `topol.top` include — tip3p, dalla pagina 02. Le coordinate sono un punto di
> partenza; i parametri vengono dalla topologia. I due modelli hanno geometria
> quasi identica, ed è per questo che un file solo serve per entrambi.

---

## Aggiungere gli ioni

Il sistema porta al momento una carica netta di +6 dovuta alla proteina. Con
l'elettrostatica che stiamo per usare (PME, pagina 05), una scatola con carica
netta non è semplicemente sbagliata: è sbagliata *in modo condizionato*. Il
metodo impone in silenzio un fondo uniforme di carica neutralizzante, e
l'energia che ottieni dipende dalla dimensione della scatola. Neutralizza come
si deve, con degli ioni.

Gli ioni vanno messi dove c'è già dell'acqua, quindi servono due passi:
costruire un `.tpr`, e poi lasciare che `genion` scambi molecole d'acqua con
ioni.

```bash
gmx grompp -f ../mdp/ions.mdp -c solv.gro -p topol.top -o ions.tpr -maxwarn 1
```

`-maxwarn 1` serve qui, e devi sapere esattamente quale avvertimento stai
zittendo:

```
WARNING 1 [file topol.top]:
  You are using Ewald electrostatics in a system with net charge. This can
  lead to severe artifacts, such as ions moving into regions with low
  dielectric, due to the uniform background charge.
```

È l'avvertimento che descrive il problema che stiamo per risolvere. Zittirlo
*qui* è corretto. Zittire gli avvertimenti per abitudine è il modo in cui si
fanno girare simulazioni rotte per settimane. Dopo `genion` il sistema è neutro
e `-maxwarn` non si usa più da nessuna parte in questa esercitazione.

```bash
echo SOL | gmx genion -s ions.tpr -o solv_ions.gro -p topol.top \
                      -pname NA -nname CL -neutral -conc 0.15
```

| opzione | |
|---|---|
| `-pname NA`, `-nname CL` | quali ioni |
| `-neutral` | aggiungi esattamente i controioni che servono a portare a zero la carica netta |
| `-conc 0.15` | *e poi* aggiungi NaCl fino a 0,15 mol/L |
| `echo SOL \|` | risponde alla domanda interattiva "quale gruppo posso sostituire?" — sempre il solvente, mai la proteina |

```
Replacing 68 solute molecules in topology file (topol.top) by 31 NA and 37 CL ions.
```

Trentasette cloruri: trentuno dal sale, sei per cancellare il +6 della
proteina. Lo 0,15 M è la forza ionica fisiologica — all'incirca quella del
siero e del citoplasma. Le catene laterali cariche in superficie sono schermate
dentro una cellula, e devono esserlo anche qui.

```bash
tail -6 topol.top
sed -n 2p solv_ions.gro
```

```
[ molecules ]
Protein_chain_A     1
JZ4                 1
SOL             10226
NA                 31
CL                 37
```
```
33382
```

**33 382 atomi.** Di questi, 2636 — l'otto per cento — sono la cosa che stai
studiando. Questo rapporto è normale ed è la ragione principale per cui la
dinamica molecolare è costosa.

---

Avanti: [05 — Minimizzazione dell'energia](05-minimizzazione.md)
