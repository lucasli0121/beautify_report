from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, cast
from nicegui import ui,app,events
from components import dialogs, inputs, tables
from dao.company_dao import CompanyDao
from dao.invoice_title_dao import InvoiceTitleDao
from utils import global_vars as g

@dataclass
class SearchCondition:
    company_list: list[CompanyDao] = field(default_factory=list)

search_condition = SearchCondition()

def show_invoice_title_page() -> None:
    result, company_info = g.query_company_name_company()
    if result is False:
        ui.notify('查询公司信息失败')
        return
    options = list(company_info.keys())  # 获取所有公司名称
    def on_change(value):
        if value in company_info:
            company_dao = company_info[value]
            search_condition.company_list = [company_dao]
            on_search()

    with ui.row().classes('w-full h-[60px] px-[20px] py-[10px] place-content-between items-center') \
        .style('background-color: #FFFFFF !important; border-radius: 10px;'):
        inputs.selection_w80(options, None, need_input=True, on_change=on_change)
        with ui.row().classes('h-full ml-[30px] items-center'):
            ui.button('刷新', icon='img:/static/images/refresh@2x.png', on_click=on_search) \
                .classes('w-25 rounded-md text-white') \
                .style('background-color: #6C96FB !important')
            ui.button('删除', icon='img:/static/images/delete@2x.png', on_click=del_select) \
                .classes('w-25 rounded-md text-red') \
                .style('background-color: rgba(255,77,77,0.39) !important')
            ui.button('新建', icon='img:/static/images/add_course@2x.png', on_click=add_invoice_title) \
                .classes('w-25 rounded-md text-white') \
                .style('background-color: #65B6FF !important')
    search_condition.company_list = list(company_info.values())
    table_rows: list[dict] = []
    app.storage.client['invoice_title_table'] = tables.show_invoice_title_table(table_rows, edit_invoice_title, delete_one)
    on_search()
    

def on_search() -> None:
    if 'invoice_title_table' not in app.storage.client:
        return
    app.storage.client['invoice_title_table'].rows.clear()
    row_dict: dict[str, Any] = {}
    sn = 1
    for company_dao in search_condition.company_list:
        if not isinstance(company_dao, CompanyDao):
            continue
        result, invoice_title_list = g.my_db.query_invoice_title_all(company_dao.id)
        if result is False or invoice_title_list is None:
            continue
        for invoice_title in invoice_title_list:
            dao = InvoiceTitleDao()
            dao.from_db(invoice_title)
            row_dict.update({
                'id': dao.id,
                'sn': sn,
                'company_name': company_dao.name,
                'address': company_dao.address,
                'tax_no': company_dao.tax_no,
                'bank_name': dao.bank_name,
                'bank_account': dao.bank_account,
                'contact_phone': dao.contact_phone
            })
            app.storage.client['invoice_title_table'].add_row(row_dict)
            sn += 1
    app.storage.client['invoice_title_table'].update()

def add_invoice_title() -> None:
    """
    @function: add_invoice_title
    @description: 新建发票抬头
    @param None
    @return: None
    """
    dao = InvoiceTitleDao()
    dao.company_id = ''
    dao.create_time = ''
    modify_or_new_invoice_title(dao)

