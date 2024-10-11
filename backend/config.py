import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from flask_login import LoginManager
from dotenv import load_dotenv
import logging

app = Flask(__name__, 
            template_folder='../frontend/templates',
            static_folder='../frontend/static')     

CORS(app)

# Vercel
app.instance_path = '/tmp/instance'

# Sending Message with File
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(__file__), 'users', 'messages', 'uploads')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

load_dotenv()
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL') # SSL req already at .env
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///mydatabase.db' # for local dev

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# SQLAlchemy optimizations for connection handling
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'pool_pre_ping': True,
    'pool_size': 5,  # Adjust as per your needs, smaller pools can reduce initialization time.
    'max_overflow': 10,  # Number of connections exceeding the pool size.
    'pool_timeout': 30,  # Timeout for getting a connection from the pool.
    'pool_recycle': 1800  # Recycle connections every 30 minutes.
}

# db = SQLAlchemy(app)
db = SQLAlchemy(app, session_options={"autocommit": False, "autoflush": False})
migrate = Migrate(app, db)

# Flask Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'users.login'

@login_manager.user_loader
def load_user(user_id):
    from .users.models import User
    return User.query.get(user_id)

# Adjust logging to reduce verbosity
logging.basicConfig(level=logging.WARNING)