from datetime import datetime
from typing import Any
from nicegui import app, ui,run
from dao.company_dao import CompanyDao
from dao.recognize_info_dao import RecognizeInfoDao
from dao.service_record_dao import ServiceRecordDao, ServiceStatus
from utils import ocr_manager as ocr_mgr
from db.mydb import MyDb
my_db = MyDb()
ocr_mgr = ocr_mgr.OcrManager()

def validate_input_float(value, input_component:ui.input) -> None:
    if value is None or len(str(value).strip()) == 0:
        return
    try:
        num = float(value)
    except ValueError:
        ui.notify('格式不正确,请输入有效的数字')

"""
# @function format_currency
# @description 格式化货币值，保留两位小数并添加千分位符
# @param value 货币值
# @return 格式化后的字符串
"""
def format_currency(value: float) -> str:
    return '{:,.2f}'.format(value)

"""
# @function show_refresh_process
# @description 显示刷新过程的对话框
# @param msg 提示信息
# @return 对话框对象
"""
def show_refresh_process(msg: str) -> ui.dialog:
    with ui.dialog().props('persistent') as dialog, ui.card().classes('') \
        .style('background-color: #FFFFFF !important; border-radius: 10px;'):
        with ui.row().classes('w-full mt-2 place-content-center items-center gap-1'):
            ui.label('提示:').classes(' text-[18px] text-[#333333] font-medium')
            ui.label(msg).classes('text-[16px] text-[#333333] font-normal')
            ui.spinner('dots', size='20px', color='red').classes('w-[20px] h-[20px]')
    dialog.open()
    return dialog

def query_company_name_company() -> tuple[bool, dict[str, CompanyDao]]:
    result, list_values = my_db.query_all_company('','','','')
    if result is False:
        return False, {}
    company_info = {}
    company_info['所有'] = CompanyDao()
    if result and list_values is not None:
        for item in list_values:
            company = CompanyDao()
            company.from_db(item)
            company_info[company.brief_name] = company
    return True, company_info

"""
# @function add_out_company
# @description 添加外部公司信息
# @param onComplete 添加完成后的回调函数
# @return None
"""
def add_out_company(onComplete) -> None:
    """
    添加外部公司信息
    :param data: 外部公司信息字典
    :return: 成功返回True，否则返回False
    """
    company_dao = CompanyDao()
    with ui.dialog().props('persistent') as dialog, ui.card().classes('w-1/2') \
        .style('background-color: #FFFFFF !important; border-radius: 10px;'):
        ui.label('创建外部公司').classes('w-full text-[20px] text-[#333333] font-medium')
        with ui.row().classes('w-full mt-5 place-content-start items-center'):
            ui.label('名称').classes('w-[20%] text-[16px] text-[#333333] font-medium')
            ui.input(placeholder='请输入公司名称') \
                .props('rounded-md outlined dense') \
                .classes('w-[70%] self-center item-center ') \
                .bind_value_to(company_dao, 'name')
        with ui.row().classes('w-full place-content-start items-center'):
            ui.label('简称').classes('w-[20%] text-[16px] text-[#333333] font-medium')
            ui.input(placeholder='请输入公司简称') \
                .props('rounded-md outlined dense') \
                .classes('w-[30%] self-center item-center ') \
                .bind_value_to(company_dao, 'brief_name')
        with ui.row().classes('w-full place-content-start items-center'):
            ui.label('地址').classes('w-[20%] text-[16px] text-[#333333] font-medium')
            ui.input(placeholder='请输入公司地址') \
                .props('rounded-md outlined dense') \
                .classes('w-[70%] self-center item-center ') \
                .bind_value_to(company_dao, 'address')
        with ui.row().classes('w-full place-content-start items-center'):
            ui.label('信用代码').classes('w-[20%] text-[16px] text-[#333333] font-medium')
            ui.input(placeholder='请输入统一信用代码') \
                .props('rounded-md outlined dense') \
                .classes('w-[30%] self-center item-center ') \
                .bind_value_to(company_dao, 'tax_no')
        with ui.row().classes('w-full place-content-end'):
            ui.button('取消', color=None, on_click=dialog.close) \
                .props('flat') \
                .classes('w-[120px] text-[16px] text-[#888888] font-[400]') \
                .style('background-color: #FFFFFF !important;border-radius: 10px;border: 1px solid #888888;')
            def on_create_company():
                if company_dao.name == "" or company_dao.brief_name == "" or company_dao.address == "" :
                    ui.notify('公司名称,简称,地址不能为空')
                    return
                company_dao.type = 2 # 外部公司
                data = company_dao.to_db()
                result, values = my_db.query_same_company(data['name'], data['brief_name'])
                if result and values and len(values) > 0:
                    ui.notify('公司名称或简称已存在，请修改后再试')
                    return
                result, id = my_db.add_company(data)
                if result is True:
                    company_dao.id = str(id)
                    ui.notify('添加外部公司成功')
                    dialog.close()
                    if onComplete is not None:
                        onComplete(company_dao)
                else:
                    ui.notify('添加公司失败')
            ui.button('确定', color=None, on_click=on_create_company) \
                .props('flat') \
                .classes('w-[120px] text-[16px] text-white font-[400]') \
                .style('background-color: #65B6FF !important; border-radius: 10px')
        dialog.open()
