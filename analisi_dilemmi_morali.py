import pandas as pd
import os
import re

def process_participant_data(participant_folder):
    """
    Processa i dati di un singolo partecipante, combinando i file
    summary dell'eye-tracker e l'output di PsychoPy.
    Se il file summary non è presente, calcola solo i dati comportamentali.

    Args:
        participant_folder (str): Il percorso della cartella del partecipante.

    Returns:
        str: Il percorso del file CSV generato, o None se fallisce.
    """
    summary_file = None
    psychopy_file = None

    # 1. Trova i file CSV necessari nella cartella del partecipante
    for f in os.listdir(participant_folder):
        if f.startswith('summary') and f.endswith('.csv'):
            summary_file = os.path.join(participant_folder, f)
        elif f.endswith('.csv') and not f.startswith('summary') and not f.endswith('_processed_data.csv'):
            psychopy_file = os.path.join(participant_folder, f)

    if not psychopy_file:
        print(f"ATTENZIONE: File di output di PsychoPy non trovato in {participant_folder}. Salto.")
        return None
    
    print(f"  - File PsychoPy trovato: {os.path.basename(psychopy_file)}")
    df_psychopy = pd.read_csv(psychopy_file)
    
    # Estrai l'ID del partecipante, controllando sia 'participant' che 'ID'
    participant_id_from_psychopy = None
    if 'participant' in df_psychopy.columns:
        participant_id_from_psychopy = df_psychopy['participant'].dropna().iloc[0]
    elif 'ID' in df_psychopy.columns:
        participant_id_from_psychopy = df_psychopy['ID'].dropna().iloc[0]
    else:
        print(f"ERRORE: Impossibile trovare la colonna identificativa ('participant' o 'ID') nel file {os.path.basename(psychopy_file)}. Salto.")
        return None


    if not summary_file:
        print(f"ATTENZIONE: File 'summary...' non trovato in {participant_folder}. Procedo con il solo calcolo dei dati comportamentali.")
        
        processed_rows = []
        
        # Filtra le righe dei dilemmi effettivi, escludendo il tutorial
        dilemmi_psychopy = df_psychopy[df_psychopy['main_img'].notna() & ~df_psychopy['main_img'].str.contains('Tutorial', na=False)].copy()

        for _, trial_data in dilemmi_psychopy.iterrows():
            # Estrai l'identificatore del dilemma per creare i nomi degli eventi
            match = re.search(r'dilemma_(.*?)_main_(\d+)', trial_data['main_img'])
            if not match:
                continue
            dilemma_type = match.group(1)
            dilemma_number = match.group(2)
            
            # Crea una riga per l'evento MAIN
            main_row = {
                'participant': participant_id_from_psychopy,
                'event': f"images/Main/All/dilemma_{dilemma_type}_main_{dilemma_number}.jpg_start"
            }
            processed_rows.append(main_row)
            
            # Crea e popola la riga per l'evento CHOICE
            choice_row = {
                'participant': participant_id_from_psychopy,
                'event': f"images/Buttons/All_Buttons/dilemma_{dilemma_type}_choice_{dilemma_number}.jpg_start"
            }

            # A. Tasto premuto e lato della risposta
            key_pressed = trial_data.get('key_resp.keys')
            response_side = None
            if isinstance(key_pressed, str):
                if 'z' in key_pressed:
                    response_side = 'left'
                elif 'm' in key_pressed:
                    response_side = 'right'
            
            # B. Correttezza
            correct_answer_str = trial_data.get('correct')
            is_correct = None
            if isinstance(correct_answer_str, str) and response_side is not None:
                is_correct = ('left' in correct_answer_str and response_side == 'left') or \
                             ('right' in correct_answer_str and response_side == 'right')

            # C. Calcolo del tempo di reazione
            reaction_time = None
            try:
                dilemma_stopped_time = trial_data['Dilemma.stopped']
                left_choice_started = trial_data['left_choice_image.started']
                right_choice_started = trial_data['right_choice_image.started']
                avg_choice_start_time = (left_choice_started + right_choice_started) / 2.0
                reaction_time = dilemma_stopped_time - avg_choice_start_time
            except (KeyError, TypeError):
                reaction_time = None

            choice_row['key_pressed'] = key_pressed
            choice_row['response_side'] = response_side
            choice_row['is_correct'] = is_correct
            choice_row['reaction_time_custom_s'] = reaction_time
            
            processed_rows.append(choice_row)
            
        final_df = pd.DataFrame(processed_rows)
        
        # Assicura che le colonne richieste siano presenti nell'ordine corretto
        required_cols = ['participant', 'event', 'key_pressed', 'response_side', 'is_correct', 'reaction_time_custom_s']
        for col in required_cols:
            if col not in final_df.columns:
                final_df[col] = pd.NA
        
        final_df = final_df[required_cols]

    else: # Se il file summary è presente, esegui la logica originale
        print(f"  - File Summary trovato: {os.path.basename(summary_file)}")
        df_summary = pd.read_csv(summary_file)
        processed_rows = []
        main_events = df_summary[df_summary['event'].str.contains('_main_', na=False)].copy()

        for main_event_index in main_events.index:
            main_row = df_summary.loc[main_event_index].copy()
            main_event_name = main_row['event']
            processed_rows.append(main_row)

            match = re.search(r'dilemma_(.*?)_main_(\d+)', main_event_name)
            if not match:
                continue
            dilemma_type = match.group(1)
            dilemma_number = match.group(2)
            
            try:
                search_slice = df_summary.loc[main_event_index + 1:]
                next_red_dot_series = search_slice['event'].str.contains('red_dot_start', na=False)
                first_red_dot_index = next_red_dot_series.idxmax()
                choice_event_index = first_red_dot_index + 1
                choice_eye_tracker_data = df_summary.loc[choice_event_index].copy()

                if f"dilemma_{dilemma_type}_choice_{dilemma_number}" not in choice_eye_tracker_data['event']:
                    print(f"ATTENZIONE: Sequenza evento non corrispondente per {main_event_name}. Salto CHOICE.")
                    continue

            except (ValueError, IndexError, KeyError):
                print(f"ATTENZIONE: Impossibile trovare l'evento CHOICE per {main_event_name} tramite sequenza. Salto.")
                continue

            psychopy_trial_row = df_psychopy[df_psychopy['main_img'].str.contains(f'{dilemma_type}_main_{dilemma_number}', na=False)]

            if not psychopy_trial_row.empty:
                trial_data = psychopy_trial_row.iloc[0]
                
                key_pressed = trial_data.get('key_resp.keys')
                response_side = None
                if isinstance(key_pressed, str):
                    if 'z' in key_pressed:
                        response_side = 'left'
                    elif 'm' in key_pressed:
                        response_side = 'right'
                
                correct_answer_str = trial_data.get('correct')
                is_correct = None
                if isinstance(correct_answer_str, str) and response_side is not None:
                    is_correct = ('left' in correct_answer_str and response_side == 'left') or \
                                 ('right' in correct_answer_str and response_side == 'right')

                try:
                    dilemma_stopped_time = trial_data['Dilemma.stopped']
                    left_choice_started = trial_data['left_choice_image.started']
                    right_choice_started = trial_data['right_choice_image.started']
                    avg_choice_start_time = (left_choice_started + right_choice_started) / 2.0
                    reaction_time = dilemma_stopped_time - avg_choice_start_time
                    choice_eye_tracker_data['reaction_time_custom_s'] = reaction_time
                except (KeyError, TypeError):
                    choice_eye_tracker_data['reaction_time_custom_s'] = None

                choice_eye_tracker_data['key_pressed'] = key_pressed
                choice_eye_tracker_data['response_side'] = response_side
                choice_eye_tracker_data['is_correct'] = is_correct

            else:
                choice_eye_tracker_data['key_pressed'] = None
                choice_eye_tracker_data['response_side'] = None
                choice_eye_tracker_data['is_correct'] = None
                choice_eye_tracker_data['reaction_time_custom_s'] = None
            
            processed_rows.append(choice_eye_tracker_data)

        if not processed_rows:
            print(f"Nessun dato processato per {participant_folder}.")
            return None
            
        final_df = pd.DataFrame(processed_rows)
        
        new_cols_order = ['participant', 'event', 'key_pressed', 'response_side', 'is_correct', 'reaction_time_custom_s']
        existing_cols = [col for col in new_cols_order if col in final_df.columns]
        remaining_cols = [col for col in final_df.columns if col not in existing_cols]
        final_df = final_df[existing_cols + remaining_cols]

    participant_id_folder = os.path.basename(participant_folder)
    output_filename_csv = os.path.join(participant_folder, f"{participant_id_folder}_processed_data.csv")
    output_filename_xlsx = os.path.join(participant_folder, f"{participant_id_folder}_processed_data.xlsx")
    final_df.to_csv(output_filename_csv, index=False, float_format='%.4f')
    final_df.to_excel(output_filename_xlsx, index=False, float_format='%.4f')

    return output_filename_csv, output_filename_xlsx


def main():
    """
    Funzione principale che esegue lo script.
    """
    base_dir = 'participants'
    if not os.path.isdir(base_dir):
        print(f"Errore: La cartella '{base_dir}' non è stata trovata.")
        print("Assicurati di creare la cartella e di inserirvi le sottocartelle dei partecipanti.")
        return

    print("Inizio elaborazione dati con logica aggiornata...")
    for participant_id in sorted(os.listdir(base_dir)):
        participant_folder = os.path.join(base_dir, participant_id)
        if os.path.isdir(participant_folder):
            print(f"--- Processando '{participant_id}' ---")
            output_file = process_participant_data(participant_folder)
            if output_file:
                print(f"Salvataggio completato: {output_file}\n")

    print("\nElaborazione terminata.")

if __name__ == '__main__':
    main()