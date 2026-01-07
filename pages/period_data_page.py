from dataclasses import dataclass
from datetime import datetime
from nicegui import ui,events, app
from components import inputs, tables, dialogs
from typing import Any, Optional, cast
from dao.company_dao import CompanyDao
from dao.period_data_dao import PeriodDataDao
from utils import global_vars as g

@dataclass
class SearchCondition:
    company_id: str = ""
    company_name: str = ""
    record_month: str = ""
search_condition = SearchCondition()

def show_period_data_page():
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
            
        ui.button('刷新', icon='img:/static/images/refresh@2x.png', on_click=on_search) \
            .classes('w-25 rounded-md text-white') \
            .style('background-color: #6C96FB !important')
        ui.button('删除', icon='img:/static/images/delete@2x.png', on_click=del_select) \
            .classes('w-25 rounded-md text-red') \
            .style('background-color: rgba(255,77,77,0.39) !important')
        ui.button('新建', icon='img:/static/images/add_course@2x.png', on_click=show_add) \
            .classes('w-25 rounded-md text-white') \
            .style('background-color: #65B6FF !important')
            
    table_rows: list[dict] = []
    app.storage.client['period_data_table'] = tables.show_period_data_table(table_rows, show_edit, delete_one)
    on_search()

def on_search() -> None:
    result, list_values = g.my_db.query_all_period_data(search_condition.company_id, search_condition.record_month)
    if result is False:
        ui.notify('查询期初数据失败')
        return
    if 'period_data_table' in app.storage.client:
        app.storage.client['period_data_table'].rows.clear()
        app.storage.client['period_data_table'].update()
        if list_values is None or len(list_values) == 0:
            ui.notify('没有查询到期初数据')
            return
        sn = 1
        for item in list_values:
            row_dict: dict[str, Any] = {}
            row_dict['sn'] = sn
            dao = PeriodDataDao()
            dao.from_db(item)
            row_dict.update(dao.to_db())
            result, company_dao = g.my_db.query_company_by_id(dao.company_id)
            company_name = '未知开票方'
            if result and company_dao is not None:
                company_name = company_dao.brief_name
            row_dict['company_name'] = company_name
            app.storage.client['period_data_table'].add_row(row_dict)
            sn += 1
        app.storage.client['period_data_table'].update()

def show_edit(e: events.GenericEventArguments) -> None:
    id = e.args['id']
    if id is None or len(id) == 0:
        ui.notify('请选择要编辑的记录')
        return
    result, dao = g.my_db.query_period_data_by_id(id)
    if result is False or dao is None:
        ui.notify('查询期初数据失败')
        return
    modify_or_new(dao, is_add=False)

#
# @description: 新增
# @param None
# @return: None
#             
def show_add():
    dao = PeriodDataDao()
    modify_or_new(dao, is_add=True)

def modify_or_new(dao: PeriodDataDao, is_add: bool = True) -> None:
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
    with ui.dialog().props('persistent') as dialog, ui.card().classes('w-1/2') \
        .style('background-color: #FFFFFF !important; border-radius: 10px;'):
        if is_add:
            ui.label('新增数据').classes('w-full text-[20px] text-[#333333] font-medium')
        else:
            ui.label('修改数据').classes('w-full text-[20px] text-[#333333] font-medium')
        with ui.column().classes('w-full mt-5 place-content-start items-center'):
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
            with ui.row().classes('w-full place-content-start items-center gap-1'):
                ui.label('上月未认证').classes('w-[20%] text-[16px] text-[#333333] font-medium')
                ui.input('上月未认证金额') \
                    .props('rounded-md outlined dense ') \
                    .classes('w-[50%] self-center item-center ') \
                    .bind_value_from(dao, 'last_month_no_verify') \
                    .bind_value_to(dao, 'last_month_no_verify')
            with ui.row().classes('w-full place-content-start items-center gap-1'):
                ui.label('上月留抵').classes('w-[20%] text-[16px] text-[#333333] font-medium')
                ui.input('上月留抵金额') \
                    .props('rounded-md outlined dense ') \
                    .classes('w-[50%] self-center item-center ') \
                    .bind_value_from(dao, 'last_month_stay_pay') \
                    .bind_value_to(dao, 'last_month_stay_pay')
            with ui.row().classes('w-full place-content-start items-center gap-1'):
                ui.label('开票额').classes('w-[20%] text-[16px] text-[#333333] font-medium')
                ui.input('开票额') \
                    .props('rounded-md outlined dense ') \
                    .classes('w-[50%] self-center item-center ') \
                    .bind_value_from(dao, 'billing_amount') \
                    .bind_value_to(dao, 'billing_amount')
            with ui.row().classes('w-full place-content-start items-center gap-1'):
                ui.label('年月').classes('w-[20%] text-[16px] text-[#333333] font-medium')
                year_input = inputs.selection_w40([str(x) for x in range(2001, 2031)], None, False, None)
                if is_add is False and len(dao.create_time) >= 4:
                    year_input.set_value(dao.create_time[0:4])
                month_select = inputs.selection_w40([str(x).zfill(2) for x in range(1, 13)], None, False, None)
                if is_add is False and len(dao.create_time) >= 7:
                    month_select.set_value(dao.create_time[5:7])
            with ui.row().classes('w-full place-content-end'):
                ui.button('取消', color=None, on_click=dialog.close) \
                    .props('flat') \
                    .classes('w-[120px] text-[16px] text-[#888888] font-[400]') \
                    .style('background-color: #FFFFFF !important;border-radius: 10px;border: 1px solid #888888;')
                def on_create():
                    if dao.company_id is None or len(dao.company_id) == 0:
                        ui.notify('请选择公司')
                        return
                    if dao.last_month_no_verify is None:
                        dao.last_month_no_verify = 0.0
                    if dao.last_month_stay_pay is None:
                        dao.last_month_stay_pay = 0.0
                    if dao.billing_amount is None:
                        dao.billing_amount = 0.0
                    if year_input.value is not None and month_select.value is not None:
                        dao.create_time = f"{year_input.value}-{month_select.value.zfill(2)}"
                    if dao.create_time is None or len(dao.create_time) == 0:
                        ui.notify('请选择年月')
                        return
                    if is_add:
                        result = g.my_db.add_period_data(dao.to_db())
                        if result is False:
                            ui.notify('新增期初数据失败')
                            return
                        on_search()
                        ui.notify('新增期初数据成功')
                    else:
                        result = g.my_db.update_period_data(dao.to_db(), {'id': dao.id})
                        if result is False:
                            ui.notify('修改期初数据失败')
                            return
                        on_search()
                        ui.notify('修改期初数据成功')
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
    if 'period_data_table' not in app.storage.client:
        ui.notify('请先查询记录')
        return
    selection = app.storage.client['period_data_table'].selected
    if not selection:
        ui.notify('请选择要删除的记录')
        return
    ids = [item['id'] for item in selection]
    if not ids:
        ui.notify('没有选中任何记录')
        return
    del_by_ids(ids)
    app.storage.client['period_data_table'].selected.clear()

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
            result = g.my_db.delete_period_data(id)
            if result is False:
                delok = False
                ui.notify(f'删除记录失败: {id}')
                return
        if delok is True:
            ui.notify('删除记录成功')
            on_search()

    dialogs.make_sure_dialog('确认要进行删除操作?', on_ok=make_delete)