import os
import pandas as pd
from flask import request, jsonify
from werkzeug.utils import secure_filename

def clean_phone_number(number):
    # Remove any non-digit characters, except for leading '+' 
    cleaned = ''.join(filter(lambda x: x.isdigit() or x == '+', str(number)))
    # If the number starts with '55'
    if cleaned.startswith('55'):
        # Remove the first two characters ('55') if the number is longer than 11 digits
        return cleaned[2:] if len(cleaned) > 11 else cleaned
    return cleaned

# Função para processar os arquivos CSV
def process_csv_files(botox_file_path=None, preenchimento_file_path=None):
    df_list = []

    try:
        if botox_file_path:
            # Ensure the file exists and is read correctly
            df_botox = pd.read_csv(botox_file_path)
            df_botox['filename'] = 'botox'  # Adiciona a coluna 'filename' com o valor 'botox'
            df_list.append(df_botox)

        if preenchimento_file_path:
            df_preenchimento = pd.read_csv(preenchimento_file_path)
            df_preenchimento['filename'] = 'preenchimento'  # Adiciona a coluna 'filename' com o valor 'preenchimento'
            df_list.append(df_preenchimento)

        # If no files were processed, return an empty DataFrame
        if not df_list:
            return pd.DataFrame()

        # Combina todos os DataFrames em um só
        df_leads_whatsapp = pd.concat(df_list, ignore_index=True)

        # Realize aqui o processamento necessário nos DataFrames
        df_leads_whatsapp['Whatsapp'] = df_leads_whatsapp['Whatsapp'].astype(str)
        df_leads_whatsapp['Whatsapp'] = df_leads_whatsapp['Whatsapp'].apply(clean_phone_number)

        return df_leads_whatsapp

    except Exception as e:
        # Handle exceptions like missing files or bad CSV formatting
        print(f"Error processing CSV files: {str(e)}")
        return None