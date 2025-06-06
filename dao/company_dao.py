from dataclasses import dataclass
from datetime import datetime
import json
import logging
from typing import Any
import pytz
import MySQLdb as SqlDb
from utils import global_vars

logger = logging.getLogger(__name__)

@dataclass
class CompanyDao:
    id: int
    name: str
    address: str
    contacts: str
    phone: str
    email: str
    invoice_limit: int
    has_invoiced: float
    tax_id: int
    
    def __init__(self, id=0, name="", address="", contacts="", phone="", email="", invoice_limit=0, has_invoiced=0.0, tax_id=0):
        self.id = id
        self.name = name
        self.address = address
        self.contacts = contacts
        self.phone = phone
        self.email = email
        self.invoice_limit = invoice_limit
        self.has_invoiced = has_invoiced
        self.tax_id = tax_id

    def from_db(self, data: dict[str, Any]) -> None:
        self.id = data.get('id', 0)
        self.name = data.get('name', "")
        self.address = data.get('address', "")
        self.contacts = data.get('contacts', "")
        self.phone = data.get('phone', '')
        self.email = data.get('email', '')
        self.invoice_limit = data.get('invoice_limit', 10)
        self.has_invoiced = round(data.get('has_invoiced', 0.0), 2)
        self.tex_id = data.get('tex_id', "")
        

    def to_db(self) -> dict[str, Any]:
        return self.__dict__

    def table_name(self) -> str:
        return "company_tbl"
    
    """
    function:
    description: 从服务器查询公司信息
    param {*} course
    return {*}
    """
    def query_company_by_id(self) -> bool:
        try:
            db = global_vars.mysql_impl.get_connection()
            if db is None:
                logger.error("数据库连接失败")
                return False
            tbl_name = self.table_name()
            query_sql = f"SELECT * FROM {tbl_name} WHERE id = {self.id}"
            cur = db.cursor(SqlDb.cursors.DictCursor)
            cur.execute(query_sql)
            ret = cur.fetchone()
            cur.close()
            self.from_db(ret)
        except Exception as e:
            logger.error(f"查询公司信息失败: {e}")
            return False
        finally:
            global_vars.mysql_impl.close_connection(db)
        return True
    """
    function:
    description: 添加公司信息到数据库
    param {*} self
    return {*}
    """
    def add_company(self) -> bool:
        try:
            data = self.to_db()
            db = global_vars.mysql_impl.get_connection()
            if db is None:
                logger.error("数据库连接失败")
                return False
            tbl_name = self.table_name()
            insert_sql = global_vars.mysql_impl.dict_to_insert_sql(tbl_name, data)
            cur = db.cursor()
            cur.execute(insert_sql)
            db.commit()
            cur.close()
        except Exception as e:
            logger.error(f"添加公司信息失败: {e}")
            return False
        finally:
            global_vars.mysql_impl.close_connection(db)
        return True

    """
    function:
    description: 向服务器更新公司信息
    param {*} self
    return {*}
    """
    def update_company(self) -> bool:
        try:
            data = self.to_db()
            db = global_vars.mysql_impl.get_connection()
            if db is None:
                logger.error("数据库连接失败")
                return False
            tbl_name = self.table_name()
            update_sql = global_vars.mysql_impl.dict_to_update_sql(tbl_name, data, f"id = {self.id}")
            cur = db.cursor()
            cur.execute(update_sql)
            db.commit()
            cur.close()
        except Exception as e:
            logger.error(f"更新公司信息失败: {e}")
            return False
        finally:
            global_vars.mysql_impl.close_connection(db)
        return True

    """
    function:
    description: 删除公司信息
    param {*} self
    return {*}
    """
    def delete_company(self, id: int) -> bool:
        sql = f"DELETE FROM {self.table_name()} WHERE id = {id}"
        try:
            db = global_vars.mysql_impl.get_connection()
            if db is None:
                logger.error("数据库连接失败")
                return False
            cur = db.cursor()
            cur.execute(sql)
            db.commit()
            cur.close()
        except Exception as e:
            logger.error(f"删除公司信息失败: {e}")
            return False
        finally:
            global_vars.mysql_impl.close_connection(db)
        return True

"""
function:
description: 从服务器查询课程列表
param {*} course
return {*}
"""
def get_all_company(name: str, address: str, contacts: str) -> tuple[bool, None|list[CompanyDao]]:
    try:
        db = global_vars.mysql_impl.get_connection()
        if db is None:
            logger.error("数据库连接失败")
            return False, None
        company_dao = CompanyDao()
        tbl_name = company_dao.table_name()
        filter = []
        if name:
            filter.append(f"name LIKE '%{name}%'")
        if address:
            filter.append(f"address LIKE '%{address}%'")
        if contacts:
            filter.append(f"contacts LIKE '%{contacts}%'")
        filter_sql = " AND ".join(filter)
        if filter_sql:
            query_sql = f"SELECT * FROM {tbl_name} WHERE {filter_sql}"
        else:
            query_sql = f"SELECT * FROM {tbl_name}"
        cur = db.cursor(SqlDb.cursors.DictCursor)
        cur.execute(query_sql)
        ret = cur.fetchall()
        cur.close()
        if not ret:
            return True, []
        company_list = []
        for item in ret:
            company = CompanyDao()
            company.from_db(item)
            company_list.append(company)
        return True, company_list            
    except Exception as e:
        logger.error(f"查询公司信息失败: {e}")
        return False, None
    finally:
        global_vars.mysql_impl.close_connection(db)
