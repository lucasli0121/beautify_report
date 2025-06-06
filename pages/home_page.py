from nicegui import ui, app

def show_home_page() -> None:
    with ui.row().classes('w-full h-full px-[20px] mt-0 place-content-between gap-0') \
        .style('background-color: #F4F9FD !important; border-radius: 10px;'):
        with ui.column().classes('w-full h-full items-center'):
            ui.label('欢迎使用').classes('text-[24px] text-[#333333] font-bold')
            ui.label('这是一个示例首页').classes('text-[16px] text-[#333333] font-medium')