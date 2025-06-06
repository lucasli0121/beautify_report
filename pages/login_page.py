import os
from typing import Optional
from nicegui import ui,app
from fastapi.responses import RedirectResponse
from components import inputs

passwords = {'admin': 'admin', 'user': 'user'}

@ui.page('/login')
def login() -> Optional[RedirectResponse]:

    ui.add_css('''
        .q-page {
            padding: 0 !important;
            margin: 0 !important;
            width: 100% !important;
            height: 100% !important;
            background: url('/static/images/login_background@2x.png') no-repeat center center / cover !important;
        }
    ''')
    def try_login() -> None:
        if passwords.get(username.value) == password.value:
            app.storage.user.update({'username': username.value, 'authenticated': True})
            ui.navigate.to(app.storage.user.get('referrer_path', '/'))  # go back to where the user wanted to go
        else:
            ui.notify('账号或密码错误', color='negative')

    if app.storage.user.get('authenticated', False):
        return RedirectResponse('/')
    
    # ui.element('div').classes('item-center place-content-center') \
    #     .style('''
    #         position: absolute;
    #         left: 90px;
    #         top: 90px;
    #         width: 328px;
    #         height: 79px;
    #         background: url('/static/images/login_logo@2x.png') no-repeat center center / cover;
    #     ''')

        
    with ui.card().classes('place-content-center') \
        .style('''
            position: absolute;
            left: calc(55.0% - 0px);
            top: 50%;
            transform: translateY(-50%); /* 垂直居中 */
            width: 544px;
            height: 582px;
            border-radius: 20px;
        ''') as card:
        with ui.column().classes('size-full item-center place-content-evenly gap-0'):
            ui.label('登录').classes('text-[36px] text-center text-bold text-[#65B6FF] place-self-center')
            with ui.column().classes('w-full item-center place-content-between gap-[44px]'):
                username = inputs.input_user_w60('请输入账号', try_login)
                password = inputs.input_password_w60('请输入密码', try_login)
                ui.button('登录', on_click=try_login) \
                    .classes('w-[370px] h-[64px] self-center text-white rounded-[32px]') \
                    .style('background-color: #65B6FF; font-size:16px;')
    return None