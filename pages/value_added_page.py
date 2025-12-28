from dataclasses import dataclass
from datetime import datetime
import asyncio
from nicegui import ui,events, app, run
from components import inputs, tables, dialogs
from typing import Any, Optional, cast
from dao.company_dao import CompanyDao
from dao.period_data_dao import PeriodDataDao
from dao.value_added_dao import ValueAddedDao
from utils import global_vars as g

@dataclass
class SearchCondition:
    company_id: str = ""
    company_name: str = ""
    record_month: str = ""
search_condition = SearchCondition()

def show_value_added_page():
    result, company_info = g.query_company_name_company()
    if result is False:
        ui.notify('查询公司信息失败')
        return
    options = list(company_info.keys())  # 获取所有公司名称
    with ui.row().classes('w-full px-[20px] py-[10px] mt-0 place-content-start items-center gap-2') \
        .style('background-color: #FFFFFF !important; border-radius: 10px;'):
        ui.label('公司').classes('text-[16px] text-[#333333] font-medium')
        def on_company_change(value):
            if value in company_info:
                search_condition.company_id = company_info[value].id
                search_condition.company_name = value
        inputs.selection_w60(options, None, need_input=True, on_change=on_company_change)
        def on_year_select(value):
            if month_select.value is not None:
                search_condition.record_month = f"{value}-{month_select.value.zfill(2)}"
        year_select = inputs.selection_w40([str(x) for x in range(2001, 2031)], None, False, on_change=on_year_select)
        def on_month_select(value):
            if year_select.value is not None:
                search_condition.record_month = f"{year_select.value}-{value.zfill(2)}"
        month_select = inputs.selection_w40([str(x).zfill(2) for x in range(1, 13)], None, False, on_change=on_month_select)
            
        search_button = ui.button('刷新', icon='img:/static/images/refresh@2x.png', on_click=on_search) \
            .classes('w-25 rounded-md text-white') \
            .style('background-color: #6C96FB !important')
        ui.button('汇总', icon='img:/static/images/subject@2x.png', on_click=show_summary_value_added) \
            .classes('w-25 rounded-md text-white') \
            .style('background-color: #6C96FB !important')
        ui.button('删除', icon='img:/static/images/delete@2x.png', on_click=del_select) \
            .classes('w-25 rounded-md text-red') \
            .style('background-color: rgba(255,77,77,0.39) !important')
        ui.button('新建', icon='img:/static/images/add_course@2x.png', on_click=show_add) \
            .classes('w-25 rounded-md text-white') \
            .style('background-color: #65B6FF !important')
            
    table_rows: list[dict] = []
    app.storage.client['value_added_table'] = tables.show_value_added_table(table_rows, show_edit, delete_one)
    on_search()

