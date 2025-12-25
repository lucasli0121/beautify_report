from datetime import datetime
from typing import Any
from nicegui import app, ui
from dao.company_dao import CompanyDao
from dao.service_record_dao import ServiceRecordDao
from mq.mq_impl import MqImpl
from db.mydb import MyDb
mq_impl = MqImpl()
my_db = MyDb()

def create_mq() -> bool:
    if mq_impl.connect() is False:
        return False
    mq_impl.loop_for_thread()
    return True

def subscribe_online_topic(mac: str, handle_online_func) -> bool:
    return mq_impl.subscribe(f'hjy-dev/device/heart_beat/{mac.lower()}', handle_online_func)
def unsubscribe_online_topic(mac: str) -> bool:
    return mq_impl.unsubscribe(f'hjy-dev/device/heart_beat/{mac.lower()}')
def subscribe_event_topic(mac: str, handle_event_func) -> bool:
    return mq_impl.subscribe(f'server-h03/study/event/{mac.lower()}', handle_event_func)
def subscribe_attr_topic(mac: str, handle_attr_func) -> bool:
    return mq_impl.subscribe(f'server-t1/study/attr/{mac.lower()}', handle_attr_func)
def unsubscribe_event_topic(mac: str):
    mq_impl.unsubscribe(f'server-h03/study/event/{mac.lower()}')
def unsubscribe_attr_topic(mac: str):
    mq_impl.unsubscribe(f'server-t1/study/attr/{mac.lower()}')


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
    service_dao.invoice_money += invoice_money
    if service_dao.invoice_money > service_dao.payment_money:
        service_dao.status = 2 # 更新状态为待付款
    if service_dao.invoice_money < service_dao.payment_money:
        service_dao.status = 3 # 更新状态为待开票
    if service_dao.invoice_money == service_dao.contract_money and service_dao.payment_money == service_dao.contract_money:
        service_dao.status = 4 # 更新状态为完成
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
    service_dao.payment_money += payment_money
    if service_dao.payment_money > service_dao.invoice_money:
        service_dao.status = 3 # 更新状态为待付款
    if service_dao.payment_money < service_dao.invoice_money:
        service_dao.status = 2 # 更新状态为待开票
    if service_dao.payment_money == service_dao.contract_money and service_dao.invoice_money == service_dao.contract_money:
        service_dao.status = 4 # 更新状态为完成
    service_dao.latest_payment_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return my_db.update_service_record(service_dao.to_db(), {})