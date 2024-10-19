import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from flask_login import LoginManager
from dotenv import load_dotenv
import logging
import re
from markupsafe import Markup
from sqlalchemy import event, Engine


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
# app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL') # SSL req already at .env
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL') + "&connect_timeout=300"

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

# Set the statement timeout to 20 minutes (1,200,000 ms)
@event.listens_for(Engine, "connect")
def set_timeout(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("SET statement_timeout = 1200000;")  # 20 minutes
    cursor.close()

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
# Enable SQLAlchemy engine logging for debugging (replace `INFO` with `DEBUG` for more detail)
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)
# Optionally, you can log errors specifically for SQLAlchemy
logging.getLogger('sqlalchemy.pool').setLevel(logging.INFO)
logging.getLogger('sqlalchemy.dialects').setLevel(logging.INFO)

# Custom filter to replace newlines with <br> tags
def nl2br(value):
    if value is None:
        value = ''  # If value is None, set it to an empty string

    # Replace consecutive newlines (\n\n) with <br><br> (paragraph break)
    value = value.replace("\n\n", "<br><br>")

    # Replace single newlines (\n) with a space, avoiding extra <br> tags
    value = value.replace("\n", " ")

    return Markup(value)

# Registering custom filter with the Flask app
app.jinja_env.filters['nl2br'] = nl2br