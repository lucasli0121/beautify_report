from asyncio import run
from dataclasses import dataclass
from datetime import datetime
from nicegui import ui,events, app
from components import inputs, tables, dialogs
from typing import Any, Optional
from dao.company_dao import CompanyDao
from dao.invoice_record_dao import InvoiceRecordDao
from dao.payment_record_dao import PaymentRecordDao
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
            inputs.selection_w40(['所有', '无合同', '待付款', '待开票', '完成'], None, False, on_change=on_status_change)
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
            ui.button('同步', icon='currency_exchange', on_click=sync_service) \
                .classes('w-25 rounded-md text-white') \
                .style('background-color: #65B6FF !important')
            
    table_rows: list[dict] = []
    app.storage.client['service_record_table'] = tables.show_service_record_table(table_rows, show_edit, delete_one)
    on_search()

def on_search() -> None:
    if 'service_record_table' not in app.storage.client:
        return
    result, list_values = g.my_db.query_all_service_record(
        search_condition.from_company_id,
        search_condition.to_company_id,
        search_condition.status,
        search_condition.begin_time,
        search_condition.end_time,)
    if result is False:
        ui.notify('查询业务记录失败')
        return
    app.storage.client['service_record_table'].rows.clear()
    app.storage.client['service_record_table'].update()
    rows: list[dict[str, Any]] = []
    if list_values is not None:
        sn = 1
        for item in list_values:
            dao = ServiceRecordDao()
            dao.from_db(item)
            row_dict: dict[str, Any] = dao.to_db()
            row_dict['sn'] = sn
            result, from_company_dao = g.my_db.query_company_by_id(dao.from_company_id)
            if result and from_company_dao is not None:
                row_dict['from_company_name'] = from_company_dao.brief_name
            else:
                row_dict['from_company_name'] = '未知甲方'
            result, to_company_dao = g.my_db.query_company_by_id(dao.to_company_id)
            if result and to_company_dao is not None:
                row_dict['to_company_name'] = to_company_dao.brief_name
            else:
                row_dict['to_company_name'] = '未知乙方'
            gap_money = dao.payment_money - dao.invoice_money
            row_dict['invoice_gap_money'] = g.format_currency(0 if gap_money < 0 else gap_money)
            row_dict['payment_gap_money'] = g.format_currency(dao.contract_money - dao.payment_money)
            row_dict['contract_money'] = g.format_currency(dao.contract_money)
            row_dict['invoice_money'] = g.format_currency(dao.invoice_money)
            row_dict['payment_money'] = g.format_currency(dao.payment_money)
            rows.append(row_dict)
            sn += 1
    app.storage.client['service_record_table'].rows = rows
    app.storage.client['service_record_table'].update()

"""
# @description: 同步业务数据, 分别从发票记录和付款记录里面查询数据进行同步
# 根据合同ID，同步合同金额，甲方乙方，公司名称，最近付款时间，最近开票时间，开票金额，付款金额，状态等信息
# 能够做到开票金额，发票差额，付款金额，付款差额等信息的自动计算
# 原则: 乙方给甲方开票，甲方和乙方付款
# @param None
# @return: None
"""
async def sync_service():
    if 'service_record_table' not in app.storage.client:
        ui.notify('请先查询记录')
        return
    selection = app.storage.client['service_record_table'].selected
    if not selection:
        ui.notify('请选择要同步的记录')
        return
    ids = [item['id'] for item in selection]
    if not ids:
        ui.notify('没有选中任何记录')
        return
    app.storage.client['service_record_table'].selected.clear()
    with ui.dialog().props('persistent') as dialog, ui.card().style('width: 30%; max-width: 30%;') \
        .style('background-color: #FFFFFF !important; border-radius: 10px;'):
        ui.label('同步发票及付款数据').classes('w-full text-[20px] text-[#333333] font-medium')
        with ui.column().classes('w-full mt-5 place-content-start items-center'):
            with ui.row().classes('w-full place-content-start items-center gap-1'):
                ui.label('年月').classes('w-[20%] text-[16px] text-[#333333] font-medium')
                from_year = datetime.now().year - 3
                to_year = datetime.now().year + 2
                year_select = inputs.selection_w40([str(x) for x in range(from_year, to_year + 1)], None, False, None)
                year_select.set_value(datetime.now().strftime("%Y"))
                month_select = inputs.selection_w40([str(x).zfill(2) for x in range(1, 13)], None, False, None)
                month_select.set_value(datetime.now().strftime("%m").zfill(2))
            with ui.row().classes('w-full place-content-start items-center gap-1'):
                ui.label('公司').classes('w-[20%] text-[16px] text-[#333333] font-medium')
                company_select = inputs.selection_w60(options, None, need_input=True, on_change=None)
            with ui.row().classes('w-full place-content-center items-center gap-1'):
                
                ui.button('关闭', color=None, on_click=dialog.close) \
                    .props('flat') \
                    .classes('w-[120px] text-[16px] text-[#888888] font-[400]') \
                    .style('background-color: #FFFFFF !important;border-radius: 10px;border: 1px solid #888888;')
                ui.button('汇总增值税', color=None, on_click=on_summary) \
                    .props('flat') \
                    .classes('w-[120px] text-[16px] text-white font-[400]') \
                    .style('background-color: #65B6FF !important; border-radius: 10px')
    dialog.open()

    refresh_dialog = g.show_refresh_process("数据同步中，请稍候...")
    result, msg = await run.io_bound(do_sync_service, ids)
    if result is False:
        ui.notify(f"同步数据失败,{msg}")
    else:
        ui.notify("同步数据成功")
        on_search()
    refresh_dialog.close()

