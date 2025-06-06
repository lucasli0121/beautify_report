
from datetime import datetime
from typing import Optional
from nicegui import ui, app
import logging
from dao.company_dao import CompanyDao
from pages.invoice_title_page import show_invoice_title_page
from pages.invoice_record_page import show_invoice_record_page
from pages.paytax_record_page import show_paytax_record_page
from pages.brief_report_page import show_brief_report_page
from resources import strings
from utils import global_vars
import navigation

logger = logging.getLogger(__name__)

def show_company_detail_page(company_id: int) -> None:
    if 'company_dao' not in app.storage.user:
        app.storage.user['company_dao'] = CompanyDao()
    app.storage.user['company_dao'].id = company_id
    result = app.storage.user['company_dao'].query_company_by_id()
    if result is False:
        ui.notify('获取公司信息失败')
        return
    with ui.row().classes('w-full mt-0 place-content-center gap-0') \
        .style('background-color: #65B6FF !important;'):
        with ui.tabs().props('w-full').classes('text-white') as tabs:
            invoice_title = ui.tab(strings.get('invoice_title'))
            invoiced_record = ui.tab(strings.get('invoiced_record'))
            # payment_record = ui.tab(strings.get('payment_record'))
            paytax_record = ui.tab(strings.get('paytax_record'))
            brief_report = ui.tab(strings.get('brief_report'))
    with ui.tab_panels(tabs, value=invoice_title) \
        .classes('w-full  q-pa-none') \
        .style('margin: 0 !important; padding: 0 !important;'):
        with ui.tab_panel(invoice_title).classes('gap-0'):
            show_invoice_title_page()
        with ui.tab_panel(invoiced_record).classes('gap-0').style('margin: 0 !important; padding: 0 !important; background-color: #F4F9FD !important;'):
            show_invoice_record_page()
        # with ui.tab_panel(payment_record).classes('gap-0').style('margin: 0 !important; padding: 0 !important; background-color: #F4F9FD !important;'):
        #     ui.label('payment_record').classes('text-2xl font-bold text-gray-800')
        with ui.tab_panel(paytax_record).classes('gap-0').style('margin: 0 !important; padding: 0 !important; background-color: #F4F9FD !important;'):
            show_paytax_record_page()
        with ui.tab_panel(brief_report).classes('gap-0').style('margin: 0 !important; padding: 0 !important; background-color: #F4F9FD !important;'):
            show_brief_report_page()
    


