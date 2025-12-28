from dataclasses import dataclass
from nicegui import ui

from pages.period_data_page import show_period_data_page
from pages.value_added_page import show_value_added_page

@dataclass
class SearchCondition:
    select_year: str = ""
search_condition = SearchCondition()

def show_paytax_page():
    ui.add_css('''
        .paytax-tabs .q-tab__indicator {
            background-color: #FF0000 !important;  /* 下划线红色 */
        }
        .paytax-tabs .q-tab__label {
            font-size: 20px !important;  # 修改字体大小
            color: #ffff !important;  # 修改字体颜色
        }

        .paytax-tabs .q-tab--active,
        .paytax-tabs .q-tab.q-tab--active,
        .paytax-tabs .q-tab[aria-selected="true"] {
            background-color: #449DEE !important;  /* 选中的 tab 背景颜色 */
        }
        .paytax-tabs {
            padding: 0 !important;
            margin-top: 0px !important;
            margin-left: 0 !important;
            margin-right: 0 !important;
            width: 100% !important;
            height: 100% !important;
            align-items: center !important;
        }
        .paytax-tabs .q-tab {
            background-color: #65B6FF !important;  /* 未选中的 tab 背景颜色 */
            border-radius: 0 !important;
            margin: 0 !important;
            padding: 0 !important;
            width: 100% !important;
            height: 100% !important;
        }
        
    ''')
    with ui.tabs().props('no-caps inline-label').classes('text-white paytax-tabs gap-0') as tabs:
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
