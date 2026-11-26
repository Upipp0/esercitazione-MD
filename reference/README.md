# La traiettoria di riferimento

Una simulazione già completata dello stesso sistema, venti volte più lunga di
quella che esegui nell'esercitazione. Sta qui perché l'analisi della
[pagina 08](../guida/08-analisi.md) funzioni sempre — che la tua simulazione sia
finita o no, e che sia andata bene o no.

## Che cos'è

| | |
|---|---|
| sistema | lisozima T4 L99A/M102Q + 2-propilfenolo (JZ4), PDB 3HTB |
| costruito con | esattamente i comandi delle pagine 01–06 della guida |
| simulato | 33 382 atomi: proteina, ligando, 10 226 acque TIP3P, 31 Na⁺, 37 Cl⁻ |
| campo di forze | amber99sb-ildn (proteina) + GAFF2/AM1-BCC (ligando) |
| equilibratura | 100 ps NVT poi 100 ps NPT, soluto vincolato |
| produzione | **5 ns**, 300 K, 1 bar, nessun vincolo |
| impostazioni | `../mdp/md_reference.mdp` — identico a `md.mdp` salvo la durata e la frequenza di scrittura |
| fotogrammi | 501, uno ogni 10 ps |
| eseguita su | Bombina, GROMACS 2026.2, 30 thread, nessuna GPU, 112,9 ns/day, circa un'ora |

## I file

| | |
|---|---|
| `md_ref.tpr` | la topologia, **già ridotta ai 2636 atomi salvati** — quindi non serve `convert-tpr` |
| `md_ref.xtc` | la traiettoria, solo proteina e ligando, già ricomposta e centrata |
| `analysis/*.xvg` | l'output di ogni comando di analisi della pagina 08 |
| `analysis/analysis.png` | la figura finita |
| `analysis/pocket.txt` | i residui che delimitano il sito del ligando |

Alla traiettoria è già stato applicato `gmx trjconv -pbc mol -center`, quindi
puoi puntarci direttamente i programmi di analisi. (Farlo due volte è
innocuo.)

## Come usarla

```bash
cd ~/esercitazione-MD/run
bash ../scripts/analyse.sh ../reference/md_ref.tpr ../reference/md_ref.xtc ref_analysis
~/mdvenv/bin/python ../scripts/plot_analysis.py ref_analysis
```

## Che cosa confrontare

La tua simulazione dura 250 ps; questa 5 ns. L'esercizio interessante non è
verificare che i numeri coincidano — è trovare dove **non** coincidono, e
capire a quale dei due crederesti.

- Il plateau dell'RMSD dello scheletro dovrebbe essere simile, e qui
  leggermente più alto, perché una simulazione più lunga ha più tempo per
  trovare una struttura media un po' diversa.
- Il profilo dell'RMSF dovrebbe avere la stessa forma — stesse anse molli,
  stesso nucleo rigido — con picchi meglio risolti.
- **L'occupanza dei legami a idrogeno è dove 250 ps e 5 ns differiscono di
  più.** Un legame che si rompe e si riforma su una scala di 10–100 ps è
  campionato male da 125 fotogrammi. Guarda di quanto si sposta il numero, e
  considera quello la tua stima dell'incertezza su qualunque simulazione breve.
- **Quanti residui rivestono il sito.** `gmx select` ne trova 20 sui 250 ps e
  27 sui 5 ns: più tempo passa, più residui si affacciano prima o poi sulla
  tasca. Nessuno dei due numeri è "giusto": dipendono entrambi da quanto hai
  guardato.
