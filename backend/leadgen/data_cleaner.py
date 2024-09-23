import os
import pandas as pd
from flask import request, jsonify
from werkzeug.utils import secure_filename

# Função para processar os arquivos CSV
def process_csv_files(botox_file_path=None, preenchimento_file_path=None):
    df_list = []

    if botox_file_path:
        df_botox = pd.read_csv(botox_file_path)
        df_botox['filename'] = 'botox'  # Adiciona a coluna 'filename' com o valor 'botox'
        df_list.append(df_botox)

    if preenchimento_file_path:
        df_preenchimento = pd.read_csv(preenchimento_file_path)
        df_preenchimento['filename'] = 'preenchimento'  # Adiciona a coluna 'filename' com o valor 'preenchimento'
        df_list.append(df_preenchimento)

    # Combina todos os DataFrames em um só
    df_leads_whatsapp = pd.concat(df_list, ignore_index=True)

    # Realize aqui o processamento necessário nos DataFrames

    return df_leads_whatsapp