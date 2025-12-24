from dataclasses import dataclass
from datetime import datetime
from typing import Any


@dataclass
class PeriodDataDao:
    id: str
    company_id: str
    #上月未认证
    last_month_no_verify: float
    #上月留抵
    last_month_stay_pay: float
    #可开票额
    billing_amount: float
    #创建时间
    create_time: str

    def __init__(self, id: str = "", company_id: str = "", last_month_no_verify: float = 0.0,
                 last_month_stay_pay: float = 0.0, billing_amount: float = 0.0,
                 create_time: str = "") -> None:
        self.id = id
        self.company_id = company_id
        self.last_month_no_verify = last_month_no_verify
        self.last_month_stay_pay = last_month_stay_pay
        self.billing_amount = billing_amount
        self.create_time = create_time if create_time else datetime.now().strftime("%Y-%m")
        
    def from_db(self, data: dict[str, Any]) -> None:
        self.id = str(data.get('_id', ''))
        self.company_id = data.get('company_id', "")
        self.last_month_no_verify = data.get('last_month_no_verify', 0.0)
        self.last_month_stay_pay = data.get('last_month_stay_pay', 0.0)
        self.billing_amount = data.get('billing_amount', 0.0)
        self.create_time = data.get('create_time', "")

    def to_db(self) -> dict[str, Any]:
        return self.__dict__