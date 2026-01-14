from dataclasses import dataclass
from datetime import datetime
from nicegui import ui,events, app
from components import inputs, tables, dialogs
from typing import Any, Optional
from dao.company_bank_account_dao import CompanyBankAccountDao
from dao.company_dao import CompanyDao
from dao.payment_record_dao import PaymentRecordDao, PaymentStatus
from dao.service_record_dao import ServiceRecordDao
from utils import global_vars as g

@dataclass
class SearchCondition:
    payment_from_id: str = ""
    payment_from_name: str = ""
    payment_to_id: str = ""
    payment_to_name: str = ""
    status: int = -1
    begin_time: str = ""
    end_time: str = ""
search_condition = SearchCondition()

def show_payment_record_page():
    result, company_info = g.query_company_name_company()
    if result is False:
        ui.notify('查询公司信息失败')
        return
    options = list(company_info.keys())  # 获取所有公司名称
    with ui.column().classes('w-full px-[20px] py-[10px] mt-0 items-center gap-2') \
        .style('background-color: #FFFFFF !important; border-radius: 10px;'):
        with ui.row().classes('w-full place-content-start items-center'):
            with ui.row().classes('w-[25%] place-content-start items-center'):
                ui.label('付款方').classes('w-[20%] text-[16px] text-[#333333] font-medium')
                def on_from_change(value):
                    if value in company_info:
                        search_condition.payment_from_id = company_info[value].id
                        search_condition.payment_from_name = value
                inputs.selection_w60(options, None, need_input=True, on_change=on_from_change)
            with ui.row().classes('w-[25%] place-content-start items-center'):
                ui.label('收款方').classes('w-[20%] text-[16px] text-[#333333] font-medium')
                def on_to_change(value):
                    if value in company_info:
                        search_condition.payment_to_id = company_info[value].id
                        search_condition.payment_to_name = value
                inputs.selection_w60(options, None, need_input=True, on_change=on_to_change)
            def on_status_change(value):
                if value == '未完成':
                    search_condition.status = PaymentStatus.NotFinished.value
                elif value == '完成':
                    search_condition.status = PaymentStatus.HasFinished.value
                elif value == '取消':
                    search_condition.status = PaymentStatus.Canceled.value
                else:
                    search_condition.status = -1
            inputs.selection_w40(['所有','未完成', '完成', '取消'], None, False, on_change=on_status_change)
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
            ui.button('付款', icon='img:/static/images/add_course@2x.png', on_click=add_payment) \
                .classes('w-25 rounded-md text-white') \
                .style('background-color: #65B6FF !important')
            
    table_rows: list[dict] = []
    app.storage.client['payment_record_table'] = tables.show_payment_record_table(table_rows, show_edit, delete_one)
    on_search()

def on_search() -> None:
    if 'payment_record_table' not in app.storage.client:
        return
    
    result, list_values = g.my_db.query_all_payment_record(
        search_condition.payment_from_id,
        search_condition.payment_to_id,
        search_condition.status,
        search_condition.begin_time,
        search_condition.end_time,)
    if result is False:
        ui.notify('查询付款记录失败')
        return
    app.storage.client['payment_record_table'].rows.clear()
    app.storage.client['payment_record_table'].update()
    if list_values is None or len(list_values) == 0:
        ui.notify('没有查询到付款记录')
        return
    sn = 1
    rows: list[dict[str, Any]] = []
    for item in list_values:
        payment_record = PaymentRecordDao()
        payment_record.from_db(item)
        row_dict: dict[str, Any] = payment_record.to_db()
        row_dict['sn'] = sn
        result, from_company_dao = g.my_db.query_company_by_id(payment_record.from_company_id)
        if result and from_company_dao is not None:
            row_dict['from_company_name'] = from_company_dao.brief_name
        else:
            row_dict['from_company_name'] = '未知付款方'
        result, to_company_dao = g.my_db.query_company_by_id(payment_record.to_company_id)
        if result and to_company_dao is not None:
            row_dict['to_company_name'] = to_company_dao.brief_name
        else:
            row_dict['to_company_name'] = '未知收款方'
        result, service_dao = g.my_db.query_service_record_by_id(payment_record.contract_id)
        if result and service_dao is not None:
            row_dict['contract_name'] = service_dao.contract_name
        else:
            row_dict['contract_name'] = '无'
        result, bank_account_dao = g.my_db.query_company_bank_account_by_id(payment_record.from_bank_id)
        if result and bank_account_dao is not None:
            row_dict['from_bank_name'] = bank_account_dao.bank_name
        else:
            row_dict['from_bank_name'] = '无'
        result, bank_account_dao = g.my_db.query_company_bank_account_by_id(payment_record.to_bank_id)
        if result and bank_account_dao is not None:
            row_dict['to_bank_name'] = bank_account_dao.bank_name
        else:
            row_dict['to_bank_name'] = '无'
        row_dict['payment_money'] = g.format_currency(payment_record.payment_money)
        rows.append(row_dict)
        sn += 1
    app.storage.client['payment_record_table'].rows = rows
    app.storage.client['payment_record_table'].update()


