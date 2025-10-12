from dataclasses import dataclass
from datetime import datetime
from nicegui import ui,events, app
from components import inputs, tables, dialogs
from typing import Any, Callable, Optional
import pandas as pd
import io
import os
from dao.company_dao import CompanyDao
from dao.invoice_record_dao import InvoiceRecordDao
from dao.service_record_dao import ServiceRecordDao
from utils import global_vars as g
from utils import upload_files as uf

@dataclass
class SearchCondition:
    invoice_from_id: str = ""
    invoice_from_name: str = ""
    invoice_to_id: str = ""
    invoice_to_name: str = ""
    invoice_content: str = ""
    begin_time: str = ""
    end_time: str = ""
    invoice_number: str = ""
    status: int = -1 # -1: 全部, 0: 未开票, 1: 已开票, 2: 已作废, 3: 已红冲
search_condition = SearchCondition()

def show_invoice_record_page():
    result, company_info = g.query_company_name_company()
    if result is False:
        ui.notify('查询公司信息失败')
        return
    options = list(company_info.keys())  # 获取所有公司名称
    
    with ui.column().classes('w-full px-[20px] py-[10px] mt-0 items-center gap-2') \
        .style('background-color: #FFFFFF !important; border-radius: 10px;'):
        with ui.row().classes('w-full place-content-start items-center gap-1'):
            with ui.row().classes('w-[25%] place-content-start items-center'):
                ui.label('开票方').classes('w-[20%] text-[16px] text-[#333333] font-medium')
                def on_from_change(value):
                    if value in company_info:
                        search_condition.invoice_from_id = company_info[value].id
                        search_condition.invoice_from_name = value
                inputs.selection_w60(options, None, need_input=True, on_change=on_from_change)
            with ui.row().classes('w-[25%] place-content-start items-center'):
                ui.label('受票方').classes('w-[20%] text-[16px] text-[#333333] font-medium')
                def on_to_change(value):
                    if value in company_info:
                        search_condition.invoice_to_id = company_info[value].id
                        search_condition.invoice_to_name = value
                inputs.selection_w60(options, None, need_input=True, on_change=on_to_change)
            inputs.input_search_w40('发票内容', on_search) \
                .bind_value_to(search_condition, 'invoice_content')
            inputs.date_input_w40('开始时间', on_search) \
                .bind_value_to(search_condition, 'begin_time')
            inputs.date_input_w40('结束时间', on_search) \
                .bind_value_to(search_condition, 'end_time')
        with ui.row().classes('w-full place-content-start items-center gap-1'):
            with ui.row().classes('w-[25%] place-content-start items-center'):
                ui.label('状态').classes('w-[20%] text-[16px] text-[#333333] font-medium')
                def on_status_change(value):
                    if value == '全部':
                        search_condition.status = -1
                    elif value == '未开票':
                        search_condition.status = 0
                    elif value == '已开票':
                        search_condition.status = 1
                    elif value == '已作废':
                        search_condition.status = 2
                    elif value == '已红冲':
                        search_condition.status = 3
                    on_search()
                inputs.selection_w60(['全部', '未开票', '已开票', '已作废', '已红冲'], '全部', need_input=False, on_change=on_status_change)
            with ui.row().classes('w-[25%] place-content-start items-center'):
                inputs.input_search_w60('发票号码', on_search).bind_value_to(search_condition, 'invoice_number')
            with ui.row().classes('w-[49%] place-content-start items-center gap-1'):
                ui.button('刷新', icon='refresh', on_click=on_search) \
                    .classes('w-25 rounded-md text-white') \
                    .style('background-color: #6C96FB !important')
                ui.button('删除', icon='delete', on_click=del_select) \
                    .classes('w-25 rounded-md text-red') \
                    .style('background-color: rgba(255,77,77,0.39) !important')
                ui.button('开票计划', icon='add_chart', on_click=add_invoice) \
                    .classes('w-25 rounded-md text-white') \
                    .style('background-color: #65B6FF !important')
                ui.button('导出', icon='file_download', on_click=export_invoice_to_excel) \
                    .classes('w-25 rounded-md text-white') \
                    .style('background-color: #65B6FF !important')
                ui.button('上传发票', icon='upload', on_click=upload_invoice_pdf) \
                    .classes('w-25 rounded-md text-white') \
                    .style('background-color: #65B6FF !important')
            
    table_rows: list[dict] = []
    app.storage.client['invoice_record_table'] = tables.show_open_invoice_table(table_rows, show_edit, delete_one)
    on_search()

