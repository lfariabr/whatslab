from backend.config import db
from flask_login import login_user, logout_user, login_required
from flask import Blueprint, render_template, redirect, url_for, flash, request, send_from_directory, jsonify
import os
import pandas as pd
from werkzeug.utils import secure_filename
from datetime import datetime
import logging
from sqlalchemy import desc
from .data_cleaner import process_csv_files # triggered on line 122 *task* highlight


# Absolute imports
from backend.leadgen.models import LeadLandingPage, LeadWhatsapp
from backend.leadgen.forms import LeadForm, LeadWhatsappForm

leadgen_blueprint = Blueprint('leadgen', __name__)

@leadgen_blueprint.route('/test_flash', methods=['GET'])
def test_flash():
    
    flash('Mensagem de teste')
    return redirect(url_for('leadgen.botox'))

@leadgen_blueprint.route('/botox', methods=['GET', 'POST'])
def botox():
    
    form = LeadForm()
    if form.validate_on_submit():
        name = form.name.data
        phone = form.phone.data
        store = form.store.data
        source = 'landing page'
        tag = 'botox'

        lead = LeadLandingPage(name=name, phone=phone, store=store, tag=tag, source=source)        
        db.session.add(lead)
        db.session.commit()
        flash('Obrigado, recebemos o seu cadastro!')

        return render_template('botox.html', form=form)
    else:
        print("Erros de validação: ", form.errors)  # Para verificar se há erros
    
    return render_template('botox.html', form=form)

####### IMPORT CSV

# Defining upload folder - local
# upload_folder = os.path.join(os.path.dirname(__file__), 'uploads')
# os.makedirs(upload_folder, exist_ok=True)

allowed_extensions = {'csv', 'xlsx'}  

# Test Vercel
upload_folder = '/tmp/uploads'
os.makedirs(upload_folder, exist_ok=True)


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions

@leadgen_blueprint.route('/upload_csv', methods=['GET', 'POST'])
def upload():
    logging.info("Entrou na rota de upload CSV")
    if request.method == 'POST':
        # used to capture the date within the form
        # that comes from the website managed by user
        # manually importing contacts from csv file
        # if it's empty, set it to current date
        date_str = request.form.get('date')
        if not date_str:
            # automatically set date to current date&time
            created_date = datetime.now()  
        else:
            try:
                # Convert to datetime because dealing with 
                # dates and times is DELICATE/DELICIOUS
                created_date = datetime.strptime(date_str, '%Y-%m-%d')  
            except ValueError:
                flash('Ops... Wrong date format!')
                logging.error("Ops... Wrong date format!")
                return redirect(url_for('leadgen.upload'))
        logging.info(f"Data recebida: {date_str}")

        # Grab the uploaded files *task*
        # an improvement could be make them not mandatory
        # for example user might upload only 1 file    
        botox_file = request.files.get('botox_file')
        preenchimento_file = request.files.get('preenchimento_file')
        logging.info(f"Arquivos recebidos - Botox: {botox_file}, Preenchimento: {preenchimento_file}")

        if not botox_file and not preenchimento_file:
            flash('Nenhum arquivo selecionado')
            return redirect(url_for('leadgen.upload'))
        # *task* create a library that does exactly what
        # i want with the *task* thing... 
        # you import it, then you run it on the page
        # later on it scraps your code for you
        # or you can just put it in a function and call it (IA insight)
        # and grabs all *task* points from the code and 
        # generates a to-do list integrated with trello or jira or your email
        # or something like that
        # could it be an open source project? is there anything similar of it?
        botox_file_path = None
        preenchimento_file_path = None

        if botox_file and allowed_file(botox_file.filename):
            botox_filename = secure_filename(botox_file.filename)
            botox_file_path = os.path.join(upload_folder, botox_filename)
            botox_file.save(botox_file_path)
            flash('Arquivo de Botox enviado com sucesso!')

        if preenchimento_file and allowed_file(preenchimento_file.filename):
            preenchimento_filename = secure_filename(preenchimento_file.filename)
            preenchimento_file_path = os.path.join(upload_folder, preenchimento_filename)
            preenchimento_file.save(preenchimento_file_path)
            flash('Arquivo de Preenchimento enviado com sucesso!')

        # Processar os arquivos enviados
        if botox_file or preenchimento_file:
            df_leads_whatsapp = process_csv_files(
                                    botox_file_path, 
                                    preenchimento_file_path
                                )

            # Iterando sobre as linhas do DataFrame e salvando no banco
            for index, row in df_leads_whatsapp.iterrows():
                try:
                    name = str(row['Nome'])
                    phone = str(row['Whatsapp'])

                    if not name or not phone:
                        continue
                    # Defining the tag on the database to be according to the filename
                    tag = 'Preenchimento' if 'preenchimento' in row['filename'] else 'Botox'

                    # Preparing the data for the database
                    lead = LeadWhatsapp(
                                    name=row['Nome'],
                                    phone=row['Whatsapp'],
                                    created_date=created_date,  # Usando a data selecionada no front-end
                                    tag=tag,
                                    source='Whatsapp',
                                    #store=row['Unidade'],
                                    #region=row['Região'],
                                    #tags=row['Tags']
                                    store=row.get('Unidade', 'CENTRAL'),
                                    region=row.get('Região', 'São Paulo'),
                                    tags=row.get('Tags', 'SEM TAGS')
                                )
                    db.session.add(lead)
                    db.session.commit()
                
                except Exception as e:
                    print(f"Erro ao adicionar lead: {e}, Linha: {index}")
                    continue
        flash('Leads adicionados ao banco de dados com sucesso!')
        return redirect(url_for('leadgen.view_leads_whatsapp'))

    return render_template('core/upload.html')

