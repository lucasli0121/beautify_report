import asyncio
from typing import Any
import unittest

from dao.invoice_record_dao import InvoiceRecordDao
from utils import global_vars as g
from pages.invoice_record_alarm_page import do_analyze


class TestInvoiceAlarm(unittest.TestCase):

    def setUp(self) -> None:
        return super().setUp()

    def tearDown(self) -> None:
        return super().tearDown()

    def test_alarm_analyze(self):
        result, values_list = g.my_db.query_invoice_record_by_from_and_year("", "2026")
        if result and values_list:
            filtered_scan_list: list[dict[str, Any]] = []
            seen_to_company_ids: set[tuple[str, str]] = set()
            for item in values_list:
                pair = (item['from_company_id'], item['to_company_id'])
                if pair in seen_to_company_ids:
                    continue
                seen_to_company_ids.add(pair)
                filtered_scan_list.append(item)
            for item in filtered_scan_list:
                invoice_record = InvoiceRecordDao()
                invoice_record.from_db(item)
                asyncio.run(do_analyze(
                    invoice_record.from_company_id,
                    invoice_record.to_company_id,
                    "2026",
                    filtered_scan_list.copy(),
                    [invoice_record],
                    visited=set()))
                # do_analyze,
                #     org_from_company_id=invoice_record.from_company_id,
                #     next_from_company_id=invoice_record.to_company_id,
                #     invoice_year="2026",
                #     scan_invoice_list=filtered_scan_list.copy(),
                #     invoice_path_list=[invoice_record])

if __name__ == '__main__':
    unittest.main()                