def on_search() -> None:
    result, list_values = g.my_db.query_all_invoice_record(
        search_condition.invoice_from_id,
        search_condition.invoice_to_id,
        search_condition.invoice_content,
        search_condition.invoice_number,
        search_condition.status,
        search_condition.begin_time,
        search_condition.end_time,)
    if result is False:
        ui.notify('查询开票记录失败')
        return
    if 'invoice_record_table' in app.storage.client:
        app.storage.client['invoice_record_table'].rows.clear()
        if list_values is not None:
            sn = 1
            for item in list_values:
                invoice_record = InvoiceRecordDao()
                invoice_record.from_db(item)
                row_dict: dict[str, Any] = {}
                row_dict['sn'] = sn
                row_dict.update(invoice_record.to_db())
                result, company_dao = g.my_db.query_company_by_id(invoice_record.from_company_id)
                if result and company_dao is not None:
                    from_company_name = company_dao.brief_name
                else:
                    from_company_name = '未知开票方'
                row_dict['from_company_name'] = from_company_name
                result, to_company_dao = g.my_db.query_company_by_id(invoice_record.to_company_id)
                if result and to_company_dao is not None:
                    row_dict['to_company_name'] = to_company_dao.brief_name
                else:
                    row_dict['to_company_name'] = '未知受票方'
                result, service_dao = g.my_db.query_service_record_by_id(invoice_record.contract_id)
                if result and service_dao is not None:
                    row_dict['contract_name'] = service_dao.contract_name
                else:
                    row_dict['contract_name'] = '无'
                row_dict['before_tax_money'] = '{:,.2f}'.format(invoice_record.before_tax_money)
                row_dict['added_tax'] = '{:,.2f}'.format(invoice_record.added_tax)
                row_dict['invoice_money'] = '{:,.2f}'.format(invoice_record.invoice_money)
                app.storage.client['invoice_record_table'].add_row(row_dict)
                sn += 1
        app.storage.client['invoice_record_table'].update()

def handle_import_pdf(d: dict) -> None:
    if d is None or len(d) == 0:
        ui.notify('导入的pdf文件不能为空')
        return
    for sheet_name, df in d.items():
        if sheet_name != '开票记录':
            continue
        required_columns = ['开票方', '受票方', '类型', '开票额', '已开额']
        for col in required_columns:
            if col not in df.columns:
                ui.notify(f'导入的Excel文件缺少必要的列: {col}')
                return
        success_count = 0
        fail_count = 0
        df = df.fillna('')  # 将NaN值替换为空字符串
        for index, row in df.iterrows():
            dao = InvoiceRecordDao()
            dao.invoice_time = str(row['开票时间']).replace('/', '-').strip()
            from_company_name = str(row['开票方']).strip()
            to_company_name = str(row['受票方']).strip()
            invoice_type_str = str(row['类型']).strip()
            invoice_money_str = str(row['开票额']).strip()
            has_invoice_money_str = str(row['已开额']).strip()
            if from_company_name == '' or to_company_name == '':
                ui.notify(f'第 {index + 2} 行数据不完整，开票方和受票方不能为空，跳过该行')
                fail_count += 1
                continue
            result, from_company_dao = g.my_db.query_company_by_brief_name(from_company_name)
            if not result or from_company_dao is None:
                ui.notify(f'第 {index + 2} 行开票方 "{from_company_name}" 不存在，跳过该行')
                fail_count += 1
                continue
            dao.from_company_id = from_company_dao.id
            result, to_company_dao = g.my_db.query_company_by_brief_name(to_company_name)
            if not result or to_company_dao is None:
                ui.notify(f'第 {index + 2} 行受票方 "{to_company_name}" 不存在，跳过该行')
                fail_count += 1
                continue
            dao.to_company_id = to_company_dao.id
            if invoice_type_str == '专票':
                dao.invoice_type = 1
            else:
                dao.invoice_type = 0

