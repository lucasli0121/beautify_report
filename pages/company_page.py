'''
Author: liguoqiang
Date: 2025-03-13 11:31:42
LastEditors: liguoqiang
LastEditTime: 2025-03-19 14:21:03
Description: 
'''
from dataclasses import dataclass
from nicegui import ui,app,events
from components import tables, inputs, dialogs
import navigation
from dao.company_dao import CompanyDao, get_all_company
from typing import Optional

@dataclass
class SearchCondition:
    name: str = ""
    address: str = ""
    contacts: str = ""
search_condition = SearchCondition()

#
# @description: 显示公司页面
# @return {*}
#
def show_company_page() -> None:
    with ui.row().classes('w-full h-[80px] px-[20px] mt-0 place-content-between gap-0') \
        .style('background-color: #FFFFFF !important; border-radius: 10px;'):
        with ui.row().classes('h-full items-center'):
            name_input = inputs.input_search_w40('名称', on_search)
            name_input.bind_value_to(search_condition, 'name')
            address_input = inputs.input_search_w40('地址', on_search)
            address_input.bind_value_to(search_condition, 'address')
            contacts_input = inputs.input_search_w40('联系人', on_search)
            contacts_input.bind_value_to(search_condition, 'contacts')
        with ui.row().classes('h-full items-center'):
            ui.button('删除', icon='img:/static/images/delete@2x.png', on_click=del_select_company) \
                .classes('w-25 rounded-md text-red') \
                .style('background-color: rgba(255,77,77,0.39) !important')
            ui.button('刷新', icon='img:/static/images/refresh@2x.png', on_click=on_search) \
                .classes('w-25 rounded-md text-white') \
                .style('background-color: #6C96FB !important')
            ui.button('创建公司', icon='img:/static/images/add_course@2x.png', on_click=add_company) \
                .classes('w-25 rounded-md text-white') \
                .style('background-color: #65B6FF !important')
            
    table_rows: list[dict] = []
    course_table: Optional[ui.table] = tables.show_company_table(table_rows, show_company_detail, show_company_delete)
    app.storage.client['company_table'] = course_table
    on_search()

def on_search() -> None:
    result, company_list = get_all_company(search_condition.name, search_condition.address, search_condition.contacts)
    if result is False:
        ui.notify('查询公司失败')
        return
    if 'company_table' in app.storage.client:
        app.storage.client['company_table'].rows.clear()
        if company_list is None or len(company_list) == 0:
            ui.notify('没有查询到公司信息')
            return
        sn = 1
        for item in company_list:
            row_dict = item.__dict__
            row_dict['sn'] = sn
            app.storage.client['company_table'].add_row(item.__dict__)
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
# @description: 显示添加公司对话框
# @return {*}
#
def add_company():
    company_dao = CompanyDao()
    with ui.dialog().props('persistent') as dialog, ui.card().classes('w-1/2 h-full') \
        .style('background-color: #FFFFFF !important; border-radius: 10px;'):
        ui.label('创建公司').classes('w-full text-[20px] text-[#333333] font-medium')
        with ui.row().classes('w-full mt-5 place-content-between'):
            ui.label('名称').classes('w-full text-[16px] text-[#333333] font-medium')
            classes_ui = ui.input(placeholder='请输入公司名称') \
                .props('rounded-md outlined dense') \
                .classes('w-full self-center item-center ')
            classes_ui.bind_value_to(company_dao, 'name')
        with ui.row().classes('w-full place-content-between'):
            ui.label('地址').classes('w-full text-[16px] text-[#333333] font-medium')
            subject_ui = ui.input(placeholder='请输入公司地址') \
                .props('rounded-md outlined dense') \
                .classes('w-full self-center item-center ')
            subject_ui.bind_value_to(company_dao, 'address')
        with ui.row().classes('w-full place-content-between'):
            ui.label('联系人').classes('w-full text-[16px] text-[#333333] font-medium')
            teacher_ui = ui.input(placeholder='请输入联系人姓名') \
                .props('rounded-md outlined dense') \
                .classes('w-full self-center item-center ')
            teacher_ui.bind_value_to(company_dao, 'contacts')
        with ui.row().classes('w-full place-content-between'):
            ui.label('电话').classes('w-full text-[16px] text-[#333333] font-medium')
            ui.input(placeholder='请输入联系人电话') \
                .props('rounded-md outlined dense') \
                .classes('w-full self-center item-center ') \
                .bind_value_to(company_dao, 'phone')
        with ui.row().classes('w-full place-content-between'):
            ui.label('邮箱').classes('w-full text-[16px] text-[#333333] font-medium')
            ui.input(placeholder='请输入联系人邮箱') \
                .props('rounded-md outlined dense') \
                .classes('w-full self-center item-center ') \
                .bind_value_to(company_dao, 'email')
        with ui.row().classes('w-full place-content-between'):
            ui.label('开票限额').classes('w-full text-[16px] text-[#333333] font-medium')
            ui.input(placeholder='请输入开票最高限额') \
                .props('rounded-md outlined dense') \
                .classes('w-[1/2] self-center item-center ') \
                .bind_value_to(company_dao, 'invoice_limit')
            ui.label('万').classes('text-[16px] text-[#333333] font-medium')
        with ui.row().classes('w-full place-content-between'):
            ui.label('信用代码').classes('w-full text-[16px] text-[#333333] font-medium')
            ui.input(placeholder='请输入统一信用代码') \
                .props('rounded-md outlined dense') \
                .classes('w-full self-center item-center ') \
                .bind_value_to(company_dao, 'tax_id')
        with ui.row().classes('w-full place-content-end'):         
            ui.button('取消', color=None, on_click=dialog.close) \
                .props('flat') \
                .classes('w-[120px] text-[16px] text-[#888888] font-[400]') \
                .style('background-color: #FFFFFF !important;border-radius: 10px;border: 1px solid #888888;')
            def on_create_company():
                if company_dao.name == "" or company_dao.address == "" or company_dao.contacts == "":
                    ui.notify('公司名称,地址,联系人不能为空')
                    return
                result = company_dao.add_company()
                if result is True:
                    ui.notify('添加公司成功')
                    on_search()
                    dialog.close()
                else:
                    ui.notify('添加公司失败')
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

def del_company_by_ids(ids: list[int]) -> None:
    if ids is None or len(ids) == 0:
        ui.notify('请选择要删除的公司')
        return
    def make_delete():
        delok = True
        for id in ids:
            if id is None or id <= 0:
                continue
            company_dao = CompanyDao()
            company_dao.id = id
            result = company_dao.delete_company(id)
            if result is False:
                delok = False
                ui.notify(f'删除公司失败: {id}')
                return
        if delok is True:
            ui.notify('删除公司成功')
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

