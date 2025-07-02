from dataclasses import dataclass
from datetime import datetime
from nicegui import ui,events, app
from components import inputs, tables, dialogs
from typing import Any, Optional
from dao.company_dao import CompanyDao
from dao.invoice_record_dao import InvoiceRecordDao
from utils import global_vars as g

@dataclass
class SearchCondition:
    invoice_from_id: str = ""
    invoice_from_name: str = ""
    invoice_to_id: str = ""
    invoice_to_name: str = ""
    invoice_content: str = ""
    begin_time: str = ""
    end_time: str = ""
search_condition = SearchCondition()

def show_invoice_record_page():
    result, company_info = g.query_company_name_company()
    if result is False:
        ui.notify('查询公司信息失败')
        return
    options = list(company_info.keys())  # 获取所有公司名称
    
    with ui.column().classes('w-full px-[20px] py-[10px] mt-0 items-center gap-2') \
        .style('background-color: #FFFFFF !important; border-radius: 10px;'):
        with ui.row().classes('w-full place-content-start items-center'):
            with ui.row().classes('w-[25%] place-content-start items-center'):
                ui.label('开票方').classes('w-[20%] text-[16px] text-[#333333] font-medium')
                def on_from_change(value):
                    if value in company_info:
                        search_condition.invoice_from_id = company_info[value].id
                        search_condition.invoice_from_name = value
                inputs.selection_w60(options, None, need_input=True, on_change=on_from_change)
            with ui.row().classes('w-[25%] place-content-start items-center'):
                ui.label('受票方').classes('w-[20%] text-[16px] text-[#333333] font-medium')
                def on_to_change(value):
                    if value in company_info:
                        search_condition.invoice_to_id = company_info[value].id
                        search_condition.invoice_to_name = value
                inputs.selection_w60(options, None, need_input=True, on_change=on_to_change)
            inputs.input_search_w40('发票内容', on_search) \
                .bind_value_to(search_condition, 'invoice_content')
            inputs.date_input_w40('开始时间', on_search) \
                .bind_value_to(search_condition, 'begin_time')
            inputs.date_input_w40('结束时间', on_search) \
                .bind_value_to(search_condition, 'end_time')
        with ui.row().classes('w-full place-content-end items-center'):
            ui.button('刷新', icon='img:/static/images/refresh@2x.png', on_click=on_search) \
                .classes('w-25 rounded-md text-white') \
                .style('background-color: #6C96FB !important')
            ui.button('删除', icon='img:/static/images/delete@2x.png', on_click=del_select) \
                .classes('w-25 rounded-md text-red') \
                .style('background-color: rgba(255,77,77,0.39) !important')
            ui.button('开票', icon='img:/static/images/add_course@2x.png', on_click=add_invoice) \
                .classes('w-25 rounded-md text-white') \
                .style('background-color: #65B6FF !important')
            
    table_rows: list[dict] = []
    app.storage.client['invoice_record_table'] = tables.show_open_invoice_table(table_rows, delete_one)
    on_search()

def on_search() -> None:
    result, list_values = g.my_db.query_all_invoice_record(
        search_condition.invoice_from_id,
        search_condition.invoice_to_id,
        search_condition.invoice_content,
        search_condition.begin_time,
        search_condition.end_time,)
    if result is False:
        ui.notify('查询开票记录失败')
        return
    if 'invoice_record_table' in app.storage.client:
        app.storage.client['invoice_record_table'].rows.clear()
        if list_values is not None:
            sn = 1
            for item in list_values:
                invoice_record = InvoiceRecordDao()
                invoice_record.from_db(item)
                row_dict: dict[str, Any] = {}
                row_dict['sn'] = sn
                result, company_dao = g.my_db.query_company_by_id(invoice_record.from_company_id)
                if result and company_dao is not None:
                    from_company_name = company_dao.name
                else:
                    from_company_name = '未知开票方'
                row_dict['from_company_name'] = from_company_name
                result, to_company_dao = g.my_db.query_company_by_id(invoice_record.to_company_id)
                if result and to_company_dao is not None:
                    row_dict['to_company_name'] = to_company_dao.name
                else:
                    row_dict['to_company_name'] = '未知受票方'
                row_dict.update(invoice_record.to_db())
                app.storage.client['invoice_record_table'].add_row(row_dict)
                sn += 1
        app.storage.client['invoice_record_table'].update()