"""
# @description: 执行同步业务数据的具体逻辑
# @param ids: 需要同步的业务记录ID列表
# @return: (是否同步成功, 错误信息)
"""
def do_sync_service(ids: list[str]) -> tuple[bool, str]:
    for id in ids:
        if id is None or len(id) == 0:
            continue
        # 原则，乙方给甲方开票，甲方和乙方付款
        # 根据合同id查询对应的发票记录
        result, service_dao = g.my_db.query_service_record_by_id(id)
        if result and service_dao is not None:
            result, list_values = g.my_db.query_invoice_record_by_contract_id(service_dao.id)
            if result and list_values is not None:
                for item in list_values:
                    invoice_dao = InvoiceRecordDao()
                    invoice_dao.from_db(item)
                    # 乙方给甲方开票
                    if invoice_dao.to_company_id == service_dao.from_company_id and invoice_dao.from_company_id == service_dao.to_company_id:
                        g.update_contract_invoice_money_using_service_dao(service_dao, invoice_dao.invoice_money)
            # 根据合同id查询对应的付款记录
            result, list_values = g.my_db.query_payment_record_by_contract_id(id)
            if result and list_values is not None:
                for item in list_values:
                    payment_dao = PaymentRecordDao()
                    payment_dao.from_db(item)
                    # 甲方付款给乙方
                    if payment_dao.from_company_id == service_dao.from_company_id and payment_dao.to_company_id == service_dao.to_company_id:
                        g.update_contract_payment_money_using_service_dao(service_dao, payment_dao.payment_money)
    return True, "同步成功"
    
def show_edit(e: events.GenericEventArguments) -> None:
    id = e.args['id']
    if id is None or len(id) == 0:
        ui.notify('请选择要编辑的公司银行账户')
        return
    result, dao = g.my_db.query_service_record_by_id(id)
    if result is False or dao is None:
        ui.notify('查询公司银行账户信息失败')
        return
    modify_or_new_service(dao, is_add=False)

#
# @description: 新增业务
# @param None
# @return: None
#             
def add_service():
    dao = ServiceRecordDao()
    modify_or_new_service(dao, is_add=True)

