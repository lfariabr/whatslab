import os
import json
import pandas as pd
from dotenv import load_dotenv
from datetime import datetime, timedelta

from backend.config import db, app
from backend.leadgen.models import LeadLandingPage, LeadWhatsapp
from backend.apisocialhub.models import MessageLog, MessageList
from backend.apisocialhub.resolvers import message_handler, send_message
from backend.apicrmgraphql.resolvers.appointments_resolver import fetch_appointments, filter_and_clean_appointments
from backend.apicrmgraphql.resolvers.leads_resolver import fetch_all_leads, filter_and_clean_leads

# Funções para obter e processar dados

def get_leads_from_core():
    leads_landing = LeadLandingPage.query.all()
    leads_whatsapp = LeadWhatsapp.query.all()
    return leads_landing, leads_whatsapp
# Pensar em ter um limite (paginação - 100 por vez)
# trazer uma contagem inicial de leads

def get_leads_landing():
    return LeadLandingPage.query.all()

def get_leads_whatsapp():
    leads = LeadWhatsapp.query.all()
    print(f"Retrieved {len(leads)} leads from WhatsApp.")
    return leads
    # return LeadWhatsapp.query.all()

# Depois fazer o mesmo para o LeadLandingPage
def count_sent_messages_to_lead_phone():
    return db.session.query(
        LeadWhatsapp.phone, db.func.count(MessageLog.id)
    ).join(
        MessageLog, LeadWhatsapp.id == MessageLog.lead_phone_id
    ).group_by(LeadWhatsapp.phone).all()


def get_appointments(start_date, end_date):
    return fetch_appointments(start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'))

def get_leads(start_date, end_date):
    return fetch_all_leads(start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'))

def data_wrestling(leads_landing, leads_whatsapp, appointments, count_messages_by_phone, leads):
    df_leads_receive_message = leads_whatsapp + leads_landing
    sent_messages_phones = {row[0]: row[1] for row in count_messages_by_phone}
    appointment_phones = {appointment['telephones'][0] for appointment in appointments if appointment['telephones']}
    leads_phones = {lead['telephone'][0] for lead in leads if lead['telephone']}
    
    leads_df = []
    for lead in df_leads_receive_message:
        phone = lead.phone.strip()
        sent_message_count = sent_messages_phones.get(phone, 0)
        has_appointment = phone in appointment_phones
        has_lead = phone in leads_phones
        leads_df.append({
            'phone': phone,
            'created_date': lead.created_date,
            'source': lead.source,
            'sent_message_count': sent_message_count,
            'has_appointment': has_appointment,
            'has_lead': has_lead
        })

    return pd.DataFrame(leads_df)

# Função principal para executar o processamento
def run_data_wrestling():
    # Configurar datas e carregar env
    load_dotenv()
    api_token = os.getenv("API_KEY")

    start_date = datetime.now() - timedelta(days=0)
    end_date = datetime.now() + timedelta(days=0)

    # Obter dados
    leads_landing, leads_whatsapp = get_leads_from_core()
    df_count_messages_by_phone = count_sent_messages_to_lead_phone()
    appointments_data = get_appointments(start_date, end_date)
    leads_data = get_leads(start_date, end_date)

    # Processar dados       //     #get_leads_landing e #get_leads_whatsapp
    leads_df = data_wrestling(leads_landing, leads_whatsapp, appointments_data, df_count_messages_by_phone, leads_data)

    # Convert the DataFrame to a list of dictionaries
    leads_list = leads_df.to_dict(orient='records')

    # Serialize the list to a JSON-formatted string
    leads_json = json.dumps(leads_list, default=str, ensure_ascii=False, indent=4)

    # Print the JSON string
    print(leads_json)

    # Enviar mensagens com base nos leads processados
    today = datetime.now().strftime("%d/%m/%Y")
    for index, cliente in leads_df.iterrows():
        phone = cliente['phone']
        contador = cliente['sent_message_count']
        source = cliente['source']
        has_appointment = cliente['has_appointment']
        has_lead = cliente['has_lead']

        if not has_appointment and not has_lead:

            if source == "Whatsapp":  # Exemplo de lógica para uma campanha
                if contador >= 0:
                    # mensagem = MessageList(title="Botox Primeira Mensagem", text=f"Teste de mensagem!")
                    # response = send_message(phone, mensagem.to_dict(), api_token)
                    
                    mensagem = "Teste de Mensagem!!!!"
                    response = send_message(phone, mensagem, api_token)
                    status_envio = response.get("success", False)

                    if status_envio:
                        print(f"botoxd1 enviada para: {phone}")
                        log = MessageLog([phone, "botoxd1", today, response])
                    else:
                        print(f"Erro ao enviar para: {phone}")
                        print(f"Resposta: {response}")

def test_function():
    print("aaaaaaaaaaaa --- This is a test!")

# Executar somente se for chamado diretamente o resolvers.py
if __name__ == "__main__":
    with app.app_context():
        run_data_wrestling()