import sys
import os
from datetime import datetime

# Ensure we have the same Python version compatibility fixes as in delete_leads.py
if sys.version_info >= (3, 10):
    import collections
    import collections.abc
    collections.Mapping = collections.abc.Mapping
    collections.MutableMapping = collections.abc.MutableMapping
    collections.Iterable = collections.abc.Iterable

# Assuming your Flask app is structured within a package named 'backend'
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.main import app, db
from backend.leadgen.models import LeadWhatsapp

def create_lead(name, phone, tag, source='Whatsapp', created_date=None):
    with app.app_context():
        try:
            new_lead = LeadWhatsapp(
                name=name,
                phone=phone,
                tag=tag,
                source=source,
                created_date=created_date or datetime.now()
            )
            db.session.add(new_lead)
            db.session.commit()
            print(f"Lead created successfully with name: {name}")
            return new_lead
        except Exception as e:
            db.session.rollback()
            print(f"Failed to create lead. Error: {e}")
        finally:
            db.session.close()

if __name__ == "__main__":
    # Example usage:
    lead_name = "Luis Test"
    lead_phone = "11963546222"
    lead_tag = "Botox"

    # Optionally set a specific date, or leave as None for current date
    lead_date = None  # or datetime.strptime("2023-10-01", "%Y-%m-%d")

    created_lead = create_lead(lead_name, lead_phone, lead_tag, "Whatsapp", lead_date)
    if created_lead:
        print(f"Lead ID: {created_lead.id}")