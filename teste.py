from backend.config import db, app
from backend.apisocialhub.models import MessageList, MessageLog
from backend.users.models import UserPhone
from backend.leadgen.models import LeadWhatsapp
from backend.apisocialhub.resolvers import send_message_test
import os
from dotenv import load_dotenv

load_dotenv()


# Passo 1: Definir a API Key e o telefone real para teste
api_key = os.getenv("SOCIALHUB_TOKEN_BOTOX")
telefone_teste = "11963546222"  # Telefone real para enviar a mensagem de teste (formato internacional com código do país)

with app.app_context():
    # Passo 2: Criar uma nova mensagem de teste
    nova_mensagem = MessageList(title="Teste de Mensagem", text="Oi, esse é um teste!")
    db.session.add(nova_mensagem)

    # Passo 3: Criar um telefone de disparo (UserPhone) e um lead de teste (LeadWhatsapp)
    telefone_disparador = UserPhone(user_id=1, phone_number="11942424242", phone_token="token_ficticio")
    telefone_lead = LeadWhatsapp(phone="11963546222", name="Lead de Teste")

    db.session.add(telefone_disparador)
    db.session.add(telefone_lead)
    db.session.commit()

    # Exibir IDs criados
    print(f"Mensagem criada com sucesso! ID: {nova_mensagem.id}")
    print(f"Disparador criado com sucesso! ID: {telefone_disparador.id}")
    print(f"Lead criado com sucesso! ID: {telefone_lead.id}")

    # Passo 4: Enviar a mensagem usando a função `send_message`
    response = send_message_test(
        telephone=telefone_teste,  # O telefone de teste real para onde a mensagem será enviada
        message=nova_mensagem.text,
        api_token=api_key
    )

    # Passo 5: Criar um log no banco de dados do envio
    log = MessageLog(
    message_id=nova_mensagem.id,            # ID da mensagem
    sender_phone_id=telefone_disparador.id, # ID do telefone do disparador
    source="lead_whatsapp",                 # Fonte da mensagem
    lead_phone_id=telefone_lead.id,         # ID do telefone do lead
    status=response.get('success', 'failed') # Status do envio da mensagem
)

    db.session.add(log)
    db.session.commit()

    print(f"Mensagem enviada para {telefone_teste}! Status: {response.get('success', 'failed')}")