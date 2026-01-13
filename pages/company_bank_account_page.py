'''
Author: liguoqiang
Date: 2025-03-13 11:31:42
LastEditors: liguoqiang
LastEditTime: 2025-03-19 14:21:03
Description: 
'''
from dataclasses import dataclass, field
from nicegui import ui,app,events
from components import tables, inputs, labels, dialogs
from dao.company_dao import CompanyDao
from dao.company_bank_account_dao import BackType, CompanyBankAccountDao
from typing import Any, Optional, cast
from utils import global_vars as g

@dataclass
class SearchCondition:
    company_dao: CompanyDao = CompanyDao()
search_condition = SearchCondition()

#
# @description: 显示公司银行账户页面
# @return {*}
#
def show_company_bank_account_page() -> None:
    result, company_info = g.query_company_name_company()
    if result is False:
        ui.notify('查询公司信息失败')
        return
    options = list(company_info.keys())  # 获取所有公司名称
    def on_change(value):
        if value in company_info:
            search_condition.company_dao = company_info[value]
            on_search()
    with ui.row().classes('w-full h-[60px] px-[20px] py-[10px] place-content-between items-center') \
        .style('background-color: #FFFFFF !important; border-radius: 10px;'):
        with ui.row().classes('h-full items-center'):
            company_search_select = inputs.selection_w80(options, None, need_input=True, on_change=on_change)
        with ui.row().classes('h-full ml-[30px] items-center'):
            ui.button('刷新', icon='img:/static/images/refresh@2x.png', on_click=on_search) \
                .classes('w-25 rounded-md text-white') \
                .style('background-color: #6C96FB !important')
            ui.button('删除', icon='img:/static/images/delete@2x.png', on_click=del_select) \
                .classes('w-25 rounded-md text-red') \
                .style('background-color: rgba(255,77,77,0.39) !important')
            ui.button('新建', icon='img:/static/images/add_course@2x.png', on_click=add_company_bank_account) \
                .classes('w-25 rounded-md text-white') \
                .style('background-color: #65B6FF !important')
            
    table_rows: list[dict] = []
    app.storage.client['company_bank_account_table'] = tables.show_company_bank_account_table(table_rows, show_edit, show_delete)
    on_search()

def on_search() -> None:
    if 'company_bank_account_table' not in app.storage.client:
        return
    app.storage.client['company_bank_account_table'].rows.clear()
    app.storage.client['company_bank_account_table'].update()
    result, list_values = g.my_db.query_all_company_bank_account(search_condition.company_dao.id)
    if result is False:
        ui.notify('查询公司银行账户信息失败')
        return
    if list_values is None or len(list_values) == 0:
        ui.notify('没有公司银行账户信息')
        return
    def do_refresh() -> list[dict[str, Any]]:
        sn = 1
        rows: list[dict[str, Any]] = []
        for item in list_values:
            row_dict: dict[str, Any] = {}
            dao = CompanyBankAccountDao()
            dao.from_db(item)
            result, company_dao = g.my_db.query_company_by_id(dao.company_id)
            row_dict['sn'] = sn
            company_name = '未知开票方'
            if result and company_dao is not None:
                company_name = company_dao.brief_name
            row_dict['company_name'] = company_name
            row_dict['opening_balance'] = g.format_currency(dao.opening_balance)
            row_dict['current_balance'] = g.format_currency(dao.current_balance)
            row_dict.update(dao.to_db())
            rows.append(row_dict)
            sn += 1
        return rows
    app.storage.client['company_bank_account_table'].rows = do_refresh()
    app.storage.client['company_bank_account_table'].update()

#
# @description: 显示删除操作，由table组件触发
#
def show_delete(e: events.GenericEventArguments) -> None:
    id = e.args['id']
    del_by_ids([id])


#
# @description: 批量删除
# @return {*}
#
def del_select():
    if 'company_bank_account_table' not in app.storage.client:
        return
    selection = app.storage.client['company_bank_account_table'].selected
    ids = [item['id'] for item in selection]
    del_by_ids(ids)
    app.storage.client['company_bank_account_table'].selected.clear()

def del_by_ids(ids: list[str]) -> None:
    if ids is None or len(ids) == 0:
        ui.notify('请选择要删除的公司银行账户')
        return
    def make_delete():
        delok = True
        for id in ids:
            if id is None or len(id) == 0:
                continue
            result = g.my_db.delete_company_bank_account(id)
            if result is False:
                delok = False
                ui.notify(f'删除公司银行账户失败: {id}')
                return
        if delok is True:
            ui.notify('删除成功')
            on_search()
    dialogs.make_sure_dialog('确认要进行删除操作?', make_delete)

def show_edit(e: events.GenericEventArguments) -> None:
    id = e.args['id']
    if id is None or len(id) == 0:
        ui.notify('请选择要编辑的公司银行账户')
        return
    result, dao = g.my_db.query_company_bank_account_by_id(id)
    if result is False or dao is None:
        ui.notify('查询公司银行账户信息失败')
        return
    modify_or_new_company_bank_account(dao, is_add=False)
#
# @description: 显示添加公司银行账户对话框
# @return {*}
#
def add_company_bank_account():
    account_dao = CompanyBankAccountDao()
    modify_or_new_company_bank_account(account_dao, is_add=True)


