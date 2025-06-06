from dataclasses import dataclass
from nicegui import ui,events, app
from components import inputs, tables
from typing import Optional

@dataclass
class SearchCondition:
    invoice_to: str = ""
    contract: str = ""
    begin_time: str = ""
    end_time: str = ""
search_condition = SearchCondition()

def show_invoice_record_page():
    with ui.row().classes('w-full h-[80px] px-[20px] mt-0 place-content-between gap-0') \
        .style('background-color: #FFFFFF !important; border-radius: 10px;'):
        with ui.row().classes('h-full items-center'):
            inputs.input_search_w40('受票方', on_search) \
                .bind_value_to(search_condition, 'invoice_to')
            inputs.input_search_w40('合同内容', on_search) \
                .bind_value_to(search_condition, 'address')
            inputs.input_search_w40('联系人', on_search) \
                .bind_value_to(search_condition, 'contacts')
            inputs.date_input_w40('开始时间', on_search) \
                .bind_value_to(search_condition, 'begin_time')
            inputs.date_input_w40('结束时间', on_search) \
                .bind_value_to(search_condition, 'end_time')
        with ui.row().classes('h-full items-center'):
            ui.button('删除', icon='img:/static/images/delete@2x.png', on_click=del_select) \
                .classes('w-25 rounded-md text-red') \
                .style('background-color: rgba(255,77,77,0.39) !important')
            ui.button('刷新', icon='img:/static/images/refresh@2x.png', on_click=on_search) \
                .classes('w-25 rounded-md text-white') \
                .style('background-color: #6C96FB !important')
            ui.button('开票', icon='img:/static/images/add_course@2x.png', on_click=add_invoice) \
                .classes('w-25 rounded-md text-white') \
                .style('background-color: #65B6FF !important')
            
    table_rows: list[dict] = []
    record_table: Optional[ui.table] = tables.show_open_invoice_table(table_rows, delete_one)
    app.storage.client['invoice_record_table'] = record_table
    on_search()

def on_search() -> None:
    pass

#
# @description: 开票
# @param None
# @return: None
#             
def add_invoice():
    with ui.dialog().props('persistent') as dialog, ui.card().classes('w-1/2 h-full') \
        .style('background-color: #FFFFFF !important; border-radius: 10px;'):
        ui.label('开票').classes('w-full text-[20px] text-[#333333] font-medium')
        with ui.row().classes('w-full mt-5 place-content-between'):
            ui.label('受票方').classes('w-full text-[16px] text-[#333333] font-medium')
            ui.input(placeholder='请输入对方公司名称') \
                .props('rounded-md outlined dense') \
                .classes('w-full self-center item-center ')
        with ui.row().classes('w-full place-content-between'):
            ui.label('开票额').classes('w-full text-[16px] text-[#333333] font-medium')
            ui.input(placeholder='请输入开票额') \
                .props('rounded-md outlined dense') \
                .classes('w-full self-center item-center ')
        with ui.row().classes('w-full place-content-end'):         
            ui.button('取消', color=None, on_click=dialog.close) \
                .props('flat') \
                .classes('w-[120px] text-[16px] text-[#888888] font-[400]') \
                .style('background-color: #FFFFFF !important;border-radius: 10px;border: 1px solid #888888;')
            def on_create():
                dialog.close()
            ui.button('确定', color=None, on_click=on_create) \
                .props('flat') \
                .classes('w-[120px] text-[16px] text-white font-[400]') \
                .style('background-color: #65B6FF !important; border-radius: 10px')
    dialog.open()

'''
# @description: 批量删除
# @param None  
# @return: None
# 
'''
def del_select():
    pass

def delete_one(e: events.GenericEventArguments):
    pass