from dataclasses import dataclass
from nicegui import ui,events, app
from components import inputs, tables,cards
from typing import Optional
from datetime import datetime

@dataclass
class SearchCondition:
    select_year: str = ""
search_condition = SearchCondition()

def show_paytax_record_page():
    with ui.row().classes('w-full h-[80px] px-[20px] mt-0 place-content-between gap-0') \
        .style('background-color: #FFFFFF !important; border-radius: 10px;'):
        with ui.row().classes('h-full items-center'):
            curyear = datetime.now().year
            years_value = [f'{year}年' for year in range(curyear, 2020, -1)]
            def on_search_yeas(value):
                on_search()
            inputs.selection_w40(years_value, years_value[0], on_search_yeas) \
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
