# 05 — Minimizzazione dell'energia

**Tempo: 20 minuti**, di cui il calcolatore ne usa circa uno.

---

## Perché esiste questo passo

Niente di quello che hai costruito finora è stato costruito con cura.
`gmx solvate` ha riempito la scatola impilando copie di un cubetto d'acqua
pre-equilibrato e cancellando le molecole che si sovrapponevano al soluto — e
la "sovrapposizione" è stata giudicata con una tabella di raggi di van der
Waals, non con l'energia. `gmx genion` ha lasciato cadere ioni in posizioni
d'acqua. E le coordinate della proteina vengono da un cristallo, raffinate
contro la densità elettronica con una funzione di energia diversa da quella che
stai per usare.

Quindi da qualche parte in quei 33 382 atomi ci sono coppie leggermente troppo
vicine. Nel termine di Lennard-Jones, "leggermente troppo vicine" non è una
cosa da poco:

$$
V_{\mathrm{LJ}} \propto \left(\frac{\sigma}{r}\right)^{12}
$$

Dimezza la distanza e la repulsione cresce di un fattore 4096. Fai partire la
dinamica da lì e quell'atomo riceve una forza enorme, fa un passo enorme,
atterra in un posto assurdo, e la simulazione muore — di solito con un
`LINCS warning` o semplicemente con `nan`.

La **minimizzazione dell'energia** scende lungo la superficie di energia
potenziale finché non ci sono più forze grandi. Non è dinamica. Non c'è tempo,
né temperatura, né velocità; non si sta campionando nulla. È una riparazione.

---

## Eseguirla

```bash
gmx grompp -f ../mdp/em.mdp -c solv_ions.gro -p topol.top -o em.tpr
gmx mdrun -deffnm em -nt 2
```

Nota che questa volta **non c'è `-maxwarn`**. Il sistema adesso è neutro; se
`grompp` protesta, qualcosa non va e il messaggio va letto.

`-deffnm em` è una comodità: fa sì che ogni file di output si chiami
`em.qualcosa` invece dei nomi predefiniti (`confout.gro`, `md.log`,
`ener.edr`…), cosa che conta appena hai quattro simulazioni nella stessa
cartella.

`-nt 2` chiede **due thread in tutto**. Per favore lascialo a due finché gli
altri stanno lavorando; la pagina 07 spiega che cosa fa quel numero.

> **Usa `-nt`, non `-ntomp`.** Non sono la stessa cosa e la differenza conta su
> una macchina condivisa. `-ntomp 2` imposta i thread OpenMP *per rank* e lascia
> a `mdrun` la scelta del numero di rank — che sceglie riempiendo la macchina.
> Su Bombina `gmx mdrun -ntomp 2` riporta
>
> ```
> Using 16 MPI threads
> Using 2 OpenMP threads per tMPI thread
> ```
>
> cioè 32 thread: tutto quello che la macchina ha. `-nt 2` ti dà un rank con
> due thread, ed è quello che serve oggi.

Ci mette qualche secondo:

```
Steepest Descents converged to Fmax < 1000 in 778 steps
Potential Energy  = -5.2527219e+05
Maximum force     =  9.8748755e+02 on atom 1709
```

> **I tuoi numeri non saranno identici a questi, ed è giusto così.**
> `gmx genion` ha scelto a caso quali molecole d'acqua trasformare in ioni,
> quindi la tua configurazione di partenza differisce da questa per
> sessantotto molecole. Aspettati lo stesso numero di passi a meno di qualche
> centinaio e la stessa energia a meno dello 0,1 % circa. Un numero molto
> diverso significa che c'è dell'altro che non va.

### Leggere quell'output

**`Potential Energy = -5,25e+05 kJ/mol`** — grande e negativo, che è quello che
deve dare una scatola d'acqua legata a idrogeno. Un numero positivo qui
significa che c'è ancora qualcosa di gravemente sbagliato.

**`Maximum force = 987 kJ mol⁻¹ nm⁻¹`**, sotto i 1000 che avevamo chiesto,
quindi si è fermata. Nota che il criterio è sulla forza *massima* su un singolo
atomo, non sulla media: una sola sovrapposizione irrisolta basta a rovinare una
simulazione, quindi il test deve essere sul caso peggiore.

**`converged ... in 778 steps`** — se invece leggi
`did not converge in 50000 steps`, non tirare avanti e basta. O c'è una
sovrapposizione irrisolvibile (due molecole realmente compenetrate, per un
errore alla pagina 03) oppure la struttura ha bisogno di più passi. Guarda
`Maximum force`: se è qualche migliaio, in genere si può proseguire; se è 10⁵ o
più, torna indietro.

---

