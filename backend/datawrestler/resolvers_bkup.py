
from backend.config import db, app
import os
import pandas as pd
from backend.leadgen.models import LeadLandingPage, LeadWhatsapp
from backend.apisocialhub.models import MessageLog
from datetime import datetime, timedelta
from backend.apicrmgraphql.resolvers.appointments_resolver import fetch_appointments, filter_and_clean_appointments
from backend.apicrmgraphql.resolvers.leads_resolver import fetch_all_leads, filter_and_clean_leads

# Disponível caso queira rodar resolvers.py direto
# Executar isso no root:
# python -m backend.datawrestler.resolvers
# para poder ver todos os prints direto aqui no terminal

# Caso contrário, seguir: python wsgi.py

start_date = datetime.now() - timedelta(days=0)
end_date = datetime.now() + timedelta(days=0)

# para testar: python -m backend.datawrestler.resolvers
# with app.app_context(): 

################################
# STEP 1: lead grabber
################################

def get_leads_from_core():
    leads_landing = LeadLandingPage.query.all()
    leads_whatsapp = LeadWhatsapp.query.all()

    # Exibindo as informações detalhadas
    for lead in leads_landing:
        print(f"Lead: {lead.name}, Phone: {lead.phone}, Store: {lead.store}, Created: {lead.created_date}, Tag: {lead.tag}")

    for lead in leads_whatsapp:
        print(f"Lead: {lead.name}, Phone: {lead.phone}, Created: {lead.created_date}, Tag: {lead.tag}, Source: {lead.source}")

    return leads_landing, leads_whatsapp

# testing...
leads_landing, leads_whatsapp = get_leads_from_core()
# print("leads LP:")
# print(leads_landing)
# print("leads WP:")
# print(leads_whatsapp)

################################
# STEP 2: sent messages counter
################################

def count_sent_messages_to_lead_phone():
    # Fazendo o JOIN entre MessageLog e LeadWhatsapp para pegar o número de telefone real
    return db.session.query(
        LeadWhatsapp.phone, db.func.count(MessageLog.id)
    ).join(
        MessageLog, LeadWhatsapp.id == MessageLog.lead_phone_id
    ).group_by(LeadWhatsapp.phone).all()
    # Ajustar polimorfismo depois pra puxar LeadWhatsapp e LeadLandingPage

# testing...
df_count_messages_by_phone = count_sent_messages_to_lead_phone()
# print("df groupby msg sent:")
# print(df_count_messages_by_phone)

################################
# STEP 3: appointments
################################

