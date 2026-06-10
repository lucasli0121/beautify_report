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
from dao.invoice_alarm_dao import InvoiceAlarmDao
from db.mongo.mongo_impl import MongoImpl

class MongoInvoiceAlarmImpl():
    def __init__(self, mongo_impl: MongoImpl):
        super().__init__()
        self.logger = logging.getLogger(__name__)
        self.mongo_impl = mongo_impl


    # 表名
    def invoice_alarm_tbl(self) -> None|Collection:
        if self.mongo_impl.db is None:
            self.logger.error("MongoDB connection is not established.")
            return None
        return self.mongo_impl.db['invoice_alarm_tbl']
    
    
    """
    添加记录到数据库
    :param data: 
    :return: 成功返回True，否则返回False
    """
    def add(self, data: dict[str, Any]) -> tuple[bool, str|None]:
        tbl_name = self.invoice_alarm_tbl()
        if tbl_name is None:
            self.logger.error("invoice table not found in MongoDB.")
            return False, None
        return self.mongo_impl.add(tbl_name, data)
        
    """ 
    :param data: 
    :param condition: 更新条件，例如 "id = 1"
    :return: 成功返回True，否则返回False
    """
    def update(self, data: dict[str, Any], condition: dict[str, Any]) -> bool:
        tbl_name = self.invoice_alarm_tbl()
        if tbl_name is None:
            self.logger.error("invoice table not found in MongoDB.")
            return False
        return self.mongo_impl.update(tbl_name, data, condition)
        
    """
    :param condition: 查询条件，例如 "id = 1"
    :return: 查询结果列表，每个元素是一个字典，包含公司信息
    """
    def query_all(self, company_id: str, invoice_year: str, page: int = 1, page_size: int = 10) -> tuple[bool, Any|None]:
        tbl_name = self.invoice_alarm_tbl()
        if tbl_name is None:
            self.logger.error("invoice table not found in MongoDB.")
            return False, None
        query = {}
        if company_id and len(company_id) > 0:
            query['company_id'] = {'$eq': company_id}
        if invoice_year and len(invoice_year) > 0:
            query['invoice_year'] = {'$eq': invoice_year}
        try:
            page = max(1, int(page))
        except Exception:
            page = 1
        try:
            page_size = max(1, int(page_size))
        except Exception:
            page_size = 10
        skip = (page - 1) * page_size
        try:
            cursor = tbl_name.find(query).sort('create_time', -1).skip(skip).limit(page_size)
            results = list(cursor)
            total = tbl_name.count_documents(query)
            return True, {'total': total, 'rows': results}
        except Exception as e:
            self.logger.error(f"分页查询开票预警失败: {e}")
            return False, None
    
    
    """
    function:
    description: 从服务器查询信息
    param {*} course
    return {*}
    """
    def query_by_id(self, id: str) -> tuple[bool, InvoiceAlarmDao|None]:
        tbl_name = self.invoice_alarm_tbl()
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
        dao = InvoiceAlarmDao()
        dao.from_db(value[0])
        return True, dao

    """
    function:
    description: 删除信息
    param {*} self
    return {*}
    """
    def delete(self, id: str) -> bool:
        tbl_name = self.invoice_alarm_tbl()
        if tbl_name is None:
            self.logger.error("Invoice table not found in MongoDB.")
            return False
        query = {'_id': ObjectId(id)}
        return self.mongo_impl.delete(tbl_name, query)