#
# @description: 开票
# @param None
# @return: None
#             
def add_invoice():
    result, company_info = g.query_company_name_company()
    if result is False:
        ui.notify('查询公司信息失败')
        return
    options = list(company_info.keys())  # 获取所有公司名称
    dao = InvoiceRecordDao()
    with ui.dialog().props('persistent') as dialog, ui.card().classes('w-1/2') \
        .style('background-color: #FFFFFF !important; border-radius: 10px;'):
        ui.label('开票').classes('w-full text-[20px] text-[#333333] font-medium')
        with ui.row().classes('w-full mt-5 place-content-start items-center'):
            ui.label('开票方').classes('w-[20%] text-[16px] text-[#333333] font-medium')
            def on_from_change(value):
                if value in company_info:
                    dao.from_company_id = company_info[value].id
            inputs.selection_w60(options, None, need_input=True, on_change=on_from_change)
        with ui.row().classes('w-full place-content-start items-center'):
            ui.label('受票方').classes('w-[20%] self-right text-[16px] text-[#333333] font-medium')
            def on_to_change(value):
                if value in company_info:
                    dao.to_company_id = company_info[value].id
            inputs.selection_w60(options, None, need_input=True, on_change=on_to_change)
        with ui.row().classes('w-full place-content-start items-center'):
            ui.label('发票类型').classes('w-[20%] self-right text-[16px] text-[#333333] font-medium')
            inputs.selection_w40(['普票', '专票'], '普票', on_change=lambda value: setattr(dao, 'invoice_type', 0 if value == '普票' else 1))
        with ui.row().classes('w-full place-content-start items-center'):
            ui.label('税率').classes('w-[20%] self-right text-[16px] text-[#333333] font-medium')
            inputs.selection_w40(['0.03', '0.06'], '0.03', on_change=lambda value: setattr(dao, 'tax_rate', float(value)))
            dao.tax_rate = 0.03  # 默认税率为0.03
        with ui.row().classes('w-full place-content-start items-center'):
            ui.label('发票内容').classes('w-[20%] self-right text-[16px] text-[#333333] font-medium')
            ui.input(placeholder='请输入发票内容') \
                .props('rounded-md outlined dense') \
                .classes('w-[30%] self-center item-center ').bind_value_to(dao, 'invoice_content')
        with ui.row().classes('w-full place-content-start items-center'):
            ui.label('税前额').classes('w-[20%] self-right text-[16px] text-[#333333] font-medium')
            def on_before_tax_change(e: events.ValueChangeEventArguments) -> None:
                value = e.value
                if value is None or value == '':
                    dao.before_tax_money = 0
                else:
                    try:
                        dao.before_tax_money = float(value)
                        add_tax_input.set_value(dao.before_tax_money * dao.tax_rate if dao.before_tax_money and dao.tax_rate else 0)
                        invoice_money_input.set_value(dao.before_tax_money - dao.added_tax if dao.before_tax_money and dao.added_tax else 0)
                    except ValueError:
                        ui.notify('税前额必须是数字')
                        dao.before_tax_money = 0
            ui.input(placeholder='请输入开票总额') \
                .props('rounded-md outlined dense') \
                .classes('w-[30%] self-center item-center ') \
                    .bind_value_to(dao, 'before_tax_money') \
                    .on_value_change(on_before_tax_change)
        with ui.row().classes('w-full place-content-start items-center'):
            ui.label('增值税').classes('w-[20%] self-right text-[16px] text-[#333333] font-medium')
            add_tax_input = ui.input(placeholder='请输入增值税') \
                .props('rounded-md outlined dense') \
                .classes('w-[30%] self-center item-center ') \
                    .bind_value_to(dao, 'added_tax')
        with ui.row().classes('w-full place-content-start items-center'):
            ui.label('开票金额').classes('w-[20%] self-right text-[16px] text-[#333333] font-medium')
            invoice_money_input = ui.input(placeholder='请输入增值税') \
                .props('rounded-md outlined dense') \
                .classes('w-[30%] self-center item-center ') \
                    .bind_value_to(dao, 'invoice_money')
        with ui.row().classes('w-full place-content-start items-center'):
            ui.label('合同内容').classes('w-[20%] self-right text-[16px] text-[#333333] font-medium')
            ui.input(placeholder='请输入合同内容') \
                .props('rounded-md outlined dense') \
                .classes('w-[30%] self-center item-center ') \
                    .bind_value_to(dao, 'contract_content')
        with ui.row().classes('w-full place-content-end'):         
            ui.button('取消', color=None, on_click=dialog.close) \
                .props('flat') \
                .classes('w-[120px] text-[16px] text-[#888888] font-[400]') \
                .style('background-color: #FFFFFF !important;border-radius: 10px;border: 1px solid #888888;')
            def on_create():
                if dao.to_company_id == "" or dao.invoice_content == "" or dao.before_tax_money == 0:
                    ui.notify('受票方,发票内容,税前额不能为空')
                    return
                dao.create_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                if g.my_db.add_invoice_record(dao.to_db()):
                    ui.notify('添加开票信息成功')
                    on_search()
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
    if 'invoice_record_table' not in app.storage.client:
        ui.notify('请先查询开票记录')
        return
    selection = app.storage.client['invoice_record_table'].selected
    if not selection:
        ui.notify('请选择要删除的开票记录')
        return
    ids = [item['id'] for item in selection]
    if not ids:
        ui.notify('没有选中任何开票记录')
        return
    del_by_ids(ids)
    

def delete_one(e: events.GenericEventArguments):
    id = e.args['id']
    del_by_ids([id])

def del_by_ids(ids: list[str]) -> None:
    if ids is None or len(ids) == 0:
        ui.notify('请选择要删除的开票记录')
        return
    def make_delete():
        delok = True
        for id in ids:
            if id is None or len(id) == 0:
                continue
            result = g.my_db.delete_invoice_record(id)
            if result is False:
                delok = False
                ui.notify(f'删除开票记录失败: {id}')
                return
        if delok is True:
            ui.notify('删除开票记录成功')
            on_search()

    dialogs.make_sure_dialog('确认要进行删除操作?', on_ok=make_delete)
    