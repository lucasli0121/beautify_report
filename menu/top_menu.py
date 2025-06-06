'''
Author: liguoqiang
Date: 2025-03-03 21:35:35
LastEditors: liguoqiang
LastEditTime: 2025-03-16 17:20:56
Description: 
'''
from nicegui import ui,app

def logout() -> None:
    try:
        app.storage.user.clear()
        app.storage.browser.clear()
        app.storage.general.clear()
        app.storage.client.clear()
        app.storage.user['authenticated'] = False
    except Exception as e:
        pass
    ui.navigate.to('/login')

def top_menu() -> None:
    # ui.button(icon='notifications', on_click=lambda: ui.notify('Hello, world!')).classes('text-white')
    with ui.button(on_click=logout) \
        .props('flat') \
        .classes('bg-transparent') \
        .style('color: #333333 !important; font-size:16px; width: 100px; height: 36px;'):
        with ui.row().classes('w-full items-center place-content-center gap-1'):
            ui.image('/static/images/logout.png').classes('pr-[3px]').style('width: 24px; height: 24px;')
            ui.label('退出').classes('pl-[3px]')
        