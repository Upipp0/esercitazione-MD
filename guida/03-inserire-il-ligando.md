# 03 — Inserire il ligando

**Tempo: 30 minuti. È la pagina più difficile, ed è la più utile.**

---

## Il problema

`pdb2gmx` ha costruito la topologia della proteina con un solo comando, perché
amber99sb-ildn contiene una descrizione completa di tutti e venti gli
amminoacidi. Chiedigli di fare lo stesso per il 2-propilfenolo e ti dirà che
non ha mai sentito parlare di un residuo chiamato `JZ4`.

Il ligando non ha niente di speciale. Gli serve esattamente ciò che serviva
alla proteina — tipi atomici, cariche, legami, angoli, diedri — ma **nessuno li
ha mai scritti**, perché le piccole molecole possibili sono cento milioni e gli
amminoacidi venti.

Quindi il lavoro si divide in due:

1. **Procurarsi i parametri del ligando.** Fatto per te; spiegato qui sotto,
   così sai di che cosa ti stai fidando.
2. **Inserirli correttamente nella topologia.** Questo lo farai a mano, ed è
   dove quasi tutti commettono il primo errore.

---

## 1. Da dove vengono i parametri del ligando

I file sono in `input/`. Sono stati prodotti così (**non devi eseguire questi
comandi** — sono qui perché la provenienza non sia un mistero):

```bash
# aggiungi gli idrogeni che la struttura cristallografica non ha
obabel -ipdb jz4_crystal.pdb -omol2 -O jz4_h.mol2 -h

# assegna i tipi atomici GAFF2 e le cariche parziali AM1-BCC
acpype -i jz4_h.mol2 -b JZ4 -n 0 -a gaff2 -c bcc
```

Nel secondo comando si nascondono due decisioni.

**GAFF2** — il *General AMBER Force Field* — è la controparte di
amber99sb-ildn per le piccole molecole. Copre la chimica organica per *tipo
atomico*: `ca` è un carbonio aromatico, `c3` un carbonio sp³, `oh` un ossigeno
ossidrilico. I suoi parametri sono stati costruiti perché le molecole fatte con
questi tipi siano compatibili con le proteine AMBER. Usare un campo di forze
generale per il ligando e uno specializzato per la proteina è la pratica
normale, e funziona proprio perché i due sono stati progettati per essere
mescolati.

**AM1-BCC** è il modo in cui sono state ottenute le cariche parziali: un
calcolo quantistico semi-empirico veloce (AM1) sulla molecola, seguito da
correzioni di carica di legame calibrate per riprodurre le cariche che si
otterrebbero da un calcolo molto più costoso. Per una molecola di queste
dimensioni richiede circa un secondo.

> **Questo passo è l'anello debole di qualunque simulazione proteina–ligando.**
> I parametri della proteina sono stati raffinati per venticinque anni da molti
> gruppi. I parametri del ligando sono stati generati in un secondo da un
> programma che questa molecola non l'aveva mai vista. Quando una simulazione
> proteina–ligando dà un risultato che ti sorprende, sospetta prima di tutto
> dei parametri del ligando.

Guarda che cosa ne è uscito:

```bash
head -30 ../input/jz4.itp
```

```
[ moleculetype ]
;name            nrexcl
 JZ4              3

[ atoms ]
;   nr  type  resi  res  atom  cgnr     charge      mass
     1   c3     1   JZ4    C4    1    -0.092100     12.01000
     2   ca     1   JZ4    C7    2    -0.162000     12.01000
    ...
    10   oh     1   JZ4   OAB   10    -0.498099     16.00000
    ...
    22   ho     1   JZ4   H11   22     0.417000      1.00800 ; qtot 0.000
```

La stessa struttura `[ moleculetype ]` / `[ atoms ]` / `[ bonds ]` che hai letto
alla pagina 02. Ventidue atomi: i dieci pesanti più i dodici idrogeni aggiunti.
Nota che le cariche sommano esattamente a zero, e che l'atomo 10 (l'ossigeno
ossidrilico, −0,50) e l'atomo 22 (il suo idrogeno, +0,42) portano le cariche
più grandi della molecola. **Quei due atomi sono il legame a idrogeno che
cercherai alla pagina 08.**

A differenza della sezione `[ bonds ]` della proteina, questa ha dei numeri
dentro: acpype scrive i parametri esplicitamente invece di affidarsi alla
ricerca per tipo. Vanno bene entrambi i modi.

---

## 2. Inserirlo — tre cose devono essere d'accordo

Una topologia GROMACS si legge rigorosamente dall'alto in basso, ed è costruita
sul presupposto che **tutto sia dichiarato prima di essere usato**. Il ligando
va infilato in tre punti diversi, e tutti e tre devono essere coerenti:

| | dove | che cosa succede se sbagli |
|---|---|---|
| **a. tipi atomici** | `topol.top`, subito dopo l'include del campo di forze | `grompp` si ferma: "Atomtype c3 not found" |
| **b. la molecola** | `topol.top`, dopo il blocco della proteina | la molecola non esiste |
| **c. le coordinate** | `complex.gro` | `grompp` si ferma: numero di atomi non corrispondente — o, peggio, non si ferma |

### a. I tipi atomici vengono prima — e perché stanno in un file a parte

acpype ha scritto la molecola e i suoi tipi atomici in un unico file. Non può
funzionare, per una regola che GROMACS applica in modo assoluto:

> **Ogni blocco `[ atomtypes ]` deve comparire prima del primo
> `[ moleculetype ]` nella topologia assemblata.**

Il `[ moleculetype ]` della proteina è alla riga 23 di `topol.top`. Se i tipi
atomici del ligando arrivano insieme al ligando, alla riga 24 000, sono
largamente in ritardo.

Per questo il file è stato diviso in due: `input/jz4_atomtypes.itp` contiene il
blocco `[ atomtypes ]`, `input/jz4.itp` tutto il resto. Copiali entrambi:

```bash
cp ../input/jz4_atomtypes.itp ../input/jz4.itp ../input/posre_jz4.itp .
```

Adesso modifica `topol.top`. Trova queste due righe vicino all'inizio:

```
; Include forcefield parameters
#include "amber99sb-ildn.ff/forcefield.itp"
```

e aggiungi **subito dopo**:

```
; Tipi atomici del ligando -- devono precedere ogni [ moleculetype ]
#include "jz4_atomtypes.itp"
```

Apri il file che hai appena incluso e leggi il commento in cima. Spiega una
trappola che vale la pena conoscere:

```
[ atomtypes ]
;name  bond_type  at.num    mass     charge  ptype   sigma         epsilon
 c3      c3          6    12.01000  0.00000   A     3.39771e-01   4.51035e-01
 ca      ca          6    12.01000  0.00000   A     3.31521e-01   4.13379e-01
 oh      oh          8    16.00000  0.00000   A     3.24287e-01   3.89112e-01
 hc      hc          1     1.00800  0.00000   A     2.60018e-01   8.70272e-02
 ha      ha          1     1.00800  0.00000   A     2.62548e-01   6.73624e-02
 ho      ho          1     5.37925e-02 ...
```

La terza colonna, `at.num`, è il numero atomico, e **acpype non la scrive**.
Alla dinamica non importa: l'integratore usa la massa e i parametri di
Lennard-Jones, entrambi presenti. Ma significa che gli atomi del ligando non
hanno nessun elemento associato, e un programma di analisi che ragiona in
termini chimici non può funzionare.

In concreto: `gmx hbond` cerca donatori e accettori guardando azoto e ossigeno.
Senza `at.num` riporta

```
Selection 'resname JZ4' has 0 acceptors and 0 donors.
```

per una molecola che ha un gruppo ossidrilico — e poi ti dice che non ci sono
legami a idrogeno, cosa che potresti anche credere. Nel file che ti è stato
dato la colonna è stata aggiunta a mano. Se un giorno ti generi da solo i
parametri di un ligando, aggiungila: carbonio 6, azoto 7, ossigeno 8, idrogeno
1, zolfo 16, fosforo 15.

### b. La molecola, dopo la proteina

Più in basso in `topol.top`, trova:

```
; Include water topology
#include "amber99sb-ildn.ff/tip3p.itp"
```

e inserisci **prima**:

```
; Il ligando
#include "jz4.itp"

#ifdef POSRES_LIG
#include "posre_jz4.itp"
#endif
```

Il blocco `#ifdef` è inerte finché qualcosa non definisce `POSRES_LIG`. La
pagina 06 lo farà, da un file `.mdp`. `posre_jz4.itp` fissa i dieci atomi
pesanti del ligando, allo stesso modo in cui `posre.itp` fissa quelli della
proteina.

Poi trova `[ molecules ]` in fondo e aggiungi il ligando all'inventario:

```
[ molecules ]
; Compound        #mols
Protein_chain_A     1
JZ4                 1
```

> **L'ordine delle righe in `[ molecules ]` è l'ordine degli atomi nel file di
> coordinate.** Prima la proteina, poi il ligando — quindi le coordinate del
> ligando devono venire dopo quelle della proteina, che è quello che faremo
> adesso. Inverti l'uno senza invertire l'altro e GROMACS costruirà
> allegramente una topologia in cui i parametri della proteina si applicano
> agli atomi del ligando. Nessuno ti avviserà; la simulazione semplicemente
> esploderà — o, peggio, non esploderà.