def on_search() -> None:
    result, list_values = g.my_db.query_all_value_added(search_condition.company_id, search_condition.record_month)
    if result is False:
        ui.notify('查询期初数据失败')
        return
    if 'value_added_table' in app.storage.client:
        app.storage.client['value_added_table'].rows.clear()
        app.storage.client['value_added_table'].update()
        if list_values is None or len(list_values) == 0:
            ui.notify('没有查询到增值税数据')
            return
        def do_refresh() -> list[dict[str, Any]]:
            sn = 1
            rows: list[dict[str, Any]] = []
            for item in list_values:
                row_dict: dict[str, Any] = {}
                row_dict['sn'] = sn
                dao = ValueAddedDao()
                dao.from_db(item)
                row_dict['id'] = dao.id
                row_dict['create_time'] = dao.create_time
                row_dict['last_month_no_verify'] = f"{round(dao.last_month_no_verify, 2):,.2f}"
                row_dict['last_month_stay_pay'] = f"{round(dao.last_month_stay_pay, 2):,.2f}"
                row_dict['opened_input_tax'] = f"{round(dao.opened_input_tax, 2):,.2f}"
                row_dict['opened_output_tax'] = f"{round(dao.opened_output_tax, 2):,.2f}"
                row_dict['to_open_input_tax'] = f"{round(dao.to_open_input_tax, 2):,.2f}"
                row_dict['to_open_output_tax'] = f"{round(dao.to_open_output_tax, 2):,.2f}"
                row_dict['payable_tax'] = f"{round(dao.payable_tax, 2):,.2f}"
                row_dict['sales_amount'] = f"{round(dao.sales_amount, 2):,.2f}"
                row_dict['opened_billing_amount'] = f"{round(dao.opened_billing_amount, 2):,.2f}"
                row_dict['remaining_billing_amount'] = f"{round(dao.remaining_billing_amount, 2):,.2f}"
                row_dict['billing_amount'] = f"{round(dao.billing_amount, 2):,.2f}"
                result, company_dao = g.my_db.query_company_by_id(dao.company_id)
                company_name = '未知公司'
                if result and company_dao is not None:
                    company_name = company_dao.brief_name
                row_dict['company_name'] = company_name
                rows.append(row_dict)
                sn += 1
            return rows
        # sn = 1
        # for item in list_values:
        #     row_dict: dict[str, Any] = {}
        #     row_dict['sn'] = sn
        #     dao = ValueAddedDao()
        #     dao.from_db(item)
        #     row_dict['id'] = dao.id
        #     row_dict['create_time'] = dao.create_time
        #     row_dict['last_month_no_verify'] = f"{round(dao.last_month_no_verify, 2):,.2f}"
        #     row_dict['last_month_stay_pay'] = f"{round(dao.last_month_stay_pay, 2):,.2f}"
        #     row_dict['opened_input_tax'] = f"{round(dao.opened_input_tax, 2):,.2f}"
        #     row_dict['opened_output_tax'] = f"{round(dao.opened_output_tax, 2):,.2f}"
        #     row_dict['to_open_input_tax'] = f"{round(dao.to_open_input_tax, 2):,.2f}"
        #     row_dict['to_open_output_tax'] = f"{round(dao.to_open_output_tax, 2):,.2f}"
        #     row_dict['payable_tax'] = f"{round(dao.payable_tax, 2):,.2f}"
        #     row_dict['sales_amount'] = f"{round(dao.sales_amount, 2):,.2f}"
        #     row_dict['opened_billing_amount'] = f"{round(dao.opened_billing_amount, 2):,.2f}"
        #     row_dict['remaining_billing_amount'] = f"{round(dao.remaining_billing_amount, 2):,.2f}"
        #     row_dict['billing_amount'] = f"{round(dao.billing_amount, 2):,.2f}"
        #     result, company_dao = g.my_db.query_company_by_id(dao.company_id)
        #     company_name = '未知公司'
        #     if result and company_dao is not None:
        #         company_name = company_dao.brief_name
        #     row_dict['company_name'] = company_name
        rows = do_refresh()
        app.storage.client['value_added_table'].rows = rows
        app.storage.client['value_added_table'].update()