#
# 查询服务记录的合同名称字典
# 返回的字典以合同名称为键，ServiceRecordDao对象为值
# from_company_id: 发起方公司ID
# to_company_id: 接收方公司ID
# 返回: (查询成功与否, {合同名称: ServiceRecordDao对象})
#
def query_service_name_dict(from_company_id: str, to_company_id: str) -> tuple[bool, dict[str, ServiceRecordDao]]:
    result, value_list = my_db.query_all_service_record(from_company_id, to_company_id, 0, '', '')
    if result is False or value_list is None:
        return False, {}
    service_name_dict = {}
    for item in value_list:
        dao = ServiceRecordDao()
        dao.from_db(item)
        service_name_dict[dao.contract_name] = dao
    return True, service_name_dict

#
# 更新合同的开票金额
# contract_id: 合同ID
# invoice_money: 要增加的开票金额
# 返回: 成功返回True，否则返回False
#
def update_contract_invoice_money(contract_id: str, invoice_money: float) -> bool:
    result, service_dao = my_db.query_service_record_by_id(contract_id)
    if not result or service_dao is None:
        return False
    return update_contract_invoice_money_using_service_dao(service_dao, invoice_money)

def update_contract_invoice_money_using_service_dao(service_dao: ServiceRecordDao, invoice_money: float) -> bool:
    service_dao.invoice_money += invoice_money
    if service_dao.invoice_money > service_dao.payment_money:
        service_dao.status = ServiceStatus.WaitPayment.value # 更新状态为待付款
    if service_dao.invoice_money < service_dao.payment_money:
        service_dao.status = ServiceStatus.WaitInvoice.value # 更新状态为待开票
    if service_dao.invoice_money == service_dao.contract_money and service_dao.payment_money == service_dao.contract_money:
        service_dao.status = ServiceStatus.Finished.value # 更新状态为完成
    else:
        if service_dao.is_contract == 0:
            service_dao.status = ServiceStatus.NotContract.value # 更新状态为无合同
        else:
            service_dao.status = ServiceStatus.NotFinished.value # 更新状态为未完成
    service_dao.latest_invoice_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return my_db.update_service_record(service_dao.to_db(), {})

#
# 更新合同的付款金额
# contract_id: 合同ID
# invoice_money: 要增加的开票金额
# 返回: 成功返回True，否则返回False
#
def update_contract_payment_money(contract_id: str, payment_money: float) -> bool:
    result, service_dao = my_db.query_service_record_by_id(contract_id)
    if not result or service_dao is None:
        return False
    return update_contract_payment_money_using_service_dao(service_dao, payment_money)

def update_contract_payment_money_using_service_dao(service_dao: ServiceRecordDao, payment_money: float) -> bool:
    service_dao.payment_money += payment_money
    if service_dao.payment_money > service_dao.invoice_money:
        service_dao.status = ServiceStatus.WaitInvoice.value # 更新状态为待开票
    if service_dao.payment_money < service_dao.invoice_money:
        service_dao.status = ServiceStatus.WaitPayment.value # 更新状态为待付款
    if service_dao.payment_money == service_dao.contract_money and service_dao.invoice_money == service_dao.contract_money:
        service_dao.status = ServiceStatus.Finished.value # 更新状态为完成
    else:
        if service_dao.is_contract == 0:
            service_dao.status = ServiceStatus.NotContract.value # 更新状态为无合同
        else:
            service_dao.status = ServiceStatus.NotFinished.value # 更新状态为未完成
    service_dao.latest_payment_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return my_db.update_service_record(service_dao.to_db(), {})

