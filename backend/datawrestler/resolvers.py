import os
import json
import pandas as pd
from dotenv import load_dotenv
from datetime import datetime, timedelta

from backend.config import db, app
from backend.users.models import UserPhone
from backend.leadgen.models import LeadLandingPage, LeadWhatsapp
from backend.apisocialhub.models import MessageLog, MessageList
from backend.apisocialhub.resolvers import send_message
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
# def count_sent_messages_to_lead_phone():
#     return db.session.query(
#         LeadWhatsapp.phone, db.func.count(MessageLog.id)
#     ).join(
#         MessageLog, LeadWhatsapp.id == MessageLog.lead_phone_id
#     ).group_by(LeadWhatsapp.phone).all()

def count_sent_messages_to_lead_phone():
    return db.session.query(
        MessageLog.lead_phone_number, db.func.count(MessageLog.id)
    ).group_by(MessageLog.lead_phone_number).all()

    # print(result)

def get_appointments(start_date, end_date):
    return fetch_appointments(start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'))

def get_leads(start_date, end_date):
    return fetch_all_leads(start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'))

def get_message():
    # # Testing purposes:
    # print(MessageList.query.all())

    # Creating an empty dic to be filled upon query
    messages_dic = {}
    # Runnig the query to grab MessageList from DB
    messages = MessageList.query.all()

    # For to retrieve each individual message and their data
    for item in messages:
        type_of_message = item.title
        messages_dic[type_of_message] = {
            'text': item.text,
            'interval': item.interval,
            'file': item.file
        }
    # return the dic to serve datawrestler
    return messages_dic

def get_phone_token():
    # Creating an empty dic to be filled upon a query
    phones_dic = {}
    phone_list = UserPhone.query.all()

    # For to retrieve each individual phone (id, number and token)
    for phone in phone_list:
        phones_dic[phone.phone_number] = {
            'id': phone.id, 
            'phone_number': phone.phone_number,
            'phone_token': phone.phone_token, 
            'phone_description': phone.phone_description
        }
    # print("Phones Dictionary:", phones_dic)  # Debugging print
    return phones_dic

    ## TESTES....
    # print(phones_dic)


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

# Main function to process all the data we have carefully gathered
def run_data_wrestling():
    print("Executing...")
    
    # Initial data
    start_date = datetime.now() - timedelta(days=0)
    end_date = datetime.now() + timedelta(days=0)
    today = datetime.now().strftime("%d/%m/%Y")

    load_dotenv()
    # api_token = os.getenv("API_KEY")
    ## The above has been commented beacause we're now 
    ## grabbing the api token from the UserPhone model

    # Get data
    leads_landing, leads_whatsapp = get_leads_from_core()
    df_count_messages_by_phone = count_sent_messages_to_lead_phone()
    appointments_data = get_appointments(start_date, end_date)
    leads_data = get_leads(start_date, end_date)

    # Process data
    # maybe change individually to get_leads_landing e #get_leads_whatsapp
    leads_df = data_wrestling(leads_landing, leads_whatsapp, appointments_data, df_count_messages_by_phone, leads_data)

    # Convert the DataFrame to a list of dictionaries
    leads_list = leads_df.to_dict(orient='records')
    leads_json = json.dumps(leads_list, default=str, ensure_ascii=False, indent=4)
    print(leads_json)

    # Get the messages from the database
    messages_dic = get_message()

    # Get the phones from the database
    phones_dic = get_phone_token()

    # Send messages based on processed leads
    for index, cliente in leads_df.iterrows():
        phone = cliente['phone']
        contador = cliente['sent_message_count']
        source = cliente['source']
        has_appointment = cliente['has_appointment']
        has_lead = cliente['has_lead']
        ####### TASK ########
        # Integrar este contador acima com o contador cadastrado pelo UserPhone

        if not has_appointment and not has_lead and source == "Whatsapp":

            # Defining message based on conditions
            if contador == 0:
                message_key = "botoxd1"
            elif contador == 1:
                message_key = "botoxd2"

            # Fetching appropriate message and file
            mensagem = messages_dic.get(message_key, {}).get("text", None)
            file = messages_dic.get(message_key, {}).get("file", None)

            if not mensagem:
                print(f"Erro ao buscar mensagem: {message_key}")
                continue
            
            # Fetching appropriate phone number that is sending the message
            # Using the first sender phone in the dictionary
            sender_phone_data = list(phones_dic.values())[0]  
            
            ###### TASK #######
            # Here we can add more logic to handle multiple sender phones 
            # Ativo Botox/Ativo Preenchimento/Falta/Pós-Vendas/NPS...

            # Fetching appropriate phone token
            api_token = sender_phone_data.get("phone_token", None)

            if not api_token:
                print(f"Erro ao buscar phone_token for sender: {sender_phone_data}")
                continue

            # Sending the message
            response = send_message(phone, mensagem, api_token)
            status_envio = response.get("success", False)
            
            # Handling response and logging
            if status_envio:
                lead = db.session.query(LeadWhatsapp).filter_by(phone=cliente['phone']).first()
                print(f"{message_key} enviada para: {phone}")
                log = MessageLog(
                    sender_phone_id=sender_phone_data['id'],
                    sender_phone_number=sender_phone_data['phone_number'],  # Agora registrando o número
                    source="Whatsapp",
                    lead_phone_id=lead.id,
                    lead_phone_number=cliente['phone'],
                    status="sent",
                    message_id=message_key,  # Add this if it's the message ID
                    message_text=mensagem,
                    date_sent=datetime.now()
                )
                db.session.add(log)
                db.session.commit()
                
def view_logs():
    logs = MessageLog.query.all()
    for log in logs:
        print(f"ID: {log.lead_phone_id}, LeadPhone: {log.lead_phone_number}, Message ID: {log.message_id}, Status: {log.status}, Sender PhoneNb: {log.sender_phone_number}, Date Sent: {log.date_sent}")
    # print(logs)

# Execute only if we call directly from resolvers.py
if __name__ == "__main__":
    with app.app_context():
        run_data_wrestling()