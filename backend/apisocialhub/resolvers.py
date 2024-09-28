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

# cert_path = '/Applications/XAMPP/_flaskv3/api_socialhub_com.pem'
# os.environ['SSL_CERT_FILE'] = '/Applications/XAMPP/_flaskv3/api_socialhub_com.pem'

# Função para enviar a mensagem via API
def send_message(telephone, message, api_token):
    telephone = str(telephone)
    api_token = "MOOygXTIL373eLY4YTgbJvyjvW6fswp6"

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

    print(f"Enviando a requisição com o seguinte payload: {json.dumps(request_data, indent=2)}")

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

# Função para lidar com o envio de mensagens e registrar o log
# TESTANDO DISPARAR PELO TESTE.PY
def message_handler_test(lead_phone, message_id, user_phone_id):
    lead_phone = str(lead_phone)
    # Pega a mensagem pelo ID
    message = db.session.query(MessageList).filter_by(id=message_id).first()

    if not message:
        return {"success": False, "message": "Mensagem não encontrada."}

    # Envia a mensagem usando a função send_message
    response = send_message(lead_phone, message.text, api_token)

    # Criar log do disparo no banco de dados

    # Teste pelo arquivo / fora da API
    log = MessageLog(lead_phone=lead_phone, message=message, sender_phone_id=user_phone_id, status=response.get('success', 'failed'))

    db.session.add(log)
    db.session.commit()

    return response


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


def send_message_test(telephone, message, api_token):
    telephone = str(telephone)
    
    # Preparar os dados da requisição
    request_data = {
        "api_token": api_token,
        "phone": telephone,
        "message": message,
        "preview_url": True
    }

    # Converter o payload para JSON
    request_body = json.dumps(request_data)

    # Configurações da requisição
    headers = {
        "Content-Type": "application/json"
    }

    try:
        # Fazer a requisição POST usando 'data' em vez de 'json'
        response = requests.post(api_url, headers=headers, data=request_body) #

        # Verificar o status da resposta
        if response.status_code == 200:
            data = response.json()
            print(f"Mensagem enviada com sucesso para o {telephone}. Response {data}")
            return data
        else:
            print(f"Failed to send message. Status code: {response.status_code}, Response: {response.text}")
            return {"status": False, "error": f"HTTP {response.status_code}: {response.text}"}

    except requests.exceptions.RequestException as e:
        # Registrar qualquer exceção levantada durante a requisição
        print(f"Exception occurred: {str(e)}")
        return {"status": False, "error": str(e)}
