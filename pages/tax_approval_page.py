'''
Author: liguoqiang
Date: 2025-03-13 11:31:42
LastEditors: liguoqiang
LastEditTime: 2025-03-19 14:21:03
Description: 
'''
from dataclasses import dataclass
import io
import json
import re
from nicegui import ui,app,events
from components import tables, inputs, dialogs
from dao.tax_approval_dao import TaxApprovalDao
from dao.company_dao import CompanyDao
from typing import Callable, Optional, cast
from typing import Any
from utils import global_vars as g
from utils import upload_files as uf

@dataclass
class SearchCondition:
    company_name: str = ""
    company_id: str = ""
    approval_no: str = ""
    ori_voucher_number: str = ""
    begin_time: str = ""
    end_time: str = ""
search_condition = SearchCondition()

#
# @description: 显示完税证明页面
# @return {*}
#
def show_tax_approval_page() -> None:
    result, company_info = g.query_company_name_company()
    if result is False:
        ui.notify('查询公司信息失败')
        return
    options = list(company_info.keys())  # 获取所有公司名称

    with ui.row().classes('w-full px-[20px] mt-0 place-content-start gap-1') \
        .style('background-color: #FFFFFF !important; border-radius: 10px;'):
        with ui.row().classes('w-[74%] place-content-start items-center gap-1'):
            ui.label('纳税人').classes('text-[16px] px-[5px] text-[#333333] font-medium')
            def on_from_change(value):
                if value in company_info:
                    search_condition.company_id = company_info[value].id
                    search_condition.company_name = value
            inputs.selection_w60(options, None, need_input=True, on_change=on_from_change)
            search_condition.company_id = ''
            search_condition.company_name = ''
            inputs.input_search_w40('完税编号', on_search) \
                .bind_value_to(search_condition, 'approval_no')
            inputs.input_search_w40('原凭证号', on_search) \
                .bind_value_to(search_condition, 'ori_voucher_number')
            inputs.date_input_w40('开始时间', on_search) \
                .bind_value_to(search_condition, 'begin_time')
            inputs.date_input_w40('结束时间', on_search) \
                .bind_value_to(search_condition, 'end_time')
            
        with ui.row().classes('w-[25%] place-content-start items-center gap-1'):
            ui.button('刷新', icon='img:/static/images/refresh@2x.png', on_click=on_search) \
                .classes('w-25 rounded-md text-white') \
                .style('background-color: #6C96FB !important')
            ui.button('删除', icon='img:/static/images/delete@2x.png', on_click=del_select) \
                .classes('w-25 rounded-md text-red') \
                .style('background-color: rgba(255,77,77,0.39) !important')
            ui.button('上传凭证', icon='upload', on_click=upload_approval_pdf) \
                    .classes('w-25 rounded-md text-white') \
                    .style('background-color: #65B6FF !important')
            
    table_rows: list[dict] = []
    course_table: Optional[ui.table] = tables.show_tax_approval_table(table_rows, show_edit, show_delete)
    app.storage.client['tax_approval_table'] = course_table
    on_search()

def on_search() -> None:
    result, list_values = g.my_db.query_all_tax_approval(search_condition.company_id, search_condition.approval_no, search_condition.ori_voucher_number, search_condition.begin_time, search_condition.end_time)
    if result is False:
        ui.notify('查询完税证明失败')
        return
    if 'tax_approval_table' in app.storage.client:
        app.storage.client['tax_approval_table'].rows.clear()
        app.storage.client['tax_approval_table'].update()
        if list_values is None or len(list_values) == 0:
            ui.notify('没有查询到完税证明信息')
            return
        sn = 1
        for item in list_values:
            row_dict: dict[str, Any] = {}
            row_dict['sn'] = sn
            dao = TaxApprovalDao()
            dao.from_db(item)
            res, company_dao = g.my_db.query_company_by_id(dao.company_id)
            if res and company_dao is not None:
                row_dict['company_name'] = company_dao.brief_name
            else:
                row_dict['company_name'] = '未知公司'
            row_dict.update(dao.to_db())
            app.storage.client['tax_approval_table'].add_row(row_dict)
            sn += 1
        app.storage.client['tax_approval_table'].update()

