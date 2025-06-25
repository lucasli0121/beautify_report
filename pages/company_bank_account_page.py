'''
Author: liguoqiang
Date: 2025-03-13 11:31:42
LastEditors: liguoqiang
LastEditTime: 2025-03-19 14:21:03
Description: 
'''
from nicegui import ui,app,events
from components import tables, inputs, labels
from dao.company_dao import CompanyDao
from dao.company_bank_account_dao import CompanyBankAccountDao
from typing import Any, Optional
from utils import global_vars as g

#
# @description: 显示公司银行账户页面
# @return {*}
#
def show_company_bank_account_page() -> None:
    with ui.row().classes('w-full h-[80px] px-[20px] mt-0 place-content-between gap-0') \
        .style('background-color: #FFFFFF !important; border-radius: 10px;'):
        with ui.row().classes('h-full items-center'):
            name = ''
            if 'company_dao' in app.storage.user:
                company_dao: CompanyDao = app.storage.user['company_dao']
                name = company_dao.name
            labels.normal_sm_black_label(f'公司银行账户: {name}') \
                .classes('text-[16px] text-[#333333] font-medium')
            
        with ui.row().classes('h-full ml-[30px] items-center'):
            ui.button('新建账户', icon='img:/static/images/add_course@2x.png', on_click=add_company_bank_account) \
                .classes('w-25 rounded-md text-white') \
                .style('background-color: #65B6FF !important')
            
    table_rows: list[dict] = []
    course_table: Optional[ui.table] = tables.show_company_bank_account_table(table_rows, show_delete)
    app.storage.client['company_bank_account_table'] = course_table
    on_search()

def on_search() -> None:
    if 'company_dao' not in app.storage.user:
        return
    company_dao: CompanyDao = app.storage.user['company_dao']
    result, result_list = g.my_db.query_all_company_bank_account(str(company_dao.id))
    if result is False:
        ui.notify('查询公司银行账户失败')
        return
    if 'company_bank_account_table' in app.storage.client:
        app.storage.client['company_bank_account_table'].rows.clear()
        app.storage.client['company_bank_account_table'].update()
        if result_list is None or len(result_list) == 0:
            ui.notify('没有查询到公司银行账户信息')
            return
        sn = 1
        for item in result_list:
            row_dict: dict[str, Any] = {}
            row_dict['sn'] = sn
            row_dict['name'] = company_dao.name
            row_dict.update(item.__dict__)
            app.storage.client['company_bank_account_table'].add_row(row_dict)
            sn += 1
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
        dialog.close()

    with ui.dialog().props('persistent') as dialog, ui.card() \
        .style('background-color: #FFFFFF !important; border-radius: 10px;'):
        ui.label('确认要进行删除操作?').classes('w-full text-[20px] text-[#333333] font-medium')
        with ui.row().classes('w-full place-content-end'):
            ui.button('取消', color=None, on_click=dialog.close) \
                .props('flat') \
                .classes('w-[120px] text-[16px] text-[#888888] font-[400]') \
                .style('background-color: #FFFFFF !important;border-radius: 10px;border: 1px solid #888888;')
            ui.button('确定', color=None, on_click=make_delete) \
                .props('flat') \
                .classes('w-[120px] text-[16px] text-white font-[400]') \
                .style('background-color: #65B6FF !important; border-radius: 10px')
    
    dialog.open()

#
# @description: 显示添加公司银行账户对话框
# @return {*}
#
def add_company_bank_account():
    account_dao = CompanyBankAccountDao()
    if 'company_dao' in app.storage.user:
        company_dao: CompanyDao = app.storage.user['company_dao']
        account_dao.company_id = str(company_dao.id)
    else:
        ui.notify('请先选择公司')
        return
    with ui.dialog().props('persistent') as dialog, ui.card().classes('w-1/2') \
        .style('background-color: #FFFFFF !important; border-radius: 10px;'):
        ui.label('增加银行账户').classes('w-full text-[20px] text-[#333333] font-medium')
        with ui.row().classes('w-full mt-5 place-content-between'):
            ui.label('账号').classes('w-full text-[16px] text-[#333333] font-medium')
            classes_ui = ui.input(placeholder='请输入银行账户') \
                .props('rounded-md outlined dense') \
                .classes('w-full self-center item-center ')
            classes_ui.bind_value_to(account_dao, 'bank_account')
        with ui.row().classes('w-full place-content-between'):
            ui.label('银行名称').classes('w-full text-[16px] text-[#333333] font-medium')
            subject_ui = ui.input(placeholder='请输入银行名称') \
                .props('rounded-md outlined dense') \
                .classes('w-full self-center item-center ')
            subject_ui.bind_value_to(account_dao, 'bank_name')
        with ui.row().classes('w-full place-content-between'):
            ui.label('账户类型').classes('w-full text-[16px] text-[#333333] font-medium')
            def on_change(value):
                if value is None or len(value) == 0:
                    return
                match value:
                    case '基本户':
                        account_dao.account_type = 0
                    case '一般户':
                        account_dao.account_type = 1
                    case _:
                        account_dao.account_type = 0
            inputs.selection_w40(['基本户', '一般户'], value='基本户', on_change=on_change)
        with ui.row().classes('w-full place-content-between'):
            ui.label('银行地址').classes('w-full text-[16px] text-[#333333] font-medium')
            ui.input(placeholder='请输入银行地址') \
                .props('rounded-md outlined dense') \
                .classes('w-full self-center item-center ') \
                .bind_value_to(account_dao, 'bank_address')
        
        with ui.row().classes('w-full place-content-end'):         
            ui.button('取消', color=None, on_click=dialog.close) \
                .props('flat') \
                .classes('w-[120px] text-[16px] text-[#888888] font-[400]') \
                .style('background-color: #FFFFFF !important;border-radius: 10px;border: 1px solid #888888;')
            def on_create_account():
                if account_dao.bank_account == "" or account_dao.bank_name == "" or account_dao.bank_address == "":
                    ui.notify('账户名称,地址不能为空')
                    return
                data = account_dao.to_db()
                result = g.my_db.add_company_bank_account(data)
                if result is True:
                    ui.notify('添加成功')
                    on_search()
                    dialog.close()
                else:
                    ui.notify('添加失败')
            ui.button('确定', color=None, on_click=on_create_account) \
                .props('flat') \
                .classes('w-[120px] text-[16px] text-white font-[400]') \
                .style('background-color: #65B6FF !important; border-radius: 10px')
    dialog.open()


