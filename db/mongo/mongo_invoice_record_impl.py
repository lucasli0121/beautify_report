'''
Author: liguoqiang
Date: 2021-08-06 14:10:41
LastEditors: liguoqiang
LastEditTime: 2025-09-18 19:35:46
Description: 
'''
# coding="utf8"

from pymongo.collection import Collection
import logging
from typing import Any
from bson.objectid import ObjectId
from dao.invoice_record_dao import InvoiceRecordDao
from db.mongo.mongo_impl import MongoImpl

class MongoInvoiceRecordImpl():
    def __init__(self, mongo_impl: MongoImpl):
        super().__init__()
        self.logger = logging.getLogger(__name__)
        self.mongo_impl = mongo_impl


    # 开票记录表名
    def invoice_record_tbl(self) -> None|Collection:
        if self.mongo_impl.db is None:
            self.logger.error("MongoDB connection is not established.")
            return None
        return self.mongo_impl.db['invoice_record_tbl']
    
    
    """
    添加开票记录
    :param data: 开票记录信息字典
    :return: 成功返回True，否则返回False
    """
    def add(self, data: dict[str, Any]) -> tuple[bool, str|None]:
        tbl_name = self.invoice_record_tbl()
        if tbl_name is None:
            self.logger.error("invoice table not found in MongoDB.")
            return False, None
        return self.mongo_impl.add(tbl_name, data)
        
    """ 
    更新开票记录信息到数据库
    :param data: 开票记录字典
    :param condition: 更新条件，例如 "id = 1"
    :return: 成功返回True，否则返回False
    """
    def update(self, data: dict[str, Any], condition: dict[str, Any]) -> bool:
        tbl_name = self.invoice_record_tbl()
        if tbl_name is None:
            self.logger.error("invoice table not found in MongoDB.")
            return False
        return self.mongo_impl.update(tbl_name, data, condition)
        
    """
    查询开票记录信息
    :param condition: 查询条件，例如 "id = 1"
    :return: 查询结果列表，每个元素是一个字典，包含公司信息
    """
    def query_all(self, from_company_id: str, to_company_id: str, invoice_content: str, invoice_number: str, status: int, begin_time: str, end_time: str) -> tuple[bool, Any|None]:
        tbl_name = self.invoice_record_tbl()
        if tbl_name is None:
            self.logger.error("invoice table not found in MongoDB.")
            return False, None
        query = {}
        if from_company_id or len(from_company_id) > 0:
            query['from_company_id'] = {'$eq': from_company_id}
        if to_company_id or len(to_company_id) > 0:
            query['to_company_id'] = {'$eq': to_company_id}
        if invoice_content or len(invoice_content) > 0:
            query['invoice_content'] = {'$regex': invoice_content, '$options': 'i'}
        if invoice_number or len(invoice_number) > 0:
            query['invoice_number'] = {'$eq': invoice_number}
        if status >= 0:
            query['status'] = {'$eq': status}
        if begin_time or len(begin_time) > 0:
            query['create_time'] = {'$gte': begin_time}
        if end_time or len(end_time) > 0:
            if 'create_time' in query:
                query['create_time']['$lte'] = end_time
            else:
                query['create_time'] = {'$lte': end_time}
        # 执行查询
        return self.mongo_impl.query_by_condition(tbl_name, query, {'invoice_time': -1})
    
    """
    查询开票记录信息
    :param condition: 查询条件，例如 "id = 1"
    :return: 查询结果列表，每个元素是一个字典，包含公司信息
    """
    def query_by_invoice_time(self, from_company_id: str, to_company_id: str, invoice_content: str, begin_invoice_time: str, end_invoice_time: str) -> tuple[bool, Any|None]:
        tbl_name = self.invoice_record_tbl()
        if tbl_name is None:
            self.logger.error("invoice table not found in MongoDB.")
            return False, None
        query = {}
        if from_company_id or len(from_company_id) > 0:
            query['from_company_id'] = {'$eq': from_company_id}
        if to_company_id or len(to_company_id) > 0:
            query['to_company_id'] = {'$eq': to_company_id}
        # if invoice_content or len(invoice_content) > 0:
        #     query['invoice_content'] = {'$regex': invoice_content, '$options': 'i'}
        if begin_invoice_time or len(begin_invoice_time) > 0:
            query['invoice_time'] = {'$gte': begin_invoice_time}
        if end_invoice_time or len(end_invoice_time) > 0:
            if 'invoice_time' in query:
                query['invoice_time']['$lte'] = end_invoice_time
            else:
                query['invoice_time'] = {'$lte': end_invoice_time}
        # 执行查询
        return self.mongo_impl.query_by_condition(tbl_name, query, {'invoice_time': -1})
    
    def query_by_number(self, invoice_number: str) -> tuple[bool, Any|None]:
        tbl_name = self.invoice_record_tbl()
        if tbl_name is None:
            self.logger.error("invoice table not found in MongoDB.")
            return False, None
        query = {}
        if invoice_number or len(invoice_number) > 0:
            query['invoice_number'] = {'$eq': invoice_number}
        # 执行查询
        return self.mongo_impl.query_by_condition(tbl_name, query, {'invoice_time': -1})
    """
    function:
    description: 从服务器查询信息
    param {*} course
    return {*}
    """
    def query_by_id(self, id: str) -> tuple[bool, InvoiceRecordDao|None]:
        tbl_name = self.invoice_record_tbl()
        if tbl_name is None:
            self.logger.error("Company table not found in MongoDB.")
            return False, None
        if id is None or len(id) == 0:
            return False, None
        query = {'_id': ObjectId(id)}
        result, value = self.mongo_impl.query_by_condition(tbl_name, query, None)
        if not result or value is None:
            self.logger.error("No invoice record found with the given ID.")
            return False, None
        dao = InvoiceRecordDao()
        dao.from_db(value[0])
        return True, dao
    """
    function: query_by_contract_id
    description: 根据合同ID从服务器查询信息
    param {*} contract_id
    return {*}
    """
    def query_by_contract_id(self, contract_id: str) -> tuple[bool, list[Any]|None]:
        tbl_name = self.invoice_record_tbl()
        if tbl_name is None:
            self.logger.error("Company table not found in MongoDB.")
            return False, None
        if contract_id is None or len(contract_id) == 0:
            return False, None
        query = {'contract_id': contract_id}
        return self.mongo_impl.query_by_condition(tbl_name, query, {'invoice_time': -1})
    
    """
    function:
    description: 删除信息
    param {*} self
    return {*}
    """
    def delete(self, id: str) -> bool:
        tbl_name = self.invoice_record_tbl()
        if tbl_name is None:
            self.logger.error("Invoice table not found in MongoDB.")
            return False
        query = {'_id': ObjectId(id)}
        return self.mongo_impl.delete(tbl_name, query)
    
    """
    function: summary_input_added_tax_by_month
    description: 汇总某公司某月的进项增值税信息
    param {*} company_id
    param {*} record_month
    return {*}
    """
    def summary_input_added_tax_by_month(self, company_id: str, record_month: str) -> tuple[bool, dict[str, Any]|None]:
        tbl_name = self.invoice_record_tbl()
        if tbl_name is None:
            self.logger.error("Invoice table not found in MongoDB.")
            return False, None
        match_stage = {
            '$match': {
                'to_company_id': company_id,
                'invoice_type': 1,
                '$expr': {
                    '$eq': [{'$substrBytes': ['$invoice_time', 0, 7]}, record_month]
                }
            }
        }
        group_stage = {
            '$group': {
                '_id': {'$substrBytes': ['$invoice_time', 0, 7] },
                'total_added_tax': {'$sum': '$added_tax'},
                'total_before_tax_money': {'$sum': '$before_tax_money'},
                'total_invoice_money': {'$sum': '$invoice_money'}
            }
        }
        pipeline = [match_stage, group_stage]
        value = list(tbl_name.aggregate(pipeline))
        if not value:
            self.logger.info("No invoice records found for the given company and month.")
            return True, {
                'total_added_tax': 0.0,
                'total_before_tax_money': 0.0,
                'total_invoice_money': 0.0
            }
        summary = value[0]
        return True, {
            'total_added_tax': summary.get('total_added_tax', 0.0),
            'total_before_tax_money': summary.get('total_before_tax_money', 0.0),
            'total_invoice_money': summary.get('total_invoice_money', 0.0)
        }
    
    """
    function: summary_output_added_tax_by_month
    description: 汇总某公司某月的销项增值税信息
    param {*} company_id
    param {*} record_month
    return {*}
    """
    def summary_output_added_tax_by_month(self, company_id: str, record_month: str) -> tuple[bool, dict[str, Any]|None]:
        tbl_name = self.invoice_record_tbl()
        if tbl_name is None:
            self.logger.error("Invoice table not found in MongoDB.")
            return False, None
        match_stage = {
            '$match': {
                'from_company_id': company_id,
                # 'invoice_type': 1, # 销项发票 销售出去的票都要统计
                '$expr': {
                    '$eq': [{'$substrBytes': ['$invoice_time', 0, 7]}, record_month]
                }
            }
        }
        group_stage = {
            '$group': {
                '_id': {'$substrBytes': ['$invoice_time', 0, 7] },
                'total_added_tax': {'$sum': '$added_tax'},
                'total_before_tax_money': {'$sum': '$before_tax_money'},
                'total_invoice_money': {'$sum': '$invoice_money'}
            }
        }
        pipeline = [match_stage, group_stage]
        value = list(tbl_name.aggregate(pipeline))
        if not value:
            self.logger.info("No invoice records found for the given company and month.")
            return True, {
                'total_added_tax': 0.0,
                'total_before_tax_money': 0.0,
                'total_invoice_money': 0.0
            }
        summary = value[0]
        return True, {
            'total_added_tax': summary.get('total_added_tax', 0.0),
            'total_before_tax_money': summary.get('total_before_tax_money', 0.0),
            'total_invoice_money': summary.get('total_invoice_money', 0.0)
        }
