from dataclasses import dataclass
from enum import Enum
import logging
from typing import Any

logger = logging.getLogger(__name__)

class BackType(Enum):
    BASIC = 0
    GENERAL = 1
    OTHER = 2

@dataclass
class CompanyBankAccountDao:
    id: str
    company_id: str
    bank_account: str
    bank_name: str
    account_type: int # 0: 基本户, 1: 一般户, 2: 其他
    opening_balance: float # 期初余额
    current_balance: float # 当前余额
    bank_address: str

    def __init__(self, id: str = "", company_id: str = "", bank_account: str = "", bank_name: str = "", account_type: int = 0, opening_balance: float = 0.0, current_balance: float = 0.0, bank_address: str = "") -> None:
        self.id = id
        self.company_id = company_id
        self.bank_account = bank_account
        self.bank_name = bank_name
        self.account_type = account_type
        self.opening_balance = opening_balance
        self.current_balance = current_balance
        self.bank_address = bank_address

    def from_db(self, data: dict[str, Any]) -> None:
        self.id = str(data.get('_id', ''))
        self.company_id = str(data.get('company_id', ''))
        self.bank_account = str(data.get('bank_account', ''))
        self.bank_name = str(data.get('bank_name', ''))
        self.account_type = int(data.get('account_type', 0))
        self.opening_balance = float(data.get('opening_balance', 0.0))
        self.current_balance = float(data.get('current_balance', 0.0))
        self.bank_address = str(data.get('bank_address', ''))

    def to_db(self) -> dict[str, Any]:
        return self.__dict__
    

