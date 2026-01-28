'''
Author: liguoqiang
Date: 2025-03-03 13:40:09
LastEditors: liguoqiang
LastEditTime: 2025-11-11 13:55:27
Description: 
'''
import os
import sys
from typing import Optional
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request
from fastapi.responses import RedirectResponse
from nicegui import ui,app
from resources import strings
import logging
import logging.config
import yaml
from utils import global_vars as g
from pages import main_page, login_page

# 定义全局颜色
# ui.colors(primary='#65B6FF', onprimary='#FFFFFF', secondary='#65B6FF', accent='#111B1E', positive='#53B689')

class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if not app.storage.user.get('authenticated', False):
            if not request.url.path.startswith('/_nicegui') \
                and not request.url.path.startswith('/login') \
                and not request.url.path.startswith('/static'):
                app.storage.user['referrer_path'] = request.url.path
                return RedirectResponse('/login')
        return await call_next(request)

def init_logger():
    cfg_path = 'cfg/log.yaml'
    if not os.path.exists("log"):
        os.makedirs("log")
    if os.path.exists(cfg_path):
        with open(cfg_path, "r", encoding="utf-8") as f:
            config = yaml.load(f, yaml.FullLoader)
            logging.config.dictConfig(config)
    else:
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s-%(name)s-%(lineno)s-%(levelname)s-%(message)s",
            filename="log/beautify_report.log",
            filemode="w",
        )

def init_app():
    app.add_middleware(AuthMiddleware)
    # 添加以下代码以注册静态文件目录
    # 获取当前文件所在目录的路径
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # 注册静态文件目录
    # app.mount("/static", StaticFiles(directory=os.path.join(current_dir, "../static")), name="static")
    app.add_static_files('/static', os.path.join(current_dir, "static"))
    # 添加自定义字体
    # ui.add_head_html('''
    #     <style>
    #         @font-face {
    #             font-family: 'Source Han Sans CN';
    #             src: url('/static/fonts/SourceHanSansCN-Regular.otf') format('opentype');
    #             font-weight: normal;
    #             font-style: normal;
    #         }
    #         @font-face {
    #             font-family: 'Source Han Sans CN';
    #             src: url('/static/fonts/SourceHanSansCN-Bold.otf') format('opentype');
    #             font-weight: bold;
    #             font-style: normal;
    #         }
    #         @font-face {
    #             font-family: 'Source Han Sans CN';
    #             src: url('/static/fonts/SourceHanSansCN-Light.otf') format('opentype');
    #             font-weight: 300;
    #             font-style: normal;
    #         }
    #         /* 设置全局默认字体 */
    #         html, body {
    #             font-family: 'Source Han Sans CN';
    #         }        
    #     </style>
    # ''')
    @ui.page('/login')
    def login()-> Optional[RedirectResponse]:
        return login_page.login()
    @ui.page('/')
    def main_page_view():
        ui.add_css('''
            .custom-border.q-field--outlined .q-field__control:before {
                border: 1px solid #65B6FF !important;
            }
        ''')
        main_page.main_page()
        
'''
function app_startup
description: 应用启动时执行的函数，启动OCR管理器
parameters: []
'''
@app.on_startup
async def app_startup():
    # 启动OCR管理器
    g.ocr_mgr.start()
    # pass

'''
function app_shutdown
description: 应用关闭时执行的函数，清理存储
parameters: []
'''
@app.on_shutdown
async def app_shutdown():
    # 关闭OCR管理器
    g.ocr_mgr.stop()
    """应用关闭时清理存储"""
    authenticated = app.storage.user['authenticated']
    try:
        app.storage.user.clear()
        app.storage.client.clear()
        app.storage.browser.clear()
        app.storage.general.clear()
    except Exception as e:
        pass
    app.storage.user['authenticated'] = authenticated

if __name__ in {"__main__", "__mp_main__"}:
    if getattr(sys, '_main_already_running', False):
        sys.exit(0)
    init_logger()
    logger = logging.getLogger(__name__)
    init_app()
    # if global_vars.create_mq() is False:
    #     logger.error("MQTT连接失败，请检查配置文件")
    # api_manager.api_https = ulib.PoolManager(timeout=60.0)
    ui.run(title=strings.APP_NAME,
        port=8083,
        language='zh-CN',
        reconnect_timeout=120,
        storage_secret='a719a08c-30c5-4d19-8116-05af7d6b3cec',
        reload=False)  # 禁用自动重载