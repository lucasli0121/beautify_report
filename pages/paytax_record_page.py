from dataclasses import dataclass
from nicegui import ui,events, app
from components import inputs, tables,cards
from typing import Optional
from datetime import datetime

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
    
    with ui.tab_panels(tabs, value=period_data_tab):
        with ui.tab_panel(period_data_tab):
            # 期初数据页面内容
            show_period_page()
        with ui.tab_panel(added_value_tab):
            show_added_value_page()

# 期初数据页面内容
# 
def show_period_page():
    pass
def show_added_value_page():
    with ui.row().classes('w-full h-[80px] px-[20px] mt-0 place-content-between gap-0') \
        .style('background-color: #FFFFFF !important; border-radius: 10px;'):
        with ui.row().classes('h-full items-center'):
            curyear = datetime.now().year
            years_value = [f'{year}年' for year in range(curyear, 2020, -1)]
            def on_search_yeas(value):
                on_search()
            inputs.selection_w40(years_value, years_value[0], False, on_search_yeas) \
                .bind_value_to(search_condition, 'select_year')
        with ui.row().classes('h-full items-center'):
            ui.button('刷新', icon='img:/static/images/refresh@2x.png', on_click=on_search) \
                .classes('w-25 rounded-md text-white') \
                .style('background-color: #6C96FB !important')
            
    month = [f'{i}' for i in range(1, 13)]
    with ui.card().classes('w-full mt-2 no-shadow') \
        .props('borderless') \
        .style('padding: 15px; background-color: #FFFFFF !important; border-radius: 10px;'):
        for row in range(0, 3):
            with ui.row().classes('w-full items-center place-content-evenly'):
                for col in range(0, 4):
                    month_index = row * 4 + col
                    if month_index < len(month):
                        tax = {'month': month[month_index], 'added_tax': 0.0, 'stamp_tax': '0.0', 'income_tax': 0.0, 'total_tax': 0.0}
                        cards.show_paytax_card(tax)

def on_search() -> None:
    pass