"""
# @description: 解析上传结果到DAO对象
# @param {list[dict[str, Any]]} results 上传结果列表
# @return {Optional[TaxApprovalDao]} 完税证明DAO对象
"""
def parse_upload_result_to_dao(results: list[dict[str, Any]]) -> Optional[None|list[TaxApprovalDao]]:
    if results is None or len(results) == 0:
        ui.notify('上传文件识别失败')
        return None
    result_data = results[0]
    ori_number_list = result_data.get('原凭证号', [])
    tax_type_list = result_data.get('税种', [])
    item_name_list = result_data.get('品目名称', [])
    tax_period_list = result_data.get('税款所属日期', [])
    entry_date_list = result_data.get('入库日期', [])
    paid_in_money_list = result_data.get('实缴金额', [])
    company_name = result_data.get('名称', '')
    result, company_list = g.my_db.query_all_company(company_name, '', '', '')
    if result is False or company_list is None or len(company_list) == 0:
        ui.notify(f'上传文件中的公司名称 {company_name} 未在系统中找到，请先添加公司信息')
        return None
    if ori_number_list is None or len(ori_number_list) == 0:
        ui.notify('上传文件中未识别到原凭证号，上传失败')
        return None
    company_dao = CompanyDao()
    company_dao.from_db(company_list[0])
    dao_list: list[TaxApprovalDao] = []
    for i in range(len(ori_number_list)):
        dao = TaxApprovalDao()
        dao.company_id = company_dao.id
        dao.approval_no = result_data.get('No', '')
        text = result_data.get('日期', '')
        pattern = r"^(\d{4})年(\d{1,2})月(\d{1,2})日$"
        if re.match(pattern, text):
            dao.create_time = re.sub(pattern, r"\1-\2-\3", text)
        else:
            dao.create_time = text  # 不匹配则保持原样
        dao.tax_authority = result_data.get('税务机关', '')
        dao.ori_voucher_number = ori_number_list[i]
        dao.tax_type = tax_type_list[i] if i < len(tax_type_list) else ''
        dao.tax_period = tax_period_list[i] if i < len(tax_period_list) else ''
        dao.item_name = item_name_list[i] if i < len(item_name_list) else ''
        dao.entry_date = entry_date_list[i] if i < len(entry_date_list) else ''
        dao.paid_in_money = float(paid_in_money_list[i]) if i < len(paid_in_money_list) else 0.0
        dao.total_money = float(result_data.get('总金额', 0.0))
        dao.remark = result_data.get('备注', '')
        dao_list.append(dao)
    return dao_list

def read_pdf_from_upload(handle_upload: Callable) -> None:
    def upload_ocr(result: list) -> None:
        dao_list = parse_upload_result_to_dao(result)
        if handle_upload is not None and dao_list is not None:
            handle_upload(dao_list)
    uf.open_ocr_certificate_dialog(upload_ocr)

def upload_approval_pdf() -> None:
    def handle_upload(dao_list: list[TaxApprovalDao]) -> None:
        for dao in dao_list:
            res, _ = g.my_db.add_tax_approval(dao.to_db())
            if not res:
                ui.notify('保存凭证信息失败')
                return
        ui.notify('保存凭证信息成功')
        on_search()
    read_pdf_from_upload(handle_upload)
#
# @description: 显示删除操作，由table组件触发
#
def show_delete(e: events.GenericEventArguments) -> None:
    id = e.args['id']
    del_by_ids([id])

#
#
# @description: 显示编辑对话框
# @param {events.GenericEventArguments} e 事件参数
# @return {*}
#
def show_edit(e: events.GenericEventArguments) -> None:
    id = e.args['id']
    result, value = g.my_db.query_tax_approval_by_id(id)
    if result is False:
        ui.notify('查询失败')
        return
    if value is not None:
        dao = cast(TaxApprovalDao, value)
        modify_or_new(dao, False)

#
# @description: 显示添加对话框
# @return {*}
#
def add():
    dao = TaxApprovalDao()
    modify_or_new(dao, True)


