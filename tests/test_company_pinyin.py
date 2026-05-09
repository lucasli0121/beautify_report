import asyncio
import string
from typing import Any
import unittest
from pypinyin import lazy_pinyin
from dao.company_dao import CompanyDao
from utils import global_vars as g


class TestInvoiceAlarm(unittest.TestCase):

    def setUp(self) -> None:
        return super().setUp()

    def tearDown(self) -> None:
        return super().tearDown()

    def get_pinyin(self, text):
        pinyin_name = ''.join(lazy_pinyin(text)).lower().strip()
        return pinyin_name
        # return  pinyin_name[0] if pinyin_name else ''

    def test_update_company_pinyin(self):
        res, company_list = g.my_db.query_all_company('', '', '', '', '')
        if res and company_list is not None:
            for item in company_list:
                dao = CompanyDao()
                dao.from_db(item)
                dao.brief_name_pinyin = self.get_pinyin(dao.brief_name)
                res = g.my_db.update_company(dao.to_db(), {})
                if not res:
                    print("update company failed")

if __name__ == '__main__':
    unittest.main()                