def parse_upload_result_to_dao(result: list) -> Optional[InvoiceRecordDao]:
    if result is None or len(result) == 0:
        ui.notify('未识别到发票信息')
        return None
    dao = InvoiceRecordDao()
    dao.invoice_content = result[0].get('发票内容', '')
    dao.invoice_number = result[0].get('发票号码', '')
    invoice_date_str = result[0].get('开票日期', '')
    if invoice_date_str != '':
        try:
            if '年' in invoice_date_str:
                dt = datetime.strptime(invoice_date_str, '%Y年%m月%d日')
            elif '-' in invoice_date_str:
                dt = datetime.strptime(invoice_date_str, '%Y-%m-%d')
            else:
                dt = datetime.strptime(invoice_date_str, '%Y/%m/%d')
            dao.invoice_time = dt.strftime('%Y-%m-%d')
        except ValueError:
            dao.invoice_time = ''
    before_tax_money = result[0].get('含税额', 0.0)
    tax_money = result[0].get('税额', 0.0)
    invoice_money = result[0].get('金额', 0.0)
    tax_rate = result[0].get('税率', 0.0)
    if tax_rate == '1%':
        dao.tax_rate = 0.01
    elif tax_rate == '3%':
        dao.tax_rate = 0.03
    elif tax_rate == '6%':
        dao.tax_rate = 0.06
    elif tax_rate == '9%':
        dao.tax_rate = 0.09
    elif tax_rate == '13%':
        dao.tax_rate = 0.13
    dao.before_tax_money = before_tax_money
    dao.added_tax = tax_money
    dao.invoice_money = invoice_money
    dao.is_red = 1 if result[0].get('红字发票', False) else 0
    dao.blue_invoice_number = result[0].get('蓝字发票号码', '') if dao.is_red == 1 else ''
    from_company_name = result[0].get('购买方', '')
    to_company_name = result[0].get('销售方', '')
    if from_company_name == '' or to_company_name == '':
        ui.notify('发票信息不完整，开票方和受票方不能为空')
        return None
    res, from_company_list = g.my_db.query_all_company(from_company_name, '', '')
    if not res:
        ui.notify(f'查询 "{from_company_name}" 失败')
        return None
    if from_company_list is None or len(from_company_list) == 0:
        ui.notify(f'发票开票方 "{from_company_name}" 不存在，请先添加该公司信息')
        return None
    company_dao: CompanyDao = CompanyDao()
    company_dao.from_db(from_company_list[0])
    dao.from_company_id = company_dao.id
    if to_company_name == '' or to_company_name == '':
        ui.notify('发票信息不完整，开票方和受票方不能为空')
        return None
    res, to_company_list = g.my_db.query_all_company(to_company_name, '', '')
    if not res:
        ui.notify(f'查询 "{to_company_name}" 失败')
        return None
    if to_company_list is None or len(to_company_list) == 0:
        ui.notify(f'发票购买方 "{to_company_name}" 不存在，请先添加该公司信息')
        return None
    company_dao.from_db(to_company_list[0])
    dao.to_company_id = company_dao.id
    dao.quantity = result[0].get('数量', 0)
    dao.specifi = result[0].get('规格', '')
    dao.unit_price = result[0].get('单价', 0.0)
    dao.remark = result[0].get('备注', '')
    dao.operator_flag = 1 # 上传发票
    dao.status = 1 # 已开票
    if dao.is_red == 1:
        dao.status = 3 # 已红冲
    return dao

def read_pdf_from_upload(handle_upload: Callable) -> None:
    def upload_invoice_ocr(result: list) -> None:
        dao = parse_upload_result_to_dao(result)
        if handle_upload is not None and dao is not None:
            handle_upload(dao)
    uf.open_ocr_invoice_dialog(upload_invoice_ocr)

# @description: 上传发票PDF
# @param None
# @return: None

def upload_invoice_pdf() -> None:
    def handle_upload(dao: InvoiceRecordDao) -> None:
        res, record_list = g.my_db.query_invoice_record_by_time(dao.from_company_id, dao.to_company_id, dao.invoice_content, dao.invoice_time)
        if res and record_list is not None and len(record_list) > 0:
            ui.notify(f'发票 "{dao.invoice_number}" 已存在，不能重复上传')
            return
        res, _ = g.my_db.add_invoice_record(dao.to_db())
        if not res:
            ui.notify('保存发票信息失败')
            return
        if dao.is_red == 1:
            res, record_list = g.my_db.query_invoice_record_by_number(dao.blue_invoice_number)
            if res and record_list is not None and len(record_list) > 0:
                blue_dao = InvoiceRecordDao()
                blue_dao.from_db(record_list[0])
                blue_dao.status = 2 # 已作废
                if not g.my_db.update_invoice_record(blue_dao.to_db(), {'id': blue_dao.id}):
                    ui.notify('更新蓝字发票状态失败')
                    return
        ui.notify('保存发票信息成功')
    read_pdf_from_upload(handle_upload)
    
