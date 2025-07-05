from dataclasses import dataclass
from datetime import datetime
from nicegui import ui,events, app
from components import inputs, tables, dialogs
from typing import Any, Optional
from dao.service_record_dao import ServiceRecordDao
from utils import global_vars as g

@dataclass
class SearchCondition:
    from_company_id: str = ""
    from_company_name: str = ""
    to_company_id: str = ""
    to_company_name: str = ""
    status: int = -1
    begin_time: str = ""
    end_time: str = ""
search_condition = SearchCondition()

def show_service_record_page():
    result, company_info = g.query_company_name_company()
    if result is False:
        ui.notify('查询公司信息失败')
        return
    options = list(company_info.keys())  # 获取所有公司名称
    with ui.column().classes('w-full px-[20px] py-[10px] mt-0 items-center gap-2') \
        .style('background-color: #FFFFFF !important; border-radius: 10px;'):
        with ui.row().classes('w-full place-content-start items-center'):
            with ui.row().classes('w-[25%] place-content-start items-center'):
                ui.label('甲方').classes('w-[20%] text-[16px] text-[#333333] font-medium')
                def on_from_change(value):
                    if value in company_info:
                        search_condition.from_company_id = company_info[value].id
                        search_condition.from_company_name = value
                inputs.selection_w60(options, None, need_input=True, on_change=on_from_change)
            with ui.row().classes('w-[25%] place-content-start items-center'):
                ui.label('乙方').classes('w-[20%] text-[16px] text-[#333333] font-medium')
                def on_to_change(value):
                    if value in company_info:
                        search_condition.to_company_id = company_info[value].id
                        search_condition.to_company_name = value
                inputs.selection_w60(options, None, need_input=True, on_change=on_to_change)
            def on_status_change(value):
                if value == '无':
                    search_condition.status = 0
                elif value == '无合同':
                    search_condition.status = 1
                elif value == '待付款':
                    search_condition.status = 2
                elif value == '待开票':
                    search_condition.status = 3
                elif value == '完成':
                    search_condition.status = 4
                else:
                    search_condition.status = -1
            inputs.selection_w40(['所有', '无合同', '待付款', '待开票', '完成'], None, on_change=on_status_change)
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
            ui.button('新建', icon='img:/static/images/add_course@2x.png', on_click=add_service) \
                .classes('w-25 rounded-md text-white') \
                .style('background-color: #65B6FF !important')
            
    table_rows: list[dict] = []
    app.storage.client['service_record_table'] = tables.show_service_record_table(table_rows, delete_one)
    on_search()

def on_search() -> None:
    result, list_values = g.my_db.query_all_service_record(
        search_condition.from_company_id,
        search_condition.to_company_id,
        search_condition.status,
        search_condition.begin_time,
        search_condition.end_time,)
    if result is False:
        ui.notify('查询业务记录失败')
        return
    if 'service_record_table' in app.storage.client:
        app.storage.client['service_record_table'].rows.clear()
        if list_values is not None:
            sn = 1
            for item in list_values:
                dao = ServiceRecordDao()
                dao.from_db(item)
                row_dict: dict[str, Any] = {}
                row_dict['sn'] = sn
                result, from_company_dao = g.my_db.query_company_by_id(dao.from_company_id)
                if result and from_company_dao is not None:
                    row_dict['from_company_name'] = from_company_dao.name
                else:
                    row_dict['from_company_name'] = '未知甲方'
                result, to_company_dao = g.my_db.query_company_by_id(dao.to_company_id)
                if result and to_company_dao is not None:
                    row_dict['to_company_name'] = to_company_dao.name
                else:
                    row_dict['to_company_name'] = '未知乙方'
                gap_money = dao.payment_money - dao.invoice_money
                row_dict['invoice_gap_money'] = 0 if gap_money < 0 else gap_money
                row_dict['payment_gap_money'] = dao.contract_money - dao.payment_money
                row_dict.update(dao.to_db())
                app.storage.client['service_record_table'].add_row(row_dict)
                sn += 1
        app.storage.client['service_record_table'].update()

