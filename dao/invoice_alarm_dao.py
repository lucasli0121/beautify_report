from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any

class InvoiceAlarmType(Enum):
    InvoiceCircleAlarm = 0 # 未完成

@dataclass
class InvoiceAlarmDao:
    id: str
    company_id: str
    alarm_type: int
    alarm_desc: str
    detail: str
    invoice_year: str
    #创建时间
    create_time: str

    def __init__(self, id: str = "", company_id: str = "", alarm_type: int = 0, alarm_desc: str = "", detail: str = "",
                invoice_year: str = "", create_time: str = "") -> None:
        self.id = id
        self.company_id = company_id
        self.alarm_type = alarm_type
        self.alarm_desc = alarm_desc
        self.detail = detail
        self.invoice_year = invoice_year
        self.create_time = create_time if create_time else datetime.now().strftime("%Y-%m")
        
    def from_db(self, data: dict[str, Any]) -> None:
        self.id = str(data.get('_id', ''))
        self.company_id = str(data.get('company_id', ''))
        self.alarm_type = data.get('alarm_type', 0)
        self.alarm_desc = data.get('alarm_desc', "")
        self.detail = data.get('detail', "")
        self.invoice_year = data.get('invoice_year', "")
        self.create_time = data.get('create_time', "")

    def to_db(self) -> dict[str, Any]:
        return self.__dict__
    
    def get_alarm_desc(self, alarm_type: int) -> str:
        if alarm_type == InvoiceAlarmType.InvoiceCircleAlarm.value:
            return "循环开票预警"
        else:
            return "未知预警类型"