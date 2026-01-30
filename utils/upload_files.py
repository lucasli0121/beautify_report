'''
Author: liguoqiang
Date: 2025-04-15 21:00:10
LastEditors: liguoqiang
LastEditTime: 2025-09-30 16:51:15
Description: 
'''
from datetime import datetime
from typing import Callable
from nicegui import ui, events
from nicegui.elements.upload_files import FileUpload
import os
import matplotlib
import logging
from utils import global_vars as g

from dao.recognize_info_dao import RecognizeInfoDao, RecognizeResult, RecognizeType
from grpc_protoc.invoice_recognize_client import recognize_certificate, recognize_invoice
matplotlib.use('Agg')  # 使用非交互式后端

logger = logging.getLogger(__name__)

"""
# @function: handle_common_upload_file
# @description: 处理通用文件上传

"""
async def handle_common_upload_file(files: list[FileUpload], type: int) -> bool:
    for file in files:
        # event.content 是文件的二进制内容
        file_content = await file.read()
        save_dir = './static/uploads/'
        os.makedirs(save_dir, exist_ok=True)  # 创建目录（若不存在）
        file_name = file.name
        save_path = os.path.join(save_dir, file_name)
        with open(save_path, 'wb') as f:
            f.write(file_content)
        # 通过 gRPC 进行发票识别
        recognize_dao = RecognizeInfoDao()
        recognize_dao.file_name = file_name
        recognize_dao.type = type
        recognize_dao.result = RecognizeResult.Waiting.value
        recognize_dao.retry_count = 0
        recognize_dao.create_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        dt = recognize_dao.to_db()
        res, value = g.my_db.add_recognize_info(dt)
        if res is False:
            return False
    return True

'''
    打开发票 OCR 对话框
'''
def open_ocr_invoice_dialog():
    with ui.dialog().props('persistent') as dialog, ui.card().classes('w-1/2 h-1/2') \
        .style('background-color: #FFFFFF !important; border-radius: 10px;'):
        with ui.row().classes('w-full h-[60%] mt-5 place-content-between'):
            async def handle_upload_invoice_ocr(e: events.MultiUploadEventArguments):
                res = await handle_common_upload_file(e.files, RecognizeType.InvoiceType.value)
                if not res:
                    ui.notify("保存到数据库失败", color='negative')
                dialog.close()
            ui.upload(label="请选择批量上传文件", multiple=True) \
                .props('flat batch accept=".pdf"') \
                .classes('size-full') \
                .on_multi_upload(handle_upload_invoice_ocr)
        with ui.row().classes('w-full place-content-center') as loading_row:
            ui.icon('autorenew').classes('animate-spin text-4xl text-blue-500')
            ui.label("识别仅支持 CPU 识别，识别速度较慢，请耐心等待...")
            loading_row.visible = False
        with ui.row().classes('w-full h-[30%] place-content-center'):
            ui.button('关闭', on_click=lambda: dialog.close()).classes('w-1/3')

    dialog.open()

'''
    打开完税凭证 OCR 对话框
'''
def open_ocr_certificate_dialog():
    with ui.dialog().props('persistent') as dialog, ui.card().classes('w-1/2 h-1/2') \
        .style('background-color: #FFFFFF !important; border-radius: 10px;'):
        with ui.row().classes('w-full h-[60%] mt-5 place-content-between'):
            async def handle_upload_ocr(e: events.MultiUploadEventArguments):
                res = await handle_common_upload_file(e.files, RecognizeType.TaxProofType.value)
                if not res:
                    ui.notify("保存到数据库失败", color='negative')
                dialog.close()
            ui.upload(label="请选择批量上传文件", multiple=True) \
                .props('flat batch accept=".pdf"') \
                .classes('size-full') \
                .on_multi_upload(handle_upload_ocr)
        with ui.row().classes('w-full place-content-center') as loading_row:
            ui.icon('autorenew').classes('animate-spin text-4xl text-blue-500')
            ui.label("识别仅支持 CPU 识别，识别速度较慢，请耐心等待...")
            loading_row.visible = False
        with ui.row().classes('w-full place-content-center'):
            ui.button('关闭', on_click=lambda: dialog.close()).classes('w-1/3')

    dialog.open()    