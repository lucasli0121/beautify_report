import asyncio
from dataclasses import dataclass
from datetime import datetime
from nicegui import ui,events, app, run
from components import inputs, tables, dialogs
from typing import Any, Callable, Optional
import pandas as pd
import io
import os
from openpyxl.utils import get_column_letter
from dao.company_dao import CompanyDao, CompanyType
from dao.invoice_alarm_dao import InvoiceAlarmDao, InvoiceAlarmType
from dao.invoice_record_dao import InvoiceRecordDao
from dao.recognize_info_dao import RecognizeInfoDao, RecognizeResult, RecognizeType
from dao.service_record_dao import ServiceRecordDao
from utils import global_vars as g
from utils import upload_files as uf
from utils import ocr_manager

@dataclass
class SearchCondition:
    invoice_from_id: str = ""
    invoice_from_name: str = ""
    invoice_year: str = ""
search_condition = SearchCondition()

async def show_invoice_alarm_page():
    result, company_info = g.query_company_name_company()
    if result is False:
        ui.notify('查询公司信息失败')
        return
    options = list(company_info.keys())  # 获取所有公司名称
    
    with ui.column().classes('w-full px-[20px] py-[10px] mt-0 items-center gap-2') \
        .style('background-color: #FFFFFF !important; border-radius: 10px;'):
        with ui.row().classes('w-full place-content-start items-center gap-1'):
            with ui.row().classes('w-[20%] place-content-start items-center'):
                ui.label('开票方').classes('w-[20%] text-[16px] text-[#333333] font-medium')
                def on_from_change(value):
                    if value in company_info:
                        search_condition.invoice_from_id = company_info[value].id
                        search_condition.invoice_from_name = value
                inputs.selection_w40(options, None, need_input=True, on_change=on_from_change)
                search_condition.invoice_from_id = ''
                search_condition.invoice_from_name = ''
            def on_year_select(value):
                search_condition.invoice_year = value
            from_year = datetime.now().year - 3
            to_year = datetime.now().year + 2
            year_select = inputs.selection_w40([str(x).zfill(4) for x in range(from_year, to_year)], None, False, on_change=on_year_select)
            year_select.set_value(str(datetime.now().year))
        
            with ui.row().classes('w-[55%] place-content-start items-center gap-1'):
                ui.button('刷新', icon='refresh', on_click=on_search) \
                    .classes('w-25 rounded-md text-white') \
                    .style('background-color: #6C96FB !important')
            
    table_rows: list[dict] = []
    app.storage.client['invoice_alarm_table'] = tables.show_open_invoice_alarm_table(table_rows)
    await on_search()

async def on_search() -> None:
    if 'invoice_alarm_table' not in app.storage.client:
        return
    app.storage.client['invoice_alarm_table'].rows.clear()
    def do_search() -> tuple[bool, list[dict], str]:
        rows: list[dict] = []
        result, list_values = g.my_db.query_all_invoice_alarm(
            search_condition.invoice_from_id,
            search_condition.invoice_year
        )
        if result is False:
            return False, rows, '查询开票预警信息失败'
        if list_values is not None:
            sn = 1
            for item in list_values:
                invoice_alarm = InvoiceAlarmDao()
                invoice_alarm.from_db(item)
                row_dict: dict[str, Any] = {}
                row_dict['sn'] = sn
                row_dict.update(invoice_alarm.to_db())
                result, company_dao = g.my_db.query_company_by_id(invoice_alarm.company_id)
                if result and company_dao is not None:
                    company_name = company_dao.brief_name
                else:
                    company_name = '未知开票方'
                row_dict['company_name'] = company_name
                rows.append(row_dict)
                sn += 1
        return True, rows, ""
    refresh_dialog = g.show_refresh_process("刷新，请稍候")
    success, rows, message = await run.io_bound(do_search)
    if not success:
        refresh_dialog.close()
        ui.notify(message or '查询开票预警记录失败')
        return
    app.storage.client['invoice_alarm_table'].rows = rows
    app.storage.client['invoice_alarm_table'].update()
    refresh_dialog.close()
    

async def do_analyze(
        org_from_company_id: str,
        next_from_company_id: str,
        invoice_year: str,
        scan_invoice_list: list[Any],
        invoice_path_list: list[InvoiceRecordDao],
        visited: set[str]):
    if next_from_company_id in visited:
        return  # 避免重复访问，防止无限递归
    visited.add(next_from_company_id)

    # 预过滤并去重: 只保留from_company_id等于next_from_company_id
    filtered_scan_list: list[dict[str, Any]] = [
        item for item in scan_invoice_list
        if item['from_company_id'] == next_from_company_id
    ]
    # seen_to_company_ids: set[str] = set()
    # for item in scan_invoice_list:
    #     if item['from_company_id'] != next_from_company_id:
    #         continue
    #     to_company_id = item.get('to_company_id')
    #     if to_company_id in seen_to_company_ids:
    #         continue
    #     seen_to_company_ids.add(to_company_id)
    #     filtered_scan_list.append(item)
    # path_log = f"当前路径: "
    # for item in invoice_path_list:
    #     result, company_dao = g.my_db.query_company_by_id(item.from_company_id)
    #     if result and company_dao:
    #         path_log += f"from: {company_dao.brief_name} -> "
    #     result, company_dao = g.my_db.query_company_by_id(item.to_company_id)
    #     if result and company_dao:
    #         path_log += f"to: {company_dao.brief_name} | "
    # path_log += f"发票数量: {len(filtered_scan_list)}; "
    # print(path_log)
    for i in range(len(filtered_scan_list)):
        # print("分析发票记录索引: ", i)
        invoice_record = InvoiceRecordDao()
        invoice_record.from_db(filtered_scan_list[i])
        if invoice_record.to_company_id == org_from_company_id:
            dao = InvoiceAlarmDao()
            dao.company_id = org_from_company_id
            dao.invoice_year = invoice_year
            dao.alarm_type = InvoiceAlarmType.InvoiceCircleAlarm.value
            dao.alarm_desc = dao.get_alarm_desc(dao.alarm_type)
            result, company_dao = g.my_db.query_company_by_id(org_from_company_id)
            if result and company_dao:
                dao.detail = "from: " + company_dao.brief_name
            temp_list: list[InvoiceRecordDao] = invoice_path_list.copy()
            temp_list.append(invoice_record)
            for values in temp_list:
                to_company_id = values.to_company_id
                result, company_dao = g.my_db.query_company_by_id(to_company_id)
                if result and company_dao:
                    to_company_name = company_dao.brief_name
                else:
                    to_company_name = '未知公司'
                dao.detail += f" ->to: {to_company_name}\n"
            g.my_db.add_invoice_alarm(dao.to_db())
        else:
            new_invoice_list: list[InvoiceRecordDao] = invoice_path_list.copy()
            new_invoice_list.append(invoice_record)
            next_from_id = invoice_record.to_company_id
            await do_analyze(
                org_from_company_id=org_from_company_id,
                next_from_company_id=next_from_id,
                scan_invoice_list=scan_invoice_list.copy(),
                invoice_path_list=new_invoice_list,
                invoice_year=invoice_year,
                visited=visited)  # 传递副本以避免共享状态问题
    