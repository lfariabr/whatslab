from flask import Blueprint, render_template
from flask_login import login_required
from backend.config import db
from backend.users.models import User

core_blueprint = Blueprint('core', __name__)

@core_blueprint.route('/admin')
@login_required
def index():
    return render_template('core/core.html')