def get_appointments(start_date, end_date):
    return fetch_appointments(start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'))

# testing...
appointments_data = get_appointments(start_date, end_date)
#print("Appointments:")
#print(appointments_data)

################################
# STEP 4: leads
################################

def get_leads(start_date, end_date):
    return fetch_all_leads(start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'))

# testing...
leads_data = get_leads(start_date, end_date)
#print("Leads:")
#print(leads_data)
print("")
print("datawrestling begins...")

################################
# STEP 5: crossing data
# Leads: counter (how many?), leads (phone number is there? true or false?), appointments (phone number is there? true or false?)
################################

def data_wrestling(leads_landing, leads_whatsapp, appointments, count_messages_by_phone, leads):
    
    # Combina os leads que possivelmente receberão msg
    df_leads_receive_message = leads_whatsapp + leads_landing

    # Contador de Leads
    total_leads_to_receive_message = len(df_leads_receive_message)
    print(f"Total leads to receive message: {total_leads_to_receive_message}")

    # Preparar para verificar telefones em mensagens enviadas e agendamentos
    # sent_messages_phones = {row[0] for row in count_messages_by_phone} # Telefone nas mensagens enviadas

    # Criar um dicionário que mapeia telefone -> quantidade de mensagens enviadas
    sent_messages_phones = {row[0]: row[1] for row in count_messages_by_phone}  # Telefone e quantidade de mensagens enviadas

    appointment_phones = {appointment['telephones'][0] for appointment in appointments_data if appointment['telephones']}  # Telefones nos agendamentos
    leads_phones = {lead['telephone'][0] for lead in leads_data if lead['telephone']}  # Telefones nos leads

    # Cria uma lista pra guardar os leads
    leads_df = []

    # Processar os leads para verificar a existencia de agendamentos e mensagens enviadas e leads
    for lead in df_leads_receive_message:
        phone = lead.phone.strip()
        created_date = lead.created_date
        source = lead.source
        sent_message_count = sent_messages_phones.get(phone, 0)  # Retorna 0 se não houver mensagens
        has_appointment = phone in appointment_phones
        has_lead = phone in leads_phones
        print(f"Phone: {phone}, Source: {source}, Created: {created_date}, Sent Messages: {sent_message_count}, Has appointment: {has_appointment}, Has lead: {has_lead}")

        # Adiciona dados em lista de dicionários:
        leads_df.append({
            'phone': phone,
            'created_date': created_date,
            'source': source,
            'sent_message_count': sent_message_count,
            'has_appointment': has_appointment,
            'has_lead': has_lead
        })

        # Converte a lista em dataframe
    leads_df = pd.DataFrame(leads_df)

    return leads_df
print("invocando datawrestler")
# testing...
# data_wrestling(leads_landing, leads_whatsapp, appointments_data, df_count_messages_by_phone, leads_data)

# part 6
# agora que a parte 5 está feita (data_wrestling), preciso finalmente classificar os leads in df_leads_receive_message em:
# has appointment == False
# has lead == False
# e baseador no contador, seguir algumas lógicas...

# Import Send Messages from apisocialhub resolvers
from ..apisocialhub.resolvers import send_message
from ..apisocialhub.models import MessageLog, MessageList
from dotenv import load_dotenv

print("invocando loaddotenv e api key")
# Importing Data
load_dotenv()
api_token = os.getenv("API_KEY")

print("invocando datawrestling")
# chama o datawrestling e processa os leads
leads_df = data_wrestling(leads_landing, leads_whatsapp, appointments_data, df_count_messages_by_phone, leads_data)

today = datetime.now().strftime("%d/%m/%Y")
print("comecando o for loop")
# Processamento dos leads no loop
for index, cliente in leads_df.iterrows():
    phone = cliente['phone']
    contador = cliente['sent_message_count']  # Quantidade de mensagens enviadas
    source = cliente['source']
    created_date = cliente['created_date']
    has_appointment = cliente['has_appointment']  # Verifica se tem appointment
    has_lead = cliente['has_lead']  # Verifica se é um lead existente

    print(f"Contador: {contador}, phone: {phone}, source: {source}, Has appointment: {has_appointment}, Has lead: {has_lead}")

    # Lógica para leads que não têm appointment e não são leads existentes
    if not has_appointment and not has_lead:
        if source == "unknown": # Botox
            if contador >= 0: # == 0
                mensagem = MessageList(title= "Botox Primeira Mensagem", text=f"Oi {phone}, venha fazer sua avaliação de Botox!")
                response = send_message(phone, mensagem.to_dict(), api_token)

                status_envio = response["success"]

                if status_envio:
                    print(f"botoxd1 enviada para: {phone}")
                    log = MessageLog([phone, "botoxd1", today, response])  # Registrando o log
                else:
                    print(f"Erro ao enviar para: {phone}")
                    print(f"Resposta: {response}")

            elif contador == 1:  # Segunda mensagem (exemplo)
                mensagem = MessageList(title="Botox Follow-up", text=f"Oi {phone}, estamos te esperando para sua avaliação de Botox!")
                response = send_message(phone, mensagem, api_token)

                status_envio = response["success"]

                if status_envio:
                    print(f"Follow-up enviado para: {phone}")
                    log = MessageLog([phone, "follow-up", today, response])  # Registrando o log
                else:
                    print(f"Erro ao enviar para: {phone}")
                    print(f"Resposta: {response}")

            # Adicionar mais regras conforme necessário 
            # para outros contadores e sources!
        
    else:
        print(f"Lead {phone} já tem appointment ou já é lead existente. Ignorando...")