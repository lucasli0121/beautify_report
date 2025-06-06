'''
Author: liguoqiang
Date: 2025-03-15 16:18:09
LastEditors: liguoqiang
LastEditTime: 2025-03-16 17:13:05
Description: 
'''
from nicegui import ui

ui.add_css('''
    .custom-border.q-field--outlined .q-field__control:before {
        border: 1px solid #65B6FF !important;
    }
''')

# 登录用户输入框
def input_user_w60(placeholder, on_enterkey) -> ui.input:
    with ui.input(placeholder=placeholder) \
        .props('autofocus outlined rounded') \
        .classes('w-[370px] h-[64px] self-center item-center') as input:
        with input.add_slot('prepend'):
            ui.icon('img:/static/images/user.png').on('click', on_enterkey).classes('cursor-pointer')
    input.on('keydown.enter', on_enterkey)
    return input

def input_password_w60(placeholder, on_enterkey) -> ui.input:
    with ui.input(placeholder=placeholder, password=True, password_toggle_button=True) \
        .props('autofocus outlined rounded') \
        .classes('w-[370px] h-[64px] self-center item-center') as input:
        with input.add_slot('prepend'):
            ui.icon('img:/static/images/password.png').on('click', on_enterkey).classes('cursor-pointer')
    input.on('keydown.enter', on_enterkey)
    return input

def input_search_w40(placeholder, on_enterkey) -> ui.input:
    with ui.input(placeholder=placeholder) \
        .props('autofocus outlined dense') \
        .classes('w-40 rounded-md self-center custom-border') as input:
        with input.add_slot('append'):
            ui.icon('img:/static/images/search@2x.png').on('click', on_enterkey).classes('cursor-pointer')
    input.on('on_enterkey', on_enterkey)
    input.on('keydown.enter', on_enterkey)
    return input

def input_search_w60(placeholder, on_enterkey) -> ui.input:
    with ui.input(placeholder=placeholder) \
        .props('autofocus rounded-md outlined dense') \
        .classes('w-60 self-center item-center ') as input:
        input.add_slot('append', r'''
            <q-btn flat round dense icon="search" @click="() => $parent.$emit('on_enterkey')"/>
        ''')
    input.on('on_enterkey', on_enterkey)
    input.on('keydown.enter', on_enterkey)
    return input

def date_input_w40(placeholder, on_enterkey) -> ui.input:
    with ui.input(placeholder=placeholder) \
        .props('autofocus rounded-md outlined dense') \
        .classes('w-40 self-center item-center ') as date_input:
        with ui.menu().props('no-parent-event') as menu:
            with ui.date().bind_value(date_input).on_value_change(on_enterkey):
                with ui.row().classes('justify-end'):
                    ui.button('Close', on_click=menu.close).props('flat')
    with date_input.add_slot('append'):
        ui.icon('img:/static/images/calendar@2x.png').on('click', menu.open).classes('cursor-pointer')
    date_input.on('keydown.enter', on_enterkey)
    return date_input

def selection_w40(options, value, on_change) -> ui.select:
    return ui.select(options=options, value=value, with_input=False, on_change=lambda e: on_change(e.value)) \
        .props('autofocus rounded-md outlined dense') \
        .classes('w-40 self-center item-center transition-all')

def show_add_device_input(placeholder) -> ui.input:
    intput = ui.input(placeholder=placeholder) \
        .props('rounded-md outlined dense') \
        .classes('size-full self-center item-center custom-border')
    return intput