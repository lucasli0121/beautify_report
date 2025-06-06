'''
Author: liguoqiang
Date: 2025-03-03 13:40:09
LastEditors: liguoqiang
LastEditTime: 2025-03-19 14:57:09
Description: 
'''
import os
from fastapi import Request
from fastapi.responses import RedirectResponse
from starlette.middleware.base import BaseHTTPMiddleware
from nicegui import ui,app
from dao.classroom_dao import ClassRoomSeatsDao, get_class_room_seats_by_classes_id
from resources import strings
import logging
import logging.config
import yaml
from utils import global_vars
from pages import main_page, login_page


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

# 添加以下代码以注册静态文件目录
# 获取当前文件所在目录的路径
current_dir = os.path.dirname(os.path.abspath(__file__))
# 注册静态文件目录
# app.mount("/static", StaticFiles(directory=os.path.join(current_dir, "../static")), name="static")
app.add_static_files('/static', os.path.join(current_dir, "static"))

# 添加自定义字体
ui.add_head_html('''
    <style>
        @font-face {
            font-family: 'Source Han Sans CN';
            src: url('/static/fonts/SourceHanSansCN-Regular.otf') format('opentype');
            font-weight: normal;
            font-style: normal;
        }
        @font-face {
            font-family: 'Source Han Sans CN';
            src: url('/static/fonts/SourceHanSansCN-Bold.otf') format('opentype');
            font-weight: bold;
            font-style: normal;
        }
        @font-face {
            font-family: 'Source Han Sans CN';
            src: url('/static/fonts/SourceHanSansCN-Light.otf') format('opentype');
            font-weight: 300;
            font-style: normal;
        }
        /* 设置全局默认字体 */
        html, body {
            font-family: 'Source Han Sans CN';
        }        
    </style>
''')

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


app.add_middleware(AuthMiddleware)

def app_shutdown():
    try:
        status, seats_list = get_class_room_seats_by_classes_id(global_vars.get_class_room().id)
        if status == 200:
            for item in seats_list:
                if isinstance(item, ClassRoomSeatsDao):
                    if item.mac is not None and item.mac != "":
                        global_vars.unsubscribe_online_topic(item.mac)
    except Exception as e:
        pass
    authenticated = app.storage.user['authenticated']
    try:
        app.storage.user.clear()
        app.storage.client.clear()
        app.storage.browser.clear()
        app.storage.general.clear()
    except Exception as e:
        pass
    app.storage.user['authenticated'] = authenticated
                    
app.on_shutdown(app_shutdown)

if __name__ in {"__main__", "__mp_main__"}:
    init_logger()
    logger = logging.getLogger(__name__)
    # if global_vars.create_mq() is False:
    #     logger.error("MQTT连接失败，请检查配置文件")
    # api_manager.api_https = ulib.PoolManager(timeout=60.0)
    ui.run(title=strings.APP_NAME,
        port=8083,
        language='zh-CN',
        reconnect_timeout=120,
        storage_secret='a719a08c-30c5-4d19-8116-05af7d6b3cec')