## Che cosa significano le impostazioni

```bash
cat ../mdp/em.mdp
```

### `integrator = steep`

Un `.mdp` ha sempre un `integrator`, ma `steep` non lo è. La **discesa più
ripida** (*steepest descent*) sposta semplicemente ogni atomo un po' lungo la
forza che agisce su di esso:

$$
\mathbf{r}_{n+1} = \mathbf{r}_n + \frac{\mathbf{F}_n}{\max|\mathbf{F}_n|}\, h_n
$$

Se l'energia è scesa, accetta il passo e aumenta $h$; se è salita, rifiutalo e
dimezza $h$. È rozzo, smette di fare progressi vicino al minimo, ed è
esattamente ciò che serve per questo compito, perché il compito è sistemare i
pochi contatti peggiori, non trovare un vero minimo.

Gli integratori veri compaiono nella pagina successiva.

### `emtol = 1000.0` ed `emstep = 0.01`

La soglia di convergenza in kJ mol⁻¹ nm⁻¹ e il passo iniziale in nm. 1000 è il
valore convenzionale per una biomolecola solvatata. Non ha niente di magico: è
"abbastanza piccolo perché la dinamica non esploda".

### `cutoff-scheme = Verlet` e `rvdw = 1.0`

Le interazioni non legate non si calcolano fra tutte le 33 382² coppie. Ogni
atomo tiene un elenco dei vicini entro un certo raggio, e l'elenco viene
ricostruito ogni `nstlist` passi. Le interazioni oltre `rvdw = 1.0 nm` non si
calcolano affatto.

È difendibile per Lennard-Jones perché decade come $r^{-6}$: a 1 nm vale un
millesimo del valore alla distanza di contatto. Il residuo viene corretto
analiticamente da `DispCorr` nei file `.mdp` successivi.

`Verlet` è lo schema moderno: aggiunge un margine al raggio dell'elenco,
dimensionato automaticamente perché la deriva di energia dovuta alle
interazioni perse resti sotto una tolleranza che imposti tu. Il vecchio schema
`group` non esiste più, e tutto quello che leggi in rete che lo usa è
obsoleto.

### `coulombtype = PME` — quella che non si può troncare

La legge di Coulomb decade come $r^{-1}$. In un sistema periodico è un
disastro: il numero di atomi in un guscio a distanza $r$ cresce come $r^2$,
quindi il contributo totale di un guscio cresce come $r$. **Troncare
l'elettrostatica non converge.** Tagliarla a 1 nm produce struttura artificiale
nel solvente, distribuzioni ioniche sbagliate e superfici proteiche distorte —
e questi artefatti hanno un aspetto del tutto plausibile.

Il **Particle-Mesh Ewald** lo risolve spezzando ogni carica puntiforme in due
pezzi la cui somma è la carica originale:

1. una carica **schermata**, che decade in fretta e si somma direttamente nello
   spazio reale entro `rcoulomb`;
2. una distribuzione di carica **liscia** che compensa, innocua nello spazio
   reale ma che, essendo liscia, si risolve a poco prezzo nello spazio
   *reciproco* — la si spalma su una griglia, una FFT, una moltiplicazione, una
   FFT inversa.

Il risultato è la somma elettrostatica periodica infinita esatta, a un costo di
$\mathcal{O}(N \log N)$ invece di $\mathcal{O}(N^2)$. Non è
un'approssimazione che si tollera; è il modo in cui si fa.

Due impostazioni governano la parte reciproca, e le ritroverai alla pagina 07
perché sono il bersaglio abituale quando si ottimizzano le prestazioni:

| | |
|---|---|
| `fourierspacing = 0.12` | il passo della griglia in nm. Griglia più fine, più accurata, più lenta |
| `pme-order = 4` | l'ordine dell'interpolazione sulla griglia (cubica) |

> **`rcoulomb` non è una manopola di accuratezza.** Spostare la divisione
> reale/reciproca cambia come il lavoro si ripartisce fra le due parti, non
> quanto è accurata la risposta: PME compensa da solo. È proprio per questo che
> è utile per l'ottimizzazione, ed è ciò che `gmx mdrun -tunepme` regola a
> tempo di esecuzione.

---

## Un'occhiata a quello che hai

```bash
gmx energy -f em.edr -o potential.xvg <<< "Potential"
```

Il file `.edr` contiene ogni termine energetico che GROMACS ha registrato.
`gmx energy` è il modo di arrivarci; eseguilo senza input per vedere la lista.
Il grafico non ti serve adesso, ma userai lo stesso programma alla pagina 06
per controllare che l'equilibratura abbia funzionato.

---

Avanti: [06 — Equilibratura](06-equilibratura.md)
