# 08 — Analisi

**Tempo: 40 minuti.**

Hai una traiettoria. Tre domande, in quest'ordine:

1. **È stabile?** — RMSD
2. **Che cosa si è mosso?** — RMSF
3. **Il ligando è rimasto legato, e da che cosa?** — legami a idrogeno

> Ogni comando di questa pagina funziona sul tuo `md.xtc` **oppure** su
> `reference/md_ref.xtc`, che è lo stesso sistema simulato per 5 ns. Usa prima
> il tuo. Se non è finito, o se vuoi statistiche migliori, cambia i nomi dei
> file — non cambia nient'altro. I comandi per la traiettoria di riferimento
> sono in fondo alla pagina.

```bash
cd ~/esercitazione-MD/run
mkdir -p analysis
```

---

## Passo 1: sistemare il contorno periodico

Prima di misurare qualunque cosa c'è un problema che sembra estetico e non lo
è.

Gli atomi sono memorizzati ripiegati dentro la scatola. Una molecola che sta su
una faccia ha alcuni atomi su un bordo e il resto sul bordo opposto:
chimicamente intatta, ma numericamente sparsa su 7,8 nm. Calcola un RMSD su
quella e ottieni numeri privi di senso. Peggio: la proteina diffonde lentamente,
quindi la "distanza percorsa" sarebbe dominata dall'intera molecola che
vagabonda, non da qualcosa che cambia forma.

Due rimedi, in un solo comando: ricomporre le molecole e togliere la
traslazione d'insieme.

Prima, un piccolo passo di contabilità. Il tuo `md.xtc` contiene solo i 2636
atomi di `Protein_JZ4` (pagina 07), mentre `md.tpr` ne descrive 33 382.
Costruisci un `.tpr` che corrisponda alla traiettoria:

```bash
printf 'Protein_JZ4\n' | gmx convert-tpr -s md.tpr -n index.ndx -o analysis/pl.tpr
```

```
Will write subset Protein_JZ4 of original tpx containing 2636 atoms
```

Quel `.tpr` ha i propri gruppi predefiniti — `Protein`, `Backbone`, `C-alpha`,
`JZ4` — e da qui in poi `index.ndx` non serve più.

```bash
printf 'Protein\nSystem\n' | gmx trjconv -s analysis/pl.tpr -f md.xtc \
       -o analysis/traj.xtc -pbc mol -center
```

| | |
|---|---|
| `-pbc mol` | rimetti insieme ogni **molecola intera**, giudicandola dal suo centro di massa |
| `-center` | centra il sistema sul primo gruppo che scegli (`Protein`) in ogni fotogramma |
| prima risposta `Protein` | su che cosa centrare |
| seconda risposta `System` | che cosa scrivere in uscita |

Fallo **prima** di qualunque altra analisi. Dimenticarlo è la causa singola più
frequente di un grafico di RMSD con salti impossibili dentro.

---

## Passo 2: RMSD — è stabile?

Scarto quadratico medio: prendi una struttura di riferimento, sovrapponi il
fotogramma a essa nel modo migliore possibile, e misura quanto gli atomi si
siano allontanati da dove erano.

$$
\mathrm{RMSD}(t) = \sqrt{\frac{1}{N}\sum_{i=1}^{N} \left| \mathbf{r}_i(t) - \mathbf{r}_i^{\mathrm{rif}} \right|^2 }
$$

La sovrapposizione è la parte importante. Senza, staresti misurando traslazione
e rotazione dell'intera proteina, che non dicono niente. Per questo `gmx rms`
fa **due** domande: su quali atomi sovrapporre, e quali atomi misurare.

### La proteina

```bash
printf 'Backbone\nBackbone\n' | gmx rms -s analysis/pl.tpr -f analysis/traj.xtc \
        -o analysis/rmsd_backbone.xvg -tu ns
```

Sovrapponi sullo scheletro, misura lo scheletro. Le catene laterali sono
escluse perché sono flessibili per natura e sommergerebbero il segnale che
vuoi, cioè se la *struttura terziaria* sta tenendo.

### Il ligando — e perché i due gruppi sono diversi

```bash
printf 'Backbone\nJZ4\n' | gmx rms -s analysis/pl.tpr -f analysis/traj.xtc \
        -o analysis/rmsd_jz4.xvg -tu ns
```