"""
function: show_summary_value_added
description: 显示增值税汇总对话框
param {*}
return {*}
"""
async def show_summary_value_added() -> None:
    result, company_info = g.query_company_name_company()
    if result is False:
        ui.notify('查询公司信息失败')
        return
    options = list(company_info.keys())  # 获取所有公司名称
    with ui.dialog().props('persistent') as dialog, ui.card().style('width: 30%; max-width: 30%;') \
        .style('background-color: #FFFFFF !important; border-radius: 10px;'):
        ui.label('汇总增值税数据').classes('w-full text-[20px] text-[#333333] font-medium')
        with ui.column().classes('w-full mt-5 place-content-start items-center'):
            with ui.row().classes('w-full place-content-start items-center gap-1'):
                ui.label('年月').classes('w-[20%] text-[16px] text-[#333333] font-medium')
                year_input = inputs.selection_w40([str(x) for x in range(2001, 2031)], None, False, None)
                year_input.set_value(datetime.now().strftime("%Y"))
                month_select = inputs.selection_w40([str(x).zfill(2) for x in range(1, 13)], None, False, None)
                month_select.set_value(datetime.now().strftime("%m").zfill(2))
            with ui.row().classes('w-full place-content-start items-center gap-1'):
                ui.label('公司').classes('w-[20%] text-[16px] text-[#333333] font-medium')
                company_select = inputs.selection_w60(options, None, need_input=True, on_change=None)
            with ui.row().classes('w-full place-content-center items-center gap-1'):
                async def on_summary():
                    company_id = ''
                    if company_select.value is not None:
                        company_id = company_info[company_select.value].id
                    if year_input.value is None or month_select.value is None:
                        ui.notify('请选择年月')
                        return
                    refresh_dialog = g.show_refresh_process("汇总中，请稍候...")
                    record_month = f"{year_input.value}-{month_select.value.zfill(2)}"
                    result, count = await run.io_bound(do_summary_update, company_id, record_month)
                    if result is False:
                        ui.notify("汇总增值税数据失败,没有查询到相关数据")
                        refresh_dialog.close()
                        return
                    refresh_dialog.close()
                    ui.notify(f"汇总增值税数据成功，共处理{count}条记录")
                    on_search()
                def do_summary_update(company_id: str, record_month: str) -> tuple[bool, int]:
                    summary_list = summary_value_added(company_id, record_month)
                    if summary_list is None or len(summary_list) == 0:
                        return False, 0
                    i = 0
                    for dao in summary_list:
                        if dao.id is None or len(dao.id) == 0:
                            g.my_db.add_value_added(dao.to_db())
                        else:
                            g.my_db.update_value_added(dao.to_db(), {'id': dao.id})
                        i += 1
                    return True, i
                ui.button('关闭', color=None, on_click=dialog.close) \
                    .props('flat') \
                    .classes('w-[120px] text-[16px] text-[#888888] font-[400]') \
                    .style('background-color: #FFFFFF !important;border-radius: 10px;border: 1px solid #888888;')
                ui.button('汇总增值税', color=None, on_click=on_summary) \
                    .props('flat') \
                    .classes('w-[120px] text-[16px] text-white font-[400]') \
                    .style('background-color: #65B6FF !important; border-radius: 10px')
    dialog.open()
                
def show_edit(e: events.GenericEventArguments) -> None:
    id = e.args['id']
    if id is None or len(id) == 0:
        ui.notify('请选择要编辑的记录')
        return
    result, dao = g.my_db.query_value_added_by_id(id)
    if result is False or dao is None:
        ui.notify('查询增值税数据失败')
        return
    modify_or_new(dao, is_add=False)

#
# @description: 新增
# @param None
# @return: None
#             
def show_add():
    dao = ValueAddedDao()
    modify_or_new(dao, is_add=True)

