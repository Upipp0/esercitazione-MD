# 02 — La topologia della proteina

**Tempo: 30 minuti.**

È qui che la struttura smette di essere un elenco di coordinate e diventa
qualcosa con della fisica attaccata.

---

## Eseguire pdb2gmx

```bash
gmx pdb2gmx -f protein.pdb \
            -o protein_processed.gro \
            -p topol.top \
            -i posre.itp \
            -ff amber99sb-ildn \
            -water tip3p
```

| opzione | |
|---|---|
| `-f` | la proteina ripulita della pagina 01 |
| `-o` | coordinate in uscita, nel formato proprio di GROMACS |
| `-p` | **la topologia** — l'output che conta |
| `-i` | file dei vincoli posizionali, usato alla pagina 06 |
| `-ff` | quale campo di forze |
| `-water` | quale modello d'acqua |

Deve finire con:

```
Now there are 163 residues with 2614 atoms
There are 7252 dihedrals,  522 impropers, 4751 angles
          6847 pairs,     2634 bonds and     0 virtual sites
Total mass 18512.384 a.m.u.
Total charge 6.000 e
```

Tre numeri su cui fermarsi.

**2614 atomi, da 1300.** `pdb2gmx` ha aggiunto 1314 idrogeni. Sa dove metterli
perché il campo di forze contiene, per ogni residuo, l'elenco di quali idrogeni
esistono e a quale atomo pesante ciascuno è legato.

**Carica totale +6.** A pH neutro questa proteina porta una carica netta di +6:
più arginine e lisine che aspartati e glutammati. Non è un errore, ma va
gestito — una scatola periodica carica è non fisica con l'elettrostatica che
stiamo per usare. La pagina 04 aggiunge sei ioni cloruro.

**Zero siti virtuali.** Niente di esotico; lo segnalo solo perché un numero
diverso da zero significherebbe che il campo di forze ha introdotto punti di
interazione privi di massa.

### Le due scelte che hai appena fatto

`-ff amber99sb-ildn` e `-water tip3p` non sono impostazioni da accettare a
occhi chiusi.

**amber99sb-ildn** è un campo di forze per proteine della famiglia AMBER. `99`
è l'anno del set di parametri, `sb` indica che la catena principale è stata
riparametrizzata, e `ildn` che i rotameri delle catene laterali di isoleucina,
leucina, aspartato e asparagina sono stati riparametrizzati di nuovo nel 2010.
È una scelta standard e ben collaudata per proteine ripiegate. Altri distribuiti
con GROMACS (`charmm27`, `oplsaa`, la famiglia `gromos`, i più recenti
`amber14sb`/`amber19sb`) sarebbero tutti difendibili; quello che **non** è
difendibile è mescolarli.

**tip3p** è un modello d'acqua: tre punti, un ossigeno con una carica e due
idrogeni, rigido, non polarizzabile. È grezzo ed è veloce, ed è il modello
insieme al quale sono stati parametrizzati i parametri proteici AMBER — che è
la vera ragione per usarlo qui. **Campi di forze e modelli d'acqua vanno in
coppia.** Abbinare una proteina AMBER a un modello d'acqua con cui non è stata
parametrizzata è un modo comune e silenzioso di ottenere risposte sbagliate.

> **Se pdb2gmx fallisce:** le cause abituali sono un atomo che non riconosce
> (qualcosa avanzato dalla pulizia), due atomi nello stesso punto (una posizione
> alternativa che hai dimenticato di togliere), o un residuo che non sa
> chiamare. Il messaggio di errore nomina il residuo e l'atomo. Torna alla
> pagina 01.

---

## Che cosa c'è dentro topol.top

```bash
grep -n '^\[\|^#include' topol.top
```

```
20: ; Include forcefield parameters
21: #include "amber99sb-ildn.ff/forcefield.itp"
23: [ moleculetype ]
27: [ atoms ]
2807: [ bonds ]
5444: [ pairs ]
12294: [ angles ]
17048: [ dihedrals ]
24303: [ dihedrals ]
24830: #include "posre.itp"
24834: #include "amber99sb-ildn.ff/tip3p.itp"
24844: #include "amber99sb-ildn.ff/ions.itp"
24846: [ system ]
24850: [ molecules ]
```

Venticinquemila righe, ma solo sei idee.

### `#include` — il file è assemblato da pezzi

La riga 21 tira dentro l'intero campo di forze: ogni tipo atomico, ogni
lunghezza di legame, ogni barriera diedrale. La tua topologia non contiene
quei numeri; contiene i *nomi* dei parametri, e l'include fornisce i valori.
**L'ordine degli include è determinante**, e la pagina 03 parla in gran parte
di questo.

### `[ moleculetype ]` — un blocco per ogni tipo di molecola

```
[ moleculetype ]
; Name            nrexcl
Protein_chain_A     3
```

Dichiara una molecola che si chiama `Protein_chain_A`. Tutto ciò che segue,
fino al prossimo `[ moleculetype ]`, la descrive.

`nrexcl 3` significa: **non calcolare interazioni non legate fra atomi separati
da tre legami o meno.** Quegli atomi sono già tenuti dai termini di legame,
angolo e diedro; aggiungerci sopra una repulsione di Lennard-Jones sarebbe
contare due volte. È anche il motivo per cui esiste una sezione `[ pairs ]`: le
coppie 1-4 (esattamente a tre legami di distanza) sono escluse dal calcolo non
legato normale e poi rimesse con intensità ridotta, perché i parametri diedrali
sono stati ricavati così.

