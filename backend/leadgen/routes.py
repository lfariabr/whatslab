from backend.config import db
from flask_login import login_user, logout_user, login_required
from flask import Blueprint, render_template, redirect, url_for, flash, request, send_from_directory, jsonify
import os
import pandas as pd
from werkzeug.utils import secure_filename
from .data_cleaner import process_csv_files
from datetime import datetime
import logging

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
        # Capturando a data do formulário. Se estiver vazia, define como data atual.
        date_str = request.form.get('date')
        if not date_str:
            created_date = datetime.now()  # Mantemos como objeto datetime
    
        else:
            try:
                created_date = datetime.strptime(date_str, '%Y-%m-%d')  # Convertendo para datetime
            except ValueError:
                flash('Formato de data inválido. Use o formato YYYY-MM-DD.')
                logging.error("Formato de data inválido")
                return redirect(url_for('leadgen.upload'))
        logging.info(f"Data recebida: {date_str}")    
        botox_file = request.files.get('botox_file')
        preenchimento_file = request.files.get('preenchimento_file')
        logging.info(f"Arquivos recebidos - Botox: {botox_file}, Preenchimento: {preenchimento_file}")

        if not botox_file and not preenchimento_file:
            flash('Nenhum arquivo selecionado')
            return redirect(url_for('leadgen.upload'))

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
            df_leads_whatsapp = process_csv_files(botox_file_path, preenchimento_file_path)

            # Iterando sobre as linhas do DataFrame e salvando no banco
            for index, row in df_leads_whatsapp.iterrows():
                try:
                    name = str(row['Nome'])
                    phone = str(row['Whatsapp'])

                    if not name or not phone:
                        continue
                    # Definindo a tag com base no arquivo enviado
                    tag = 'Preenchimento' if 'preenchimento' in row['filename'] else 'Botox'
                    lead = LeadWhatsapp(
                        name=row['Nome'],
                        phone=row['Whatsapp'],
                        created_date=created_date,  # Usando a data selecionada no front-end
                        tag=tag,
                        source='Whatsapp'
                    )
                    db.session.add(lead)
                    db.session.commit()
                    flash('Leads adicionados ao banco de dados com sucesso!')
                
                except Exception as e:
                    print(f"Erro ao adicionar lead: {e}, Linha: {index}")
                    continue

        return redirect(url_for('leadgen.view_leads_whatsapp'))

    return render_template('core/upload.html')

#### CHECKING WHATSAPP LEADS
@leadgen_blueprint.route('/leads_whatsapp', methods=['GET'])
@login_required 
def view_leads_whatsapp():
    try:
        leads = LeadWhatsapp.query.all()
    except TypeError as e:
        # Log the error, inform the user, or return a friendly error message
        return "Oh dear, the time machine broke. We've got dates flying all over the place!", 500
    return render_template('core/view_leads.html', leads=leads)

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
