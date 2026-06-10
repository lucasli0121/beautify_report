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
    """
    显示开票预警页面 UI。

    此函数负责构建页面搜索表单、表格占位以及下方的分页控件。
    - 从全局获取公司名称映射用于下拉选择。
    - 初始化 `app.storage.client['invoice_alarm_paging']` 分页状态。
    - 创建表格并在表格下方创建分页按钮（首页/上一页/下一页/尾页）。
    - 发起首次查询 `on_search()` 以填充表格数据。

    注意：分页逻辑使用 `app.storage.client['invoice_alarm_paging']` 保存当前页、页面大小和总条数。
    """
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
        # 分页控件将放在表格下方以避免与表格内置分页冲突
    app.storage.client.setdefault('invoice_alarm_paging', {'page': 1, 'page_size': 10, 'total': 0})
    table_rows: list[dict] = []
    app.storage.client['invoice_alarm_table'] = tables.show_open_invoice_alarm_table(table_rows)
    # 在表格下方显示分页控件（首页/上一页/下一页/尾页）
    async def go_first(*_) -> None:
        await on_search(1)

    async def go_prev(*_) -> None:
        await on_search(max(1, app.storage.client['invoice_alarm_paging']['page'] - 1))

    async def go_next(*_) -> None:
        await on_search(app.storage.client['invoice_alarm_paging']['page'] + 1)

    async def go_last(*_) -> None:
        await on_search(max(1, (app.storage.client['invoice_alarm_paging']['total'] + app.storage.client['invoice_alarm_paging']['page_size'] - 1) // app.storage.client['invoice_alarm_paging']['page_size']))

    with ui.row().classes('w-full items-center justify-center gap-2'):
        first_btn = ui.button('首页', on_click=go_first)
        prev_btn = ui.button('上一页', on_click=go_prev)
        page_label = ui.label('')
        next_btn = ui.button('下一页', on_click=go_next)
        last_btn = ui.button('尾页', on_click=go_last)
        app.storage.client['invoice_alarm_first_btn'] = first_btn
        app.storage.client['invoice_alarm_prev_btn'] = prev_btn
        app.storage.client['invoice_alarm_next_btn'] = next_btn
        app.storage.client['invoice_alarm_last_btn'] = last_btn
        app.storage.client['invoice_alarm_page_label'] = page_label
    await on_search()

async def on_search(page: int = 1) -> None:
    """
    根据搜索条件查询开票预警并更新表格与分页控件。

    参数:
    - page: 要查询的页码（从1开始）。

    行为:
    - 读取并更新 `app.storage.client['invoice_alarm_paging']` 状态。
    - 使用 `g.my_db.query_all_invoice_alarm(...)` 进行服务端分页查询，返回 `{'total','rows'}`。
    - 为当前页收集所需的公司ID并通过 `g.my_db.query_companies_by_ids` 批量获取公司信息，避免每行单独查询（避免N+1问题）。
    - 更新表格数据、页码显示以及翻页按钮的启用/禁用状态。
    """
    if 'invoice_alarm_table' not in app.storage.client:
        return
    paging = app.storage.client.setdefault('invoice_alarm_paging', {'page': 1, 'page_size': 10, 'total': 0})
    try:
        page = int(page)
    except Exception:
        page = 1
    if page < 1:
        page = 1
    paging['page'] = page
    page_size = paging.get('page_size', 10)

    app.storage.client['invoice_alarm_table'].rows.clear()
    def do_search() -> tuple[bool, list[dict], str, int]:
        rows: list[dict] = []
        result, list_values = g.my_db.query_all_invoice_alarm(
            search_condition.invoice_from_id,
            search_condition.invoice_year,
            page,
            page_size
        )
        if result is False:
            return False, rows, '查询开票预警信息失败', 0
        total = 0
        data_list: list[dict[str, Any]]
        if list_values is None:
            data_list = []
        elif isinstance(list_values, dict):
            total = int(list_values.get('total', 0))
            data_list = list_values.get('rows', []) or []
        else:
            data_list = list_values
            total = len(data_list)

        company_ids = [str(item.get('company_id', '')) for item in data_list if item.get('company_id')]
        companies: dict[str, CompanyDao] = {}
        if company_ids:
            result, company_dict = g.my_db.query_companies_by_ids(company_ids)
            if result and company_dict is not None:
                companies = company_dict

        sn = (page - 1) * page_size + 1
        for item in data_list:
            invoice_alarm = InvoiceAlarmDao()
            invoice_alarm.from_db(item)
            row_dict: dict[str, Any] = {}
            row_dict['sn'] = sn
            row_dict.update(invoice_alarm.to_db())
            company = companies.get(invoice_alarm.company_id)
            row_dict['company_name'] = company.brief_name if company is not None else '未知开票方'
            rows.append(row_dict)
            sn += 1
        return True, rows, "", total
    refresh_dialog = g.show_refresh_process("刷新，请稍候")
    success, rows, message, total = await run.io_bound(do_search)
    if not success:
        refresh_dialog.close()
        ui.notify(message or '查询开票预警记录失败')
        return
    refresh_dialog.close()
    app.storage.client['invoice_alarm_table'].rows = rows
    app.storage.client['invoice_alarm_table'].update()
    paging['total'] = total
    total_pages = (total + page_size - 1) // page_size if page_size > 0 else 1
    total_pages = max(1, total_pages)
    if page > total_pages:
        page = total_pages
        paging['page'] = page
        success, rows, message, total = await run.io_bound(do_search)
        if not success:
            ui.notify(message or '查询开票预警记录失败')
            return
        app.storage.client['invoice_alarm_table'].rows = rows
        app.storage.client['invoice_alarm_table'].update()
    if 'invoice_alarm_page_label' in app.storage.client:
        app.storage.client['invoice_alarm_page_label'].set_text(f"第 {page} / {total_pages} 页，共 {total} 条")
    if 'invoice_alarm_prev_btn' in app.storage.client:
        app.storage.client['invoice_alarm_prev_btn'].disabled = (page <= 1)
    if 'invoice_alarm_next_btn' in app.storage.client:
        app.storage.client['invoice_alarm_next_btn'].disabled = (page >= total_pages)
    if 'invoice_alarm_first_btn' in app.storage.client:
        app.storage.client['invoice_alarm_first_btn'].disabled = (page <= 1)
    if 'invoice_alarm_last_btn' in app.storage.client:
        app.storage.client['invoice_alarm_last_btn'].disabled = (page >= total_pages)
    

async def do_analyze(
        org_from_company_id: str,
        next_from_company_id: str,
        invoice_year: str,
        scan_invoice_list: list[Any],
        invoice_path_list: list[InvoiceRecordDao],
        visited: set[str]):
    """
    递归分析发票链以发现可能的循环开票（发票回路）并生成预警记录。

    参数:
    - org_from_company_id: 原始起始公司ID（用于判断回路归属）。
    - next_from_company_id: 当前递归步的下一步起始公司ID。
    - invoice_year: 发票对应的年份，用于生成预警记录。
    - scan_invoice_list: 要扫描的所有发票记录（原始数据列表）。
    - invoice_path_list: 已经经过的发票路径（用于构造预警详情）。
    - visited: 已访问的公司ID集合，防止无限递归。

    行为:
    - 若 `next_from_company_id` 已在 `visited` 中则直接返回，防止重复访问。
    - 过滤 `scan_invoice_list` 找到以 `next_from_company_id` 为开票方的记录，逐条分析是否形成回路。
    - 若发现回路，构造 `InvoiceAlarmDao` 并调用 `g.my_db.add_invoice_alarm` 保存预警。
    """
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
    