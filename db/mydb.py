'''
Author: liguoqiang
Date: 2021-08-06 14:10:41
LastEditors: liguoqiang
LastEditTime: 2025-09-18 15:52:07
Description: mydb 类，数据库代理类，根据配置文件选择数据库实现类
    包括mysql, mongo
'''
# coding="utf8"

from datetime import datetime
from typing import Any, Optional
from configparser import ConfigParser, NoSectionError
import logging
from dao.payment_record_dao import PaymentRecordDao
from dao.period_data_dao import PeriodDataDao
from dao.recognize_info_dao import RecognizeInfoDao
from dao.service_record_dao import ServiceRecordDao
from dao.value_added_dao import ValueAddedDao
from db.mongo.mongo_impl import MongoImpl
from db.mongo.mongo_invoice_alarm_impl import MongoInvoiceAlarmImpl
from db.mongo.mongo_invoice_title_impl import MongoInvoiceTitleImpl
from db.mongo.mongo_period_data_impl import MongoPeriodDataImpl
from db.mongo.mongo_recognize_info_impl import MongoRecognizeInfoImpl
from db.mongo.mongo_value_added_impl import MongoValueAddedImpl
from db.mysql.mysql_db import MySqlImpl
from db.mongo.mongo_company_impl import MongoCompanyImpl
from db.mongo.mongo_invoice_record_impl import MongoInvoiceRecordImpl
from db.mongo.mongo_payment_record_impl import MongoPaymentRecordImpl
from db.mongo.mongo_service_record_impl import MongoServiceRecordImpl
from db.mongo.mongo_tax_approval_impl import MongoTaxApprovalImpl
from db.mysql.mysql_company_impl import MySqlCompanyImpl
from dao.company_dao import CompanyDao
from dao.company_bank_account_dao import CompanyBankAccountDao
from dao.tax_approval_dao import TaxApprovalDao

