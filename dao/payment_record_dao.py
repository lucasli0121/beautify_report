from dataclasses import dataclass
from datetime import datetime
from typing import Any
from enum import Enum

class PaymentStatus(Enum):
    NotFinished = 0 # 未完成
    HasFinished = 1 # 已完成
    Canceled = 2 # 已取消

@dataclass
class PaymentRecordDao:
    id: str  # 发票记录ID
    from_company_id: str
    to_company_id: str
    item_name: str # 事项
    contract_id: str  # 合同ID
    from_bank_id: str # 付款方银行账户ID
    to_bank_id: str # 收款方银行账户ID
    payment_money: float # 金额
    should_invoice_money: float # 应开票金额
    has_invoice_money: float # 已开票金额
    remain_invoice_money: float # 剩余开票金额
    status: int # 状态 0: 未完成, 1: 已完成, 2: 已取消
    create_time: str
    remarks: str = '' # 备注

    def __init__(self, id: str = '', from_company_id: str = "", to_company_id: str = "", item_name: str = "",
                 contract_id='', from_bank_id: str = '', to_bank_id: str = '', payment_money: float = 0.0,
                 should_invoice_money: float = 0.0, has_invoice_money: float = 0.0,
                 remain_invoice_money: float = 0.0, status: int = 0, create_time: str = "") -> None:
        self.id = id
        self.from_company_id = from_company_id
        self.to_company_id = to_company_id
        self.item_name = item_name
        self.contract_id = contract_id
        self.from_bank_id = from_bank_id
        self.to_bank_id = to_bank_id
        self.payment_money = payment_money
        self.should_invoice_money = should_invoice_money
        self.has_invoice_money = has_invoice_money
        self.remain_invoice_money = remain_invoice_money
        self.status = status
        self.create_time = create_time if create_time else datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def from_db(self, data: dict[str, Any]) -> None:
        self.id = str(data.get('_id', ''))
        self.from_company_id = str(data.get('from_company_id', ''))
        self.to_company_id = str(data.get('to_company_id', ''))
        self.item_name = str(data.get('item_name', ''))
        self.contract_id = str(data.get('contract_id', ''))
        self.from_bank_id = str(data.get('from_bank_id', ''))
        self.to_bank_id = str(data.get('to_bank_id', ''))
        self.payment_money = float(data.get('payment_money', 0.0))
        self.should_invoice_money = float(data.get('should_invoice_money', 0.0))
        self.has_invoice_money = float(data.get('has_invoice_money', 0.0))
        self.remain_invoice_money = float(data.get('remain_invoice_money', 0.0))
        self.status = int(data.get('status', 0))
        self.create_time = str(data.get('create_time', datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        self.remarks = str(data.get('remarks', ''))

    def to_db(self) -> dict[str, Any]:
        return self.__dict__