from dataclasses import dataclass
from nicegui import ui

from pages.invoice_record_alarm_page import show_invoice_alarm_page
from pages.invoice_record_page import show_invoice_record_page

async def show_invoice_main_page():
    with ui.tabs().props('no-caps inline-label narrow-indicator').classes('text-primary') as tabs:
        period_data_tab = ui.tab('开票记录', icon='data_object').props('icon-left').classes('w-[100px] h-[60px] rounded-md')
        added_value_tab =ui.tab('预警信息', icon='paid').props('icon-left').classes('w-[100px] h-[60px] rounded-md')
    
    with ui.tab_panels(tabs, value=period_data_tab) \
        .classes('w-full h-full q-pa-none') \
        .style('margin: 0 !important; padding: 0 !important;') as tab_panels:
        with ui.tab_panel(period_data_tab).classes('gap-0').style('margin: 0 !important; padding: 0 !important; background-color: #F4F9FD !important;'):
            # 期初数据页面内容
            await show_invoice_page()
        with ui.tab_panel(added_value_tab).classes('gap-0').style('margin: 0 !important; padding: 0 !important; background-color: #F4F9FD !important;'):
            await show_alarm_page()

# 期初数据页面内容
# 
async def show_invoice_page():
    await show_invoice_record_page()

async def show_alarm_page():
    await show_invoice_alarm_page()
