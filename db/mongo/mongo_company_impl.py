'''
Author: liguoqiang
Date: 2021-08-06 14:10:41
LastEditors: liguoqiang
LastEditTime: 2024-06-06 21:00:51
Description: 
'''
# coding="utf8"

from pymongo.collection import Collection
import logging
from typing import Any
from bson.objectid import ObjectId
from dao.company_dao import CompanyDao
from dao.company_bank_account_dao import CompanyBankAccountDao
from db.mongo.mongo_impl import MongoImpl

class MongoCompanyImpl():
    def __init__(self, mongo_impl: MongoImpl):
        super().__init__()
        self.logger = logging.getLogger(__name__)
        self.mongo_impl = mongo_impl


    # 公司信息表名
    def company_tbl(self) -> None|Collection:
        if self.mongo_impl.db is None:
            self.logger.error("MongoDB connection is not established.")
            return None
        return self.mongo_impl.db['company_tbl']
    # 公司银行账户表名
    def company_bank_account_tbl(self) -> None|Collection:
        if self.mongo_impl.db is None:
            self.logger.error("MongoDB connection is not established.")
            return None
        return self.mongo_impl.db['company_bank_account_tbl']
    
    """
    添加公司信息到数据库
    :param data: 公司信息字典
    :return: 成功返回True，否则返回False
    """
    def add_company(self, data: dict[str, Any]) -> bool:
        try:
            tbl_name = self.company_tbl()
            if tbl_name is None:
                self.logger.error("Company table not found in MongoDB.")
                return False
            if 'id' in data:
                del data['id']
            ret = tbl_name.insert_one(data)
            return ret.acknowledged  # 确认插入操作已被确认
        except Exception as e:
            self.logger.error(f"添加公司信息失败: {e}")
            return False
        
    """ 
    更新公司信息到数据库
    :param data: 公司信息字典
    :param condition: 更新条件，例如 "id = 1"
    :return: 成功返回True，否则返回False
    """
    def update_company(self, data: dict[str, Any], condition: dict[str, Any]) -> bool:
        try:
            tbl_name = self.company_tbl()
            if tbl_name is None:
                self.logger.error("Company table not found in MongoDB.")
                return False
            if 'id' in data:
                del data['id']
            ret = tbl_name.update_one(condition, {'$set': data})
            return ret.modified_count > 0  # 返回是否有记录被修改
        except Exception as e:
            self.logger.error(f"更新公司信息失败: {e}")
            return False
        
    """
    查询公司信息
    :param condition: 查询条件，例如 "id = 1"
    :return: 查询结果列表，每个元素是一个字典，包含公司信息
    """
    def query_all_company(self, name: str, address: str, contacts: str) -> tuple[bool, None|list[Any]]:
        try:
            tbl_name = self.company_tbl()
            if tbl_name is None:
                self.logger.error("Company table not found in MongoDB.")
                return False, None
            query = {}
            if name or len(name) > 0:
                query['name'] = {'$regex': name, '$options': 'i'}
            if address or len(address) > 0:
                query['address'] = {'$regex': address, '$options': 'i'}
            if contacts or len(contacts) > 0:
                query['contacts'] = {'$regex': contacts, '$options': 'i'}
            results = list(tbl_name.find(query))
            return True, results
        except Exception as e:
            self.logger.error(f"查询公司信息失败: {e}")
            return False, None
    """
    function:
    description: 从服务器查询公司信息
    param {*} course
    return {*}
    """
    def query_company_by_id(self, id: str) -> tuple[bool, CompanyDao|None]:
        try:
            tbl_name = self.company_tbl()
            if tbl_name is None:
                self.logger.error("Company table not found in MongoDB.")
                return False, None
            query = {'_id': ObjectId(id)}
            result = tbl_name.find_one(query)
            if result is None:
                return False, None
            company_dao = CompanyDao()
            company_dao.from_db(result)
            return True, company_dao
        except Exception as e:
            self.logger.error(f"查询公司信息失败: {e}")
            return False, None
    """
    function:
    description: 删除公司信息
    param {*} self
    return {*}
    """
    def delete_company(self, id: str) -> bool:
        try:
            tbl_name = self.company_tbl()
            if tbl_name is None:
                self.logger.error("Company table not found in MongoDB.")
                return False
            query = {'_id': ObjectId(id)}
            ret = tbl_name.delete_one(query)
            return ret.deleted_count > 0  # 返回是否有记录被删除
        except Exception as e:
            self.logger.error(f"删除公司信息失败: {e}")
            return False

    """
    function: add_company_bank_account
    description: 增加公司银行账户信息
    param {dict[str, Any]} data: 公司银行账户信息字典
    param {*} self
    return {*}
    """
    def add_company_bank_account(self, data: dict[str, Any]) -> bool:
        try:
            tbl_name = self.company_bank_account_tbl()
            if tbl_name is None:
                self.logger.error("Company bank account table not found in MongoDB.")
                return False
            if 'id' in data:
                del data['id']
            ret = tbl_name.insert_one(data)
            return ret.acknowledged  # 确认插入操作已被确认
        except Exception as e:
            self.logger.error(f"添加公司银行账户信息失败: {e}")
            return False
        
    """ 
    更新公司银行账户到数据库
    :param data: 公司银行账户信息字典
    :param condition: 更新条件，例如 "id = 1"
    :return: 成功返回True，否则返回False
    """
    def update_company_bank_account(self, data: dict[str, Any], condition: dict[str, Any]) -> bool:
        try:
            tbl_name = self.company_bank_account_tbl()
            if tbl_name is None:
                self.logger.error("Company bank account table not found in MongoDB.")
                return False
            if 'id' in data:
                del data['id']
            ret = tbl_name.update_one(condition, {'$set': data})
            return ret.modified_count > 0  # 返回是否有记录被修改
        except Exception as e:
            self.logger.error(f"更新公司银行账户信息失败: {e}")
            return False
        
    """
    查询公司银行账户信息
    :param condition: 查询条件，例如 "id = 1"
    :return: 查询结果列表，每个元素是一个字典，包含公司信息
    """
    def query_all_company_bank_account(self, company_id: str) -> tuple[bool, None|list[CompanyBankAccountDao]]:
        try:
            tbl_name = self.company_bank_account_tbl()
            if tbl_name is None:
                self.logger.error("Company bank account table not found in MongoDB.")
                return False, None
            query = {}
            if company_id or len(company_id) > 0:
                query['company_id'] = {'$eq': company_id}
            
            results = list(tbl_name.find(query))
            dao_list = []
            for result in results:
                # 将查询结果转换为 CompanyDao 对象
                dao = CompanyBankAccountDao()
                dao.from_db(result)
                dao_list.append(dao)
            return True, dao_list
        except Exception as e:
            self.logger.error(f"查询公司银行账户信息失败: {e}")
            return False, None
    """
    function:
    description: 删除公司银行账户信息
    param {*} self
    return {*}
    """
    def delete_company_bank_account(self, id: str) -> bool:
        try:
            tbl_name = self.company_bank_account_tbl()
            if tbl_name is None:
                self.logger.error("Company bank account table not found in MongoDB.")
                return False
            query = {'_id': ObjectId(id)}
            ret = tbl_name.delete_one(query)
            return ret.deleted_count > 0  # 返回是否有记录被删除
        except Exception as e:
            self.logger.error(f"删除公司银行账户信息失败: {e}")
            return False