def show_edit(e: events.GenericEventArguments) -> None:
    id = e.args['id']
    if id is None or len(id) == 0:
        ui.notify('付款记录ID不能为空')
        return
    result, payment_dao = g.my_db.query_payment_record_by_id(id)
    if not result or payment_dao is None:
        ui.notify('查询付款记录失败')
        return
    modify_or_add_payment(payment_dao, is_add=False)

#
# @description: 付款
# @param None
# @return: None
#             
def add_payment():
    dao = PaymentRecordDao()
    modify_or_add_payment(dao)


def modify_or_add_payment(dao: PaymentRecordDao, is_add = True) -> None:
    result, company_info = g.query_company_name_company()
    if result is False:
        ui.notify('查询公司信息失败')
        return
    company_options = list(company_info.keys())  # 获取所有公司名称
    contract_name_dict: dict[str, ServiceRecordDao] = {}
    from_bank_account_dict: dict[str, CompanyBankAccountDao] = {}
    to_bank_account_dict: dict[str, CompanyBankAccountDao] = {}
    select_service_dao: ServiceRecordDao | None = None
    select_from_bank_account_dao: CompanyBankAccountDao | None = None
    select_to_bank_account_dao: CompanyBankAccountDao | None = None
    contract_name_select = None
    from_bank_account_select = None
    to_bank_account_select = None
    from_current_balance_label = None
    to_current_balance_label = None
    old_payment_money = dao.payment_money
    # 如果是修改付款记录，先查询合同信息
    if not is_add:
        result, contract_name_dict = g.query_service_name_dict(from_company_id=dao.from_company_id, to_company_id=dao.to_company_id)
        if result and contract_name_dict:
            for _, service_dao in contract_name_dict.items():
                if service_dao.id == dao.contract_id:
                    select_service_dao = service_dao
                    break
        # 如果处于编辑模式，则查询付款方的银行账户信息
        result, list_values = g.my_db.query_all_company_bank_account(dao.from_company_id)
        if result and list_values:
            for item in list_values:
                bank_account_dao = CompanyBankAccountDao()
                bank_account_dao.from_db(item)
                from_bank_account_dict[bank_account_dao.bank_name] = bank_account_dao
                if bank_account_dao.id == dao.from_bank_id:
                    select_from_bank_account_dao = bank_account_dao
        # 查询收款方的银行账户信息
        result, list_values = g.my_db.query_all_company_bank_account(dao.to_company_id)
        if result and list_values:
            for item in list_values:
                bank_account_dao = CompanyBankAccountDao()
                bank_account_dao.from_db(item)
                to_bank_account_dict[bank_account_dao.bank_name] = bank_account_dao
                if bank_account_dao.id == dao.to_bank_id:
                    select_to_bank_account_dao = bank_account_dao
    def change_contract_name():
        result, contract_name_dict = g.query_service_name_dict(from_company_id=dao.from_company_id, to_company_id=dao.to_company_id)
        if result is False or contract_name_dict is None or len(contract_name_dict) == 0:
            if contract_name_select is not None:
                contract_name_select.set_options([])
            return
        contract_options = list(contract_name_dict.keys())
        if contract_name_select is not None:
            contract_name_select.set_options(contract_options)
    with ui.dialog().props('persistent') as dialog, ui.card() \
        .style('background-color: #FFFFFF !important; border-radius: 10px; width: 50%; max-width: 50%;'):
        ui.label('付款').classes('w-full text-[20px] text-[#333333] font-medium')
        with ui.row().classes('w-full mt-5 place-content-start items-center'):
            ui.label('付款方').classes('w-[20%] text-[16px] text-[#333333] font-medium')
            def on_from_change(value):
                if value in company_info:
                    dao.from_company_id = company_info[value].id
                    res, list_values = g.my_db.query_all_company_bank_account(dao.from_company_id)
                    if res and list_values:
                        from_bank_account_dict.clear()
                        bank_options = []
                        for item in list_values:
                            bank_account_dao = CompanyBankAccountDao()
                            bank_account_dao.from_db(item)
                            from_bank_account_dict[bank_account_dao.bank_name] = bank_account_dao
                        bank_options = list(from_bank_account_dict.keys())
                        if from_bank_account_select is not None:
                            from_bank_account_select.set_options(bank_options)
                    if dao.to_company_id is not None and dao.to_company_id != "":
                        change_contract_name()
            from_company_select = inputs.selection_w60(company_options, None, need_input=True, on_change=on_from_change)
            def add_from_company():
                def on_complete(new_company: CompanyDao):
                    company_info[new_company.brief_name] = new_company
                    company_options.append(new_company.brief_name)
                    from_company_select.set_options(company_options)
                    to_company_select.set_options(company_options)
                    from_company_select.set_value(new_company.brief_name)
                g.add_out_company(on_complete)
            ui.button('增加公司', icon='add', on_click=add_from_company)
            if not is_add:
                if dao.from_company_id is not None and dao.from_company_id != "":
                    for company_name, company_dao in company_info.items():
                        if company_dao.id == dao.from_company_id:
                            from_company_select.set_value(company_name)
                            break
        with ui.row().classes('w-full place-content-start items-center'):
            ui.label('收款方').classes('w-[20%] text-[16px] text-[#333333] font-medium')
            def on_to_change(value):
                if value in company_info:
                    dao.to_company_id = company_info[value].id
                    res, list_values = g.my_db.query_all_company_bank_account(dao.to_company_id)
                    if res and list_values:
                        to_bank_account_dict.clear()
                        bank_options = []
                        for item in list_values:
                            bank_account_dao = CompanyBankAccountDao()
                            bank_account_dao.from_db(item)
                            to_bank_account_dict[bank_account_dao.bank_name] = bank_account_dao
                        bank_options = list(to_bank_account_dict.keys())
                        if to_bank_account_select is not None:
                            to_bank_account_select.set_options(bank_options)
                    if dao.from_company_id is not None and dao.from_company_id != "":
                        change_contract_name()
            to_company_select = inputs.selection_w60(company_options, None, need_input=True, on_change=on_to_change)
            def add_to_company():
                def on_complete(new_company: CompanyDao):
                    company_info[new_company.brief_name] = new_company
                    company_options.append(new_company.brief_name)
                    from_company_select.set_options(company_options)
                    to_company_select.set_options(company_options)
                    to_company_select.set_value(new_company.brief_name)
                g.add_out_company(on_complete)
            ui.button('增加公司', icon='add', on_click=add_to_company)
            if not is_add:
                if dao.to_company_id is not None and dao.to_company_id != "":
                    for company_name, company_dao in company_info.items():
                        if company_dao.id == dao.to_company_id:
                            to_company_select.set_value(company_name)
                            break
        with ui.row().classes('w-full place-content-start items-center'):
            ui.label('合同名称').classes('w-[20%] self-right text-[16px] text-[#333333] font-medium')
            def on_contract_change(value):
                if value in contract_name_dict:
                    select_service_dao = contract_name_dict[value]
                    dao.contract_id = select_service_dao.id
                    payment_money_label.set_text(f'未付款金额: {select_service_dao.contract_money - select_service_dao.payment_money if select_service_dao else 0}')
                    dao.should_invoice_money = select_service_dao.payment_money + dao.payment_money
                    dao.has_invoice_money = select_service_dao.invoice_money
                    gap_money = dao.should_invoice_money - select_service_dao.invoice_money
                    dao.remain_invoice_money = 0 if gap_money < 0 else gap_money
            contract_name_select = inputs.selection_w60([], None, need_input=True, on_change=on_contract_change)
            if not is_add:
                if len(contract_name_dict) > 0:
                    contract_options = list(contract_name_dict.keys())
                    contract_name_select.set_options(contract_options)
                    if select_service_dao is not None:
                        contract_name_select.set_value(select_service_dao.contract_name)
        with ui.row().classes('w-full place-content-start items-center'):
            ui.label('付款方银行账户').classes('w-[20%] self-right text-[16px] text-[#333333] font-medium')
            def on_bank_account_change(value):
                nonlocal select_from_bank_account_dao
                if value in from_bank_account_dict:
                    dao.from_bank_id = from_bank_account_dict[value].id
                    select_from_bank_account_dao = from_bank_account_dict[value]
                    if from_current_balance_label is not None and select_from_bank_account_dao is not None:
                        from_current_balance_label.set_text(g.format_currency(select_from_bank_account_dao.current_balance))
            from_bank_account_select = inputs.selection_w60(list(from_bank_account_dict.keys()), None, need_input=True, on_change=on_bank_account_change)
            if not is_add:
                if select_from_bank_account_dao is not None:
                    from_bank_account_select.set_value(select_from_bank_account_dao.bank_name)
        with ui.row().classes('w-full place-content-start items-center'):
            ui.label('付款方账户余额').classes('w-[20%] self-right text-[16px] text-[#333333] font-medium')
            from_current_balance_label = ui.label('').classes('w-[40%] text-[14px] text-red font-small self-center')
            if not is_add and select_from_bank_account_dao is not None:
                from_current_balance_label.set_text(g.format_currency(select_from_bank_account_dao.current_balance))
        with ui.row().classes('w-full place-content-start items-center'):
            ui.label('收款方银行账户').classes('w-[20%] self-right text-[16px] text-[#333333] font-medium')
            def on_bank_account_change(value):
                nonlocal select_to_bank_account_dao
                if value in to_bank_account_dict:
                    dao.to_bank_id = to_bank_account_dict[value].id
                    select_to_bank_account_dao = to_bank_account_dict[value]
                    if to_current_balance_label is not None and select_to_bank_account_dao is not None:
                        to_current_balance_label.set_text(g.format_currency(select_to_bank_account_dao.current_balance))
            to_bank_account_select = inputs.selection_w60(list(to_bank_account_dict.keys()), None, need_input=True, on_change=on_bank_account_change)
            if not is_add:
                if select_to_bank_account_dao is not None:
                    to_bank_account_select.set_value(select_to_bank_account_dao.bank_name)
        with ui.row().classes('w-full place-content-start items-center'):
            ui.label('收款方账户余额').classes('w-[20%] self-right text-[16px] text-[#333333] font-medium')
            to_current_balance_label = ui.label('').classes('w-[40%] text-[14px] text-red font-small self-center')
            if not is_add and select_to_bank_account_dao is not None:
                to_current_balance_label.set_text(g.format_currency(select_to_bank_account_dao.current_balance))
        with ui.row().classes('w-full place-content-start items-center'):
            ui.label('付款金额').classes('w-[20%] self-right text-[16px] text-[#333333] font-medium')
            def on_payment_change(e: events.ValueChangeEventArguments) -> None:
                value = e.value
                if value is None or value == '':
                    dao.payment_money = 0
                else:
                    try:
                        dao.payment_money = float(value)
                        if select_service_dao is not None:
                            gap_payment_money = select_service_dao.contract_money - select_service_dao.payment_money
                            if dao.payment_money > gap_payment_money:
                                ui.notify(f'付款金额不能大于未付款金额，未付款金额: {gap_payment_money}')
                                dao.payment_money = gap_payment_money
                                return
                            dao.should_invoice_money = select_service_dao.payment_money + dao.payment_money
                            dao.has_invoice_money = select_service_dao.invoice_money
                            gap_money = dao.should_invoice_money - select_service_dao.invoice_money
                            dao.remain_invoice_money = 0 if gap_money < 0 else gap_money
                        if select_from_bank_account_dao is not None:
                            if dao.payment_money > select_from_bank_account_dao.current_balance:
                                ui.notify(f'付款金额不能大于账户余额，当前账户余额: {g.format_currency(select_from_bank_account_dao.current_balance)}')
                                dao.payment_money = select_from_bank_account_dao.current_balance
                    except ValueError:
                        ui.notify('开票金额必须是数字')
                        dao.payment_money = 0
                # 更新金额显示
                if from_current_balance_label is not None and select_from_bank_account_dao is not None:
                    from_current_balance_label.set_text(g.format_currency(select_from_bank_account_dao.current_balance - dao.payment_money + old_payment_money))
                if to_current_balance_label is not None and select_to_bank_account_dao is not None:
                    to_current_balance_label.set_text(g.format_currency(select_to_bank_account_dao.current_balance + dao.payment_money - old_payment_money))
            ui.input(placeholder='请输入付款金额', value=str(dao.payment_money)) \
                .props('rounded-md outlined dense') \
                .classes('w-[30%] self-center item-center ') \
                .bind_value_from(dao, 'payment_money') \
                .on_value_change(on_payment_change)
            payment_money_label = ui.label('').classes('w-[40%] text-[14px] text-red font-small self-center')
        with ui.row().classes('w-full place-content-start items-center'):
            ui.label('状态').classes('w-[20%] self-right text-[16px] text-[#333333] font-medium')
            status_options = ['未完成', '完成', '取消']
            def on_status_change(value):
                if value == '未完成':
                    dao.status = PaymentStatus.NotFinished.value
                elif value == '完成':
                    dao.status = PaymentStatus.HasFinished.value
                elif value == '取消':
                    dao.status = PaymentStatus.Canceled.value
                else:                    
                    dao.status = -1
            status_select = inputs.selection_w40(status_options, None, False, on_change=on_status_change)
            if not is_add:
                if dao.status == PaymentStatus.NotFinished.value:
                    status_select.set_value('未完成')
                elif dao.status == PaymentStatus.HasFinished.value:
                    status_select.set_value('完成')
                elif dao.status == PaymentStatus.Canceled.value:
                    status_select.set_value('取消')
        with ui.row().classes('w-full place-content-start items-center'):
            ui.label('事项').classes('w-[20%] self-right text-[16px] text-[#333333] font-medium')
            ui.input(placeholder='请输入事项', value=dao.item_name) \
                .props('rounded-md outlined dense') \
                .classes('w-[30%] self-center item-center ') \
                .bind_value_from(dao, 'item_name') \
                .bind_value_to(dao, 'item_name')
        with ui.row().classes('w-full place-content-start items-center'):
            ui.label('备注').classes('w-[20%] self-right text-[16px] text-[#333333] font-medium')
            ui.input(placeholder='请输入备注', value=dao.remarks) \
                .props('rounded-md outlined dense') \
                .classes('w-[60%] self-center item-center ') \
                .bind_value_from(dao, 'remarks') \
                .bind_value_to(dao, 'remarks')
        with ui.row().classes('w-full place-content-start items-center'):
            ui.label('应开票金额').classes('w-[20%] self-right text-[16px] text-[#333333] font-medium')
            ui.label('').classes('w-[30%] text-[14px] text-red font-small self-center').bind_text_from(dao, 'should_invoice_money')
        with ui.row().classes('w-full place-content-start items-center'):
            ui.label('已开票金额').classes('w-[20%] self-right text-[16px] text-[#333333] font-medium')
            ui.label('').classes('w-[30%] text-[14px] text-red font-small self-center').bind_text_from(dao, 'has_invoice_money')
        with ui.row().classes('w-full place-content-start items-center'):
            ui.label('未开票金额').classes('w-[20%] self-right text-[16px] text-[#333333] font-medium')
            ui.label('').classes('w-[30%] text-[14px] text-red font-small self-center').bind_text_from(dao, 'remain_invoice_money')
        with ui.row().classes('w-full place-content-end'):         
            ui.button('取消', color=None, on_click=dialog.close) \
                .props('flat') \
                .classes('w-[120px] text-[16px] text-[#888888] font-[400]') \
                .style('background-color: #FFFFFF !important;border-radius: 10px;border: 1px solid #888888;')
            def on_create():
                do_create_dao(dao,
                    select_from_bank_account_dao,
                    select_to_bank_account_dao,
                    select_service_dao,
                    old_payment_money,
                    is_add)
                dialog.close()
            ui.button('确定', color=None, on_click=on_create) \
                .props('flat') \
                .classes('w-[120px] text-[16px] text-white font-[400]') \
                .style('background-color: #65B6FF !important; border-radius: 10px')
    dialog.open()

