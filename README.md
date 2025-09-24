# Guida all'Uso dello Script di Analisi per Esperimenti di Dilemmi

Questo documento descrive come utilizzare lo script Python `analisi_dilemmi_morali.py` per processare e combinare i dati provenienti da esperimenti realizzati con PsychoPy e analizzati con SPEED. 
Questo script può essere anche utilizzato solamente per analizzare i dati registrati con PsychoPy senza Eyetracker. 

## 1. Scopo dello Script

Lo scopo principale dello script è quello di automatizzare l'analisi dei dati grezzi di un esperimento sui dilemmi morali. Prende in input due file per ogni partecipante:

1. L'output dell'eye-tracker processato da **SPEED** (il file `summary...csv`).
2. L'output comportamentale generato da **PsychoPy** (il file `.csv` con tutti i log della prova).

Lo script combina le informazioni rilevanti da entrambi i file, calcola le metriche comportamentali chiave (correttezza e tempo di reazione) e produce un **singolo file CSV pulito e aggregato** per ogni partecipante, pronto per le analisi statistiche.

## 2. Prerequisiti

Prima di utilizzare lo script, assicurati di avere un ambiente Python funzionante. Per garantire che le dipendenze del progetto non entrino in conflitto con altri progetti Python sul tuo computer, è fortemente consigliato utilizzare un **ambiente virtuale**.

Di seguito trovi due opzioni principali per configurare l'ambiente.

### Opzione A: Installazione con Python e `venv` (Standard)

Questa è l'opzione più leggera se hai già Python installato sul tuo sistema.

1.  **Installa Python**: Assicurati di avere Python 3 installato. Puoi scaricarlo dal sito ufficiale di Python.

2.  **Crea un ambiente virtuale**: Apri il terminale, naviga nella cartella del progetto (`progetto_analisi/`) e crea un ambiente virtuale.
    ```bash
    python -m venv venv
    ```

3.  **Attiva l'ambiente virtuale**:
    *   Su **macOS/Linux**:
        ```bash
        source venv/bin/activate
        ```
    *   Su **Windows**:
        ```bash
        venv\Scripts\activate
        ```
    Noterai che il nome dell'ambiente (`venv`) appare all'inizio della riga del terminale.

4.  **Installa le dipendenze**: Con l'ambiente attivo, installa le librerie necessarie usando il file `requirements.txt` fornito.
    ```bash
    pip install -r requirements.txt
    ```

### Opzione B: Installazione con Anaconda/Miniconda (Consigliato per la ricerca)

Anaconda è una distribuzione pensata per il calcolo scientifico. Semplifica la gestione di pacchetti e ambienti.

1.  **Installa Anaconda o Miniconda**: Scarica l'installer per il tuo sistema operativo dalla pagina di Anaconda (versione completa) o Miniconda (versione minimale, più leggera).

2.  **Crea un ambiente Conda**: Apri l'**Anaconda Prompt** (su Windows) o il terminale (macOS/Linux) e crea un nuovo ambiente. Puoi chiamarlo `dilemmi_env` o come preferisci.
    ```bash
    conda create --name dilemmi_env python=3.9
    ```
    Ti verrà chiesto di confermare, digita `y` e premi Invio.

3.  **Attiva l'ambiente**:
    ```bash
    conda activate dilemmi_env
    ```

4.  **Installa le dipendenze**: Con l'ambiente attivo, puoi installare `pandas` tramite conda o pip.
    ```bash
    # Opzione 1: Usando conda (consigliato in un ambiente conda)
    conda install pandas

    # Opzione 2: Usando pip e il file requirements.txt
    pip install -r requirements.txt
    ```

## 3. Struttura delle Cartelle (Fondamentale)

Lo script si aspetta una specifica organizzazione dei file per funzionare correttamente. Crea una cartella principale per il tuo progetto e al suo interno organizza i file come segue:

```
progetto_analisi/
│
├── analisi_dilemmi_morali.py  <-- LO SCRIPT DEVE ESSERE QUI
│
└── participants/                                <-- UNA CARTELLA CHIAMATA "participants"
    │
    ├── partecipante_01/                         <-- UNA SOTTOCARTELLA PER OGNI PARTECIPANTE
    │   ├── summary_results_dy_p01.csv           (File di output di SPEED)
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

1. **Organizza i file**: Assicurati che le cartelle e i file siano strutturati come descritto al punto 3.
2. **Apri il Terminale**: Apri un'applicazione terminale (Terminale su macOS/Linux, Prompt dei comandi o PowerShell su Windows).
3. **Naviga nella Cartella**: Usa il comando `cd` per spostarti all'interno della cartella principale del tuo progetto. Esempio:
   ```bash
   cd <drag and drop folder>
   ```
4. **Esegui lo Script**: Lancia lo script usando il comando `python`:
   ```bash
   python analisi_dilemmi_morali.py
   ```
5. **Controlla l'Output**: Lo script stamperà a schermo lo stato di avanzamento. Al termine, troverai un nuovo file chiamato `[nome_partecipante]_processed_data.csv` all'interno di ogni sottocartella di `participants`.

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