def modify_or_new(tax_dao: TaxApprovalDao, is_add: bool) -> None:
    result, company_info = g.query_company_name_company()
    if result is False:
        ui.notify('查询公司信息失败')
        return
    options = list(company_info.keys())  # 获取所有公司名称
    with ui.dialog().props('persistent') as dialog, ui.card().classes('w-1/2') \
        .style('background-color: #FFFFFF !important; border-radius: 10px;'):
        if is_add:
            ui.label('创建完税证明').classes('w-full text-[20px] text-[#333333] font-medium')
        else:
            ui.label('修改完税证明').classes('w-full text-[20px] text-[#333333] font-medium')
        with ui.row().classes('w-full mt-5 place-content-start items-center'):
            ui.label('纳税人').classes('w-[25%] text-[16px] text-[#333333] font-medium')
            def on_company_change(value) -> None:
                if value in company_info:
                    tax_dao.company_id = company_info[value].id
            company_select = inputs.selection_w60(options, None, need_input=True, on_change=on_company_change)
            if not is_add:
                for name, dao in company_info.items():
                    if dao.id == tax_dao.company_id:
                        company_select.value = name
                        break
                company_select.disable()
        with ui.row().classes('w-full place-content-start items-center'):
            ui.label('填表日期').classes('w-[25%] text-[16px] text-[#333333] font-medium')
            def on_create_time_change() -> None:
                tax_dao.create_time = create_time_input.value
            create_time_input = inputs.date_input_w40('填表日期', on_create_time_change)
            if not is_add:
                create_time_input.value = tax_dao.create_time
        with ui.row().classes('w-full place-content-start items-center'):
            ui.label('完税编号').classes('w-[25%] text-[16px] text-[#333333] font-medium')
            ui.input(placeholder='请输入完税编号') \
                .props('rounded-md outlined dense') \
                .classes('w-[50%] self-center item-center ') \
                .bind_value_from(tax_dao, 'approval_no') \
                .bind_value_to(tax_dao, 'approval_no')
                
        with ui.row().classes('w-full place-content-start items-center'):
            ui.label('税务机关').classes('w-[25%] text-[16px] text-[#333333] font-medium')
            ui.input(placeholder='请输入税务机关') \
                .props('rounded-md outlined dense') \
                .classes('w-[50%] self-center item-center ') \
                .bind_value_from(tax_dao, 'tax_authority') \
                .bind_value_to(tax_dao, 'tax_authority')
            
        with ui.row().classes('w-full place-content-start items-center'):
            ui.label('原始凭证号码').classes('w-[25%] text-[16px] text-[#333333] font-medium')
            ui.input(placeholder='请输入原始凭证号码') \
                .props('rounded-md outlined dense') \
                .classes('w-[50%] self-center item-center ') \
                .bind_value_from(tax_dao, 'ori_voucher_number') \
                .bind_value_to(tax_dao, 'ori_voucher_number')
                
        with ui.row().classes('w-full place-content-start items-center'):
            ui.label('税种').classes('w-[25%] text-[16px] text-[#333333] font-medium')
            ui.input(placeholder='请输入税种') \
                .props('rounded-md outlined dense') \
                .classes('w-[50%] self-center item-center ') \
                .bind_value_from(tax_dao, 'tax_type') \
                .bind_value_to(tax_dao, 'tax_type')
                
        with ui.row().classes('w-full place-content-start items-center'):
            ui.label('品目名称').classes('w-[25%] text-[16px] text-[#333333] font-medium')
            ui.input(placeholder='请输入品目名称') \
                .props('rounded-md outlined dense') \
                .classes('w-[50%] self-center item-center ') \
                .bind_value_from(tax_dao, 'item_name') \
                .bind_value_to(tax_dao, 'item_name')
                
        with ui.row().classes('w-full place-content-start items-center'):
            ui.label('税款所属日期').classes('w-[25%] text-[16px] text-[#333333] font-medium')
            def on_tax_period_change() -> None:
                tax_dao.tax_period = f"{begin_time_input.value}至{end_time_input.value}"
            begin_time_input = inputs.date_input_w40('开始日期', on_tax_period_change)
            ui.label('至').classes('text-[16px] text-[#333333] font-medium')
            end_time_input = inputs.date_input_w40('结束日期', on_tax_period_change)
            if not is_add:
                tax_period = tax_dao.tax_period
                begin_time_input.value = tax_period.split('至')[0].strip()
                end_time_input.value = tax_period.split('至')[1].strip()
                
        with ui.row().classes('w-full place-content-start items-center'):
            ui.label('入(退)库日期').classes('w-[25%] text-[16px] text-[#333333] font-medium')
            def on_entry_time_change() -> None:
                tax_dao.entry_date = entry_time_input.value
            entry_time_input = inputs.date_input_w40('入(退)库日期', on_entry_time_change)
            if not is_add:
                entry_time_input.value = tax_dao.entry_date

        with ui.row().classes('w-full place-content-start items-center'):
            ui.label('实缴金额').classes('w-[25%] text-[16px] text-[#333333] font-medium')
            ui.input(placeholder='请输入实缴金额') \
                .props('type="number" step="0.01" rounded-md outlined dense') \
                .classes('w-[30%] self-center item-center ') \
                .bind_value_from(tax_dao, 'paid_in_money') \
                .bind_value_to(tax_dao, 'paid_in_money')
        
        with ui.row().classes('w-full place-content-start items-center'):
            ui.label('总金额').classes('w-[25%] text-[16px] text-[#333333] font-medium')
            ui.input(placeholder='请输入总金额') \
                .props('type="number" step="0.01" rounded-md outlined dense') \
                .classes('w-[30%] self-center item-center ') \
                .bind_value_from(tax_dao, 'total_money') \
                .bind_value_to(tax_dao, 'total_money')
            
        with ui.row().classes('w-full place-content-start items-center'):
            ui.label('备注').classes('w-[25%] text-[16px] text-[#333333] font-medium')
            ui.input(placeholder='请输入备注') \
                .props('rounded-md outlined dense') \
                .classes('w-[70%] self-center item-center ') \
                .bind_value_from(tax_dao, 'remark') \
                .bind_value_to(tax_dao, 'remark')
            
        with ui.row().classes('w-full place-content-center'):
            ui.button('取消', color=None, on_click=dialog.close) \
                .props('flat') \
                .classes('w-[120px] text-[16px] text-[#888888] font-[400]') \
                .style('background-color: #FFFFFF !important;border-radius: 10px;border: 1px solid #888888;')
            def on_create():
                if tax_dao.approval_no == "" or tax_dao.company_id == "" or tax_dao.ori_voucher_number == "":
                    ui.notify('编号、纳税人、原始凭证号码不能为空')
                    return
                data = tax_dao.to_db()
                if is_add:
                    result, _ = g.my_db.add_tax_approval(data)
                    if result is True:
                        ui.notify('添加完税证明成功')
                        on_search()
                        dialog.close()
                    else:
                        ui.notify('添加完税证明失败')
                else:
                    result = g.my_db.update_tax_approval(data, {'id': data['id']})
                    if result is True:
                        ui.notify('修改成功')
                        on_search()
                        dialog.close()
                    else:
                        ui.notify('修改失败')
            ui.button('确定', color=None, on_click=on_create) \
                .props('flat') \
                .classes('w-[120px] text-[16px] text-white font-[400]') \
                .style('background-color: #65B6FF !important; border-radius: 10px')
    dialog.open()


#
# @description: 批量删除课程
# @return {*}
#
def del_select():
    if 'tax_approval_table' not in app.storage.client:
        return
    selection = app.storage.client['tax_approval_table'].selected
    ids = [item['id'] for item in selection]
    del_by_ids(ids)

def del_by_ids(ids: list[str]) -> None:
    if ids is None or len(ids) == 0:
        ui.notify('请选择要删除的记录')
        return
    def make_delete():
        delok = True
        for id in ids:
            if id is None or len(id) == 0:
                continue
            result = g.my_db.delete_tax_approval(id)
            if result is False:
                delok = False
                ui.notify(f'删除失败: {id}')
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

