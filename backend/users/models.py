from ..config import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from datetime import datetime

class User(db.Model,UserMixin):

    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64), unique=True, index=True)
    username = db.Column(db.String(64), unique=True, index=True)
    password_hash = db.Column(db.String(256))
    profile_image = db.Column(db.String(64), nullable=True, default='default_profile.jpg')

    # posts = db.relationship('BlogPost', back_populates='author', lazy=True)
    # phones = db.relationship('Phone', backref='user', lazy=True)

    def __init__(self, email, username, password):
        self.email = email
        self.username = username
        self.password_hash = generate_password_hash(password)
    
    def check_password(self,password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"Username {self.username}"

class UserPhone(db.Model):

    __tablename__ = 'userphones'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    phone_number = db.Column(db.String(20))
    phone_token = db.Column(db.String(256))

    def __init__(self, user_id, phone_number, phone_token):
        self.user_id = user_id
        self.phone_number = phone_number
        self.phone_token = phone_token

class MessageList(db.Model):

    __tablename__ = 'messagelist'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(64))
    text = db.Column(db.String(256))
    interval = db.Column(db.Integer) # days or hours between messages
    file = db.Column(db.String(256)) # photo, video, audio, etc

    # Método para converter a instância em um dicionário
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'text': self.text,
            'interval': self.interval,
            'file': self.file
        }