### `[ atoms ]` — una riga per atomo

```
;   nr   type  resnr residue  atom   cgnr     charge       mass
     1     N3      1    MET      N      1     0.1592      14.01
     2      H      1    MET     H1      2     0.1984      1.008
```

| | |
|---|---|
| `nr` | numero dell'atomo — **è l'ordine in cui deve stare il file di coordinate** |
| `type` | il tipo atomico del campo di forze. `N3` non è "azoto", è "il tipo di azoto che AMBER chiama N3", il che ne fissa i parametri di van der Waals |
| `residue`, `atom` | nomi, per comodità tua e per i gruppi di indice |
| `cgnr` | gruppo di carica — un raggruppamento ereditato dal passato, irrilevante con gli schemi di taglio moderni |
| `charge` | la carica parziale, in unità di carica elementare |
| `mass` | in u.m.a. |

Scorri fino in fondo alla sezione e troverai `; qtot 6` — un totale progressivo
che conferma il +6.

### `[ bonds ]`, `[ angles ]`, `[ dihedrals ]` — la connettività

```
[ bonds ]
;  ai    aj funct
    1     2     1
```

L'atomo 1 è legato all'atomo 2, con funzione di tipo 1 (una molla armonica).
**Qui non ci sono numeri.** Nessuna lunghezza di equilibrio, nessuna costante di
forza. GROMACS guarda i *tipi* degli atomi 1 e 2 — `N3` e `H` — e trova i
parametri per quella coppia nel campo di forze incluso. La topologia dichiara
la chimica; il campo di forze dichiara la fisica.

È esattamente il meccanismo che sfrutteremo alla pagina successiva, ed è anche
il meccanismo che fallisce rumorosamente se i tipi atomici di un ligando non
sono stati dichiarati.

### `[ system ]` e `[ molecules ]` — l'inventario

```
[ system ]
Protein

[ molecules ]
; Compound        #mols
Protein_chain_A     1
```

`[ molecules ]` è la distinta della scatola di simulazione: quali
`[ moleculetype ]` sono presenti e quanti di ciascuno. **L'ordine delle righe
qui deve corrispondere all'ordine degli atomi nel file di coordinate**, e il
totale deve corrispondere al numero di atomi. Diventerà di cinque righe entro
la fine della pagina 04.

### posre.itp

```bash
head -8 posre.itp
wc -l posre.itp     # 1301 atomi vincolati + intestazione
```

Una riga per ogni atomo pesante, ciascuna dice "tieni questo atomo dov'è con
una molla da 1000 kJ mol⁻¹ nm⁻²". Nota che cosa *non* vincola: gli idrogeni che
`pdb2gmx` ha appena costruito, liberi di trovarsi la propria posizione. Non
serve fino alla pagina 06.

---

## Il file .gro, e in che cosa differisce da un PDB

```bash
head -3 protein_processed.gro
tail -2 protein_processed.gro
```

```
                           <- riga 1: un titolo libero
 2614                      <- riga 2: IL NUMERO DI ATOMI
    1MET      N    1   0.556  -1.596  -0.893
  ...
  163ASN    OC2 2614   0.624  -0.616  -0.140
   4.06907   4.19267   5.07333     <- ultima riga: LA SCATOLA
```

Anche qui ogni riga di atomo è a formato fisso:

```
    1MET      N    1   0.556  -1.596  -0.893
|---||---||----||---||------||------||------|
 1-5  6-10 11-15 16-20  21-28   29-36   37-44
resnr resname atom  nr    x       y       z
```

e può portare tre campi in più, di 8 caratteri ciascuno, con la velocità.

### Le differenze che contano

| | PDB | GRO |
|---|---|---|
| **unità** | ångström | **nanometri** |
| **riga 2** | niente di speciale | **il numero di atomi**, e deve essere giusto |
| **ultima riga** | niente di speciale | **i vettori della scatola**, sempre presenti |
| **velocità** | non si possono scrivere | colonne extra opzionali |
| **elemento, occupanza, fattore B** | sì | **no** |
| **identificativo di catena** | sì | **no** |
| **precisione** | 3 decimali in Å = 0,001 Å | 3 decimali in nm = 0,01 Å |

Tre di queste hanno conseguenze pratiche oggi.

**Un fattore dieci.** Ogni coordinata in `protein_processed.gro` è un decimo di
quella del PDB. Confondere i due produce una struttura dieci volte più grande,
il che fallisce in modo spettacolare e quindi innocuo.

**Niente catene.** GROMACS non traccia le catene nelle coordinate. Una proteina
a più catene diventa più voci `[ moleculetype ]`; l'identità vive nella
topologia, non nella struttura.

**La riga 2 e l'ultima riga sono dati, non decorazione.** Alla pagina
successiva modificherai un `.gro` a mano, ed entrambe dovranno sopravvivere.
Un `.gro` la cui riga 2 è in disaccordo con il numero di righe di atomo viene
troncato in silenzio, o letto oltre la fine.

> **Perché un formato a precisione più bassa?** Perché il `.gro` è una comodità
> leggibile a occhio. Le traiettorie vere si scrivono in `.xtc`, un formato
> binario compresso che memorizza le coordinate a una precisione regolabile
> (0,001 nm di default) ed è circa dieci volte più piccolo del testo
> equivalente. Ne produrrai uno alla pagina 07.

---

Avanti: [03 — Inserire il ligando](03-inserire-il-ligando.md)