Controlla il lavoro:

```bash
grep -n '#include\|^\[ molecule' topol.top
```

```
21:#include "amber99sb-ildn.ff/forcefield.itp"
24:#include "jz4_atomtypes.itp"             <- i tipi atomici...
26:[ moleculetype ]                         <- ...due righe prima della proteina
24833:#include "posre.itp"
24837:#include "jz4.itp"                    <- il ligando, dopo la proteina
24840:#include "posre_jz4.itp"
24844:#include "amber99sb-ildn.ff/tip3p.itp"
24854:#include "amber99sb-ildn.ff/ions.itp"
24860:[ molecules ]
```

La riga 24 prima della riga 26 è tutto il punto del passo (a). Se il tuo
include di `jz4_atomtypes.itp` sta da qualche parte sotto la riga 26, è troppo
tardi.

### c. Le coordinate

Adesso la topologia dice che ci sono 2636 atomi — 2614 di proteina, 22 di
ligando, in quest'ordine. `protein_processed.gro` ne ha 2614. Costruisci il
file corrispondente.

Questa è la modifica a mano di un `.gro` di cui ti avvertiva la pagina 02. Sia
il numero di atomi alla riga 2 sia la riga della scatola alla fine devono
sopravvivere:

```bash
head -2 protein_processed.gro          > complex.gro   # titolo e conteggio
sed -n '3,2616p' protein_processed.gro >> complex.gro   # i 2614 atomi di proteina
grep 'JZ4' ../input/jz4.gro            >> complex.gro   # i 22 atomi del ligando
tail -1 protein_processed.gro          >> complex.gro   # i vettori della scatola
sed -i '2s/.*/ 2636/'                     complex.gro   # correggi il conteggio
```

La riga 2616 è `2 + 2614`: due righe di intestazione, poi una riga per atomo.

Verifica — e verifica davvero, perché è il passo che corrompe in silenzio tutto
quello che viene dopo:

```bash
sed -n '2p' complex.gro                      # 2636
awk 'END{print NR-3}' complex.gro            # 2636  (totale meno 2 intestazioni e 1 scatola)
sed -n '2615,2618p' complex.gro              # la giunzione proteina/ligando
tail -1 complex.gro                          # ancora tre numeri di scatola
```

```
  163ASN    OC1 2613   0.566  -0.780  -0.053
  163ASN    OC2 2614   0.624  -0.616  -0.140
  164JZ4     C4 2615   2.429  -2.412  -0.007
  164JZ4     C7 2616   2.155  -2.721  -0.411
```

Il ligando è il residuo 164, con gli atomi numerati di seguito a quelli della
proteina. Quei numeri sono per comodità tua — GROMACS legge un `.gro`
nell'ordine delle righe — ma tenerli onesti è il modo in cui ti accorgerai di
un errore.

> **Da dove vengono gli idrogeni del ligando?** `input/jz4.gro` è l'output di
> acpype: i dieci atomi pesanti cristallografici, nelle loro posizioni
> cristallografiche, più dodici idrogeni costruiti da Open Babel. Gli atomi
> pesanti non si sono mossi, quindi il ligando è ancora nel sito in cui è stato
> trovato.

---

## Verifica che tutto regga

```bash
gmx grompp -f ../mdp/ions.mdp -c complex.gro -p topol.top -o check.tpr -maxwarn 1
```

`grompp` è il preprocessore di GROMACS: legge la topologia, le coordinate e un
file di impostazioni, risolve ogni `#include`, cerca ogni parametro e scrive un
unico file binario `.tpr` che contiene tutto il necessario per simulare. **È
anche l'unica cosa che ti dirà se l'ultima mezz'ora è stata fatta bene.**

Se arriva in fondo, topologia e coordinate sono d'accordo. Errori frequenti:

| messaggio | causa |
|---|---|
| `Atomtype c3 not found` | manca l'include di `jz4_atomtypes.itp`, o sta sotto il primo `[ moleculetype ]` |
| `number of coordinates in coordinate file does not match topology` | la riga 2 di `complex.gro`, o un atomo saltato |
| `No such moleculetype JZ4` | manca `#include "jz4.itp"`, o sta dopo `[ system ]` |
| `Atom index n in position_restraints out of bounds` | `posre_jz4.itp` incluso dentro il blocco della proteina invece che in quello del ligando |

```bash
rm check.tpr
```

---

Avanti: [04 — Scatola, acqua e ioni](04-scatola-acqua-ioni.md)