# @description: 导出选中发票记录
# @param None
# @return: None    
def export_invoice_to_excel() -> None:
    if search_condition.invoice_from_name == '':
        ui.notify('请先选择开票方')
        return
    if 'invoice_record_table' not in app.storage.client:
        ui.notify('请先查询开票记录')
        return
    selection = app.storage.client['invoice_record_table'].selected
    if not selection:
        ui.notify('请选择要导出的开票记录')
        return
    ids = [item['id'] for item in selection]
    if not ids:
        ui.notify('没有选中任何开票记录')
        return
    file_name = f"./static/{search_condition.invoice_from_name}-开票计划.xlsx"
    df1 = pd.DataFrame()
    for id in ids:
        res, record_dao = g.my_db.query_invoice_record_by_id(id)
        if not res or record_dao is None:
            continue
        res, to_dao = g.my_db.query_company_by_id(record_dao.to_company_id)
        if not res or to_dao is None:
            continue
        res, results = g.my_db.query_invoice_title_all(company_id = to_dao.id)
        title_phone: str = ''
        title_bank_account: str = ''
        title_bank_name: str = ''
        if res and results is not None:
            title_dao = results[0]
            title_phone = title_dao.contact_phone
            title_bank_account = title_dao.bank_account
            title_bank_name = title_dao.bank_name
        df2 = pd.DataFrame([['公司名称', to_dao.name], \
                    ['税号', to_dao.tax_no], \
                    ['地址电话', f'{to_dao.address} {title_phone}'], \
                    ['开户银行及账号', f'{title_bank_name} {title_bank_account}']])
        df1 = pd.concat([df1, df2], ignore_index=True)
        df3 = pd.DataFrame([['项目名称', '发票类型', '规格', '数量', '单价', '含税额', '税率', '税额', '金额'], \
                    [record_dao.invoice_content, \
                    '专票' if record_dao.invoice_type == 1 else '普票', \
                    record_dao.specifi, \
                    record_dao.quantity, \
                    record_dao.unit_price, \
                    record_dao.before_tax_money, \
                    f'{record_dao.tax_rate*100:.0f}%', \
                    record_dao.added_tax, \
                    record_dao.invoice_money]])
        df1 = pd.concat([df1, df3], ignore_index=True)
        df4 = pd.DataFrame([[None, None], [None, None]])
        df1 = pd.concat([df1, df4], ignore_index=True)
    df1.to_excel(file_name, index=False)
    ui.download.file(file_name)

                
def show_edit(e: events.GenericEventArguments) -> None:
    id = e.args['id']
    if id is None or len(id) == 0:
        ui.notify('开票记录ID不能为空')
        return
    result, invoice_dao = g.my_db.query_invoice_record_by_id(id)
    if not result or invoice_dao is None:
        ui.notify('查询开票记录失败')
        return
    modify_or_add_invoice(invoice_dao, is_add = False)      
#
# @description: 开票
# @param None
# @return: None
#             
def add_invoice():
    dao = InvoiceRecordDao()
    modify_or_add_invoice(dao, is_add=True)


