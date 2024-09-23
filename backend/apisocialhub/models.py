# IMPORT TABLE FOR TYPE OF MESSAGE (TEXT, ID, IMAGE, VIDEO, AUDIO)
# CREATE TABLE FOR SENT_MESSAGES TO KEEP LOGS

import requests
from ..config import db
from datetime import datetime
from sqlalchemy.orm import relationship
from ..users.models import UserPhone, MessageList
from ..leadgen.models import LeadWhatsapp, LeadLandingPage

# Modelo para armazenar logs de mensagens enviadas
class MessageLog(db.Model):

    __tablename__ = 'message_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Relaciona com a tabela existente MessageList
    message_id = db.Column(db.Integer, db.ForeignKey('messagelist.id'))
    message = db.relationship("MessageList")
    
    # Relacionamento com UserPhone (disparador) para associar o envio
    sender_phone_id = db.Column(db.Integer, db.ForeignKey('userphones.id'))
    sender_phone = db.relationship("UserPhone")

    # Relacionando com a origem do user para segmentarmos futuramente
    source = db.Column(db.String(50))

    # Relacionamento com LeadWhatsapp ou LeadLandingPage (contato)
    lead_phone_id = db.Column(db.Integer, db.ForeignKey('leadwhatsapp.id'))  # You can adjust for LeadLandingPage if needed
    lead_phone = db.relationship("LeadWhatsapp")
    
    date_sent = db.Column(db.DateTime, default=datetime.utcnow)  # Data de envio
    status = db.Column(db.String(50))  # e.g., 'sent', 'failed'

    def __init__(self, message_id, sender_phone_id, source, lead_phone_id, status):
        self.message_id = message_id
        self.sender_phone_id = sender_phone_id
        self.source = source
        self.lead_phone_id = lead_phone_id
        self.status = status