"""
# @function show_recognize_info_dialog
# @description 显示识别信息对话框
# @param recognize_type 识别类型
# @return None
"""
async def show_recognize_info_dialog(recognize_type: int) -> None:
    def on_refresh() ->list[dict[str, Any]]:
        rows: list[dict[str, Any]] = []
        res, values = my_db.query_all_recognize_info(recognize_type)
        if res and values is not None:
            for item in values:
                dao = RecognizeInfoDao()
                dao.from_db(item)
                row_dict: dict[str, Any] = {}
                row_dict['file_name'] = dao.file_name
                if dao.type == 1:
                    row_dict['type'] = '发票'
                else:
                    row_dict['type'] = '完税证明'
                if dao.result == -1:
                    row_dict['result'] = '识别失败'
                elif dao.result == 0:
                    row_dict['result'] = '识别中'
                elif dao.result == 1:
                    row_dict['result'] = '识别成功'
                else:
                    row_dict['result'] = '待识别'
                row_dict['msg'] = dao.msg
                row_dict['create_time'] = dao.create_time
                rows.append(row_dict)
        return rows
    refresh_dialog = show_refresh_process("正在读取，请稍候")
    rows = await run.io_bound(on_refresh)
    refresh_dialog.close()
    errmsg_label = None
    with ui.dialog().props('persistent') as dialog, ui.card() \
        .style('background-color: #FFFFFF !important; border-radius: 10px; width: 60%; max-width: 60%; height: 60%; max-height: 60%;'):
        with ui.column().classes('w-full h-full place-content-center items-center '):
            with ui.row().classes('w-full h-[80%] place-content-center items-center'):
                async def on_grid_row_click(e) -> None:
                    r = await grid.get_selected_row()
                    # msg = e.args['data'].get('msg', '')
                    if r:
                        result = r.get('result', '')
                        msg = r.get('msg', '')
                        if errmsg_label is not None:
                            errmsg_label.classes.clear()
                            if result == '识别成功':
                                errmsg_label.classes.append('w-full text-[12px] text-[#000000] font-small')
                            elif result == '识别中':
                                errmsg_label.classes.append('w-full text-[12px] text-[#000000] font-small')
                            else:
                                errmsg_label.classes('w-full text-[12px] text-[#FF0000] font-small')
                            errmsg_label.set_text(msg)
                grid = ui.aggrid({
                    'columnDefs': [
                        {'headerName': '文件名', 'field': 'file_name'},
                        {'headerName': '类别', 'field': 'type', 'cellClassRules': {
                            'text-blue-300': 'x == "发票"',
                            'text-green-300': 'x == "完税证明"',
                        }},
                        {'headerName': '识别结果', 'field': 'result', 'cellClassRules': {
                            'text-gray-300': 'x == "识别失败"',
                            'text-green-300': 'x == "识别中"',
                            'text-blue-300': 'x == "识别成功"',
                        }},
                        {'headerName': '错误信息', 'field': 'msg'},
                        {'headerName': '时间', 'field': 'create_time'}
                    ],
                    'rowData': [
                    ],
                    'rowSelection': {'mode': 'singleRow', 'enableClickSelection': 'true'}
                }).classes('w-full h-full').on('rowSelected', on_grid_row_click)
            grid.options['rowData'].clear()
            grid.options['rowData'] = rows
                    # grid.run_grid_method('ensureIndexVisible', len(grid.options['rowData']) - 1)
            with ui.row().classes('w-full h-[9%] place-content-center items-center'):
                errmsg_label = ui.label('').classes('w-full text-[12px] text-[#FF0000] font-small')
            with ui.row().classes('w-full h-[9%] place-content-center items-center'):
                ui.button('关闭', on_click=lambda: dialog.close()).classes('w-30')
        dialog.open()