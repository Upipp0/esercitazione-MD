# 00 — Prima di iniziare

**Tempo: 20 minuti.**

---

## Accesso

```bash
ssh <tuo-username>@bombina.deb.unitus.it
```

Bombina è una singola macchina Linux con 16 core (32 thread hardware), 123 GB
di memoria e **nessuna scheda grafica**. Quest'ultimo punto conta più di ogni
altro in questa esercitazione: la dinamica molecolare moderna si fa normalmente
su GPU, che sono circa venti volte più veloci dei processori in questo compito.
Tutto quello che segue è dimensionato per arrivare in fondo sui soli processori.

Non c'è nemmeno **un sistema a code**. Su un cluster scriveresti uno script, lo
sottometteresti e aspetteresti il tuo turno. Qui qualunque cosa digiti parte
immediatamente e compete con il lavoro di tutti gli altri. Per questo la guida
ti dice quanti thread chiedere, e la risposta è quasi sempre due.

## Scaricare i file

```bash
git clone https://github.com/Upipp0/esercitazione-MD.git
cd esercitazione-MD
mkdir -p run
cd run
```

Lavorerai dentro `run/`, così i file che crei restano separati da quelli che
ti sono stati dati.

## Caricare GROMACS

GROMACS non è nel tuo path per impostazione predefinita. È installato come
*modulo*: software che accendi quando ti serve.

```bash
module use /modules          # dove Bombina tiene il suo software
module load gromacs/2026.2   # accendi GROMACS
gmx --version | head -20
```

Dovresti vedere:

```
GROMACS version:     2026.2
Precision:           mixed
MPI library:         thread_mpi
OpenMP support:      enabled
GPU support:         disabled
SIMD instructions:   AVX_512
```

Due righe vale la pena leggerle adesso, e torneranno alla pagina 07.
`GPU support: disabled` è il vincolo sotto cui stai lavorando.
`SIMD instructions: AVX_512` è il compenso: questa versione sa far eseguire a
ogni core sedici operazioni aritmetiche per volta, ed è il motivo per cui una
simulazione sui soli processori è lenta e non disperata.

Se apri un nuovo terminale più tardi devi ricaricare il modulo. Entrambe le
righe `module`, ogni volta.

---

## Che cosa stai per fare, e perché servono quattro passi

Una simulazione di dinamica molecolare non è complicata in linea di principio.
Hai le coordinate di ogni atomo. Hai una regola che dà la forza su ciascun
atomo a partire dalla posizione di tutti gli altri. Usi la forza per aggiornare
la velocità, la velocità per aggiornare la posizione, e ripeti — qualche
centinaio di milioni di volte.

$$
\mathbf{F}_i = -\nabla_i V(\mathbf{r}_1 \dots \mathbf{r}_N),
\qquad m_i \ddot{\mathbf{r}}_i = \mathbf{F}_i
$$

La regola per le forze è il **campo di forze** (*force field*): una funzione
$V$ di tutte le coordinate, più le molte migliaia di numeri che la riempiono. È
una somma di termini semplici, e conviene conoscerne la forma, perché quasi
tutto quello che farai oggi consiste nel fornire i parametri che le servono:

$$
V = \underbrace{\sum_{\text{legami}} \tfrac{1}{2} k_b (r - r_0)^2
  + \sum_{\text{angoli}} \tfrac{1}{2} k_\theta (\theta - \theta_0)^2
  + \sum_{\text{diedri}} \tfrac{k_\phi}{2}\big[1 + \cos(n\phi - \delta)\big]}_{\text{legati: tengono insieme la molecola}}
  + \underbrace{\sum_{i<j} 4\epsilon_{ij}\left[\left(\tfrac{\sigma_{ij}}{r_{ij}}\right)^{12} - \left(\tfrac{\sigma_{ij}}{r_{ij}}\right)^{6}\right]
  + \sum_{i<j} \frac{q_i q_j}{4\pi\epsilon_0 r_{ij}}}_{\text{non legati: tutto il resto}}
$$

I legami sono molle. Gli angoli sono molle. Ruotare attorno a un legame costa
energia in modo periodico. Gli atomi non legati si respingono forte quando si
toccano, si attraggono debolmente quando sono vicini, e sentono la reciproca
carica elettrica.

Nota che cosa *non* c'è. Nessun elettrone. Nessun legame che si rompe o si
forma. Un campo di forze è una caricatura meccanica classica di una molecola,
costruita per riprodurre la chimica quantistica e l'esperimento per il tipo di
molecole su cui è stato parametrizzato. È ottimo sui cambiamenti
conformazionali ed è del tutto incapace di fare chimica.

Il campo di forze che useremo per la proteina è **amber99sb-ildn**, una delle
scelte standard per le proteine. Conosce tutti e venti gli amminoacidi: dato un
nome di residuo e un nome di atomo sa dirti la carica, la massa, quali atomi
sono legati e ogni parametro dell'equazione qui sopra.

Non ha mai sentito nominare il 2-propilfenolo. Per questo esiste la pagina 03.

---

## I quattro passi, e perché servono tutti

| | | |
|---|---|---|
| **1. Topologia** | pagine 02–03 | Dire che cosa *è* ogni atomo. Il PDB dà le posizioni; la topologia dà cariche, masse, legami e quali parametri del campo di forze si applicano. Senza, non ci sono forze. |
| **2. Solvatazione** | pagina 04 | Una proteina nel vuoto non è una proteina. Mettila in una scatola d'acqua con sale fisiologico. |
| **3. Equilibratura** | pagine 05–06 | Il sistema assemblato non è all'equilibrio: gli atomi si sovrappongono, l'acqua è su un reticolo, nessuno ha una velocità sensata. Risolvi le sovrapposizioni, scaldalo, portalo alla densità giusta. |
| **4. Produzione e analisi** | pagine 07–08 | Solo adesso la traiettoria vale la pena di essere conservata. |

I passi 1–3 sono preparazione e occupano la maggior parte della giornata. È
rappresentativo: nel lavoro vero, preparare correttamente una simulazione
richiede molto più tempo che eseguirla, e la maggior parte delle simulazioni
che producono risultati senza senso lo fanno per un errore commesso al passo 1.

---

Avanti: [01 — La struttura di partenza](01-la-struttura-di-partenza.md)
