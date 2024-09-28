import sys
import os

if sys.version_info >= (3, 10):
    import collections
    import collections.abc
    collections.Mapping = collections.abc.Mapping
    collections.MutableMapping = collections.abc.MutableMapping
    collections.Iterable = collections.abc.Iterable  # Add this line

# Assuming your Flask app is structured within a package named 'backend'
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.main import app, db  # Adjust the path if your app structure is different
from backend.leadgen.models import LeadWhatsapp  # Path to your LeadWhatsapp model

with app.app_context():
    def delete_all_leads():
        try:
            num_rows_deleted = db.session.query(LeadWhatsapp).delete()
            db.session.commit()
            print(f"Successfully deleted {num_rows_deleted} leads.")
        except Exception as e:
            db.session.rollback()
            print(f"Failed to delete leads. Error: {e}")
        finally:
            db.session.close()

    if __name__ == "__main__":
        delete_all_leads()