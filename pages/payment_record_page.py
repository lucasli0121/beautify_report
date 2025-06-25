from dataclasses import dataclass
from datetime import datetime
from nicegui import ui,events, app
from components import inputs, tables, dialogs
from typing import Any, Optional
from dao.company_dao import CompanyDao
from dao.payment_record_dao import PaymentRecordDao
from utils import global_vars as g

@dataclass
class SearchCondition:
    payment_to: str = ""
    status: int = -1
    begin_time: str = ""
    end_time: str = ""
search_condition = SearchCondition()

def show_payment_record_page():
    result, list_values = g.my_db.query_all_company('', '', '')  # 确保公司数据已加载
    company_info = {}
    if result and list_values is not None:
        for item in list_values:
            company = CompanyDao()
            company.from_db(item)
            company_info[company.name] = company.id
    options = list(company_info.keys())  # 获取所有公司名称
    def on_change(value):
        if value in company_info:
            search_condition.payment_to = company_info[value]
    with ui.row().classes('w-full h-[80px] px-[20px] mt-0 place-content-between gap-0') \
        .style('background-color: #FFFFFF !important; border-radius: 10px;'):
        with ui.row().classes('h-full items-center'):
            inputs.selection_w40(options, None, on_change=on_change)
            def on_status_change(value):
                if value == '未完成':
                    search_condition.status = 0
                elif value == '完成':
                    search_condition.status = 1
                elif value == '取消':
                    search_condition.status = 2
                else:
                    search_condition.status = -1
            inputs.selection_w40(['未完成', '完成', '取消'], None, on_change=on_status_change)
            inputs.date_input_w40('开始时间', on_search) \
                .bind_value_to(search_condition, 'begin_time')
            inputs.date_input_w40('结束时间', on_search) \
                .bind_value_to(search_condition, 'end_time')
        with ui.row().classes('h-full items-center'):
            ui.button('刷新', icon='img:/static/images/refresh@2x.png', on_click=on_search) \
                .classes('w-25 rounded-md text-white') \
                .style('background-color: #6C96FB !important')
            ui.button('删除', icon='img:/static/images/delete@2x.png', on_click=del_select) \
                .classes('w-25 rounded-md text-red') \
                .style('background-color: rgba(255,77,77,0.39) !important')
            ui.button('付款', icon='img:/static/images/add_course@2x.png', on_click=add_payment) \
                .classes('w-25 rounded-md text-white') \
                .style('background-color: #65B6FF !important')
            
    table_rows: list[dict] = []
    record_table: Optional[ui.table] = tables.show_payment_record_table(table_rows, delete_one)
    app.storage.client['payment_record_table'] = record_table
    on_search()

def on_search() -> None:
    from_company_id = ''
    from_company_name = ''
    if 'company_dao' in app.storage.user:
        company_dao = app.storage.user['company_dao']
        from_company_id = str(company_dao.id)
        from_company_name = company_dao.name
    else:
        ui.notify('请先选择公司')
        return
    result, list_values = g.my_db.query_all_payment_record(
        from_company_id,
        search_condition.payment_to,
        search_condition.status,
        search_condition.begin_time,
        search_condition.end_time,)
    if result is False:
        ui.notify('查询付款记录失败')
        return
    if 'payment_record_table' in app.storage.client:
        app.storage.client['payment_record_table'].rows.clear()
        app.storage.client['payment_record_table'].update()
        if list_values is None or len(list_values) == 0:
            ui.notify('没有查询到付款记录')
            return
        sn = 1
        for item in list_values:
            row_dict: dict[str, Any] = {}
            row_dict['sn'] = sn
            row_dict['from_company_name'] = from_company_name
            payment_record = PaymentRecordDao()
            payment_record.from_db(item)
            result, to_company_dao = g.my_db.query_company_by_id(payment_record.to_company_id)
            if result and to_company_dao is not None:
                row_dict['to_company_name'] = to_company_dao.name
            row_dict.update(payment_record.to_db())
            app.storage.client['payment_record_table'].add_row(row_dict)
            sn += 1
        app.storage.client['payment_record_table'].update()