def modify_or_new_service(dao: ServiceRecordDao, is_add: bool = True) -> None:
    result, company_info = g.query_company_name_company()
    if result is False:
        ui.notify('查询公司信息失败')
        return
    options = list(company_info.keys())  # 获取所有公司名称
    with ui.dialog().props('persistent') as dialog, ui.card().classes('w-1/2') \
        .style('background-color: #FFFFFF !important; border-radius: 10px;'):
        if is_add:
            ui.label('新增业务').classes('w-full text-[20px] text-[#333333] font-medium')
        else:
            ui.label('修改业务').classes('w-full text-[20px] text-[#333333] font-medium')
        with ui.row().classes('w-full mt-5 place-content-start items-center'):
            ui.label('甲方').classes('w-[20%] text-[16px] text-[#333333] font-medium')
            def on_from_change(value):
                if value in company_info:
                    dao.from_company_id = company_info[value].id
            from_company_select = inputs.selection_w60(options, None, need_input=True, on_change=on_from_change)
            def add_out_company():
                def on_complete(new_company: CompanyDao):
                    company_info[new_company.brief_name] = new_company
                    options.append(new_company.brief_name)
                    from_company_select.set_options(options)
                    to_company_select.set_options(options)
                    from_company_select.set_value(new_company.brief_name)
                g.add_out_company(on_complete)
            ui.button('增加公司', icon='add', on_click=add_out_company)
            if not is_add:
                for key, value in company_info.items():
                    if value.id == dao.from_company_id:
                        from_company_select.set_value(key)
                        break
        with ui.row().classes('w-full place-content-start items-center'):
            ui.label('乙方').classes('w-[20%] text-[16px] text-[#333333] font-medium')
            def on_to_change(value):
                if value in company_info:
                    dao.to_company_id = company_info[value].id
            to_company_select = inputs.selection_w60(options, None, need_input=True, on_change=on_to_change)
            def add_out_company():
                def on_complete(new_company: CompanyDao):
                    company_info[new_company.brief_name] = new_company
                    options.append(new_company.brief_name)
                    from_company_select.set_options(options)
                    to_company_select.set_options(options)
                    to_company_select.set_value(new_company.brief_name)
                g.add_out_company(on_complete)
            ui.button('增加公司', icon='add', on_click=add_out_company)
            if not is_add:
                for key, value in company_info.items():
                    if value.id == dao.to_company_id:
                        to_company_select.set_value(key)
                        break
        with ui.row().classes('w-full place-content-start items-center'):
            ui.label('合同名称').classes('w-[20%] self-right text-[16px] text-[#333333] font-medium')
            ui.input(placeholder='请输入合同名称') \
                .props('rounded-md outlined dense') \
                .classes('w-[50%] self-center item-center ') \
                .bind_value_from(dao, 'contract_name') \
                .bind_value_to(dao, 'contract_name')
        with ui.row().classes('w-full place-content-start items-center'):
            ui.label('合同内容').classes('w-[20%] self-right text-[16px] text-[#333333] font-medium')
            ui.input(placeholder='请输入合同内容') \
                .props('rounded-md outlined dense') \
                .classes('w-[50%] self-center item-center ') \
                .bind_value_from(dao, 'contract_content') \
                .bind_value_to(dao, 'contract_content')
        with ui.row().classes('w-full place-content-start items-center'):
            ui.label('合同金额').classes('w-[20%] self-right text-[16px] text-[#333333] font-medium')
            ui.input(placeholder='请输入合同总额') \
                .props('rounded-md outlined dense') \
                .classes('w-[30%] self-center item-center ') \
                .bind_value_from(dao, 'contract_money') \
                .bind_value_to(dao, 'contract_money')
        with ui.row().classes('w-full place-content-start items-center'):
            ui.label('是否有合同').classes('w-[20%] self-right text-[16px] text-[#333333] font-medium')
            contract_select = inputs.selection_w40(['无', '有'], '无', False, on_change=lambda value: setattr(dao, 'is_contract', 0 if value == '无' else 1))
            if is_add:
                dao.is_contract = 0  # 默认无合同
            else:
                if dao.is_contract == 0:
                    contract_select.set_value('无')
                else:
                    contract_select.set_value('有')
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
            status_select = inputs.selection_w40(['无', '无合同', '待付款', '待开票', '完成'], None, False, on_change=on_status_change)
            if is_add:
                dao.status = 0  # 默认状态为无
            else:
                if dao.status == 0:
                    status_select.set_value('无')
                elif dao.status == 1:
                    status_select.set_value('无合同')
                elif dao.status == 2:
                    status_select.set_value('待付款')
                elif dao.status == 3:
                    status_select.set_value('待开票')
                elif dao.status == 4:
                    status_select.set_value('完成')
                else:
                    status_select.set_value('无')
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
                if is_add:
                    dao.create_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    result, _ = g.my_db.add_service_record(dao.to_db())
                    if result:
                        ui.notify('添加成功')
                        on_search()
                    else:
                        ui.notify('添加失败')
                else:
                    result = g.my_db.update_service_record(dao.to_db(), {'id': dao.id})
                    if result:
                        ui.notify('修改成功')
                        on_search()
                    else:
                        ui.notify('修改失败')
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
    app.storage.client['service_record_table'].selected.clear()

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