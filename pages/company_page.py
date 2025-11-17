'''
Author: liguoqiang
Date: 2025-03-13 11:31:42
LastEditors: liguoqiang
LastEditTime: 2025-03-19 14:21:03
Description: 
'''
from dataclasses import dataclass
import json
from nicegui import ui,app,events
from components import tables, inputs, dialogs
import navigation
from dao.company_dao import CompanyDao, CompanyType
from typing import Optional, cast
from typing import Any
from utils import global_vars as g

@dataclass
class SearchCondition:
    name: str = ""
    address: str = ""
    contacts: str = ""
    company_type: str = "" # general: 一般纳税人, small: 小规模纳税人
search_condition = SearchCondition()

#
# @description: 显示公司页面
# @return {*}
#
def show_company_page() -> None:
    with ui.row().classes('w-full px-[20px] mt-0 place-content-start gap-1').style('background-color: #FFFFFF !important; border-radius: 10px;'):
        with ui.row().classes('w-[65%] place-content-start items-center gap-1'):
            name_input = inputs.input_search_w60('简称', on_search)
            name_input.bind_value_to(search_condition, 'name')
            address_input = inputs.input_search_w40('地址', on_search)
            address_input.bind_value_to(search_condition, 'address')
            contacts_input = inputs.input_search_w40('联系人', on_search)
            contacts_input.bind_value_to(search_condition, 'contacts')
            ui.label('公司类型').classes('text-[16px] text-[#333333] font-medium')
            def on_company_type_change(e: events.GenericEventArguments) -> None:
                value = e.args['value']
                if value == '全部':
                    search_condition.company_type = ''
                elif value == '一般纳税人':
                    search_condition.company_type = CompanyType.GENERAL.value
                elif value == '小规模纳税人':
                    search_condition.company_type = CompanyType.SMALL.value
                else:
                    search_condition.company_type = ''
                on_search()
            inputs.selection_w40(['全部','一般纳税人','小规模纳税人'], '全部', False, on_change=on_company_type_change)
            search_condition.company_type = ''
        with ui.row().classes('w-[30%] place-content-start items-center gap-1'):
            ui.button('刷新', icon='img:/static/images/refresh@2x.png', on_click=on_search) \
                .classes('w-25 rounded-md text-white') \
                .style('background-color: #6C96FB !important')
            ui.button('删除', icon='img:/static/images/delete@2x.png', on_click=del_select_company) \
                .classes('w-25 rounded-md text-red') \
                .style('background-color: rgba(255,77,77,0.39) !important')
            ui.button('新建', icon='img:/static/images/add_course@2x.png', on_click=add_company) \
                .classes('w-25 rounded-md text-white') \
                .style('background-color: #65B6FF !important')
            
    table_rows: list[dict] = []
    course_table: Optional[ui.table] = tables.show_company_table(table_rows, show_company_edit, show_company_delete)
    app.storage.client['company_table'] = course_table
    on_search()

def on_search() -> None:
    result, list_values = g.my_db.query_inner_company(search_condition.name, search_condition.address, search_condition.contacts, search_condition.company_type)
    if result is False:
        ui.notify('查询公司失败')
        return
    if 'company_table' in app.storage.client:
        app.storage.client['company_table'].rows.clear()
        app.storage.client['company_table'].update()
        if list_values is None or len(list_values) == 0:
            ui.notify('没有查询到公司信息')
            return
        sn = 1
        for item in list_values:
            row_dict: dict[str, Any] = {}
            row_dict['sn'] = sn
            company = CompanyDao()
            company.from_db(item)
            row_dict.update(company.to_db())
            # If 'extends' should be an int, assign a default or extract an int value
            # row_dict['extends'] = 0  # Example: assign 0 if no int value is available

            # If 'extends' should be a string, ensure the table schema supports it
            row_dict['extends'] = json.dumps(company.extends, ensure_ascii=False, indent=4)
            app.storage.client['company_table'].add_row(row_dict)
            sn += 1
        app.storage.client['company_table'].update()

#
# @description: 显示课堂删除操作，由table组件触发
#
def show_company_delete(e: events.GenericEventArguments) -> None:
    id = e.args['id']
    del_company_by_ids([id])

#
#
# @description: 显示公司详情页面
# @param {events.GenericEventArguments} e 事件参数
# @return {*}
#
def show_company_detail(e: events.GenericEventArguments) -> None:
    id = e.args['id']
    def onback():
        navigation.navigation_company_page()
    navigation.navigation_company_detail_page(id, e.args['name'], onback)

#
#
# @description: 显示公司编辑对话框
# @param {events.GenericEventArguments} e 事件参数
# @return {*}
#
def show_company_edit(e: events.GenericEventArguments) -> None:
    id = e.args['id']
    result, value = g.my_db.query_company_by_id(id)
    if result is False:
        ui.notify('查询公司失败')
        return
    if value is not None:
        company_dao = cast(CompanyDao, value)
        modify_or_new_company(company_dao, False)