def modify_or_new(dao: ValueAddedDao, is_add: bool = True) -> None:
    result, company_info = g.query_company_name_company()
    if result is False:
        ui.notify('查询公司信息失败')
        return
    options = list(company_info.keys())  # 获取所有公司名称
    # company_dao: CompanyDao = CompanyDao()
    # if not is_add:
    #     result, value = g.my_db.query_company_by_id(dao.company_id)
    #     if result is False or value is None:
    #         ui.notify('查询公司信息失败')
    #         return
    #     company_dao = cast(CompanyDao, value)
    with ui.dialog().props('persistent') as dialog, ui.card().style('width: 50%; max-width: 50%;') \
        .style('background-color: #FFFFFF !important; border-radius: 10px;'):
        if is_add:
            ui.label('新增数据').classes('w-full text-[20px] text-[#333333] font-medium')
        else:
            ui.label('修改数据').classes('w-full text-[20px] text-[#333333] font-medium')
        with ui.column().classes('w-full mt-5 place-content-start items-center'):
            with ui.row().classes('w-full place-content-start items-center gap-1'):
                ui.label('年月').classes('w-[20%] text-[16px] text-[#333333] font-medium')
                year_input = inputs.selection_w40([str(x) for x in range(2001, 2031)], None, False, None)
                if len(dao.create_time) >= 4:
                    year_input.set_value(dao.create_time[0:4])
                month_select = inputs.selection_w40([str(x).zfill(2) for x in range(1, 13)], None, False, None)
                if len(dao.create_time) >= 7:
                    month_select.set_value(dao.create_time[5:7])
            with ui.row().classes('w-full place-content-start items-center gap-1'):
                ui.label('公司').classes('w-[20%] text-[16px] text-[#333333] font-medium')
                def on_company_change(value):
                    if value in company_info:
                        dao.company_id = company_info[value].id
                company_select = inputs.selection_w60(options, None, need_input=True, on_change=on_company_change)
                if not is_add:
                    if dao.company_id is not None and dao.company_id != "":
                        for company_name, company_dao in company_info.items():
                            if company_dao.id == dao.company_id:
                                company_select.set_value(company_name)
                                break
                def on_summary():
                    if dao.company_id is None or dao.company_id == "":
                        ui.notify('请选择公司')
                        return
                    if year_input.value is None or month_select.value is None:
                        ui.notify('请选择年月')
                        return
                    record_month = f"{year_input.value}-{month_select.value.zfill(2)}"
                    summary_list = summary_value_added(dao.company_id, record_month)
                    if summary_list is None or len(summary_list) == 0:
                        ui.notify('汇总增值税数据失败')
                        return
                    summary_dao = summary_list[0]
                    dao.last_month_no_verify = summary_dao.last_month_no_verify
                    dao.last_month_stay_pay = summary_dao.last_month_stay_pay
                    dao.opened_input_tax = summary_dao.opened_input_tax
                    dao.opened_output_tax = summary_dao.opened_output_tax
                    dao.to_open_input_tax = summary_dao.to_open_input_tax
                    dao.to_open_output_tax = summary_dao.to_open_output_tax
                    dao.payable_tax = summary_dao.payable_tax
                    dao.sales_amount = summary_dao.sales_amount
                    dao.opened_billing_amount = summary_dao.opened_billing_amount
                    dao.remaining_billing_amount = summary_dao.remaining_billing_amount
                    dao.billing_amount = summary_dao.billing_amount
                    
                ui.button('汇总增值税', color=None, on_click=on_summary) \
                    .props('flat') \
                    .classes('w-[120px] text-[16px] text-white font-[400]') \
                    .style('background-color: #65B6FF !important; border-radius: 10px')
            with ui.row().classes('w-full place-content-start items-center gap-1'):
                ui.label('上月未认证').classes('w-[20%] text-[16px] text-[#333333] font-medium')
                ui.input('上月未认证金额') \
                    .props('rounded-md outlined dense type="number"') \
                    .classes('w-[25%] self-center item-center ') \
                    .bind_value_from(dao, 'last_month_no_verify') \
                    .bind_value_to(dao, 'last_month_no_verify')
                ui.label('上月留抵').classes('w-[20%] text-[16px] text-[#333333] font-medium')
                ui.input('上月留抵金额') \
                    .props('rounded-md outlined dense type="number"') \
                    .classes('w-[25%] self-center item-center ') \
                    .bind_value_from(dao, 'last_month_stay_pay') \
                    .bind_value_to(dao, 'last_month_stay_pay')
            with ui.row().classes('w-full place-content-start items-center gap-1'):
                ui.label('已开进项税额').classes('w-[20%] text-[16px] text-[#333333] font-medium')
                ui.input('已开进项税额') \
                    .props('rounded-md outlined dense type="number"') \
                    .classes('w-[25%] self-center item-center ') \
                    .bind_value_from(dao, 'opened_input_tax') \
                    .bind_value_to(dao, 'opened_input_tax')
                ui.label('已开销项税额').classes('w-[20%] text-[16px] text-[#333333] font-medium')
                ui.input('已开销项税额') \
                    .props('rounded-md outlined dense type="number"') \
                    .classes('w-[25%] self-center item-center ') \
                    .bind_value_from(dao, 'opened_output_tax') \
                    .bind_value_to(dao, 'opened_output_tax')
            with ui.row().classes('w-full place-content-start items-center gap-1'):
                ui.label('待开进项税额').classes('w-[20%] text-[16px] text-[#333333] font-medium')
                ui.input('待开进项税额') \
                    .props('rounded-md outlined dense type="number"') \
                    .classes('w-[25%] self-center item-center ') \
                    .bind_value_from(dao, 'to_open_input_tax') \
                    .bind_value_to(dao, 'to_open_input_tax')
                ui.label('待开销项税额').classes('w-[20%] text-[16px] text-[#333333] font-medium')
                ui.input('待开销项税额') \
                    .props('rounded-md outlined dense type="number"') \
                    .classes('w-[25%] self-center item-center ') \
                    .bind_value_from(dao, 'to_open_output_tax') \
                    .bind_value_to(dao, 'to_open_output_tax')
            with ui.row().classes('w-full place-content-start items-center gap-1'):
                ui.label('应纳税额').classes('w-[20%] text-[16px] text-[#333333] font-medium')
                ui.input('应纳税额') \
                    .props('rounded-md outlined dense type="number"') \
                    .classes('w-[25%] self-center item-center ') \
                    .bind_value_from(dao, 'payable_tax') \
                    .bind_value_to(dao, 'payable_tax') \
                    .set_enabled(False)
                ui.label('开销售额').classes('w-[20%] text-[16px] text-[#333333] font-medium')
                ui.input('开销售额') \
                    .props('rounded-md outlined dense type="number"') \
                    .classes('w-[25%] self-center item-center ') \
                    .bind_value_from(dao, 'sales_amount') \
                    .bind_value_to(dao, 'sales_amount') \
                    .set_enabled(False)
            with ui.row().classes('w-full place-content-start items-center gap-1'):
                ui.label('已开票额').classes('w-[20%] text-[16px] text-[#333333] font-medium')
                ui.input('已开票额') \
                    .props('rounded-md outlined dense type="number"') \
                    .classes('w-[25%] self-center item-center ') \
                    .bind_value_from(dao, 'opened_billing_amount') \
                    .bind_value_to(dao, 'opened_billing_amount')
                ui.label('剩余开票额').classes('w-[20%] text-[16px] text-[#333333] font-medium')
                ui.input('剩余开票额') \
                    .props('rounded-md outlined dense type="number"') \
                    .classes('w-[25%] self-center item-center ') \
                    .bind_value_from(dao, 'remaining_billing_amount') \
                    .bind_value_to(dao, 'remaining_billing_amount') \
                    .set_enabled(False)
            with ui.row().classes('w-full place-content-start items-center gap-1'):
                ui.label('可开票额').classes('w-[20%] text-[16px] text-[#333333] font-medium')
                ui.input('可开票额') \
                    .props('rounded-md outlined dense type="number"') \
                    .classes('w-[25%] self-center item-center ') \
                    .bind_value_from(dao, 'billing_amount') \
                    .bind_value_to(dao, 'billing_amount')
            
            with ui.row().classes('w-full place-content-end'):
                ui.button('取消', color=None, on_click=dialog.close) \
                    .props('flat') \
                    .classes('w-[120px] text-[16px] text-[#888888] font-[400]') \
                    .style('background-color: #FFFFFF !important;border-radius: 10px;border: 1px solid #888888;')
                async def on_create():
                    if dao.company_id is None or len(dao.company_id) == 0:
                        ui.notify('请选择公司')
                        return
                    if dao.last_month_no_verify is None:
                        dao.last_month_no_verify = 0.0
                    if dao.last_month_stay_pay is None:
                        dao.last_month_stay_pay = 0.0
                    if dao.opened_input_tax is None:
                        dao.opened_input_tax = 0.0
                    if dao.opened_output_tax is None:
                        dao.opened_output_tax = 0.0
                    if dao.to_open_input_tax is None:
                        dao.to_open_input_tax = 0.0
                    if dao.to_open_output_tax is None:
                        dao.to_open_output_tax = 0.0
                    if dao.payable_tax is None:
                        dao.payable_tax = 0.0
                    if dao.sales_amount is None:
                        dao.sales_amount = 0.0
                    if dao.opened_billing_amount is None:
                        dao.opened_billing_amount = 0.0
                    if dao.remaining_billing_amount is None:
                        dao.remaining_billing_amount = 0.0
                    if dao.billing_amount is None:
                        dao.billing_amount = 0.0
                    if year_input.value is not None and month_select.value is not None:
                        dao.create_time = f"{year_input.value}-{month_select.value.zfill(2)}"
                    if dao.create_time is None or len(dao.create_time) == 0:
                        ui.notify('请选择年月')
                        return
                    if is_add:
                        result = g.my_db.add_value_added(dao.to_db())
                        if result is False:
                            ui.notify('新增增值税数据失败')
                            return
                        on_search()
                        ui.notify('新增增值税数据成功')
                    else:
                        result = g.my_db.update_value_added(dao.to_db(), {'id': dao.id})
                        if result is False:
                            ui.notify('修改增值税数据失败')
                            return
                        on_search()
                        ui.notify('修改增值税数据成功')
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
async def del_select():
    if 'value_added_table' not in app.storage.client:
        ui.notify('请先查询记录')
        return
    selection = app.storage.client['value_added_table'].selected
    if not selection:
        ui.notify('请选择要删除的记录')
        return
    ids = [item['id'] for item in selection]
    if not ids:
        ui.notify('没有选中任何记录')
        return
    await del_by_ids(ids)