#
# @description: 增加发票抬头
# @param None
# @return: None
#           
def modify_or_new_invoice_title(dao: InvoiceTitleDao, is_add: bool = True) -> None:
    result, company_info = g.query_company_name_company()
    if result is False:
        ui.notify('查询公司信息失败')
        return
    options = list(company_info.keys())  # 获取所有公司名称
    company_dao: CompanyDao = CompanyDao()
    if not is_add:
        result, value = g.my_db.query_company_by_id(dao.company_id)
        if result is False or value is None:
            ui.notify('查询公司信息失败')
            return
        company_dao = cast(CompanyDao, value)
    with ui.dialog().props('persistent') as dialog, ui.card().classes('w-1/2') \
        .style('background-color: #FFFFFF !important; border-radius: 10px;'):
        address_input = None
        taxno_input = None
        ui.label('发票抬头').classes('w-full text-[20px] text-[#333333] font-medium')
        with ui.row().classes('w-full mt-5 place-content-start items-center'):
            ui.label('公司').classes('w-[20%] text-[16px] text-[#333333] font-medium')
            def on_company_change(value):
                if value in company_info:
                    company_dao = company_info[value]
                    dao.company_id = company_dao.id
                    if address_input is not None:
                        address_input.set_value(company_dao.address)
                    if taxno_input is not None:
                        taxno_input.set_value(company_dao.tax_no)
            company_select = inputs.selection_w60(options, None, need_input=True, on_change=on_company_change)
            def add_out_company():
                def on_complete(new_company: CompanyDao):
                    company_info[new_company.name] = new_company
                    options.append(new_company.name)
                    company_select.set_options(options)
                    company_select.set_value(new_company.name)
                g.add_out_company(on_complete)
            ui.button('增加公司', icon='add', on_click=add_out_company)
            if not is_add:
                company_select.set_value(company_dao.name)
        with ui.row().classes('w-full place-content-start items-center'):
            ui.label('地址').classes('w-[20%] self-right text-[16px] text-[#333333] font-medium')
            address_input = ui.input() \
                .props('rounded-md outlined dense readonly') \
                .classes('w-[70%] self-center item-center ')
            if not is_add:
                address_input.set_value(company_dao.address)
        with ui.row().classes('w-full place-content-start items-center'):
            ui.label('税号').classes('w-[20%] self-right text-[16px] text-[#333333] font-medium')
            taxno_input = ui.input() \
                .props('rounded-md outlined dense readonly') \
                .classes('w-[50%] self-center item-center ')
            if not is_add:
                taxno_input.set_value(company_dao.tax_no)
        with ui.row().classes('w-full place-content-start items-center'):
            ui.label('银行名称').classes('w-[20%] self-right text-[16px] text-[#333333] font-medium')
            ui.input(placeholder='请输入银行名称') \
                .props('rounded-md outlined dense ') \
                .classes('w-[50%] self-center item-center ') \
                .bind_value_from(dao, 'bank_name') \
                .bind_value_to(dao, 'bank_name')
        with ui.row().classes('w-full place-content-start items-center'):
            ui.label('银行账户').classes('w-[20%] self-right text-[16px] text-[#333333] font-medium')
            ui.input(placeholder='请输入银行账户') \
                .props('rounded-md outlined dense') \
                .classes('w-[50%] self-center item-center ') \
                .bind_value_from(dao, 'bank_account') \
                .bind_value_to(dao, 'bank_account')
        with ui.row().classes('w-full place-content-start items-center'):
            ui.label('联系电话').classes('w-[20%] self-right text-[16px] text-[#333333] font-medium')
            ui.input(placeholder='请输入联系电话') \
                .props('rounded-md outlined dense') \
                .classes('w-[50%] self-center item-center ') \
                .bind_value_from(dao, 'contact_phone') \
                .bind_value_to(dao, 'contact_phone')
        with ui.row().classes('w-full place-content-end'):         
            ui.button('取消', color=None, on_click=dialog.close) \
                .props('flat') \
                .classes('w-[120px] text-[16px] text-[#888888] font-[400]') \
                .style('background-color: #FFFFFF !important;border-radius: 10px;border: 1px solid #888888;')
            def on_create():
                if dao.company_id == "" or dao.bank_name == "" or dao.bank_account == "":
                    ui.notify('公司名称、银行名称和银行账户不能为空')
                    return
                if dao.contact_phone == "":
                    ui.notify('联系电话不能为空')
                    return
                dao.create_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                if is_add:
                    result, _ = g.my_db.add_invoice_title(dao.to_db())
                    if result:
                        ui.notify('添加发票抬头成功')
                        on_search()
                        dialog.close()
                    else:
                        ui.notify('添加发票抬头失败')
                else:
                    if g.my_db.update_invoice_title(dao.to_db(), {'id': dao.id}):
                        ui.notify('更新发票抬头成功')
                        on_search()
                        dialog.close()
                    else:
                        ui.notify('更新发票抬头失败')
            ui.button('确定', color=None, on_click=on_create) \
                .props('flat') \
                .classes('w-[120px] text-[16px] text-white font-[400]') \
                .style('background-color: #65B6FF !important; border-radius: 10px')
    dialog.open()

def edit_invoice_title(e: events.GenericEventArguments):
    id = e.args['id']
    if id is None or len(id) == 0:
        ui.notify('请选择要编辑的开票记录')
        return
    result, invoice_title_dao = g.my_db.query_invoice_title_by_id(id)
    if result is False or invoice_title_dao is None:
        ui.notify('查询开票记录失败')
        return
    modify_or_new_invoice_title(invoice_title_dao, is_add=False)

'''
# @description: 批量删除
# @param None  
# @return: None
# 
'''
def del_select():
    if 'invoice_title_table' not in app.storage.client:
        ui.notify('请先查询发票抬头记录')
        return
    selection = app.storage.client['invoice_title_table'].selected
    if not selection:
        ui.notify('请选择要删除的记录')
        return
    ids = [item['id'] for item in selection]
    if not ids:
        ui.notify('没有选中任何记录')
        return
    del_by_ids(ids)
    app.storage.client['invoice_title_table'].selected.clear()
    

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
            result = g.my_db.delete_invoice_title(id)
            if result is False:
                delok = False
                ui.notify(f'删除记录失败: {id}')
                return
        if delok is True:
            ui.notify('删除记录成功')
            on_search()

    dialogs.make_sure_dialog('确认要进行删除操作?', on_ok=make_delete)