#
# @description: 显示添加公司对话框
# @return {*}
#
def add_company():
    company_dao = CompanyDao()
    modify_or_new_company(company_dao, True)


def modify_or_new_company(company_dao: CompanyDao, is_add: bool) -> None:
    old_name = company_dao.name
    old_brief_name = company_dao.brief_name
    if is_add:
        try:
            with open('static/json/company_extends.json', 'r', encoding='utf-8') as f:
                company_dao.extends = json.load(f)
        except FileNotFoundError:
            company_dao.extends = {}
    with ui.dialog().props('persistent') as dialog, ui.card().classes('w-1/2') \
        .style('background-color: #FFFFFF !important; border-radius: 10px;'):
        if is_add:
            ui.label('创建公司').classes('w-full text-[20px] text-[#333333] font-medium')
        else:
            ui.label('修改公司信息').classes('w-full text-[20px] text-[#333333] font-medium')
        with ui.row().classes('w-full mt-5 place-content-start items-center'):
            ui.label('名称').classes('w-[20%] text-[16px] text-[#333333] font-medium')
            ui.input(placeholder='请输入公司名称') \
                .props('rounded-md outlined dense') \
                .classes('w-[70%] self-center item-center ') \
                .bind_value_from(company_dao, 'name') \
                .bind_value_to(company_dao, 'name')
        with ui.row().classes('w-full place-content-start items-center'):
            ui.label('简称').classes('w-[20%] text-[16px] text-[#333333] font-medium')
            ui.input(placeholder='请输入公司简称') \
                .props('rounded-md outlined dense') \
                .classes('w-[30%] self-center item-center ') \
                .bind_value_from(company_dao, 'brief_name') \
                .bind_value_to(company_dao, 'brief_name')
                
        with ui.row().classes('w-full place-content-start items-center'):
            ui.label('公司类型').classes('w-[20%] text-[16px] text-[#333333] font-medium')
            def on_company_type_change(value) -> None:
                if value == '一般纳税人':
                    company_dao.company_type = CompanyType.GENERAL.value
                elif value == '小规模纳税人':
                    company_dao.company_type = CompanyType.SMALL.value
                else:
                    company_dao.company_type = ''
            company_type_selector = inputs.selection_w40(['一般纳税人','小规模纳税人'], '一般纳税人', on_change=on_company_type_change)
            if not is_add:
                if company_dao.company_type == CompanyType.GENERAL.value:
                    company_type_selector.value = '一般纳税人'
                elif company_dao.company_type == CompanyType.SMALL.value:
                    company_type_selector.value = '小规模纳税人'
            
        with ui.row().classes('w-full place-content-start items-center'):
            ui.label('地址').classes('w-[20%] text-[16px] text-[#333333] font-medium')
            ui.input(placeholder='请输入公司地址') \
                .props('rounded-md outlined dense') \
                .classes('w-[70%] self-center item-center ') \
                .bind_value_from(company_dao, 'address') \
                .bind_value_to(company_dao, 'address')
                
        with ui.row().classes('w-full place-content-start items-center'):
            ui.label('联系人').classes('w-[20%] text-[16px] text-[#333333] font-medium')
            ui.input(placeholder='请输入联系人姓名') \
                .props('rounded-md outlined dense') \
                .classes('w-[30%] self-center item-center ') \
                .bind_value_from(company_dao, 'contacts') \
                .bind_value_to(company_dao, 'contacts')
                
        with ui.row().classes('w-full place-content-start items-center'):
            ui.label('电话').classes('w-[20%] text-[16px] text-[#333333] font-medium')
            ui.input(placeholder='请输入联系人电话') \
                .props('rounded-md outlined dense') \
                .classes('w-[30%] self-center item-center ') \
                .bind_value_from(company_dao, 'phone') \
                .bind_value_to(company_dao, 'phone')
                
        with ui.row().classes('w-full place-content-start items-center'):
            ui.label('邮箱').classes('w-[20%] text-[16px] text-[#333333] font-medium')
            ui.input(placeholder='请输入联系人邮箱') \
                .props('rounded-md outlined dense') \
                .classes('w-[30%] self-center item-center ') \
                .bind_value_from(company_dao, 'email') \
                .bind_value_to(company_dao, 'email')
                
        with ui.row().classes('w-full place-content-start items-center'):
            ui.label('开票限额').classes('w-[20%] text-[16px] text-[#333333] font-medium')
            ui.input(placeholder='请输入开票最高限额') \
                .props('rounded-md outlined dense') \
                .classes('w-[20%] self-center item-center ') \
                .bind_value_from(company_dao, 'invoice_limit') \
                .bind_value_to(company_dao, 'invoice_limit')
                
            ui.label('万').classes('text-[16px] text-[#333333] font-medium')
        with ui.row().classes('w-full place-content-start items-center'):
            ui.label('信用代码').classes('w-[20%] text-[16px] text-[#333333] font-medium')
            ui.input(placeholder='请输入统一信用代码') \
                .props('rounded-md outlined dense') \
                .classes('w-[30%] self-center item-center ') \
                .bind_value_from(company_dao, 'tax_no') \
                .bind_value_to(company_dao, 'tax_no')
                
        for company_extend in company_dao.extends:
            with ui.row().classes('w-full place-content-start items-center'):
                ui.label(f'{company_extend}').classes('w-[20%] text-[16px] text-[#333333] font-medium')
                ui.input(placeholder=f'请输入{company_extend}') \
                    .props('rounded-md outlined dense') \
                    .classes('w-[30%] self-center item-center ') \
                    .bind_value_from(company_dao.extends, company_extend) \
                    .bind_value_to(company_dao.extends, company_extend)
                    
        extend_column = ui.column().classes('w-full place-content-start items-center')
        with ui.row().classes('w-full place-content-end'):
            def show_extends_fields():
                def create_extends_fields(field: str):
                    if field is None or len(field) == 0:
                        ui.notify('扩展字段不能为空')
                        return
                    if field in company_dao.extends:
                        ui.notify(f'扩展字段 {field} 已经存在')
                        return
                    with extend_column:
                        with ui.row().classes('w-full place-content-start items-center'):
                            ui.label(f'{field}').classes('w-[20%] text-[16px] text-[#333333] font-medium')
                            ui.input(placeholder=f'请输入{field}') \
                                .props('rounded-md outlined dense') \
                                .classes('w-[30%] self-center item-center ') \
                                .bind_value_to(company_dao.extends, field)
                dialogs.show_extents_fields_dialog(create_extends_fields)
            ui.button('扩展字段', color=None, on_click=show_extends_fields) \
                .props('flat') \
                .classes('w-[120px] text-[16px] text-white font-[400]') \
                .style('background-color: #65B6FF !important; border-radius: 10px')
            ui.button('取消', color=None, on_click=dialog.close) \
                .props('flat') \
                .classes('w-[120px] text-[16px] text-[#888888] font-[400]') \
                .style('background-color: #FFFFFF !important;border-radius: 10px;border: 1px solid #888888;')
            def on_create_company():
                if company_dao.name == "" or company_dao.address == "" or company_dao.contacts == "":
                    ui.notify('公司名称,地址,联系人不能为空')
                    return
                if len(company_dao.extends) > 0 and is_add:
                    with open('static/json/company_extends.json', 'w', encoding='utf-8') as f:
                        json.dump(company_dao.extends, f, ensure_ascii=False, indent=4)
                if is_add:
                    company_dao.type = 1 # 默认是内部公司类型
                data = company_dao.to_db()
                if is_add:
                    result, values = g.my_db.query_same_company(data['name'], data['brief_name'])
                    if result and values and len(values) > 0:
                        ui.notify('公司名称或简称已存在，请修改后再试')
                        return
                    result, _ = g.my_db.add_company(data)
                    if result is True:
                        ui.notify('添加公司成功')
                        on_search()
                        dialog.close()
                    else:
                        ui.notify('添加公司失败')
                else:
                    if old_name != data['name'] or old_brief_name != data['brief_name']:
                        result, values = g.my_db.query_same_company(data['name'], data['brief_name'])
                        if result and values and len(values) > 0:
                            ui.notify('公司名称或简称已存在，请修改后再试')
                            return
                    result = g.my_db.update_company(data, {'id': data['id']})
                    if result is True:
                        ui.notify('修改公司成功')
                        on_search()
                        dialog.close()
                    else:
                        ui.notify('修改公司失败')
            ui.button('确定', color=None, on_click=on_create_company) \
                .props('flat') \
                .classes('w-[120px] text-[16px] text-white font-[400]') \
                .style('background-color: #65B6FF !important; border-radius: 10px')
    dialog.open()


#
# @description: 批量删除课程
# @return {*}
#
def del_select_company():
    if 'company_table' not in app.storage.client:
        return
    selection = app.storage.client['company_table'].selected
    ids = [item['id'] for item in selection]
    del_company_by_ids(ids)

def del_company_by_ids(ids: list[str]) -> None:
    if ids is None or len(ids) == 0:
        ui.notify('请选择要删除的公司')
        return
    def make_delete():
        delok = True
        for id in ids:
            if id is None or len(id) == 0:
                continue
            result = g.my_db.delete_company(id)
            if result is False:
                delok = False
                ui.notify(f'删除公司失败: {id}')
                return
        if delok is True:
            ui.notify('删除公司成功')
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

