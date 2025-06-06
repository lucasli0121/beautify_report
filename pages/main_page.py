'''
Author: liguoqiang
Date: 2025-03-16 15:26:37
LastEditors: liguoqiang
LastEditTime: 2025-03-16 17:18:36
Description: 
'''
from fastapi.staticfiles import StaticFiles
from nicegui import ui,app
from resources import strings
from menu.top_menu import top_menu
from pages.company_page import show_company_page
from pages.company_detail_page import show_company_detail_page
import navigation

@ui.page('/')
def main_page() -> None:
    ui.add_css('''
        .custom-tabs .q-tab__indicator {
            display: none !important;  # 隐藏下划线
        }
        .custom-tabs .q-tab__label {
            font-size: 20px !important;  # 修改字体大小
            color: #ffff !important;  # 修改字体颜色
        }
        
        .custom-tabs .q-tab--active,
        .custom-tabs .q-tab.q-tab--active,
        .custom-tabs .q-tab[aria-selected="true"] {
            background-color: #449DEE !important;  /* 选中的 tab 背景颜色 */
        }
        .custom-tabs {
            padding: 0 !important;
            margin-top: 30px !important;
            margin-left: 0 !important;
            margin-right: 0 !important;
            width: 100% !important;
            height: 100% !important;
            align-items: center !important;
        }
        .custom-tabs .q-tab {
            background-color: #65B6FF !important;  /* 未选中的 tab 背景颜色 */
            border-radius: 0 !important;
            margin: 0 !important;
            padding: 0 !important;
            width: 100% !important;
            height: 80px !important;
        }
        /* 移除页面元素的内边距 */
        .q-page {
            padding: 0 !important;
            margin: 0 !important;
            width: 100% !important;
            background-color: #F4F9FD !important;
        }
        .q-drawer {
            top: 0;
            bottom: 0;
            padding: 0;
            margin: 0;
            height: 100%;
            background-color: #65B6FF;
        }
        .nicegui-drawer {
            padding: 0 !important;
            margin: 0 !important;
        }
        
    ''')
    if 'navigation' not in app.storage.user:
        app.storage.user['navigation'] = navigation.HOME_NAVIGATION
    with ui.header().classes('item-center place-content-between').style('background-color: white'):
        header_row = ui.row().classes('h-full items-center place-content-start gap-0')
        ui.space()
        with ui.row():
            top_menu()
    tab_panels = show_tabs()
    if app.storage.user['navigation'] == navigation.HOME_NAVIGATION or app.storage.user['navigation'] == navigation.COMPANY_NAVIGATION:
        with header_row:
            header_row.clear()
            title = ui.label(navigation.navigation_switcher.get(navigation.HOME_NAVIGATION, '')).classes('place-self-center').style('font-size: 24px; color:#65B6FF')
            title.bind_text_from(tab_panels, 'value', lambda value: value.props["label"] if not isinstance(value, str) else value)
    elif app.storage.user['navigation'] == navigation.COMPANY_DETAIL_NAVIGATION:
        with header_row:
            header_row.clear()
            onback = app.storage.user['onback']
            ui.icon('img:/static/images/back@2x.png') \
                .classes('w-[24px] h-[24px]') \
                .on('click', onback)
            ui.label('公司管理 / ').classes('ml-2 text-[20px] text-[#333333]')
            ui.label('课程详情').classes('text-[20px] text-[#65B6FF]').set_text(app.storage.user['company_name'])

def show_tabs() -> ui.tab_panels:
    with ui.left_drawer(top_corner=True).props('width=260').classes('gap-0'):
        with ui.row().classes('w-full h-[80px] p-[20px] place-content-center gap-0'):
            ui.label('报表美化系统').classes('text-[24px] text-white font-large')
            # ui.image('/static/images/logo@2x.png').classes('w-[206px] h-[47px] place-self-start')
        with ui.tabs().props('vertical no-caps inline-label').classes('text-white custom-tabs') as tabs:
            # home = ui.tab(strings.get('home_page'), icon='img:/static/images/course.png').props('icon-left').classes('w-full h-[80px]')
            company = ui.tab(strings.get('company_page'), icon='img:/static/images/devices.png').props('icon-left').classes('w-full h-[80px]')
            tab_value = company
            if app.storage.user['navigation'] == navigation.HOME_NAVIGATION:
                tab_value = company
            elif app.storage.user['navigation'] == navigation.COMPANY_NAVIGATION:
                tab_value = company
            elif app.storage.user['navigation'] == navigation.COMPANY_DETAIL_NAVIGATION:
                tab_value = company
    with ui.tab_panels(tabs, value=tab_value) \
        .props('vertical') \
        .classes('w-full h-full q-pa-none') \
        .style('margin: 0 !important; padding: 0 !important;') as tab_panels:
        with ui.tab_panel(company).classes('gap-0').style('margin: 0 !important; padding: 0 !important; background-color: #F4F9FD !important;'):
            if 'company_container' not in app.storage.user:
                app.storage.user['company_container'] = navigation.COMPANY_NAVIGATION

            if app.storage.user['company_container'] == navigation.COMPANY_NAVIGATION:
                show_company_page()
            elif app.storage.user['company_container'] == navigation.COMPANY_DETAIL_NAVIGATION:
                company_id = app.storage.user['company_id']
                show_company_detail_page(company_id)
            
        # with ui.tab_panel(home).classes('gap-0').style('margin: 0 !important; padding: 0 !important; background-color: #F4F9FD !important;') as home_panel:
        #     pass
    return tab_panels