"""
# @description: 创建付款记录DAO
# @param dao: PaymentRecordDao对象
# @param from_bank_dao: 付款方银行账户DAO对象
# @param to_bank_dao: 收款方银行账户DAO对象
# @param service_dao: 合同服务记录DAO对象
# @return: bool，表示创建是否成功
"""
def do_create_dao(dao: PaymentRecordDao,
        from_bank_dao: CompanyBankAccountDao|None,
        to_bank_dao: CompanyBankAccountDao|None,
        service_dao: ServiceRecordDao|None,
        old_payment_money: float,
        is_add: bool) -> bool:
    if dao.from_company_id == '' or dao.to_company_id == "" or dao.payment_money == 0:
        ui.notify('付款方，收款方,付款额不能为空')
        return False
    if is_add:
        dao.create_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        # if select_service_dao is not None:
        #     select_service_dao.payment_money += dao.payment_money
        #     if select_service_dao.payment_money == select_service_dao.contract_money:
        #         dao.status = 1
        #     else:
        #         dao.status = 0
        result, _ = g.my_db.add_payment_record(dao.to_db())
        if result:
            # g.update_contract_payment_money(dao.contract_id, dao.payment_money)
            # 更新付款放的银行账户余额
            if from_bank_dao is not None:
                from_bank_dao.current_balance = from_bank_dao.current_balance - dao.payment_money + old_payment_money
                g.my_db.update_company_bank_account(from_bank_dao.to_db(), {})
            # 更新收款方的银行账户余额
            if to_bank_dao is not None:
                to_bank_dao.current_balance = to_bank_dao.current_balance + dao.payment_money - old_payment_money
                g.my_db.update_company_bank_account(to_bank_dao.to_db(), {})
            ui.notify('添加记录成功')
            on_search()
        else:
            ui.notify('添加记录失败')
    else:
        # if select_service_dao is not None:
        #     select_service_dao.payment_money += dao.payment_money - old_payment_money
        #     if select_service_dao.payment_money == select_service_dao.contract_money:
        #         dao.status = 1
        #     else:
        #         dao.status = 0
        result = g.my_db.update_payment_record(dao.to_db(), {'id': dao.id})
        if result:
            # g.update_contract_payment_money(dao.contract_id, dao.payment_money - old_payment_money)
            # 更新付款放的银行账户余额
            if from_bank_dao is not None:
                from_bank_dao.current_balance = from_bank_dao.current_balance - dao.payment_money + old_payment_money
                g.my_db.update_company_bank_account(from_bank_dao.to_db(), {})
            # 更新收款方的银行账户余额
            if to_bank_dao is not None:
                to_bank_dao.current_balance = to_bank_dao.current_balance + dao.payment_money - old_payment_money
                g.my_db.update_company_bank_account(to_bank_dao.to_db(), {})
            ui.notify('修改记录成功')
            on_search()
        else:
            ui.notify('修改记录失败')
    return True

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
    app.storage.client['payment_record_table'].selected.clear()

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