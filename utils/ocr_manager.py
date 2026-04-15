
from dataclasses import dataclass
import os
from typing import Any, Callable
from nicegui import Event
from apscheduler.schedulers.asyncio import AsyncIOScheduler
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
    scheduler: AsyncIOScheduler
    ocr_event: Event[EventObj]
    
    def __init__(self) -> None:
        # self.scheduler = AsyncIOScheduler(timezone="Asia/Shanghai")
        self.ocr_event = Event()

    # def start(self):
    #     self.scheduler.add_job(self.process_ocr_files, 'interval', max_instances=1, seconds=30)
    #     self.scheduler.start()
    # def stop(self):
    #     self.scheduler.shutdown()
    
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
        res, save_dao = g.my_db.query_recognize_info_by_id(dao.id)
        if res and save_dao:
            file_dir = './static/uploads/'
            org_file_path = os.path.join(file_dir, save_dao.file_name)
            try:
                os.remove(org_file_path)  # 删除原文件
            except Exception as e:
                print(f"删除文件 {org_file_path} 失败: {e}")
        self.ocr_event.emit(EventObj(id=dao.id, type=dao.type, result=dao.result, msg=dao.msg))

    # async def process_ocr_files(self):
    #     res, list_values = g.my_db.query_recognize_waiting_list_by_type(RecognizeType.AllType.value)
    #     if res and list_values is not None:
    #         for item in list_values:
    #             dao = RecognizeInfoDao()
    #             dao.from_db(item)
    #             dao.result = RecognizeResult.InProgress.value
    #             dao.msg = '识别中'
    #             g.my_db.update_recognize_info(dao.to_db(), {'id': dao.id})
    #             # 发送一个全局事件通知，让订阅者知道正在识别
    #             event_obj = EventObj(id=dao.id, type=dao.type, result=dao.result, msg=dao.msg)
    #             self.ocr_event.emit(event_obj)
    #             response = None
    #             if dao.type == RecognizeType.InvoiceType.value:
    #                 response = await recognize_invoice(dao.file_name)
    #             elif dao.type == RecognizeType.TaxProofType.value:
    #                 response = await recognize_certificate(dao.file_name)
    #             if response is not None:
    #                 print("gRPC 返回结果：", response)
    #                 file_dir = './static/uploads/'
    #                 backup_path = './static/backup/'
    #                 os.makedirs(backup_path, exist_ok=True)  # 创建目录（若不存在）
    #                 org_file_path = os.path.join(file_dir, dao.file_name)
    #                 os.rename(org_file_path, os.path.join(backup_path, dao.file_name))
    #                 if response.result == 0:
    #                     dao.result = RecognizeResult.Success.value
    #                     dao.msg = response.msg
    #                 else:
    #                     dao.result = RecognizeResult.Failed.value
    #                     dao.msg = response.msg
    #                 g.my_db.update_recognize_info(dao.to_db(), {'id': dao.id})
    #                 self.ocr_event.emit(EventObj(id=dao.id, type=dao.type, result=dao.result, msg=dao.msg))


    