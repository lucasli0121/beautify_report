from dataclasses import dataclass
from datetime import datetime


@dataclass
class PeriodDataDao:
    id: str
    company_id: str
    last_month_no_verify: float
    last_month_stay_pay: float
    billing_amount: float
    create_time: str

    def __init__(self, id: str = "", company_id: str = "", last_month_no_verify: float = 0.0,
                 last_month_stay_pay: float = 0.0, billing_amount: float = 0.0,
                 create_time: str = "") -> None:
        self.id = id
        self.company_id = company_id
        self.last_month_no_verify = last_month_no_verify
        self.last_month_stay_pay = last_month_stay_pay
        self.billing_amount = billing_amount
        self.create_time = create_time if create_time else datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
    def from_json(self, json_data):
        self.id = json_data.get('id', 0)
        self.company_id = json_data.get('company_id', "")
        self.last_month_no_verify = json_data.get('last_month_no_verify', 0.0)
        self.last_month_stay_pay = json_data.get('last_month_stay_pay', 0.0)
        self.billing_amount = json_data.get('billing_amount', 0.0)
        self.create_time = json_data.get('create_time', "")