#
# @description: 付款
# @param None
# @return: None
#             
def add_payment():
    company_dao: CompanyDao = CompanyDao()
    if 'company_dao' in app.storage.user:
        company_dao = app.storage.user['company_dao']
    else:
        ui.notify('请先选择公司')
        return
    dao = PaymentRecordDao()
    dao.from_company_id = str(company_dao.id)
    with ui.dialog().props('persistent') as dialog, ui.card().classes('w-1/2') \
        .style('background-color: #FFFFFF !important; border-radius: 10px;'):
        ui.label('付款').classes('w-full text-[20px] text-[#333333] font-medium')
        with ui.row().classes('w-full mt-5 place-content-start items-center'):
            ui.label('受款方').classes('w-[20%] self-right text-[16px] text-[#333333] font-medium')
            result, list_values = g.my_db.query_all_company('', '', '')  # 确保公司数据已加载
            company_info = {}
            if result and list_values is not None:
                for item in list_values:
                    company = CompanyDao()
                    company.from_db(item)
                    company_info[company.name] = company.id
            options = list(company_info.keys())  # 获取所有公司名称
            def on_change(value):
                if value in company_info:
                    dao.to_company_id = company_info[value]
            inputs.selection_w40(options, None, on_change=on_change)
        with ui.row().classes('w-full place-content-start items-center'):
            ui.label('付款金额').classes('w-[20%] self-right text-[16px] text-[#333333] font-medium')
            def on_payment_change(e: events.ValueChangeEventArguments) -> None:
                value = e.value
                if value is None or value == '':
                    dao.payment_money = 0
                else:
                    try:
                        dao.payment_money = float(value)
                        invoice_money_input.set_value(dao.payment_money if dao.payment_money else 0)
                        remain = invoice_money_input.value - has_invoice_money_input.value
                        remain_invoice_money_input.set_value(remain)
                    except ValueError:
                        ui.notify('开票金额必须是数字')
                        dao.payment_money = 0
            ui.input(placeholder='请输入付款总额') \
                .props('rounded-md outlined dense') \
                .classes('w-[30%] self-center item-center ') \
                    .bind_value_to(dao, 'before_tax_money') \
                    .on_value_change(on_payment_change)
        
        with ui.row().classes('w-full place-content-start items-center'):
            ui.label('应开票金额').classes('w-[20%] self-right text-[16px] text-[#333333] font-medium')
            invoice_money_input = ui.input(placeholder='请输入开票金额') \
                .props('rounded-md outlined dense') \
                .classes('w-[30%] self-center item-center ') \
                    .bind_value_to(dao, 'total_invoice_money')
        with ui.row().classes('w-full place-content-start items-center'):
            ui.label('已开票金额').classes('w-[20%] self-right text-[16px] text-[#333333] font-medium')
            has_invoice_money_input = ui.input(placeholder='请输入已开票金额') \
                .props('rounded-md outlined dense') \
                .classes('w-[30%] self-center item-center ') \
                    .bind_value_to(dao, 'has_invoice_money')
        with ui.row().classes('w-full place-content-start items-center'):
            ui.label('未开票金额').classes('w-[20%] self-right text-[16px] text-[#333333] font-medium')
            remain_invoice_money_input = ui.input(placeholder='请输入未开票金额') \
                .props('rounded-md outlined dense') \
                .classes('w-[30%] self-center item-center ') \
                    .bind_value_to(dao, 'remain_invoice_money')
        with ui.row().classes('w-full place-content-start items-center'):
            ui.label('发票内容').classes('w-[20%] self-right text-[16px] text-[#333333] font-medium')
            ui.input(placeholder='请输入发票内容') \
                .props('rounded-md outlined dense') \
                .classes('w-[30%] self-center item-center ').bind_value_to(dao, 'invoice_content')
        with ui.row().classes('w-full place-content-start items-center'):
            ui.label('状态').classes('w-[20%] self-right text-[16px] text-[#333333] font-medium')
            inputs.selection_w40(['未完成', '已完成'], '未完成', on_change=lambda value: setattr(dao, 'status', 0 if value == '未完成' else 1))
            dao.status = 0  # 默认状态为未完成
        with ui.row().classes('w-full place-content-end'):         
            ui.button('取消', color=None, on_click=dialog.close) \
                .props('flat') \
                .classes('w-[120px] text-[16px] text-[#888888] font-[400]') \
                .style('background-color: #FFFFFF !important;border-radius: 10px;border: 1px solid #888888;')
            def on_create():
                if dao.to_company_id == "" or dao.payment_money == 0:
                    ui.notify('受款方,付款额不能为空')
                    return
                dao.create_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                if g.my_db.add_payment_record(dao.to_db()):
                    ui.notify('添加成功')
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
    if 'payment_record_table' not in app.storage.client:
        ui.notify('请先查询记录')
        return
    selection = app.storage.client['payment_record_table'].selected
    if not selection:
        ui.notify('请选择要删除的记录')
        return
    ids = [item['id'] for item in selection]
    if not ids:
        ui.notify('没有选中任何记录')
        return
    del_by_ids(ids)

def delete_one(e: events.GenericEventArguments):
    id = e.args['id']
    del_by_ids([id])

def del_by_ids(ids: list[str]) -> None:
    if ids is None or len(ids) == 0:
        ui.notify('请选择要删除的记录')
        return
    def make_delete():
        delok = True
        for id in ids:
            if id is None or len(id) == 0:
                continue
            result = g.my_db.delete_payment_record(id)
            if result is False:
                delok = False
                ui.notify(f'删除记录失败: {id}')
                return
        if delok is True:
            ui.notify('删除记录成功')
            on_search()

    dialogs.make_sure_dialog('确认要进行删除操作?', on_ok=make_delete)