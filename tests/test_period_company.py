import asyncio
import string
from typing import Any
import unittest
from utils import global_vars as g


class TestInvoiceAlarm(unittest.TestCase):

    def setUp(self) -> None:
        return super().setUp()

    def tearDown(self) -> None:
        return super().tearDown()

    def test_period_company(self):
        g.ocr_mgr.handle_every_day_task()

if __name__ == '__main__':
    unittest.main()                