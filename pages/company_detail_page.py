
from datetime import datetime
from typing import Optional
from nicegui import ui, app
import logging
from dao.company_dao import CompanyDao
from pages.invoice_title_page import show_invoice_title_page
from pages.invoice_record_page import show_invoice_record_page
from pages.company_bank_account_page import show_company_bank_account_page
from pages.payment_record_page import show_payment_record_page
from resources import strings
from utils import global_vars as g

logger = logging.getLogger(__name__)