#
# @description: 新增业务
# @param None
# @return: None
#             
def add_service():
    result, company_info = g.query_company_name_company()
    if result is False:
        ui.notify('查询公司信息失败')
        return
    options = list(company_info.keys())  # 获取所有公司名称
    dao = ServiceRecordDao()
    with ui.dialog().props('persistent') as dialog, ui.card().classes('w-1/2') \
        .style('background-color: #FFFFFF !important; border-radius: 10px;'):
        ui.label('新增业务').classes('w-full text-[20px] text-[#333333] font-medium')
        with ui.row().classes('w-full mt-5 place-content-start items-center'):
            ui.label('甲方').classes('w-[20%] text-[16px] text-[#333333] font-medium')
            def on_from_change(value):
                if value in company_info:
                    dao.from_company_id = company_info[value].id
            inputs.selection_w60(options, None, need_input=True, on_change=on_from_change)
        with ui.row().classes('w-full place-content-start items-center'):
            ui.label('乙方').classes('w-[20%] text-[16px] text-[#333333] font-medium')
            def on_to_change(value):
                if value in company_info:
                    dao.to_company_id = company_info[value].id
            inputs.selection_w60(options, None, need_input=True, on_change=on_to_change)
        with ui.row().classes('w-full place-content-start items-center'):
            ui.label('合同名称').classes('w-[20%] self-right text-[16px] text-[#333333] font-medium')
            ui.input(placeholder='请输入合同名称') \
                .props('rounded-md outlined dense') \
                .classes('w-[50%] self-center item-center ').bind_value_to(dao, 'contract_name')
        with ui.row().classes('w-full place-content-start items-center'):
            ui.label('合同内容').classes('w-[20%] self-right text-[16px] text-[#333333] font-medium')
            ui.input(placeholder='请输入合同内容') \
                .props('rounded-md outlined dense') \
                .classes('w-[50%] self-center item-center ').bind_value_to(dao, 'contract_content')
        with ui.row().classes('w-full place-content-start items-center'):
            ui.label('合同金额').classes('w-[20%] self-right text-[16px] text-[#333333] font-medium')
            ui.input(placeholder='请输入合同总额') \
                .props('rounded-md outlined dense') \
                .classes('w-[30%] self-center item-center ') \
                    .bind_value_to(dao, 'contract_money')
        with ui.row().classes('w-full place-content-start items-center'):
            ui.label('是否有合同').classes('w-[20%] self-right text-[16px] text-[#333333] font-medium')
            inputs.selection_w40(['无', '有'], '无', on_change=lambda value: setattr(dao, 'is_contract', 0 if value == '无' else 1))
            dao.is_contract = 0  # 默认无合同
        with ui.row().classes('w-full place-content-start items-center'):
            ui.label('开票金额').classes('w-[20%] self-right text-[16px] text-[#333333] font-medium')
            ui.input(placeholder='请输入开票金额') \
                .props('rounded-md outlined dense') \
                .classes('w-[30%] self-center item-center ') \
                .bind_value_from(dao, 'invoice_money') \
                .bind_value_to(dao, 'invoice_money')
        with ui.row().classes('w-full place-content-start items-center'):
            ui.label('付款金额').classes('w-[20%] self-right text-[16px] text-[#333333] font-medium')
            ui.input(placeholder='请输入付款金额') \
                .props('rounded-md outlined dense') \
                .classes('w-[30%] self-center item-center ') \
                .bind_value_from(dao, 'payment_money') \
                .bind_value_to(dao, 'payment_money')
        with ui.row().classes('w-full place-content-start items-center'):
            ui.label('状态').classes('w-[20%] self-right text-[16px] text-[#333333] font-medium')
            def on_status_change(value):
                if value == '无':
                    dao.status = 0
                elif value == '无合同':
                    dao.status = 1
                elif value == '待付款':
                    dao.status = 2
                elif value == '待开票':
                    dao.status = 3
                elif value == '完成':
                    dao.status = 4
                else:
                    dao.status = -1
            inputs.selection_w40(['无', '无合同', '待付款', '待开票', '完成'], None, on_change=on_status_change)
            dao.status = 0  # 默认状态为无
        with ui.row().classes('w-full place-content-end'):         
            ui.button('取消', color=None, on_click=dialog.close) \
                .props('flat') \
                .classes('w-[120px] text-[16px] text-[#888888] font-[400]') \
                .style('background-color: #FFFFFF !important;border-radius: 10px;border: 1px solid #888888;')
            def on_create():
                if dao.from_company_id == '' or dao.to_company_id == "" or dao.contract_money == 0:
                    ui.notify('甲方，乙方, 合同额不能为空')
                    return
                if dao.contract_name == '' or dao.contract_content == "":
                    ui.notify('合同名称，合同内容不能为空')
                    return
                dao.create_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                if g.my_db.add_service_record(dao.to_db()):
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
    if 'service_record_table' not in app.storage.client:
        ui.notify('请先查询记录')
        return
    selection = app.storage.client['service_record_table'].selected
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
            result = g.my_db.delete_service_record(id)
            if result is False:
                delok = False
                ui.notify(f'删除记录失败: {id}')
                return
        if delok is True:
            ui.notify('删除记录成功')
            on_search()

    dialogs.make_sure_dialog('确认要进行删除操作?', on_ok=make_delete)