Leggilo con attenzione: **sovrapponi sullo scheletro della proteina, misura il
ligando.** Deliberatamente *non* stai sovrapponendo sul ligando. Sovrapporre
sul ligando direbbe se il ligando ha cambiato la propria forma — interessante
per una molecola flessibile, quasi privo di significato per una rigida come
questa.

Sovrapponendo sulla proteina e misurando il ligando poni la domanda che conta:
**il ligando si è spostato rispetto al suo sito di legame?** Una traccia piatta
significa che è rimasto dove il cristallografo lo aveva trovato. Un gradino
significa che è passato a un'altra posa. Una salita costante significa che se
ne sta andando.

---

## Passo 3: RMSF — che cosa si è mosso?

L'RMSD comprime l'intera struttura in un numero per fotogramma. L'RMSF fa
l'opposto: un numero per atomo, mediato su tutti i fotogrammi.

$$
\mathrm{RMSF}_i = \sqrt{ \big\langle\, \left| \mathbf{r}_i(t) - \langle \mathbf{r}_i \rangle \right|^2 \,\big\rangle_t }
$$

Nota il riferimento: la **posizione media dell'atomo stesso**, non la struttura
di partenza. L'RMSF misura quanto un atomo tremola attorno a dove sta di
solito.

```bash
printf 'Protein\n' | gmx rmsf -s analysis/pl.tpr -f analysis/traj.xtc \
        -o analysis/rmsf_residue.xvg -res
```

`-res` media su ciascun residuo, dando un valore per residuo invece che per
atomo — molto più leggibile.

> L'RMSF è la versione simulativa del **fattore B** cristallografico, che è
> anch'esso una misura di quanto è sfumata la posizione di un atomo. Sono
> legati da $B = \frac{8\pi^2}{3}\langle u^2 \rangle$. Confrontare il tuo
> profilo di RMSF con i fattori B del PDB originale è un vero test del fatto
> che la simulazione si stia comportando bene: le stesse anse devono risultare
> molli in entrambi.

Aspettati estremità e anse superficiali in cima, e il nucleo idrofobico in
fondo.

---

## Passo 4: legami a idrogeno — il ligando è tenuto?

Questa è la domanda per cui il sistema è stato costruito. La Leu99 è stata
accorciata ad alanina per creare una cavità; la Met102 è stata trasformata in
glutammina per metterci dentro un unico gruppo polare. Se il progetto funziona,
l'ossidrile del ligando deve trovare quella glutammina.

```bash
gmx hbond -f analysis/traj.xtc -s analysis/pl.tpr \
          -r 'resname JZ4' -t 'group Protein' \
          -num analysis/hbnum.xvg \
          -dist analysis/hbdist.xvg \
          -o analysis/hbond.ndx
```

> **Questo è il `gmx hbond` di GROMACS 2024 e successivi.** Prende selezioni
> con `-r` (riferimento) e `-t` (bersaglio) invece di chiederti di scegliere i
> gruppi di indice in modo interattivo. Quasi tutti i tutorial in rete mostrano
> la vecchia interfaccia, che adesso si chiama `gmx hbond-legacy`. Se un
> comando trovato altrove non funziona, il motivo è questo.

Deve riportare:

```
Selection 'resname JZ4' has 1 acceptors and 1 donors.
Selection 'Protein' has 480 acceptors and 255 donors.
```

Un donatore e un accettore sul ligando: è l'ossigeno ossidrilico `OAB`, che può
fare entrambe le cose. **Se dice 0 e 0**, ai tipi atomici del ligando manca il
numero atomico — vedi la pagina 03.

### Il criterio geometrico

GROMACS conta un legame a idrogeno quando

- la **distanza donatore–accettore** è sotto `-hbr`, predefinito **0,35 nm**, e
- l'angolo **accettore–donatore–idrogeno** è sotto `-hba`, predefinito **30°**.

Sono entrambe convenzioni, non fisica. Non esiste un confine netto fra un
legame a idrogeno e un contatto ravvicinato, e programmi diversi tracciano la
linea in posti diversi — motivo per cui un'occupanza citata senza il suo
criterio non è un numero confrontabile con niente.

### Quale residuo è?

`-o` ha scritto i legami trovati, come terne di indici atomici: **donatore,
idrogeno, accettore**.

```bash
head -4 analysis/hbond.ndx
```

Sulla traiettoria di riferimento da 5 ns si trovano due accettori:

```
[ hbonds_resname JZ4-Protein ]
   2624   2636   1571
   2624   2636   1616
```

Cercali nel tuo file di coordinate (ricorda: l'atomo *n* sta alla riga *n+2*):

```bash
for i in 2624 2636 1571 1616; do awk -v n=$i 'NR==n+2' complex.gro; done
```

```
  164JZ4    OAB 2624   2.341  -2.354  -0.434     <- donatore:  l'ossidrile del ligando
  164JZ4    H11 2636   2.374  -2.321  -0.516     <- idrogeno:  il suo H
   99ALA      O 1571   2.129  -2.235  -0.679     <- accettore: il carbonile di Ala99
  102GLN    OE1 1616   2.410  -2.167  -0.260     <- accettore: il carbonile di Gln102
```

**Gln102 e Ala99 — entrambi i siti mutati.** L'ossidrile del ligando dona un
legame a idrogeno alla catena laterale della glutammina che la mutazione M102Q
ha messo lì, e ogni tanto al carbonile dello scheletro dell'alanina lasciata
dalla mutazione L99A. La simulazione ha trovato l'interazione progettata senza
che le sia stato detto di cercarla.

> Sulla tua simulazione da 250 ps troverai quasi certamente **solo Gln102**. Il
> secondo partner compare solo con un campionamento più lungo. Tienilo a mente:
> è una dimostrazione concreta del fatto che un'interazione assente da una
> traiettoria breve non è un'interazione che non esiste.

---

## Passo 5: le figure

Lo script dei grafici ha bisogno di `numpy` e `matplotlib`, che non sono
installati a livello di sistema. Creati un ambiente virtuale: ci vogliono circa
dieci secondi.

```bash
python3 -m venv ~/mdvenv
~/mdvenv/bin/pip install --quiet numpy matplotlib
```

Poi segna quali residui delimitano il sito di legame, così il grafico dell'RMSF
può mostrarli:

```bash
gmx select -s analysis/pl.tpr -f analysis/traj.xtc \
    -select 'same residue as (group "Protein" and within 0.45 of resname JZ4)' \
    -on analysis/pocket.ndx

~/mdvenv/bin/python - <<'EOF'
gro = open("complex.gro").read().splitlines()
resid = [int(l[:5]) for l in gro[2:2 + int(gro[1])]]
idx = [int(v) for line in open("analysis/pocket.ndx")
       if not line.startswith("[") for v in line.split()]
res = sorted({resid[i - 1] for i in idx})
open("analysis/pocket.txt", "w").write("\n".join(map(str, res)) + "\n")
print(len(res), "residui delimitano il sito:", res)
EOF
```

Sulla traiettoria di riferimento:

```
27 residui delimitano il sito: [78, 83, 84, 85, 87, 88, 90, 91, 95, 96, 98, 99,
    100, 102, 103, 111, 112, 114, 115, 117, 118, 121, 129, 133, 138, 149, 153]
```

Il residuo 99 e il residuo 102 sono entrambi in quell'elenco — le due posizioni
mutate per creare questa cavità. (Sui tuoi 250 ps ne troverai meno, circa
diciotto: meno tempo significa meno residui che prima o poi si affacciano sul
sito.)

Adesso disegna:

```bash
~/mdvenv/bin/python ../scripts/plot_analysis.py analysis/
```

Scrive `analysis/analysis.png` e stampa i numeri che ci stanno dietro. Sulla
traiettoria di riferimento da 5 ns:

```
  scheletro proteico   RMSD  media 0.087 nm   seconda meta 0.090 +- 0.014 nm   max 0.148 nm
  ligando JZ4          RMSD  media 0.118 nm   seconda meta 0.121 +- 0.034 nm   max 0.238 nm
  residui del sito     RMSF  media 0.073 nm contro 0.091 nm per il resto
  piu mobili           residui 119 (0.21 nm), 162 (0.21 nm), 163 (0.19 nm), 76 (0.17 nm), 48 (0.16 nm)
  legami a idrogeno    media 0.61 per fotogramma   almeno uno nel 61% dei fotogrammi
  lunghezza del legame media 0.299 nm (il raggio di taglio usato era 0.35 nm)
```

Copia l'immagine sul tuo computer per guardarla:

```bash
# esegui questo in un terminale sul tuo portatile, non su Bombina
scp <tuo-username>@bombina.deb.unitus.it:~/esercitazione-MD/run/analysis/analysis.png .
```

---

## Che cosa dicono i quattro pannelli

**RMSD dello scheletro attorno a 0,09 nm e piatto.** La struttura terziaria non
sta cambiando. Per riferimento: sotto ~0,2 nm è una proteina globulare stabile;
una salita costante fino a 0,3–0,5 nm nell'arco di qualche nanosecondo
significa che qualcosa si sta srotolando o che un dominio si sta muovendo.

**RMSD del ligando attorno a 0,12 nm e piatto.** Sta fermo nel suo sito,
misurato rispetto alla proteina. Non ha ruotato, non è scivolato, non se n'è
andato.

**RMSF basso nel sito, più alto altrove.** I residui del sito sono in media a
0,073 nm contro 0,091 nm per il resto: la cavità è una delle parti più rigide
della proteina, che è quello che una tasca idrofobica sepolta dovrebbe essere.
I picchi sono le estremità della catena e le anse superficiali.

**Un legame a idrogeno, presente circa il 60 % del tempo, lungo 0,30 nm.** Non
è permanente, e questa è la risposta giusta e non una delusione: un singolo
legame a idrogeno a 300 K si rompe e si riforma continuamente. Quello che tiene
fermo questo ligando è soprattutto la sepoltura idrofobica; il legame con la
Gln102 è un extra specifico e intermittente.

---

## Domande a cui rispondere prima di andare via

1. Il tuo RMSD dello scheletro sale ripidamente nei primi picosecondi e poi si
   appiattisce. Perché? È equilibratura che non hai fatto, o è altro?
2. L'occupanza del legame a idrogeno è circa il 56 % sui tuoi 250 ps e il 61 %
   sui 5 ns di riferimento. Quale numero citeresti, e che cosa ti dice la
   differenza fra i due su quanto sono lunghi 250 ps?
3. L'RMSF è basso per i residui del sito. Dai due spiegazioni diverse — una
   sulla proteina, una sul ligando — e di' che cosa simuleresti per
   distinguerle.
4. Hai sovrapposto sullo scheletro e misurato il ligando. Che aspetto avrebbe
   avuto l'RMSD del ligando se avessi sovrapposto sul ligando, e a quale
   domanda avrebbe risposto?

---

## Usare la traiettoria di riferimento

Comandi identici, due nomi di file diversi:

```bash
mkdir -p ref_analysis
printf 'Protein\nSystem\n' | gmx trjconv -s ../reference/md_ref.tpr \
       -f ../reference/md_ref.xtc -o ref_analysis/traj.xtc -pbc mol -center

printf 'Backbone\nBackbone\n' | gmx rms  -s ../reference/md_ref.tpr -f ref_analysis/traj.xtc -o ref_analysis/rmsd_backbone.xvg -tu ns
printf 'Backbone\nJZ4\n'      | gmx rms  -s ../reference/md_ref.tpr -f ref_analysis/traj.xtc -o ref_analysis/rmsd_jz4.xvg      -tu ns
printf 'Protein\n'            | gmx rmsf -s ../reference/md_ref.tpr -f ref_analysis/traj.xtc -o ref_analysis/rmsf_residue.xvg  -res
gmx hbond -f ref_analysis/traj.xtc -s ../reference/md_ref.tpr -r 'resname JZ4' -t 'group Protein' \
          -num ref_analysis/hbnum.xvg -dist ref_analysis/hbdist.xvg -o ref_analysis/hbond.ndx
~/mdvenv/bin/python ../scripts/plot_analysis.py ref_analysis/
```

`reference/md_ref.tpr` è già ridotto a 2636 atomi, quindi non serve
`convert-tpr`. La figura finita e tutti i suoi file `.xvg` sono in
`reference/analysis/` se vuoi confrontare.

Lo stesso si ottiene in un colpo solo con lo script:

```bash
bash ../scripts/analyse.sh ../reference/md_ref.tpr ../reference/md_ref.xtc ref_analysis
```

---

Questa è l'esercitazione. Hai costruito un sistema proteina–ligando da una
struttura cristallografica, parametrizzato ciò che il campo di forze non
conosceva, equilibrato in due insiemi termodinamici, eseguito la dinamica e
misurato tre proprietà dal risultato. La fisica non diventa più difficile di
così — solo i sistemi lo diventano.
