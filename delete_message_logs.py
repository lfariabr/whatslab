import sys
import os

# Ajuste de compatibilidade para versões do Python 3.10+
if sys.version_info >= (3, 10):
    import collections
    import collections.abc
    collections.Mapping = collections.abc.Mapping
    collections.MutableMapping = collections.abc.MutableMapping
    collections.Iterable = collections.abc.Iterable  # Linha adicionada para compatibilidade

# Assumindo que sua app Flask está estruturada dentro de um pacote 'backend'
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.main import app, db  # Ajuste o caminho conforme a estrutura da sua aplicação
from backend.apisocialhub.models import MessageLog  # Importando o modelo MessageLog

# Criando o contexto da aplicação para interagir com o banco de dados
with app.app_context():
    def delete_all_message_logs():
        try:
            # Deletar todos os registros de MessageLog
            num_rows_deleted = db.session.query(MessageLog).delete()
            db.session.commit()
            print(f"Successfully deleted {num_rows_deleted} message logs.")
        except Exception as e:
            db.session.rollback()
            print(f"Failed to delete message logs. Error: {e}")
        finally:
            db.session.close()
    
    # def print_all_message_logs():        
    #     try:
    #         logs = MessageLog.query.all()

    #         if logs:
    #             print(f"Found {len(logs)} message logs:")
                
    #             for log in logs:
    #                 print(f"ID: {log.id}, LeadPhone: {log.lead_phone_number}, Message ID: {log.message_id}, Status: {log.status}, Sender PhoneNb: {log.sender_phone_number}, Date Sent: {log.date_sent}")
    #         else:
    #             print("No message logs found.")
    #     except Exception as e:
    #         print(f"Failed to print message logs. Error: {e}")
    #     finally:
    #         db.session.close()

    if __name__ == "__main__":
        delete_all_message_logs()
        # print_all_message_logs()