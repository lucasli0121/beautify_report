'''
Author: liguoqiang
Date: 2025-03-03 21:20:50
LastEditors: liguoqiang
LastEditTime: 2025-03-13 10:11:12
Description: 
'''

from contextlib import contextmanager
from nicegui import ui,app, events
from typing import Callable
from resources import strings
from menu.top_menu import top_menu

HOME_NAVIGATION = 'Home'
COMPANY_NAVIGATION = 'Company'
COMPANY_DETAIL_NAVIGATION = 'CompanyDetail'

navigation_switcher = {
    HOME_NAVIGATION: strings.HOME_PAGE,
    COMPANY_NAVIGATION: strings.COMPANY_PAGE,
    COMPANY_DETAIL_NAVIGATION: strings.COMPANY_DETAIL_PAGE,
}
def show_main_page_title() -> None:
    app.storage.user['navigation'] = HOME_NAVIGATION
    ui.navigate.to('/')

            
def show_company_title() -> None:
    app.storage.user['navigation'] = COMPANY_NAVIGATION
    ui.navigate.to('/')
            

def show_company_detail_title(onback) -> None:
    app.storage.user['navigation'] = COMPANY_DETAIL_NAVIGATION
    app.storage.user['onback'] = onback
    ui.navigate.to('/')


#
# @description: 定义首页导航页面,
# @param {str} navigation 首页导航类型
def navigation_main_page() -> None:
    app.storage.user['navigation'] = HOME_NAVIGATION
    ui.navigate.to('/')

#
# @description: 定义公司管理页面,设置公司管理类型
#
def navigation_company_page() -> None:
    app.storage.user['navigation'] = COMPANY_NAVIGATION
    app.storage.user['company_container'] = COMPANY_NAVIGATION
    ui.navigate.to('/')

#
# @description: 定义公司详情页面,设置公司详情类型
# @param {int} company_id 公司ID
# @param {Callable[[], None]} onback 回调函数
# @return {*}
#
def navigation_company_detail_page(company_id: int, company_name: str, onback: Callable[[], None]) -> None:
    app.storage.user['navigation'] = COMPANY_DETAIL_NAVIGATION
    app.storage.user['onback'] = onback
    app.storage.user['company_container'] = COMPANY_DETAIL_NAVIGATION
    app.storage.user['company_id'] = company_id
    app.storage.user['company_name'] = company_name
    ui.navigate.to('/')

def navigation_content_page(navigation: str):
    pass