class MyDb:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        cp = ConfigParser()
        cp.read("cfg/beautify_report.cfg")
        self.mongo = None
        self.mysql = None
        try:
            self.enable_mysql = cp.get("default", "mysql_enable")
            self.enable_mongo = cp.get("default", "mongo_enable")
            if self.enable_mysql == "true":
                self.mysql = MySqlImpl()
            if self.enable_mongo == "true":
                self.mongo = MongoImpl()
        except NoSectionError as err:
            self.logger.error("not find section:", err.message)
        
    def __del__(self):
        if self.mongo is not None:
            del self.mongo
        if self.mysql is not None:
            del self.mysql
            
    '''
    function: add_company
    description: 添加公司信息
    param {*} self
    param {*} d
    return {*}
    '''    
    def add_company(self, d: dict[str, Any]) -> tuple[bool, str|None]:
        if self.mysql is not None:
            return False, None
        else:
            if self.mongo is not None:
                return MongoCompanyImpl(self.mongo).add_company(d)
        self.logger.error("No database implementation available for adding company.")
        return False, None
    
    def query_same_company(self, name: str, brief_name: str) -> tuple[bool, None|list[Any]]:
        if self.mysql is not None:
            return False, None
        else:
            if self.mongo is not None:
                return MongoCompanyImpl(self.mongo).query_same_company(name, brief_name)
        self.logger.error("No database implementation available for querying same company.")
        return False, None
    '''
    function: update_company
    description: 更新公司信息
    param {*} self
    param {*} d
    return {*}
    '''    
    def update_company(self, d: dict[str, Any], condition: dict[str, Any]) -> bool:
        if self.mysql is not None:
            mysql_condition = ''
            if id in condition:
                # 如果condition中有id字段，则使用id作为更新条件
                # condition = f"id = {condition['id']}"
                mysql_condition = f"id = {condition['id']}"
            return MySqlCompanyImpl(self.mysql).update_company(d, mysql_condition)
        else:
            if self.mongo is not None:
                return MongoCompanyImpl(self.mongo).update_company(d, condition)
        self.logger.error("No database implementation available for updating company.")
        return False
    
    def query_all_company(self, name: str, address: str, contacts: str, company_type: str, belongs_to: str, type: int = -1) -> tuple[bool, None|list[Any]]:
        if self.mysql is not None:
            return MySqlCompanyImpl(self.mysql).query_all_company(name, address, contacts)
        else:
            if self.mongo is not None:
                return MongoCompanyImpl(self.mongo).query_all_company(name, address, contacts, company_type, belongs_to, type)
        self.logger.error("No database implementation available for querying company.")
        return False, None
    def query_inner_company(self, name: str, address: str, contacts: str, company_type: str) -> tuple[bool, None|list[Any]]:
        if self.mysql is not None:
            return MySqlCompanyImpl(self.mysql).query_all_company(name, address, contacts)
        else:
            if self.mongo is not None:
                return MongoCompanyImpl(self.mongo).query_inner_company(name, address, contacts, company_type)
        self.logger.error("No database implementation available for querying company.")
        return False, None
    
    def query_company_by_id(self, id: str) -> tuple[bool, CompanyDao|None]:
        if self.mysql is not None:
            return MySqlCompanyImpl(self.mysql).query_company_by_id(int(id))
        else:
            if self.mongo is not None:
                return MongoCompanyImpl(self.mongo).query_company_by_id(id)
        self.logger.error("No database implementation available for querying company by id.")
        return False, None

    def query_companies_by_ids(self, ids: list[str]) -> tuple[bool, dict[str, CompanyDao]|None]:
        """
        批量根据公司ID列表查询公司信息（Facade wrapper）。

        该方法在 MyDb 层根据配置选择底层实现（Mongo 或 MySQL），
        并调用对应实现的 `query_companies_by_ids`。

        返回与底层实现一致的 (success, mapping|None)。
        """
        if self.mysql is not None:
            return False, None
        else:
            if self.mongo is not None:
                return MongoCompanyImpl(self.mongo).query_companies_by_ids(ids)
        self.logger.error("No database implementation available for querying companies by ids.")
        return False, None
    
    def query_company_by_brief_name(self, brief_name: str) -> tuple[bool, CompanyDao|None]:
        if self.mysql is not None:
            return False, None
        else:
            if self.mongo is not None:
                return MongoCompanyImpl(self.mongo).query_company_by_brief_name(brief_name)
        self.logger.error("No database implementation available for querying company by brief name.")
        return False, None
    
    def delete_company(self, id: str) -> bool:
        if self.mysql is not None:
            return MySqlCompanyImpl(self.mysql).delete_company(int(id))
        else:
            if self.mongo is not None:
                return MongoCompanyImpl(self.mongo).delete_company(id)
        self.logger.error("No database implementation available for deleting company.")
        return False
    
    def add_company_bank_account(self, d: dict[str, Any]) -> tuple[bool, str|None]:
        if self.mysql is not None:
            return False, None
        else:
            if self.mongo is not None:
                return MongoCompanyImpl(self.mongo).add_company_bank_account(d)
        self.logger.error("No database implementation available for adding company bank account.")
        return False, None
    def update_company_bank_account(self, d: dict[str, Any], condition: dict[str, Any]) -> bool:
        if self.mysql is not None:
            return False
        else:
            if self.mongo is not None:
                return MongoCompanyImpl(self.mongo).update_company_bank_account(d, condition)
        self.logger.error("No database implementation available for updating company bank account.")
        return False
    def query_all_company_bank_account(self, company_id: str) -> tuple[bool, Any|None]:
        if self.mysql is not None:
            return False, None
        else:
            if self.mongo is not None:
                return MongoCompanyImpl(self.mongo).query_all_company_bank_account(company_id)
        self.logger.error("No database implementation available for querying company bank account.")
        return False, None
    def query_company_bank_account_by_id(self, id: str) -> tuple[bool, CompanyBankAccountDao|None]:
        if self.mysql is not None:
            return False, None
        else:
            if self.mongo is not None:
                return MongoCompanyImpl(self.mongo).query_company_bank_account_by_id(id)
        self.logger.error("No database implementation available for querying company bank account by id.")
        return False, None
    
    def delete_company_bank_account(self, id: str) -> bool:
        if self.mysql is not None:
            return False
        else:
            if self.mongo is not None:
                return MongoCompanyImpl(self.mongo).delete_company_bank_account(id)
        self.logger.error("No database implementation available for deleting company bank account.")
        return False
    def add_invoice_title(self, d: dict[str, Any]) -> tuple[bool, str|None]:
        if self.mysql is not None:
            return False, None
        else:
            if self.mongo is not None:
                return MongoInvoiceTitleImpl(self.mongo).add(d)
        self.logger.error("No database implementation available for adding invoice title.")
        return False, None
    def update_invoice_title(self, d: dict[str, Any], condition: dict[str, Any]) -> bool:
        if self.mysql is not None:
            return False
        else:
            if self.mongo is not None:
                return MongoInvoiceTitleImpl(self.mongo).update(d, condition)
        self.logger.error("No database implementation available for updating invoice title.")
        return False
    def query_invoice_title_all(self, company_id: str) -> tuple[bool, Any|None]:
        if self.mysql is not None:
            return False, None
        else:
            if self.mongo is not None:
                return MongoInvoiceTitleImpl(self.mongo).query_all(company_id)
        self.logger.error("No database implementation available for querying invoice title.")
        return False, None
    def query_invoice_title_by_id(self, id: str) -> tuple[bool, Any|None]:
        if self.mysql is not None:
            return False, None
        else:
            if self.mongo is not None:
                return MongoInvoiceTitleImpl(self.mongo).query_by_id(id)
        self.logger.error("No database implementation available for querying invoice title by id.")
        return False, None
    def delete_invoice_title(self, id: str) -> bool:
        if self.mysql is not None:
            return False
        else:
            if self.mongo is not None:
                return MongoInvoiceTitleImpl(self.mongo).delete(id)
        self.logger.error("No database implementation available for deleting invoice title.")
        return False
    ############################################################################################################
    # 开票记录相关接口
    #############################################################################################################
    """
    添加开票记录
    """
    def add_invoice_record(self, d: dict[str, Any]) -> tuple[bool, str|None]:
        if self.mysql is not None:
            return False, None
        else:
            if self.mongo is not None:
                return MongoInvoiceRecordImpl(self.mongo).add(d)
        self.logger.error("No database implementation available for adding invoice record.")
        return False, None
    def update_invoice_record(self, d: dict[str, Any], condition: dict[str, Any]) -> bool:
        if self.mysql is not None:
            return False
        else:
            if self.mongo is not None:
                return MongoInvoiceRecordImpl(self.mongo).update(d, condition)
        self.logger.error("No database implementation available for updating invoice record.")
        return False
    def query_invoice_record_by_invoice_time(self, from_company_id: str, to_company_id: str, invoice_content: str, begin_invoice_time: str, end_invoice_time: str) -> tuple[bool, Any|None]:
        if self.mysql is not None:
            return False, None
        else:
            if self.mongo is not None:
                return MongoInvoiceRecordImpl(self.mongo).query_by_invoice_time(from_company_id, to_company_id, invoice_content, begin_invoice_time, end_invoice_time)
        self.logger.error("No database implementation available for querying invoice record.")
        return False, None
    
    def query_all_invoice_record(self, from_company_id: str, to_company_id: str, invoice_content: str, invoice_number: str, status: int, begin_time: str, end_time: str, page: int = 1, page_size: int = 10) -> tuple[bool, Any|None]:
        """
        查询开票记录（带分页支持）的 Facade 方法。

        - 参数 `page` 和 `page_size` 会被传递到底层实现，期望返回 {'total','rows'} 或直接列表。
        - 该封装根据配置选择 Mongo 或 MySQL 实现并调用相应方法。
        """
        if self.mysql is not None:
            return False, None
        else:
            if self.mongo is not None:
                return MongoInvoiceRecordImpl(self.mongo).query_all(from_company_id, to_company_id, invoice_content, invoice_number, status, begin_time, end_time, page, page_size)
        self.logger.error("No database implementation available for querying invoice record.")
        return False, None
    def query_invoice_record_by_from_and_year(self, from_company_id: str, invoice_year: str) -> tuple[bool, Any|None]:
        if self.mysql is not None:
            return False, None
        else:
            if self.mongo is not None:
                return MongoInvoiceRecordImpl(self.mongo).query_by_from_and_year(from_company_id, invoice_year)
        self.logger.error("No database implementation available for querying invoice record by from company and year.")
        return False, None
    def query_invoice_record_by_id(self, id: str) -> tuple[bool, Any|None]:
        if self.mysql is not None:
            return False, None
        else:
            if self.mongo is not None:
                return MongoInvoiceRecordImpl(self.mongo).query_by_id(id)
        self.logger.error("No database implementation available for querying invoice record by id.")
        return False, None
    def query_invoice_record_by_number(self, invoice_number: str) -> tuple[bool, Any|None]:
        if self.mysql is not None:
            return False, None
        else:
            if self.mongo is not None:
                return MongoInvoiceRecordImpl(self.mongo).query_by_number(invoice_number)
        self.logger.error("No database implementation available for querying invoice record by number.")
        return False, None
    def query_invoice_record_by_contract_id(self, contract_id: str) -> tuple[bool, Any|None]:
        if self.mysql is not None:
            return False, None
        else:
            if self.mongo is not None:
                return MongoInvoiceRecordImpl(self.mongo).query_by_contract_id(contract_id)
        self.logger.error("No database implementation available for querying invoice record by contract id.")
        return False, None
    def delete_invoice_record(self, id: str) -> bool:
        if self.mysql is not None:
            return False
        else:
            if self.mongo is not None:
                return MongoInvoiceRecordImpl(self.mongo).delete(id)
        self.logger.error("No database implementation available for deleting invoice record.")
        return False
    def add_invoice_alarm(self, d: dict[str, Any]) -> tuple[bool, str|None]:
        if self.mysql is not None:
            return False, None
        else:
            if self.mongo is not None:
                return MongoInvoiceAlarmImpl(self.mongo).add(d)
        self.logger.error("No database implementation available for adding invoice alarm.")
        return False, None
    def query_all_invoice_alarm(self, company_id: str, invoice_year: str, page: int = 1, page_size: int = 10) -> tuple[bool, Any|None]:
        """
        查询开票预警（支持分页）的 Facade 方法。

        返回与底层实现一致的 (success, {'total', 'rows'}|None) 或 (False, None) 表示失败。
        """
        if self.mysql is not None:
            return False, None
        else:
            if self.mongo is not None:
                return MongoInvoiceAlarmImpl(self.mongo).query_all(company_id, invoice_year, page, page_size)
        self.logger.error("No database implementation available for querying invoice alarm.")
        return False, None
    """
        根据公司ID和年月统计进项增值税额
        :param company_id: 公司ID
        :param record_month: 统计年月，格式YYYY-MM
        :return: 成功返回True和增值税额，否则返回False和None
    """
    def summary_input_added_tax_by_month(self, company_id: str, record_month: str) -> tuple[bool, dict[str, Any]|None]:
        if self.mysql is not None:
            return False, None
        else:
            if self.mongo is not None:
                return MongoInvoiceRecordImpl(self.mongo).summary_input_added_tax_by_month(company_id, record_month)
        self.logger.error("No database implementation available for summarizing input added tax by month.")
        return False, None
    """
        根据公司ID和年月统计销项增值税额
        :param company_id: 公司ID
        :param record_month: 统计年月，格式YYYY-MM
        :return: 成功返回True和增值税额，否则返回False和None
    """
    def summary_output_added_tax_by_month(self, company_id: str, record_month: str) -> tuple[bool, dict[str, Any]|None]:
        if self.mysql is not None:
            return False, None
        else:
            if self.mongo is not None:
                return MongoInvoiceRecordImpl(self.mongo).summary_output_added_tax_by_month(company_id, record_month)
        self.logger.error("No database implementation available for summarizing output added tax by month.")
        return False, None
    
    ############################################################################################################
    # 付款记录相关接口
    #############################################################################################################
    
    """
    添加付款记录
    """
    def add_payment_record(self, d: dict[str, Any]) -> tuple[bool, str|None]:
        if self.mysql is not None:
            return False, None
        else:
            if self.mongo is not None:
                return MongoPaymentRecordImpl(self.mongo).add(d)
        self.logger.error("No database implementation available for adding payment record.")
        return False, None
    def update_payment_record(self, d: dict[str, Any], condition: dict[str, Any]) -> bool:
        if self.mysql is not None:
            return False
        else:
            if self.mongo is not None:
                return MongoPaymentRecordImpl(self.mongo).update(d, condition)
        self.logger.error("No database implementation available for updating payment record.")
        return False
    def query_all_payment_record(self, from_company_id: str, to_company_id: str, status: int, begin_time: str, end_time: str) -> tuple[bool, Any|None]:
        if self.mysql is not None:
            return False, None
        else:
            if self.mongo is not None:
                return MongoPaymentRecordImpl(self.mongo).query_all(from_company_id, to_company_id, status, begin_time, end_time)
        self.logger.error("No database implementation available for querying payment record.")
        return False, None
    def query_payment_record_by_id(self, id: str) -> tuple[bool, PaymentRecordDao|None]:
        if self.mysql is not None:
            return False, None
        else:
            if self.mongo is not None:
                return MongoPaymentRecordImpl(self.mongo).query_by_id(id)
        self.logger.error("No database implementation available for querying payment record by id.")
        return False, None
    def query_payment_record_by_contract_id(self, contract_id: str) -> tuple[bool, Any|None]:
        if self.mysql is not None:
            return False, None
        else:
            if self.mongo is not None:
                return MongoPaymentRecordImpl(self.mongo).query_by_contract_id(contract_id)
        self.logger.error("No database implementation available for querying payment record by contract id.")
        return False, None
    def delete_payment_record(self, id: str) -> bool:
        if self.mysql is not None:
            return False
        else:
            if self.mongo is not None:
                return MongoPaymentRecordImpl(self.mongo).delete(id)
        self.logger.error("No database implementation available for deleting payment record.")
        return False
    ############################################################################################################
    # 服务记录相关接口
    #############################################################################################################
    def add_service_record(self, d: dict[str, Any]) -> tuple[bool, str|None]:
        if self.mysql is not None:
            return False, None
        else:
            if self.mongo is not None:
                return MongoServiceRecordImpl(self.mongo).add(d)
        self.logger.error("No database implementation available for adding service record.")
        return False, None
    def update_service_record(self, d: dict[str, Any], condition: dict[str, Any]) -> bool:
        if self.mysql is not None:
            return False
        else:
            if self.mongo is not None:
                return MongoServiceRecordImpl(self.mongo).update(d, condition)
        self.logger.error("No database implementation available for updating service record.")
        return False
    def query_all_service_record(self, from_company_id: str, to_company_id: str, status: int, begin_time: str, end_time: str) -> tuple[bool, Any|None]:
        if self.mysql is not None:
            return False, None
        else:
            if self.mongo is not None:
                return MongoServiceRecordImpl(self.mongo).query_all(from_company_id, to_company_id, status, begin_time, end_time)
        self.logger.error("No database implementation available for querying service record.")
        return False, None
    def query_service_record_by_id(self, id: str) -> tuple[bool, ServiceRecordDao|None]:
        if self.mysql is not None:
            return False, None
        else:
            if self.mongo is not None:
                return MongoServiceRecordImpl(self.mongo).query_by_id(id)
        self.logger.error("No database implementation available for querying service record by id.")
        return False, None

    def query_service_records_by_ids(self, ids: list[str]) -> tuple[bool, dict[str, ServiceRecordDao]|None]:
        if self.mysql is not None:
            return False, None
        else:
            if self.mongo is not None:
                return MongoServiceRecordImpl(self.mongo).query_service_records_by_ids(ids)
        self.logger.error("No database implementation available for querying service records by ids.")
        return False, None
    def delete_service_record(self, id: str) -> bool:
        if self.mysql is not None:
            return False
        else:
            if self.mongo is not None:
                return MongoServiceRecordImpl(self.mongo).delete(id)
        self.logger.error("No database implementation available for deleting service record.")
        return False
    
    ############################################################################################################
    # 完税证明相关接口 
    ############################################################################################################
    """
    function: add_tax_approval
    description: 添加完税证明信息到数据库
    :param {*} self
    :param data: 完税证明信息字典
    :return: 成功返回True，否则返回False    
    """    
    def add_tax_approval(self, data: dict[str, Any]) -> tuple[bool, str|None]:
        if self.mysql is not None:
            return False, None
        else:
            if self.mongo is not None:
                return MongoTaxApprovalImpl(self.mongo).add(data)
        self.logger.error("No database implementation available for adding tax approval.")
        return False, None 
    """ 
    更新完税证明信息到数据库
    :param {*} self
    :param data: 完税证明字典
    :param condition: 更新条件，例如 "id = 1"
    :return: 成功返回True，否则返回False
    """
    def update_tax_approval(self, data: dict[str, Any], condition: dict[str, Any]) -> bool:
        if self.mysql is not None:
            return False
        else:
            if self.mongo is not None:
                return MongoTaxApprovalImpl(self.mongo).update(data, condition)
        self.logger.error("No database implementation available for updating tax approval.")
        return False
    """
    查询完税证明信息
    :param {*} self
    :param condition: 查询条件，例如 "id = 1"
    :return: 查询结果列表，每个元素是一个字典，包含公司信息
    """
    def query_all_tax_approval(self, company_id: str, approval_no: str, ori_voucher_number: str, begin_time: str, end_time: str) -> tuple[bool, Any|None]:
        if self.mysql is not None:
            return False, None
        else:
            if self.mongo is not None:
                return MongoTaxApprovalImpl(self.mongo).query_all(company_id, approval_no, ori_voucher_number, begin_time, end_time)
        self.logger.error("No database implementation available for querying tax approval.")
        return False, None
    """
    function:
    description: 从服务器查询信息
    :param {*} self
    :param id: 完税证明ID
    :return: {*}
    """
    def query_tax_approval_by_id(self, id: str) -> tuple[bool, TaxApprovalDao|None]:
        if self.mysql is not None:
            return False, None
        else:
            if self.mongo is not None:
                return MongoTaxApprovalImpl(self.mongo).query_by_id(id)
        self.logger.error("No database implementation available for querying tax approval by id.")
        return False, None
    """
    function:
    description: 从服务器查询信息
    :param {*} self
    :param period_date: 期间日期，格式YYYY-MM
    :return: {*}
    """
    def query_tax_approval_by_period_date(self, company_id: str, period_date: str) -> tuple[bool, Any|None]:
        if self.mysql is not None:
            return False, None
        else:
            if self.mongo is not None:
                return MongoTaxApprovalImpl(self.mongo).query_by_period_date(company_id, period_date)
        self.logger.error("No database implementation available for querying tax approval by period date.")
        return False, None
    """
    function:
    description: 从服务器查询信息
    :param {*} self
    :param id: 完税证明No
    :return: {*}
    """
    def query_tax_approval_by_no(self, no: str) -> tuple[bool, TaxApprovalDao|None]:
        if self.mysql is not None:
            return False, None
        else:
            if self.mongo is not None:
                return MongoTaxApprovalImpl(self.mongo).query_by_approval_no(no)
        self.logger.error("No database implementation available for querying tax approval by id.")
        return False, None
    """
    function:
    description: 删除完税证明信息
    :param {*} self
    :param id: 完税证明ID
    :return: {*}
    """
    def delete_tax_approval(self, id: str) -> bool:
        if self.mysql is not None:
            return False
        else:
            if self.mongo is not None:
                return MongoTaxApprovalImpl(self.mongo).delete(id)
        self.logger.error("No database implementation available for deleting tax approval.")
        return False
    #############################################################################################################
    # 识别信息相关接口
    #############################################################################################################
    def add_recognize_info(self, d: dict[str, Any]) -> tuple[bool, str|None]:
        if self.mysql is not None:
            return False, None
        else:
            if self.mongo is not None:
                return MongoRecognizeInfoImpl(self.mongo).add(d)
        self.logger.error("No database implementation available for adding recognize info.")
        return False, None
    
    def update_recognize_info(self, d: dict[str, Any], condition: dict[str, Any]) -> bool:
        if self.mysql is not None:
            return False
        else:
            if self.mongo is not None:
                return MongoRecognizeInfoImpl(self.mongo).update(d, condition)
        self.logger.error("No database implementation available for updating recognize info.")
        return False
    def query_all_recognize_info(self, type:int) -> tuple[bool, Any|None]:
        if self.mysql is not None:
            return False, None
        else:
            if self.mongo is not None:
                return MongoRecognizeInfoImpl(self.mongo).query_all(type)
        self.logger.error("No database implementation available for querying recognize info.")
        return False, None
    def query_recognize_info_by_id(self, id: str) -> tuple[bool, RecognizeInfoDao|None]:
        if self.mysql is not None:
            return False, None
        else:
            if self.mongo is not None:
                return MongoRecognizeInfoImpl(self.mongo).query_by_id(id)
        self.logger.error("No database implementation available for querying recognize info by id.")
        return False, None
    
    def query_recognizing_list_by_type(self, type: int) -> tuple[bool, Any|None]:
        if self.mysql is not None:
            return False, None
        else:
            if self.mongo is not None:
                return MongoRecognizeInfoImpl(self.mongo).query_recognizing_list_by_type(type)
        self.logger.error("No database implementation available for querying recognizing info.")
        return False, None
    def query_recognize_waiting_list_by_type(self, type: int) -> tuple[bool, Any|None]:
        if self.mysql is not None:
            return False, None
        else:
            if self.mongo is not None:
                return MongoRecognizeInfoImpl(self.mongo).query_waiting_list_by_type(type)
        self.logger.error("No database implementation available for querying waiting info.")
        return False, None
    def delete_recognize_info(self, id: str) -> bool:
        if self.mysql is not None:
            return False
        else:
            if self.mongo is not None:
                return MongoRecognizeInfoImpl(self.mongo).delete(id)
        self.logger.error("No database implementation available for deleting recognize info.")
        return False
    ############################################################################################################
    # 期初数据相关接口
    #############################################################################################################
    """
    获取期初数据表名
    :return: 期初数据表名
    """
    def query_all_period_data(self, company_id: str, create_time: str) -> tuple[bool, Any|None]:
        if self.mysql is not None:
            return False, None
        else:
            if self.mongo is not None:
                return MongoPeriodDataImpl(self.mongo).query_all(company_id, create_time)
        self.logger.error("No database implementation available for querying period data.")
        return False, None
    def query_period_data_by_id(self, id: str) -> tuple[bool, Any|None]:
        if self.mysql is not None:
            return False, None
        else:
            if self.mongo is not None:
                return MongoPeriodDataImpl(self.mongo).query_by_id(id)
        self.logger.error("No database implementation available for querying period data by id.")
        return False, None
    def add_period_data(self, d: dict[str, Any]) -> tuple[bool, str|None]:
        if self.mysql is not None:
            return False, None
        else:
            if self.mongo is not None:
                return MongoPeriodDataImpl(self.mongo).add(d)
        self.logger.error("No database implementation available for adding period data.")
        return False, None
    def update_period_data(self, d: dict[str, Any], condition: dict[str, Any]) -> bool:
        if self.mysql is not None:
            return False
        else:
            if self.mongo is not None:
                return MongoPeriodDataImpl(self.mongo).update(d, condition)
        self.logger.error("No database implementation available for updating period data.")
        return False
    def delete_period_data(self, id: str) -> bool:
        if self.mysql is not None:
            return False
        else:
            if self.mongo is not None:
                return MongoPeriodDataImpl(self.mongo).delete(id)
        self.logger.error("No database implementation available for deleting period data.")
        return False
    ############################################################################################################
    # 增值税相关接口
    #############################################################################################################
    """
    处理增值税数据表
    :return: 期初数据表名
    """
    def query_all_value_added(self, company_id: str, create_time: str) -> tuple[bool, Any|None]:
        if self.mysql is not None:
            return False, None
        else:
            if self.mongo is not None:
                return MongoValueAddedImpl(self.mongo).query_all(company_id, create_time)
        self.logger.error("No database implementation available for querying period data.")
        return False, None
    def query_value_added_by_id(self, id: str) -> tuple[bool, Any|None]:
        if self.mysql is not None:
            return False, None
        else:
            if self.mongo is not None:
                return MongoValueAddedImpl(self.mongo).query_by_id(id)
        self.logger.error("No database implementation available for querying value added data by id.")
        return False, None
    def add_value_added(self, d: dict[str, Any]) -> tuple[bool, str|None]:
        if self.mysql is not None:
            return False, None
        else:
            if self.mongo is not None:
                return MongoValueAddedImpl(self.mongo).add(d)
        self.logger.error("No database implementation available for adding value added data.")
        return False, None
    def update_value_added(self, d: dict[str, Any], condition: dict[str, Any]) -> bool:
        if self.mysql is not None:
            return False
        else:
            if self.mongo is not None:
                return MongoValueAddedImpl(self.mongo).update(d, condition)
        self.logger.error("No database implementation available for updating value added data.")
        return False
    def delete_value_added(self, id: str) -> bool:
        if self.mysql is not None:
            return False
        else:
            if self.mongo is not None:
                return MongoValueAddedImpl(self.mongo).delete(id)
        self.logger.error("No database implementation available for deleting value added data.")
        return False
    """
    function: handle_summary_value_added_update
    description: 进行统计增值税，并更新增值税数据库
    param {*}
    return {*}
    """
    def handle_summary_value_added_update(self, company_id: str, record_month: str) -> tuple[bool, int]:
        summary_list = self.summary_value_added(company_id, record_month)
        if summary_list is None or len(summary_list) == 0:
            return False, 0
        i = 0
        for dao in summary_list:
            if dao.id is None or len(dao.id) == 0:
                self.add_value_added(dao.to_db())
            else:
                self.update_value_added(dao.to_db(), {'id': dao.id})
            i += 1
        return True, i
    
    """
    function: summary_value_added
    description: 进行统计增值税,返回统计结果
    param {*}
    return {*}
    """
    def summary_value_added(self, company_id: str, record_month: str) -> Optional[list[ValueAddedDao]|None]:
        result, list_period = self.query_all_period_data(company_id, record_month)
        if result is False:
            return None
        if list_period is None or len(list_period) == 0:
            return None
        summary_dao_list : list[ValueAddedDao] = []
        for item in list_period:
            period_dao = PeriodDataDao()
            period_dao.from_db(item)
            #查询公司信息，判断公司是否小规模，如果小规模，则不进行增值税汇总
            result, company_dao = self.query_company_by_id(period_dao.company_id)
            if result is True and company_dao is not None:
                if company_dao.is_small_scale():
                    continue
            value_added_dao = ValueAddedDao()
            value_added_dao.company_id = period_dao.company_id
            value_added_dao.create_time = period_dao.create_time
            result, list_value = self.query_all_value_added(period_dao.company_id, period_dao.create_time)
            if result is True and list_value is not None and len(list_value) > 0:
                value_added_dao.from_db(list_value[0])
            value_added_dao.last_month_no_verify = period_dao.last_month_no_verify
            value_added_dao.last_month_stay_pay = period_dao.last_month_stay_pay
            value_added_dao.billing_amount = period_dao.billing_amount
            result, dict_input_value = self.summary_input_added_tax_by_month(period_dao.company_id, period_dao.create_time)
            if result is True and dict_input_value is not None:
                value = float(dict_input_value.get('total_added_tax', 0.0))
                value_added_dao.opened_input_tax = value
            result, dict_output_value = self.summary_output_added_tax_by_month(period_dao.company_id, period_dao.create_time)
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