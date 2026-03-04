from dataclasses import dataclass
from nicegui import ui

from pages.period_data_page import show_period_data_page
from pages.value_added_page import show_value_added_page

def show_paytax_page():
    with ui.tabs().props('no-caps inline-label narrow-indicator').classes('text-primary') as tabs:
        period_data_tab = ui.tab('期初数据', icon='data_object').props('icon-left').classes('w-[100px] h-[60px] rounded-md')
        added_value_tab =ui.tab('增值税计算', icon='paid').props('icon-left').classes('w-[100px] h-[60px] rounded-md')
    
    with ui.tab_panels(tabs, value=period_data_tab) \
        .classes('w-full h-full q-pa-none') \
        .style('margin: 0 !important; padding: 0 !important;') as tab_panels:
        with ui.tab_panel(period_data_tab).classes('gap-0').style('margin: 0 !important; padding: 0 !important; background-color: #F4F9FD !important;'):
            # 期初数据页面内容
            show_period_page()
        with ui.tab_panel(added_value_tab).classes('gap-0').style('margin: 0 !important; padding: 0 !important; background-color: #F4F9FD !important;'):
            show_added_value_page()

# 期初数据页面内容
# 
def show_period_page():
    show_period_data_page()

def show_added_value_page():
    show_value_added_page()
