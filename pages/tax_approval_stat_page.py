from dataclasses import dataclass
from nicegui import ui

from pages.tax_approval_page import show_tax_approval_page
from pages.tax_brief_stat_page import show_tax_brief_stat_page

async def show_tax_approval_stat_page():
    with ui.tabs().props('no-caps inline-label narrow-indicator').classes('text-primary') as tabs:
        tax_approval_tab = ui.tab('完税证明', icon='data_object').props('icon-left').classes('w-[100px] h-[60px] rounded-md')
        tax_stat_tab =ui.tab('缴税汇总', icon='paid').props('icon-left').classes('w-[100px] h-[60px] rounded-md')
    
    with ui.tab_panels(tabs, value=tax_approval_tab) \
        .classes('w-full h-full q-pa-none') \
        .style('margin: 0 !important; padding: 0 !important;') as tab_panels:
        with ui.tab_panel(tax_approval_tab).classes('gap-0').style('margin: 0 !important; padding: 0 !important; background-color: #F4F9FD !important;'):
            # 完税证明页面内容
            await show_tax_approval_page()
        with ui.tab_panel(tax_stat_tab).classes('gap-0').style('margin: 0 !important; padding: 0 !important; background-color: #F4F9FD !important;'):
            await show_tax_brief_stat_page()

