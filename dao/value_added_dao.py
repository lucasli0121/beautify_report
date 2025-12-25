from dataclasses import dataclass
from datetime import datetime
from typing import Any


@dataclass
class ValueAddedDao:
    id: str
    company_id: str
    #上月未认证
    last_month_no_verify: float
    #上月留抵
    last_month_stay_pay: float
    #已开进项税额
    opened_input_tax: float
    #已开销项税额
    opened_output_tax: float
    #待开进项税额
    to_open_input_tax: float
    #待开销项税额
    to_open_output_tax: float
    # 应纳税额
    payable_tax: float
    #开销售额
    sales_amount: float
    #已开票额
    opened_billing_amount: float
    #剩余开票额
    remaining_billing_amount: float
    #可开票额
    billing_amount: float
    #创建时间
    create_time: str

    def __init__(self, id: str = "", company_id: str = "", last_month_no_verify: float = 0.0,
                last_month_stay_pay: float = 0.0, opened_input_tax: float = 0.0,
                opened_output_tax: float = 0.0, to_open_input_tax: float = 0.0,
                to_open_output_tax: float = 0.0, payable_tax: float = 0.0,
                sales_amount: float = 0.0, opened_billing_amount: float = 0.0,
                remaining_billing_amount: float = 0.0, billing_amount: float = 0.0,
                create_time: str = "") -> None:
        self.id = id
        self.company_id = company_id
        self.last_month_no_verify = last_month_no_verify
        self.last_month_stay_pay = last_month_stay_pay
        self.opened_input_tax = opened_input_tax
        self.opened_output_tax = opened_output_tax
        self.to_open_input_tax = to_open_input_tax
        self.to_open_output_tax = to_open_output_tax
        self.payable_tax = payable_tax
        self.sales_amount = sales_amount
        self.opened_billing_amount = opened_billing_amount
        self.remaining_billing_amount = remaining_billing_amount
        self.billing_amount = billing_amount
        self.create_time = create_time if create_time else datetime.now().strftime("%Y-%m")
        
    def from_db(self, data: dict[str, Any]) -> None:
        self.id = str(data.get('_id', ''))
        self.company_id = data.get('company_id', "")
        self.last_month_no_verify = float(data.get('last_month_no_verify', 0.0))
        self.last_month_stay_pay = float(data.get('last_month_stay_pay', 0.0))
        self.opened_input_tax = float(data.get('opened_input_tax', 0.0))
        self.opened_output_tax = float(data.get('opened_output_tax', 0.0))
        self.to_open_input_tax = float(data.get('to_open_input_tax', 0.0))
        self.to_open_output_tax = float(data.get('to_open_output_tax', 0.0))
        self.payable_tax = float(data.get('payable_tax', 0.0))
        self.sales_amount = float(data.get('sales_amount', 0.0))
        self.opened_billing_amount = float(data.get('opened_billing_amount', 0.0))
        self.remaining_billing_amount = float(data.get('remaining_billing_amount', 0.0))
        self.billing_amount = float(data.get('billing_amount', 0.0))
        self.create_time = data.get('create_time', "")

    def to_db(self) -> dict[str, Any]:
        return self.__dict__