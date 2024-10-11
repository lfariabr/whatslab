# forms.py

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField
from wtforms.validators import DataRequired, Email, EqualTo
from wtforms  import ValidationError

# Store options to be selected
store_options = [
    ('MOEMA', 'SP - Moema'),
    ('JARDINS', 'SP - Jardins'),
    ('MOOCA', 'SP - Moooca'),
    # ('ITAIM', 'SP - Itaim'),
    # ('TATUAPÉ', 'SP - Tatuapé'),
    # ('IPIRANGA', 'SP - Ipiranga'),
    # ('SÃO BERNARDO', 'SP - São Bernardo'),
    # # ('ALPHAVILLE', 'SP - Alphaville'),
    # # ('OSASCO', 'SP - Osasco'),
    # # ('TUCURUVI', 'SP - Tucuruvi'),
    # # ('SANTOS', 'SP - Santos'),
    # # ('CAMPINAS', 'SP - Campinas'),
    # # ('SANTO AMARO', 'SP - Santo Amaro'),
    # # ('SOROCABA', 'SP - Sorocaba'),
    # # ('LAPA', 'SP - Lapa'),
    # # ('RIBEIRÃO PRETO', 'SP - Ribeirão Preto'),
    # # ('COPACABANA', 'SP - Copacabana'),
    # # ('TIJUCA', 'SP - Tijuca'),
    # # ('LONDRINA', 'PR - Londrina'),

    # Adicione mais opções conforme necessário
]

class LeadForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    phone = StringField('Phone', validators=[DataRequired()])
    store = SelectField('Store', choices=store_options, validators=[DataRequired()])
    # tag = StringField('Tag', validators=[DataRequired()])
    source = StringField('Source')
    submit = SubmitField('Submit')


class LeadWhatsappForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    phone = StringField('Phone', validators=[DataRequired()])
    created_date = StringField('Created Date')
    tag = StringField('Tag')
    source = StringField('Source')
    store = StringField('Store')
    region = StringField('Region')
    tags = StringField('Tags')
    submit = SubmitField('Submit')