def modify_or_new_company_bank_account(account_dao: CompanyBankAccountDao, is_add: bool = True) -> None:
    result, company_info = g.query_company_name_company()
    if result is False:
        ui.notify('查询公司信息失败')
        return
    options = list(company_info.keys())  # 获取所有公司名称
    company_dao: CompanyDao = CompanyDao()
    if not is_add:
        result, value = g.my_db.query_company_by_id(account_dao.company_id)
        if result is False or value is None:
            ui.notify('查询公司信息失败')
        else:
            company_dao = cast(CompanyDao, value)
    with ui.dialog().props('persistent') as dialog, ui.card().classes('w-1/2') \
        .style('background-color: #FFFFFF !important; border-radius: 10px;'):
        if is_add:
            ui.label('增加银行账户').classes('w-full text-[20px] text-[#333333] font-medium')
        else:
            ui.label('修改银行账户').classes('w-full text-[20px] text-[#333333] font-medium')
        with ui.row().classes('w-full mt-5 place-content-start items-center'):
            ui.label('选择公司').classes('w-[20%] self-right text-[16px] text-[#333333] font-medium')
            def on_company_change(value):
                if value in company_info:
                    account_dao.company_id = company_info[value].id
            company_select = inputs.selection_w60(options, None, need_input=True, on_change=on_company_change)
            if not is_add:
                company_select.set_value(company_dao.brief_name)
            def add_out_company():
                def on_complete(new_company: CompanyDao):
                    options.append(new_company.brief_name)
                    company_select.set_options(options)
                    company_select.set_value(new_company.brief_name)
                g.add_out_company(on_complete)
            ui.button('增加公司', icon='add', on_click=add_out_company)
        with ui.row().classes('w-full place-content-start items-center'):
            ui.label('账号').classes('w-[20%] self-right text-[16px] text-[#333333] font-medium')
            ui.input(placeholder='请输入银行账户') \
                .props('rounded-md outlined dense') \
                .classes('self-left') \
                .bind_value_from(account_dao, 'bank_account') \
                .bind_value_to(account_dao, 'bank_account')
        with ui.row().classes('w-full place-content-start items-center'):
            ui.label('银行名称').classes('w-[20%] self-right text-[16px] text-[#333333] font-medium')
            ui.input(placeholder='请输入银行名称') \
                .props('rounded-md outlined dense') \
                .classes('self-left') \
                .bind_value_from(account_dao, 'bank_name') \
                .bind_value_to(account_dao, 'bank_name')
        with ui.row().classes('w-full place-content-start items-center'):
            ui.label('账户类型').classes('w-[20%] self-right text-[16px] text-[#333333] font-medium')
            def on_change(value):
                if value is None or len(value) == 0:
                    return
                match value:
                    case '基本户':
                        account_dao.account_type = BackType.BASIC.value
                    case '一般户':
                        account_dao.account_type = BackType.GENERAL.value
                    case _:
                        account_dao.account_type = BackType.OTHER.value
            account_type_select = inputs.selection_w40(['基本户', '一般户'], value='基本户', need_input=False, on_change=on_change)
            if not is_add:
                if account_dao.account_type == BackType.BASIC.value:
                    account_type_select.set_value('基本户')
                else:
                    account_type_select.set_value('一般户')
        with ui.row().classes('w-full place-content-start items-center'):
            ui.label('期初余额').classes('w-[20%] self-right text-[16px] text-[#333333] font-medium')
            current_balance_label = None
            def on_opening_balance_change(e: events.ValueChangeEventArguments):
                value = e.value
                if is_add and current_balance_label is not None:
                    if value is None or len(value) == 0:
                        current_balance_label.set_text(g.format_currency(0.0))
                    else:
                        current_balance_label.set_text(g.format_currency(float(value)))
            ui.input(placeholder='请输入期初余额') \
                .props('rounded-md outlined dense type="number"') \
                .classes('self-left') \
                .on_value_change(on_opening_balance_change) \
                .bind_value_from(account_dao, 'opening_balance') \
                .bind_value_to(account_dao, 'opening_balance')
        with ui.row().classes('w-full place-content-start items-center'):
            ui.label('当前余额').classes('w-[20%] self-right text-[16px] text-[#333333] font-medium')
            current_balance_label = ui.label('').classes('w-[40%] text-[14px] text-red font-small self-center')
            current_balance_label.set_text(g.format_currency(account_dao.current_balance))
        with ui.row().classes('w-full place-content-start items-center'):
            ui.label('银行地址').classes('w-[20%] self-right text-[16px] text-[#333333] font-medium')
            ui.input(placeholder='请输入银行地址') \
                .props('rounded-md outlined dense') \
                .classes('w-80 self-left') \
                .bind_value_from(account_dao, 'bank_address') \
                .bind_value_to(account_dao, 'bank_address')
        
        with ui.row().classes('w-full place-content-end items-center'):         
            ui.button('取消', color=None, on_click=dialog.close) \
                .props('flat') \
                .classes('w-[120px] text-[16px] text-[#888888] font-[400]') \
                .style('background-color: #FFFFFF !important;border-radius: 10px;border: 1px solid #888888;')
            def on_create_account():
                if account_dao.company_id is None or len(account_dao.company_id) == 0:
                    ui.notify('请选择公司')
                    return
                if account_dao.bank_account == "" or account_dao.bank_name == "" or account_dao.bank_address == "":
                    ui.notify('账户名称,地址不能为空')
                    return
                data = account_dao.to_db()
                if is_add:
                    result, _ = g.my_db.add_company_bank_account(data)
                    if result is True:
                        ui.notify('添加成功')
                        on_search()
                        dialog.close()
                    else:
                        ui.notify('添加失败')
                else:
                    result = g.my_db.update_company_bank_account(data, {'id': account_dao.id})
                    if result is True:
                        ui.notify('修改成功')
                        on_search()
                        dialog.close()
                    else:
                        ui.notify('修改失败')
            ui.button('确定', color=None, on_click=on_create_account) \
                .props('flat') \
                .classes('w-[120px] text-[16px] text-white font-[400]') \
                .style('background-color: #65B6FF !important; border-radius: 10px')
    dialog.open()


