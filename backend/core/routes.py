from flask import Blueprint, render_template, flash, redirect, url_for
from flask_login import login_required, current_user
from backend.config import db
from backend.users.models import MessageList
from backend.users.forms import MessageForm


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
    if form.validate_on_submit():
        # Create a new message record
        message = MessageList(
            title=form.title.data, 
            text=form.text.data, 
            interval=form.interval.data, 
            file=form.file.data
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
        message.file = form.file.data
        db.session.commit()
        flash('Mensagem editada com sucesso!')
        return redirect(url_for('core.message_list'))
    
    # Pass the `message` object to the template
    return render_template('core/new_message.html', form=form, message=message)

# Route for Deleting a Message
@core_blueprint.route('/delete_message/<int:id>', methods=['POST'])
@login_required
def delete_message(id):
    message = MessageList.query.get_or_404(id)
    db.session.delete(message)
    db.session.commit()
    flash('Mensagem deletada com sucesso!')
    return redirect(url_for('core.message_list'))