from dataclasses import dataclass
import logging
from typing import Any

logger = logging.getLogger(__name__)

@dataclass
class CompanyDao:
    id: str
    name: str
    brief_name: str
    address: str
    contacts: str
    phone: str
    email: str
    invoice_limit: int
    has_invoiced: float
    tax_no: str
    
    def __init__(self, id=0, name="", brief_name='', address="", contacts="", phone="", email="", invoice_limit=0, has_invoiced=0.0, tax_no=''):
        self.id = str(id)
        self.name = name
        self.brief_name = brief_name
        self.address = address
        self.contacts = contacts
        self.phone = phone
        self.email = email
        self.invoice_limit = invoice_limit
        self.has_invoiced = has_invoiced
        self.tax_no = tax_no

    def from_db(self, data: dict[str, Any]) -> None:
        if '_id' in data:
            self.id = str(data['_id'])
        else:
            self.id = str(data.get('id', 0))
        self.name = data.get('name', "")
        self.brief_name = data.get('brief_name', "")
        self.address = data.get('address', "")
        self.contacts = data.get('contacts', "")
        self.phone = data.get('phone', '')
        self.email = data.get('email', '')
        self.invoice_limit = data.get('invoice_limit', 10)
        self.has_invoiced = round(data.get('has_invoiced', 0.0), 2)
        self.tax_no = data.get('tax_no', "")
        

    def to_db(self) -> dict[str, Any]:
        return self.__dict__
    