def modify_or_add_invoice(dao: InvoiceRecordDao, is_add: bool = True):
    result, company_info = g.query_company_name_company()
    if result is False:
        ui.notify('查询公司信息失败')
        return
    options = list(company_info.keys())  # 获取所有公司名称
    contract_name_dict: dict[str, ServiceRecordDao] = {}
    select_service_dao: ServiceRecordDao | None = None
    old_before_tax_money = dao.before_tax_money
    # 如果是修改开票记录，先查询合同信息
    if not is_add:
        result, contract_name_dict = g.query_service_name_dict(from_company_id=dao.from_company_id, to_company_id=dao.to_company_id)
        if result and contract_name_dict:
            for _, service_dao in contract_name_dict.items():
                if service_dao.id == dao.contract_id:
                    select_service_dao = service_dao
                    break
    #定义变量
    contract_content_input = None
    before_tax_label = None
    contract_name_select = None
    add_tax_input = None
    invoice_money_input = None
    before_tax_money_input = None
    # 
    # 定义内部函数 当合同名称改变后被调用
    #
    def change_contract_name():
        global contract_name_dict
        result, contract_name_dict = g.query_service_name_dict(from_company_id=dao.from_company_id, to_company_id=dao.to_company_id)
        if result is False or contract_name_dict is None or len(contract_name_dict) == 0:
            if contract_name_select is not None:
                contract_name_select.set_options([])
            return
        contract_options = list(contract_name_dict.keys())
        if contract_name_select is not None:
            contract_name_select.set_options(contract_options)
    with ui.dialog().props('persistent') as dialog, ui.card().style('width: 65%; max-width: 65%;') \
        .style('background-color: #FFFFFF !important; border-radius: 10px;'):
        if is_add:
            ui.label('开票计划').classes('w-full text-[20px] text-[#333333] font-medium')
        else:
            ui.label('修改开票').classes('w-full text-[20px] text-[#333333] font-medium')
        with ui.row().classes('w-full mt-5 place-content-between items-center'):
            if not is_add:
                with ui.row().classes('w-full place-content-between'):
                    def handle_upload_invoice_ocr(event):
                        # event.content 是文件的二进制内容
                        file_content = io.BytesIO(event.content.read())
                        results = uf.recognize_invoice_pdf(file_content.read())
                        upload_dao = parse_upload_result_to_dao(results)
                        if upload_dao is not None:
                            # if dao.from_company_id != upload_dao.from_company_id or dao.to_company_id != upload_dao.to_company_id:
                            #     ui.notify('上传发票的开票方或受票方与当前编辑的发票不符，上传失败')
                            #     return
                            dao.specifi = upload_dao.specifi
                            dao.quantity = upload_dao.quantity
                            dao.unit_price = upload_dao.unit_price
                            dao.tax_rate = upload_dao.tax_rate
                            dao.invoice_number = upload_dao.invoice_number
                            dao.invoice_time = upload_dao.invoice_time
                            dao.is_red = upload_dao.is_red
                            dao.blue_invoice_number = upload_dao.blue_invoice_number
                            dao.invoice_content = upload_dao.invoice_content
                            dao.before_tax_money = upload_dao.before_tax_money
                            dao.invoice_money = upload_dao.invoice_money
                            dao.added_tax = upload_dao.added_tax
                            dao.remark = upload_dao.remark
                            dao.status = upload_dao.status
                            if before_tax_money_input is not None:
                                before_tax_money_input.set_value(dao.before_tax_money)
                    ui.upload(label="请选择批量上传文件", on_upload=handle_upload_invoice_ocr) \
                        .props('flat accept=".pdf"') \
                        .classes('size-full')
            with ui.row().classes('w-[49%] place-content-start items-center gap-1'):
                ui.label('开票方').classes('w-[20%] text-[16px] text-[#333333] font-medium')
                def on_from_change(value):
                    if value in company_info:
                        dao.from_company_id = company_info[value].id
                        if dao.to_company_id is not None and dao.to_company_id != "":
                            change_contract_name()
                from_company_select = inputs.selection_w60(options, None, need_input=True, on_change=on_from_change)
                def add_from_company():
                    def on_complete(new_company: CompanyDao):
                        company_info[new_company.brief_name] = new_company
                        options.append(new_company.brief_name)
                        from_company_select.set_options(options)
                        to_company_select.set_options(options)
                        from_company_select.set_value(new_company.brief_name)
                    g.add_out_company(on_complete)
                ui.button('增加公司', icon='add', on_click=add_from_company)
                if not is_add:
                    if dao.from_company_id is not None and dao.from_company_id != "":
                        for company_name, company_dao in company_info.items():
                            if company_dao.id == dao.from_company_id:
                                from_company_select.set_value(company_name)
                                break
            with ui.row().classes('w-[49%] place-content-start items-center gap-1'):
                ui.label('受票方').classes('w-[20%] text-[16px] text-[#333333] font-medium')
                def on_to_change(value):
                    if value in company_info:
                        dao.to_company_id = company_info[value].id
                        if dao.from_company_id is not None and dao.from_company_id != "":
                            change_contract_name()
                to_company_select = inputs.selection_w60(options, None, need_input=True, on_change=on_to_change)
                def add_to_company():
                    def on_complete(new_company: CompanyDao):
                        company_info[new_company.brief_name] = new_company
                        options.append(new_company.brief_name)
                        from_company_select.set_options(options)
                        to_company_select.set_options(options)
                        to_company_select.set_value(new_company.brief_name)
                    g.add_out_company(on_complete)
                ui.button('增加公司', icon='add', on_click=add_to_company)
                if not is_add:
                    if dao.to_company_id is not None and dao.to_company_id != "":
                        for company_name, company_dao in company_info.items():
                            if company_dao.id == dao.to_company_id:
                                to_company_select.set_value(company_name)
                                break
        with ui.row().classes('w-full place-content-between items-center'):
            with ui.row().classes('w-[49%] place-content-start items-center gap-1'):
                ui.label('合同名称').classes('w-[20%] self-right text-[16px] text-[#333333] font-medium')
                def on_contract_change(value):
                    global contract_name_dict, select_service_dao
                    if value in contract_name_dict:
                        dao.contract_id = contract_name_dict[value].id
                        select_service_dao = contract_name_dict[value]
                        if contract_content_input is not None:
                            contract_content_input.set_value(select_service_dao.contract_content if select_service_dao else '')
                        if before_tax_label is not None:
                            before_tax_label.set_text(f'税前额(未开票金额): {select_service_dao.payment_money - select_service_dao.invoice_money if select_service_dao else 0}')
                contract_name_select = inputs.selection_w60([], None, need_input=True, on_change=on_contract_change)
                if not is_add:
                    if contract_name_dict is not None:
                        contract_options = list(contract_name_dict.keys())
                        if contract_name_select is not None:
                            contract_name_select.set_options(contract_options)
                            if select_service_dao is not None:
                                contract_name_select.set_value(select_service_dao.contract_name)
            with ui.row().classes('w-[49%] place-content-start items-center gap-1'):
                ui.label('发票类型').classes('w-[20%] self-right text-[16px] text-[#333333] font-medium')
                invoice_type_select = inputs.selection_w40(['普票', '专票'], '普票', on_change=lambda value: setattr(dao, 'invoice_type', 0 if value == '普票' else 1))
                if not is_add:
                    if dao.invoice_type == 0:
                        invoice_type_select.set_value('普票')
                    else:
                        invoice_type_select.set_value('专票')
        with ui.row().classes('w-full place-content-between items-center'):
            with ui.row().classes('w-[49%] place-content-start items-center gap-1'):
                ui.label('发票内容').classes('w-[20%] self-right text-[16px] text-[#333333] font-medium')
                ui.input(placeholder='请输入发票内容') \
                    .props('rounded-md outlined dense') \
                    .classes('w-[30%] self-center item-center ') \
                    .bind_value_from(dao, 'invoice_content') \
                    .bind_value_to(dao, 'invoice_content')
            with ui.row().classes('w-[49%] place-content-start items-center gap-1'):
                ui.label('规格').classes('w-[20%] self-right text-[16px] text-[#333333] font-medium')
                ui.input(placeholder='请输入规格') \
                    .props('rounded-md outlined dense') \
                    .classes('w-[30%] self-center item-center ') \
                    .bind_value_from(dao, 'specifi') \
                    .bind_value_to(dao, 'specifi')
        with ui.row().classes('w-full place-content-between items-center'):
            with ui.row().classes('w-[49%] place-content-start items-center gap-1'):
                ui.label('数量').classes('w-[20%] self-right text-[16px] text-[#333333] font-medium')
                def on_quantity_change(e: events.ValueChangeEventArguments) -> None:
                    value = e.value
                    if value is None or value == '':
                        dao.quantity = 0
                    else:
                        try:
                            dao.quantity = int(value)
                            if before_tax_money_input is not None:
                                before_tax_money_input.set_value(dao.quantity * dao.unit_price)
                        except ValueError:
                            ui.notify('数量必须是整数')
                            dao.quantity = 0
                ui.input(placeholder='请输入数量') \
                    .props('type="number" step="1" rounded-md outlined dense') \
                    .classes('w-[30%] self-center item-center ') \
                    .on_value_change(on_quantity_change) \
                    .set_value(dao.quantity)
            with ui.row().classes('w-[49%] place-content-start items-center gap-1'):
                ui.label('单价').classes('w-[20%] self-right text-[16px] text-[#333333] font-medium')
                def on_unit_price_change(e: events.ValueChangeEventArguments) -> None:
                    value = e.value
                    if value is None or value == '':
                        dao.unit_price = 0.0
                    else:
                        try:
                            dao.unit_price = float(value)
                            if before_tax_money_input is not None:
                                before_tax_money_input.set_value(dao.quantity * dao.unit_price)
                        except ValueError:
                            ui.notify('单价必须是数字')
                            dao.unit_price = 0.0
                ui.input(placeholder='请输入单价') \
                    .props('type="number" step="0.01" rounded-md outlined dense') \
                    .classes('w-[30%] self-center item-center ') \
                    .on_value_change(on_unit_price_change) \
                    .set_value(dao.unit_price)
        with ui.row().classes('w-full place-content-between items-center'):
            with ui.row().classes('w-[49%] place-content-start items-center gap-1'):
                ui.label('含税额').classes('w-[20%] self-right text-[16px] text-[#333333] font-medium')
                def on_before_tax_change(e: events.ValueChangeEventArguments) -> None:
                    value = e.value
                    if value is None or value == '':
                        dao.before_tax_money = 0
                    else:
                        try:
                            dao.before_tax_money = float(value)
                            if select_service_dao is not None:
                                gap_invoice_money = select_service_dao.contract_money - select_service_dao.invoice_money
                                if dao.before_tax_money > gap_invoice_money:
                                    ui.notify(f'税前额不能大于未开票金额，未开票金额: {gap_invoice_money}')
                                    dao.before_tax_money = gap_invoice_money
                            add_tax = round(dao.before_tax_money / (1 + dao.tax_rate) * dao.tax_rate, 2) if dao.tax_rate else 0
                            if add_tax_input is not None:
                                add_tax_input.set_value(add_tax)
                            invoice_money = round(dao.before_tax_money / (1 + dao.tax_rate), 2)
                            if invoice_money_input is not None:
                                invoice_money_input.set_value(invoice_money)
                        except ValueError:
                            ui.notify('税前额必须是数字')
                            dao.before_tax_money = 0
                before_tax_money_input = ui.input(placeholder='请输入含税额', value=str(dao.before_tax_money)) \
                    .props('type="number" step="0.01" rounded-md outlined dense') \
                    .classes('w-[30%] self-center item-center ') \
                    .on_value_change(on_before_tax_change)
                before_tax_money_input.set_value(dao.before_tax_money)
                before_tax_label = ui.label('').classes('w-[40%] text-[14px] text-red font-small self-center')
            with ui.row().classes('w-[49%] place-content-start items-center gap-1'):
                ui.label('税率').classes('w-[20%] self-right text-[16px] text-[#333333] font-medium')
                def on_tax_rate_change(value):
                    if value == '1%':
                        dao.tax_rate = 0.01
                    elif value == '3%':
                        dao.tax_rate = 0.03
                    elif value == '6%':
                        dao.tax_rate = 0.06
                    elif value == '9%':
                        dao.tax_rate = 0.09
                    elif value == '13%':
                        dao.tax_rate = 0.13
                    add_tax = round(dao.before_tax_money / (1 + dao.tax_rate) * dao.tax_rate, 2) if dao.tax_rate else 0
                    if add_tax_input is not None:
                        add_tax_input.set_value(add_tax)
                    invoice_money = round(dao.before_tax_money / (1 + dao.tax_rate), 2)
                    if invoice_money_input is not None:
                        invoice_money_input.set_value(invoice_money)
                tax_rate_select = inputs.selection_w40(['1%','3%','6%','9%','13%'], '3%', on_change=on_tax_rate_change)
                if is_add:
                    dao.tax_rate = 0.03  # 默认税率为0.03
                else:
                    if dao.tax_rate == 0.01:
                        tax_rate_select.set_value('1%')
                    elif dao.tax_rate == 0.03:
                        tax_rate_select.set_value('3%')
                    elif dao.tax_rate == 0.06:
                        tax_rate_select.set_value('6%')
                    elif dao.tax_rate == 0.09:
                        tax_rate_select.set_value('9%')
                    elif dao.tax_rate == 0.13:
                        tax_rate_select.set_value('13%')
        with ui.row().classes('w-full place-content-between items-center'):
            with ui.row().classes('w-[49%] place-content-start items-center gap-1'):
                ui.label('增值税').classes('w-[20%] self-right text-[16px] text-[#333333] font-medium')
                add_tax_input = ui.input(placeholder='请输入增值税', value = str(dao.added_tax)) \
                    .props('type="number" step="0.01" rounded-md outlined dense') \
                    .classes('w-[30%] self-center item-center ') \
                    .bind_value_from(dao, 'added_tax') \
                    .bind_value_to(dao, 'added_tax')
            with ui.row().classes('w-[49%] place-content-start items-center gap-1'):
                ui.label('税前额').classes('w-[20%] self-right text-[16px] text-[#333333] font-medium')
                invoice_money_input = ui.input(placeholder='请输入税前额', value=str(dao.invoice_money)) \
                    .props('type="number" step="0.01" rounded-md outlined dense') \
                    .classes('w-[30%] self-center item-center ') \
                    .bind_value_from(dao, 'invoice_money') \
                    .bind_value_to(dao, 'invoice_money')
        with ui.row().classes('w-full place-content-between items-center'):
            with ui.row().classes('w-[49%] place-content-start items-center gap-1'):
                ui.label('合同内容').classes('w-[20%] self-right text-[16px] text-[#333333] font-medium')
                contract_content_input = ui.input(placeholder='请输入合同内容', value=dao.contract_content) \
                    .props('rounded-md outlined dense') \
                    .classes('w-[30%] self-center item-center ') \
                    .bind_value_from(dao, 'contract_content') \
                    .bind_value_to(dao, 'contract_content')
            with ui.row().classes('w-[49%] place-content-start items-center gap-1'):
                ui.label('状态').classes('w-[20%] self-right text-[16px] text-[#333333] font-medium')
                status_select = inputs.selection_w40(['未开票','已开票'], '未开票', on_change=lambda value: setattr(dao, 'status', 0 if value == '未开票' else 1))
                if is_add:
                    dao.status = 0  # 默认状态为未开票
                else:
                    if dao.status == 0:
                        status_select.set_value('未开票')
                    else:
                        status_select.set_value('已开票')
        if not is_add:
            with ui.row().classes('w-[49%] place-content-start items-center gap-1'):
                ui.label('开票时间').classes('w-[20%] self-right text-[16px] text-[#333333] font-medium')
                date_input = inputs.date_input_w40('开票时间', lambda e: setattr(dao, 'invoice_time', e.value))
                date_input.bind_value_from(dao, 'invoice_time')
        with ui.row().classes('w-full place-content-end'):         
            ui.button('取消', color=None, on_click=dialog.close) \
                .props('flat') \
                .classes('w-[120px] text-[16px] text-[#888888] font-[400]') \
                .style('background-color: #FFFFFF !important;border-radius: 10px;border: 1px solid #888888;')
            def on_create():
                if dao.to_company_id == "" or dao.invoice_content == "" or dao.before_tax_money <= 0 or dao.invoice_money <= 0:
                    ui.notify('受票方,发票内容,税前额,开票额不能为空')
                    return
                if is_add:
                    dao.create_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    result, _ = g.my_db.add_invoice_record(dao.to_db())
                    if result:
                        # 更新服务记录的开票金额
                        g.update_contract_invoice_money(dao.contract_id, dao.before_tax_money)
                        ui.notify('添加开票信息成功')
                        on_search()
                    else:
                        ui.notify('添加开票信息失败')
                else:
                    result = g.my_db.update_invoice_record(dao.to_db(), {'id': dao.id})
                    if not result:
                        ui.notify('更新开票记录失败')
                        return
                    # 更新服务记录的开票金额
                    if old_before_tax_money != dao.before_tax_money:
                        gap_money = dao.before_tax_money - old_before_tax_money
                        g.update_contract_invoice_money(dao.contract_id, gap_money)
                    ui.notify('修改开票信息成功')
                    on_search()
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
    if 'invoice_record_table' not in app.storage.client:
        ui.notify('请先查询开票记录')
        return
    selection = app.storage.client['invoice_record_table'].selected
    if not selection:
        ui.notify('请选择要删除的开票记录')
        return
    ids = [item['id'] for item in selection]
    if not ids:
        ui.notify('没有选中任何开票记录')
        return
    del_by_ids(ids)
    

def delete_one(e: events.GenericEventArguments):
    id = e.args['id']
    del_by_ids([id])

def del_by_ids(ids: list[str]) -> None:
    if ids is None or len(ids) == 0:
        ui.notify('请选择要删除的开票记录')
        return
    def make_delete():
        delok = True
        for id in ids:
            if id is None or len(id) == 0:
                continue
            result = g.my_db.delete_invoice_record(id)
            if result is False:
                delok = False
                ui.notify(f'删除开票记录失败: {id}')
                return
        if delok is True:
            ui.notify('删除开票记录成功')
            on_search()

    dialogs.make_sure_dialog('确认要进行删除操作?', on_ok=make_delete)
    