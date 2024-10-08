from flask import Blueprint, render_template, flash, redirect, url_for, current_app, send_from_directory
from flask_login import login_required, current_user
from backend.config import db
from backend.users.models import MessageList, UserPhone
from backend.users.forms import MessageForm, UserPhoneForm
from werkzeug.utils import secure_filename
import os

core_blueprint = Blueprint('core', __name__)

# Admin Dashboard Route
@core_blueprint.route('/admin')
@login_required
def index():
    return render_template('core/core.html')

# Route for Creating a New Message
@core_blueprint.route('/new_message', methods=['GET', 'POST'])
@login_required
def new_message():
    form = MessageForm()
    filename = None
    
    if form.validate_on_submit():
        if form.file.data and hasattr(form.file.data, 'filename'):
            # Defining file secure name
            filename = secure_filename(form.file.data.filename)

            # Complete file path where it's gonna be saved
            file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)

            # Saving file at server
            form.file.data.save(file_path)
        
        else:   
            file_path = None

        # Create a new message record
        message = MessageList(
            title=form.title.data, 
            text=form.text.data, 
            interval=form.interval.data, 
            file=filename # form.file.data
        )

        # Add and commit to the database
        db.session.add(message)
        db.session.commit()
        flash('Mensagem cadastrada com sucesso!')

        # Redirect to the message list after saving
        return redirect(url_for('core.message_list'))
    
     # Render the new message form if it's a GET request or if validation fails
    return render_template('core/new_message.html', form=form)

# Route for Viewing All Messages
@core_blueprint.route('/message_list', methods=['GET'])
@login_required
def message_list():
    # Fetch all messages from the database
    messages = MessageList.query.all()

    # Render the message list template, passing the messages to the template
    return render_template('core/message_list.html', messages=messages)

    return render_template('core/new_message.html', form=form)

# Route for Editing a Message
@core_blueprint.route('/edit_message/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_message(id):
    message = MessageList.query.get_or_404(id)
    form = MessageForm(obj=message)

    if form.validate_on_submit():
        message.title = form.title.data
        message.text = form.text.data
        message.interval = form.interval.data

        # Verificar se um novo arquivo foi enviado
        if form.file.data and hasattr(form.file.data, 'filename'):
            # Definir o nome seguro do arquivo
            filename = secure_filename(form.file.data.filename)
            # Caminho completo do arquivo onde ele será salvo
            file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)

            if not os.path.exists(current_app.config['UPLOAD_FOLDER']):
                os.makedirs(current_app.config['UPLOAD_FOLDER'])

            # Salvar o arquivo no servidor
            form.file.data.save(file_path)
            # Atualizar o caminho do arquivo na mensagem
            message.file = filename
        else:
            # Se nenhum novo arquivo foi enviado, manter o arquivo existente
            message.file = message.file  # Mantém o caminho do arquivo existente

        # Salvar as alterações no banco de dados
        db.session.commit()
        flash('Mensagem editada com sucesso!')
        return redirect(url_for('core.message_list'))
    
    # Pass the `message` object to the template
    return render_template('core/new_message.html', form=form, message=message)

@core_blueprint.route('/uploads/<filename>')
@login_required
def uploaded_file(filename):
    return send_from_directory(current_app.config['UPLOAD_FOLDER'], filename)

# Route for Deleting a Message
@core_blueprint.route('/delete_message/<int:id>', methods=['POST'])
@login_required
def delete_message(id):
    message = MessageList.query.get_or_404(id)
    db.session.delete(message)
    db.session.commit()
    flash('Mensagem deletada com sucesso!')
    return redirect(url_for('core.message_list'))

# Route for Adding new Phone
@core_blueprint.route('/new_phone', methods=['GET', 'POST'])
@login_required
def new_phone():
    form = UserPhoneForm()
    if form.validate_on_submit():
        phone = UserPhone(user_id=current_user.id,
                          phone_number=form.phone_number.data,
                          phone_token=form.phone_token.data, 
                          phone_description=form.phone_description.data)
        
        db.session.add(phone)
        db.session.commit()
        flash('Telefone cadastrado com sucesso!')
        return redirect(url_for('core.phone_list'))
    
    return render_template('core/new_phone.html', form=form)

# Route for Listing Phones
@core_blueprint.route('/phone_list', methods=['GET'])
@login_required
def phone_list():
    phones = UserPhone.query.all()
    return render_template('core/phone_list.html', phones=phones)

# Editing Phone Number
@core_blueprint.route('/edit_phone/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_phone(id):
    phone = UserPhone.query.get_or_404(id)
    form = UserPhoneForm(obj=phone)

    if form.validate_on_submit():
        phone.phone_number = form.phone_number.data
        phone.phone_token = form.phone_token.data
        phone.phone_description = form.phone_description.data
        db.session.commit()
        flash('Telefone atualizado com sucesso!')
        return redirect(url_for('core.phone_list'))

    return render_template('core/edit_phone.html', form=form, phone=phone)

# Deleting Phone Number
@core_blueprint.route('/delete_phone/<int:id>', methods=['POST'])
@login_required
def delete_phone(id):
    phone = UserPhone.query.get_or_404(id)
    db.session.delete(phone)
    db.session.commit()
    flash('Telefone deletado com sucesso!')
    return redirect(url_for('core.phone_list'))