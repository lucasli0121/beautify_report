
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from datetime import datetime
import pandas as pd
import os
from typing import Any, Callable
from nicegui import Event
from apscheduler.schedulers.background import BackgroundScheduler
from dao.period_data_dao import PeriodDataDao
from utils import global_vars as g
from dao.recognize_info_dao import RecognizeInfoDao, RecognizeResult, RecognizeType
from grpc_protoc.invoice_recognize_client import recognize_certificate, recognize_invoice

@dataclass
class EventObj:
    id: str
    type: int
    result: int
    msg: str
    
class OcrManager:
    scheduler: BackgroundScheduler
    ocr_event: Event[EventObj]
    
    def __init__(self) -> None:
        self.scheduler = BackgroundScheduler(timezone="Asia/Shanghai")
        self.ocr_event = Event()

    def start(self):
        self.scheduler.add_job(
                self.handle_every_day_task,
                trigger="cron",
                hour="0,7",
                minute="*",
                second="*",
                id="handle_every_day_task",
            )
        self.scheduler.start()
    def stop(self):
        self.scheduler.shutdown()
    
    def subscribe(self, on_event: Callable) -> None:
        self.ocr_event.subscribe(on_event)

    def unsubscribe(self, on_event: Callable) -> None:
        self.ocr_event.unsubscribe(on_event)

    """
    处理识别结果的回调函数，更新数据库并触发事件通知订阅者
    """
    def handle_recognize_response(self, response: dict[str, Any]) -> None:
        dao = RecognizeInfoDao()
        dao.id = str(response.get('id'))
        dao.type = response.get('type', 0)
        dao.result = response.get('result', 0)
        dao.msg = response.get('msg', '')
        if dao.result == RecognizeResult.Success.value:
            res, save_dao = g.my_db.query_recognize_info_by_id(dao.id)
            if res and save_dao:
                file_dir = './static/uploads/'
                org_file_path = os.path.join(file_dir, save_dao.file_name)
                try:
                    os.remove(org_file_path)  # 删除原文件
                except Exception as e:
                    print(f"删除文件 {org_file_path} 失败: {e}")
        self.ocr_event.emit(EventObj(id=dao.id, type=dao.type, result=dao.result, msg=dao.msg))

    """
    # @function handle_every_day_task
    # @description 读取excel文件，按照文件中的公司名称更新期初数据
    # @param 
    # @return
    """
    def handle_every_day_task(self):
        file_path = "static/期初数据.xlsx"
        the_month = datetime.now().date().strftime("%Y-%m")
        def read_company_values(company_names:list, sheet_name: str):
            for name in company_names:
                res, company_dao = g.my_db.query_company_by_brief_name(name)
                if not res or company_dao is None:
                    continue
                dao = PeriodDataDao()
                dao.company_id = company_dao.id
                res, values_list = g.my_db.query_all_period_data(dao.company_id, the_month)
                if not res or values_list is None or len(values_list) == 0:
                    dao.create_time = the_month
                    g.my_db.add_period_data(dao.to_db())
                g.my_db.handle_summary_value_added_update(dao.company_id, the_month)
        self.read_company_names(file_path, read_company_values)
        

    

    def read_company_names(self, file_path, values_callback: Callable):
        # 检查文件是否存在
        if not os.path.exists(file_path):
            print(f"错误：文件 {file_path} 不存在。")
            return

        try:
            # 读取Excel文件
            # sheet_name=None 表示读取所有sheet，返回一个字典，key为sheet名，value为DataFrame
            all_sheets = pd.read_excel(file_path, sheet_name=None)
            
            target_sheets =['一般纳税人', '小规模']
            
            for sheet_name in target_sheets:
                if sheet_name in all_sheets:
                    df = all_sheets[sheet_name]
                    
                    # 假设“公司名称”在Excel的第一列，或者你可以指定列名
                    # 这里假设列名为 "公司名称"，如果列名不同请修改下方代码
                    col_name = '公司' 
                    
                    if col_name in df.columns:
                        # 提取该列数据，并去除空值
                        companies = df[col_name].dropna().unique().tolist()
                        print(f"\n--- {sheet_name} ---")
                        values_callback(companies, sheet_name)
                    else:
                        print(f"\n警告：在 '{sheet_name}' 中未找到名为 '{col_name}' 的列。")
                        print(f"当前列名为: {list(df.columns)}")
                else:
                    print(f"\n警告：未找到 sheet 页 '{sheet_name}'")
                    
        except Exception as e:
            print(f"读取过程中发生错误: {e}")