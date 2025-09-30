'''
Author: liguoqiang
Date: 2025-04-15 21:00:10
LastEditors: liguoqiang
LastEditTime: 2025-09-30 16:51:15
Description: 
'''
from typing import Callable
from nicegui import ui
import pandas as pd
import re
import io
import os
import numpy as np
import paddle
from paddleocr import PaddleOCR
from pdf2image import convert_from_bytes
import logging
from paddleocr import logger
from typing import Optional
import matplotlib
matplotlib.use('Agg')  # 使用非交互式后端

import_invoice_ocr_callback: Optional[Callable] = None

os.environ["MKL_NUM_THREADS"] = "1"
os.environ["NUMEXPR_NUM_THREADS"] = "1"
os.environ["OMP_NUM_THREADS"] = "1"

fh = logging.FileHandler("paddleocr.log")
logger.addHandler(fh)

paddle.device.set_device('cpu')
paddle.set_flags({'FLAGS_use_mkldnn': False})  # 关闭 MKLDNN
# 2. 初始化 OCR
ocr = PaddleOCR(
    use_angle_cls=True, 
    lang="ch")

def extract_invoice_fields(texts: list, scores, boxes: list):
    """从 OCR 文本中提取发票关键字段"""
    result = {
        "购买方": '',
        "销售方": '',
        "规格": '',
        "数量": 0,
        "单价": 0,
        "税率": 0,
        "发票号码": '',
        "开票日期": '',
        "金额": 0,
        "税额": 0,
        "含税额": 0,
        "发票内容": '',
        "备注": ''
    }

    money_x = 0
    tax_money_x = 0
    for idx, t in enumerate(texts):
        # 发票代码（10-12位数字）
        match = re.search(r"名称[:：]?\s*([\u4e00-\u9fa5A-Za-z0-9\s\-_（）()]+)", t)
        if match:
            if boxes[idx][0][0] <= 50:  # x 坐标小于 50
                result["购买方"] = match.group(1)
            elif boxes[idx][0][0] >= 300:  # x 坐标大于 300
                result["销售方"] = match.group(1)

        match = re.search(r"项目名称", t)
        if match:
            x = 0
            y = boxes[idx][0][1] + 8 # 向下偏移 5
            name = ""
            for j, b in enumerate(boxes):
                if b[0][0] >= x and b[0][0] <= (x + 50) and b[0][1] >= y and b[0][1] <= (y + 30):
                    if name == "":
                        name = texts[j]
                        y = b[0][1] + 15  # 继续向下偏移 15
                    else:
                        name = name + texts[j]
                        break
            result["发票内容"] = name

        match = re.search(r"数量", t)
        if match:
            x = boxes[idx][0][0] - 50  # 向左偏移 50
            y = boxes[idx][0][1] + 10 # 向下偏移 10
            for j, b in enumerate(boxes):
                if b[0][0] >= x and b[0][0] <= (x + 100) and b[0][1] >= y and b[0][1] <= (y + 30):
                    result["数量"] = float(texts[j].replace(' ', '').replace(',', '.'))
                    break
        match = re.search(r"单价", t)
        if match:
            x = boxes[idx][0][0] - 50  # 向左偏移 50
            y = boxes[idx][0][1] + 10 # 向下偏移 10
            for j, b in enumerate(boxes):
                if b[0][0] >= x and b[0][0] < (x + 100) and b[0][1] >= y and b[0][1] < (y + 30):
                    result["单价"] = float(texts[j].replace(' ', '').replace(',', '.'))
                    break

        match = re.search(r"金额", t)
        if match:
            money_x = boxes[idx][0][0] - 50  # 向左偏移 50
            y = boxes[idx][0][1] + 10 # 向下偏移 50
            for j, b in enumerate(boxes):
                if b[0][0] >= money_x and b[0][0] < (money_x + 100) and b[0][1] >= y and b[0][1] < (y + 30):
                    result["金额"] = float(texts[j].replace(' ', ''))
                    break

        match = re.search(r"(\d+?%)", t)
        if match:
            result["税率"] = match.group(1)
            # x = boxes[idx][0][0]
            # y = boxes[idx][0][1] + 40 # 向下偏移 50
            # for j, b in enumerate(boxes):
            #     if b[0][0] >= x and b[0][0] < (x + 300) and b[0][1] > y and b[0][1] < (y + 100):
            #         result["税率"] = texts[j]
            #         break
        match = re.search(r"税额", t)
        if match:
            tax_money_x = boxes[idx][0][0] - 50  # 向左偏移 150
            y = boxes[idx][0][1] + 10 # 向下偏移 50
            for j, b in enumerate(boxes):
                if b[0][0] >= tax_money_x and b[0][0] < (tax_money_x + 100) and b[0][1] >= y and b[0][1] < (y + 30):
                    result["税额"] = float(texts[j].replace(' ', ''))
                    break

        match = re.match(r"合|计|合计", t)
        if match:
            if money_x == 0:
                match = re.search(r"金额", t)
                if match:
                    money_x = boxes[idx][0][0] - 50  # 向左偏移 50
            x = money_x
            y = boxes[idx][0][1] - 10
            if tax_money_x == 0:
                tax_money_x = 720
            for j, b in enumerate(boxes):
                if b[0][0] >= x and b[0][0] < (x + 100) and b[0][1] >= y and b[0][1] < (y + 30):
                    money_txt = texts[j][1:]
                    money = float(money_txt.replace(',', '').replace(' ', ''))
                    if money != result["金额"]:
                        result["金额"] = money
                if b[0][0] >= tax_money_x and b[0][0] < (tax_money_x + 100) and b[0][1] >= y and b[0][1] < (y + 30):
                    money_txt = texts[j][1:]
                    money = float(money_txt.replace(',', '').replace(' ', ''))
                    if money != result["税额"]:
                        result["税额"] = money
                    break

        match = re.search(r"小写[)）]", t)
        if match:
            # amount_pattern = r"(?:\d{1,3}(?:,\d{3})+|\d+)(?:\.\d{1,2})?"
            amount_pattern = r"\d+(?:\.\d{1,2})?"
            match = re.search(r"小写[)）].\s*(" + amount_pattern + ")", t)
            if match:
                result["含税额"] = float(match.group(1))
            else:
                x = boxes[idx][0][0] + 30  # 向右偏移 100
                y = boxes[idx][0][1] - 10
                for j, b in enumerate(boxes):
                    if b[0][0] >= x and b[0][0] < (x + 100) and b[0][1] >= y and b[0][1] < (y + 30):
                        result["含税额"] = float(texts[j][1:].replace(',', '').replace(' ', ''))
                        break

        # 发票号码（8位数字）
        match = re.search(r"发票号码[:：]?\s*([0-9]{8})", t)
        if match:
            result["发票号码"] = match.group(1)

        # 开票日期（YYYY年MM月DD日 或 YYYY-MM-DD）
        match = re.search(r"([0-9]{4}[年\-][0-9]{1,2}[月\-][0-9]{1,2}日?)", t)
        if match:
            result["开票日期"] = match.group(1)
        
        match = re.search(r"备|注|备注", t)
        if match:
            x = boxes[idx][0][0] + 10  # 向右偏移 100
            y = boxes[idx][0][1] - 50
            remark = ""
            for j, b in enumerate(boxes):
                if b[0][0] >= x and b[0][0] < (x + 200) and b[0][1] >= y and b[0][1] < (y + 50):
                    if remark == "":
                        remark = texts[j]
                        x = b[0][0] + 30  # 继续向下偏移 40
                    else:
                        remark = remark + texts[j]
                        break
            if result["备注"] == '':
                result["备注"] = remark

    if isinstance(result["含税额"], (int, float)) and isinstance(result["金额"], (int, float)) and result["含税额"] > 0 and result["金额"] > 0:
        result["税额"] = round(float(result["含税额"] - result["金额"]), 2)
    if result["备注"] == '':
        x = 30
        y = 420
        remark = ""
        for j, b in enumerate(boxes):
            if b[0][0] >= x and b[0][0] < (x + 100) and b[0][1] >= y and b[0][1] <= (y + 30):
                if remark == "":
                    remark = texts[j]
                    x = b[0][0] + 50  # 继续向右偏移 50
                else:
                    remark = remark + texts[j]
                    break
        result["备注"] = remark

    return result

