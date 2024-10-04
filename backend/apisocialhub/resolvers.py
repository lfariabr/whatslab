import requests
import certifi
import os
import json
from .models import MessageLog
from ..config import db
from ..users.models import MessageList, UserPhone
from ..leadgen.models import LeadLandingPage, LeadWhatsapp

# URL da API para enviar mensagens
api_url = "https://apinew.socialhub.pro/api/sendMessage"

# Function to Send Message via API
def send_message(telephone, message, api_token):
    telephone = str(telephone)

    # Preparar os dados da requisição
    request_data = {
        "api_token": api_token,
        "phone": telephone,
        "message": message,
        "preview_url": True
    }

    # Configurações da requisição
    headers = {
        "Content-Type": "application/json",
    }

    print(f"Payload's request: {json.dumps(request_data, indent=2)}")
    print("...")

    try:        
        # Fazendo a requisição POST com os dados no formato JSON
        response = requests.post(api_url, headers=headers, json=request_data, verify=False)
        
        # Verificar o status da resposta
        if response.status_code == 200:
            data = response.json()
            print(f"Mensagem enviada com sucesso para o {telephone}. Response {data}")
            return data
        else:
            print(f"Falha ao enviar mensagem. Código: {response.status_code}, Resposta: {response.text}")
            return {"status": False, "error": f"HTTP {response.status_code}: {response.text}"}

    except requests.exceptions.RequestException as e:
        # Registrar qualquer exceção levantada durante a requisição
        print(f"Exception occurred: {str(e)}")
        return {"status": False, "error": str(e)}

# Function to send message with Files    
def send_message_with_file(telephone, message, api_token, file_path):
    telephone = str(telephone)

    request_data = {
        "api_token": api_token,
        "phone": telephone,
        "message": message,
        "preview_url": True
    }

    headers = {
        "Content-Type": "application/json"
        # "Content-Type": "form-data"
    }

    try:
        with open(file_path, 'rb') as file_content:
            files = {'file' : (file_path.split('/')[-1], file_content, 'application/octet-stream')}
            response = requests.post(api_url, headers=headers, json=request_data, verify=False)
        
        if response.status_code == 200:
            data = response.json()
            print(f"Message with file successfully sent to {telephone}. Response {data}")
            return data
        else:
            print(f"Message with file fail to send. Status code: {response.status_code}. Response {response.text}")
            return {"status": False, "error": f"HTTP {response.status_code}: {response.text}"}
    except requests.exceptions.RequestException as e:
        print(f"Exception occurred: {str(e)}")
        return {"status": False, "error": str(e)}
    
# Cherry Pick to define if message is with file or not!
def cherry_pick_message(telephone, message, api_token, file_name=None):
    if file_name is None:
        return send_message(telephone, message, api_token)
    else:
        return send_message_with_file(telephone, message, api_token, file_name)

def message_handler(lead_phone, message_id, user_phone_id):
    # Pegar a mensagem pelo ID
    message = db.session.query(MessageList).filter_by(id=message_id).first()

    if not message:
        return {"success": False, "message": "Mensagem não encontrada."}

    # Buscar o lead pelo número de telefone
    lead = db.session.query(LeadWhatsapp).filter_by(phone=lead_phone).first()

    if not lead:
        return {"success": False, "message": "Lead não encontrado."}

    # Enviar a mensagem usando a função send_message
    response = send_message(lead.phone, message.text, api_token)

    # Checking if response = None antes de acessar seus atributos
    if response is None:
        return {"success": False, "message": "Falha ao processar a resposta da API."}

    # Criar o log do disparo no banco de dados
    log = MessageLog(
        lead_phone_id=lead.id,  # Agora temos o objeto Lead e usamos seu ID
        message_id=message.id,
        sender_phone_id=user_phone_id,
        source='api', 
        status=response.get('success', 'failed')
    )
    db.session.add(log)
    db.session.commit()

    return response

# Exemplo de como você pode obter um UserPhone dinamicamente
def get_user_phone_id():
    # Pega o primeiro user phone, mas você pode alterar isso para pegar dinamicamente
    user_phone = db.session.query(UserPhone).first()
    return user_phone.id if user_phone else None