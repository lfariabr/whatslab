from datetime import datetime
from ..config import db

class LeadsHandler(db.Model):
    __tablename__ = 'leadshandler'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    phone = db.Column(db.String(20), nullable=False)
    created_date = db.Column(db.DateTime, default=datetime.utcnow)
    source = db.Column(db.String(64), nullable=True, default='unknown')
    name = db.Column(db.String(255), nullable=True, default='')
    tag = db.Column(db.String(64), nullable=True, default='')
    sent_message_count = db.Column(db.Integer, default=0)
    has_appointment = db.Column(db.Boolean, default=False)
    has_lead = db.Column(db.Boolean, default=False)

    def to_json(self):
        return {
            'id': self.id,
            'phone': self.phone,
            'created_date': self.created_date.strftime('%Y-%m-%d %H:%M:%S'),
            'source': self.source,
            'name': self.name,
            'tag': self.tag,
            'sent_message_count': self.sent_message_count,
            'has_appointment': self.has_appointment,
            'has_lead': self.has_lead
        }