def recognize_invoice_pdf(pdf_content):
    # 1. PDF 转图片
    pages = convert_from_bytes(pdf_content, dpi=200)

    all_fields = []

    # 3. 逐页识别
    for i, page in enumerate(pages):
        print(f"\n===== 第 {i+1} 页 =====")
        # img_path = f"page_{i+1}.jpg"
        # page.save(img_path, "JPEG")

        page = page.resize((page.width // 2, page.height // 2))
        img = np.array(page)

        results = ocr.predict(img)
        texts  = results[0]['rec_texts']
        scores = results[0]['rec_scores']
        boxes  = results[0]['dt_polys']

        print("OCR 结果：")
        for text, score, box in zip(texts, scores, boxes):
            print(f"文字: {text}, 置信度: {score:.3f}, 坐标: {box}")

        fields = extract_invoice_fields(texts, scores, boxes)
        print("\n提取字段：", fields)

        all_fields.append(fields)

    return all_fields


def open_ocr_invoice_dialog(handle_ocr_callback: Callable):
    global import_invoice_ocr_callback
    import_invoice_ocr_callback = handle_ocr_callback
    with ui.dialog().props('persistent') as dialog, ui.card().classes('w-1/3 h-1/3') \
        .style('background-color: #FFFFFF !important; border-radius: 10px;'):
        with ui.row().classes('w-full h-[60%] mt-5 place-content-between'):
            def handle_upload_invoice_ocr(event):
                # event.content 是文件的二进制内容
                file_content = io.BytesIO(event.content.read())
                results = recognize_invoice_pdf(file_content.read())
                if handle_ocr_callback is not None:
                    handle_ocr_callback(results)
                dialog.close()
            ui.upload(label="请选择批量上传文件", on_upload=handle_upload_invoice_ocr) \
                .props('flat accept=".pdf"') \
                .classes('size-full')
        with ui.row().classes('w-full h-[30%] place-content-center'):
            ui.button('关闭', on_click=lambda: dialog.close()).classes('w-1/3')

    dialog.open()