#### CHECKING WHATSAPP LEADS
@leadgen_blueprint.route('/leads_whatsapp', methods=['GET'])
@login_required
def view_leads_whatsapp():
    # Pagination via query for improving efficiency
    page = request.args.get('page', 1, type=int)
    per_page = 10
    filters = {
        'name': request.args.get('name', type=str),
        'phone': request.args.get('phone', type=str),
        'creation_date': request.args.get('creation_date', type=str),
        'tag': request.args.get('tag', type=str),
        'source': request.args.get('source', type=str),
        'unit': request.args.get('unit', type=str),
        'region': request.args.get('region', type=str),
        'tags': request.args.get('tags', type=str),
    }
    
    # Building the query based on filters
    query = LeadWhatsapp.query
    for attr, value in filters.items():
        if value:
            column = getattr(LeadWhatsapp, attr, None)
            if column:
                query = query.filter(column == value)
                
    # Pagination                
    try:
        pagination = query.order_by(
                    desc(LeadWhatsapp.id)).paginate(
                        page=page, per_page=per_page
                    )
        # total_leads = LeadWhatsapp.query.count()
        # also request only one page to optimize.
        leads = pagination.items
    except TypeError as e:
        return "Ops... couln't load leads!", 500

    return render_template(
                        'core/view_leads.html', 
                        leads=leads, 
                        pagination=pagination
                        )

#### EDITING WHATSAPP LEADS
@leadgen_blueprint.route('/edit_leads/<int:lead_id>', methods=['GET', 'POST'])
@login_required
def edit_leads(lead_id):
    lead = LeadWhatsapp.query.get_or_404(lead_id)
    form = LeadWhatsappForm(obj=lead)
    
    if form.validate_on_submit():
        # Atualize os campos diretamente
        lead.name = form.name.data
        lead.phone = form.phone.data
        lead.tag = form.tag.data
        lead.source = form.source.data
        lead.store = form.store.data
        lead.region = form.region.data
        lead.tags = form.tags.data

        # Capturar a data do campo de data e definir hora como NOW
        if form.created_date.data:
            try:
                # Apenas a data fornecida, adicionando a hora atual
                selected_date = datetime.strptime(form.created_date.data, '%Y-%m-%d')
                lead.created_date = datetime.combine(selected_date, datetime.now().time())
            except ValueError:
                flash('Data inválida. Use o formato do seletor de data.')
                return render_template('core/edit_leads.html', form=form, lead=lead)
        else:
            lead.created_date = datetime.now()  # Caso o usuário não insira nada

        try:
            db.session.commit()
            flash('Lead editado com sucesso!')
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao editar o lead: {str(e)}')
        return redirect(url_for('leadgen.view_leads_whatsapp'))
    
    return render_template('core/edit_leads.html', form=form, lead=lead)

#### EXCLUDING WHATSAPP LEADS
@leadgen_blueprint.route('/delete_leads/<int:lead_id>', methods=['POST'])
@login_required
def delete_leads(lead_id):
    lead = LeadWhatsapp.query.get_or_404(lead_id)
    db.session.delete(lead)
    db.session.commit()
    flash('Lead excluído com sucesso!')
    return redirect(url_for('leadgen.view_leads_whatsapp'))