async def delete_one(e: events.GenericEventArguments):
    id = e.args['id']
    await del_by_ids([id])

async def del_by_ids(ids: list[str]) -> None:
    if ids is None or len(ids) == 0:
        ui.notify('请选择要删除的记录')
        return
    async def make_delete():
        delok = True
        for id in ids:
            if id is None or len(id) == 0:
                continue
            result = g.my_db.delete_value_added(id)
            if result is False:
                delok = False
                ui.notify(f'删除记录失败: {id}')
                return
        if delok is True:
            ui.notify('删除记录成功')
            on_search()

    dialogs.make_sure_dialog('确认要进行删除操作?', on_ok=make_delete)

def summary_value_added(company_id: str, record_month: str) -> Optional[list[ValueAddedDao]|None]:
    result, list_period = g.my_db.query_all_period_data(company_id, record_month)
    if result is False:
        ui.notify('查询期初数据失败，无法进行增值税汇总')
        return None
    if list_period is None or len(list_period) == 0:
        ui.notify('没有查询到期初数据，无法进行增值税汇总')
        return None
    summary_dao_list : list[ValueAddedDao] = []
    for item in list_period:
        period_dao = PeriodDataDao()
        period_dao.from_db(item)
        #查询公司信息，判断公司是否小规模，如果小规模，则不进行增值税汇总
        result, company_dao = g.my_db.query_company_by_id(period_dao.company_id)
        if result is True and company_dao is not None:
            if company_dao.is_small_scale():
                continue
        value_added_dao = ValueAddedDao()
        value_added_dao.company_id = period_dao.company_id
        value_added_dao.create_time = period_dao.create_time
        result, list_value = g.my_db.query_all_value_added(period_dao.company_id, period_dao.create_time)
        if result is True and list_value is not None and len(list_value) > 0:
            value_added_dao.from_db(list_value[0])
        value_added_dao.last_month_no_verify = period_dao.last_month_no_verify
        value_added_dao.last_month_stay_pay = period_dao.last_month_stay_pay
        value_added_dao.billing_amount = period_dao.billing_amount
        result, dict_input_value = g.my_db.summary_input_added_tax_by_month(period_dao.company_id, period_dao.create_time)
        if result is True and dict_input_value is not None:
            value = float(dict_input_value.get('total_added_tax', 0.0))
            value_added_dao.opened_input_tax = value
        result, dict_output_value = g.my_db.summary_output_added_tax_by_month(period_dao.company_id, period_dao.create_time)
        if result is True and dict_output_value is not None:
            value1 = float(dict_output_value.get('total_added_tax', 0.0))
            value_added_dao.opened_output_tax = value1
            value2 = float(dict_output_value.get('total_invoice_money', 0.0))
            value_added_dao.opened_billing_amount = value2
        value_added_dao.payable_tax = value_added_dao.opened_output_tax + value_added_dao.to_open_output_tax - value_added_dao.opened_input_tax - value_added_dao.to_open_input_tax - value_added_dao.last_month_stay_pay - value_added_dao.last_month_no_verify
        value_added_dao.sales_amount = value_added_dao.payable_tax * 1.06 / 0.06
        value_added_dao.remaining_billing_amount = value_added_dao.billing_amount - value_added_dao.opened_billing_amount
        summary_dao_list.append(value_added_dao)
    return summary_dao_list