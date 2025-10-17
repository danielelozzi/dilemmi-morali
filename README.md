# Guida all'Uso dello Script di Analisi per Esperimenti di Dilemmi

Questo documento descrive come utilizzare lo script Python `analisi_dilemmi_morali.py` per processare e combinare i dati provenienti da esperimenti realizzati con PsychoPy e analizzati con SPEED.

## 1. Scopo dello Script

Lo scopo principale dello script è quello di automatizzare l'analisi dei dati grezzi di un esperimento sui dilemmi morali. Prende in input due file per ogni partecipante:

1. *(Opzionale)* L'output dell'eye-tracker processato da **SPEED** (il file `summary...csv`).
2. L'output comportamentale generato da **PsychoPy** (il file `.csv` con tutti i log della prova).

Lo script combina le informazioni rilevanti da entrambi i file, calcola le metriche comportamentali chiave (correttezza e tempo di reazione) e produce un **singolo file CSV pulito e aggregato** per ogni partecipante, pronto per le analisi statistiche.

## 2. Prerequisiti

Per eseguire il progetto dai sorgenti:

1. **Installa Anaconda**: [Link](https://www.anaconda.com/)
2. *(Opzionale)* Installa CUDA Toolkit: Per l'accelerazione GPU con NVIDIA. [Link](https://developer.nvidia.com/cuda-downloads)
3. **Crea un ambiente virtuale**:

Apri il Prompt di Anaconda

```bash
conda create --name dilemmi
conda activate dilemmi
conda install pip
conda install git
git clone https://github.com/danielelozzi/dilemmi-morali.git
```
4. **Installa le librerie richieste**:

apri la cartella

```bash
cd dilemmi-morali
```

installa i requisiti

```bash
pip install -r requirements.txt
```
5. **(opzionale) Installa Pytorch CUDA**:

[https://pytorch.org/get-started/locally/](https://pytorch.org/get-started/locally/)

```bash
<command>
```

---


## 3. Struttura delle Cartelle (Fondamentale)

Lo script si aspetta una specifica organizzazione dei file per funzionare correttamente. Crea una cartella principale per il tuo progetto e al suo interno organizza i file come segue:

```
dilemmi-morali/
│
├── analisi_dilemmi_morali.py  <-- LO SCRIPT DEVE ESSERE QUI
│
└── participants/                                <-- UNA CARTELLA CHIAMATA "participants"
    │
    ├── partecipante_01/                         <-- UNA SOTTOCARTELLA PER OGNI PARTECIPANTE
    │   ├── summary_results_dy_p01.csv           (File di output di SPEED - opzionale)
    │   └── p01_psychopy_output.csv              (File di output di PsychoPy)
    │
    ├── partecipante_02/
    │   ├── summary_results_dy_p02.csv
    │   └── p02_psychopy_output.csv
    │
    └── ... (e così via per tutti gli altri partecipanti)
```

**Nota 1**: I nomi dei file `.csv` all'interno delle cartelle dei partecipanti non devono essere necessariamente identici a quelli dell'esempio, ma è cruciale che ci sia **un solo file `summary...`** e **un solo file di output di PsychoPy** per cartella.
**Nota 2**: Lo script può essere usato anche senza il file output di SPEED. 


## 4. Come Usare lo Script


1.  **Organizza i file**: Assicurati che le cartelle e i file siano strutturati come descritto al punto 3.
2.  **Apri il Terminale**: Apri un'applicazione terminale (es. Terminale su macOS/Linux, Anaconda Prompt su Windows).
3.  **Attiva l'ambiente virtuale**: Digita il comando per attivare l'ambiente Conda preparato in precedenza:
    ```bash
    conda activate dilemmi
    ```
4.  **Naviga nella Cartella**: Usa il comando `cd` per spostarti nella cartella principale del progetto (quella che contiene lo script e la cartella `participants`).
    *Suggerimento: su molti terminali, puoi scrivere `cd ` e poi trascinare la cartella direttamente nella finestra per incollare il suo percorso.* Esempio:
   ```bash
    cd /percorso/della/tua/cartella/dilemmi-morali
   ```
5.  **Esegui lo Script**: Lancia lo script con il comando `python`:
    ```bash
    python analisi_dilemmi_morali.py
    ```
6.  **Controlla l'Output**: Lo script stamperà a schermo lo stato di avanzamento. Al termine, troverai un nuovo file chiamato `[nome_partecipante]_processed_data.csv` all'interno di ogni sottocartella in `participants`.

## 5. Funzionamento Dettagliato dello Script

Lo script esegue i seguenti passaggi per ogni partecipante:

1. **Identificazione dei File**: Cerca i due file `.csv` necessari (summary e PsychoPy).
2. **Selezione Eventi `MAIN`**: Legge il file `summary...` e seleziona solo le righe che corrispondono alla presentazione del dilemma (eventi contenenti `_main_`). Tutti gli altri eventi vengono ignorati.
3. **Selezione Eventi `CHOICE`**: Per ogni evento `MAIN`, lo script analizza le righe successive nel file `summary...` per trovare l'evento di scelta corretto. Lo fa cercando il primo `red_dot_start` che segue il `MAIN` e selezionando la riga immediatamente successiva, che corrisponde all'inizio della schermata di scelta. Questo garantisce che vengano presi i dati di eye-tracking corretti per la fase di decisione, ignorando eventi spuri.
4. **Collegamento con i Dati PsychoPy**: Lo script trova la riga corrispondente nel file di PsychoPy per estrarre i dati comportamentali.
5. **Calcolo del Tempo di Reazione**: Calcola il tempo di reazione (in secondi) usando la formula precisa basata sui timestamp di PsychoPy:
   `RT = Dilemma.stopped - ((left_choice_image.started + right_choice_image.started) / 2)`
6. **Valutazione della Correttezza**: Aggiunge una colonna booleana `is_correct` (`True`/`False`). Il valore è `True` solo se la risposta data ('z' per sinistra, 'm' per destra) corrisponde alla risposta corretta indicata nella colonna `correct` del file PsychoPy.
7. **Creazione del File di Output**: Combina i dati dell'eye-tracker (dalle righe `MAIN` e `CHOICE`) con le nuove colonne calcolate (`key_pressed`, `response_side`, `is_correct`, `reaction_time_custom_s`) e salva tutto in un nuovo file CSV.

## 6. Descrizione del File di Output

Per ogni partecipante, verrà creato un file `[nome_partecipante]_processed_data.csv`. Questo file avrà la seguente struttura:

* Una riga per l'evento `MAIN` con tutti i dati originali dell'eye-tracker.
* Subito dopo, una riga per l'evento `CHOICE` che contiene:
  * Tutti i dati originali dell'eye-tracker per la fase di scelta.
  * Le nuove colonne aggiunte dallo script:
    * `key_pressed`: Il tasto premuto ('z' o 'm').
    * `response_side`: Il lato corrispondente ('left' o 'right').
    * `is_correct`: `True` se la risposta è corretta, altrimenti `False`.
    * `reaction_time_custom_s`: Il tempo di reazione calcolato.

Questo formato "pulito" è ideale per essere importato in software statistici come R, SPSS, o per ulteriori analisi con Python stesso.

**Nota**: Nel caso in cui non fosse presente l'output di SPEED, le uniche colonne che saranno generate saranno le seguenti:

* `key_pressed`: Il tasto premuto ('z' o 'm').
* `response_side`: Il lato corrispondente ('left' o 'right').
* `is_correct`: `True` se la risposta è corretta, altrimenti `False`.
* `reaction_time_custom_s`: Il tempo di reazione calcolato.

senza quelle relative alle features estratte dall'eyetracker.
