'''
Author: liguoqiang
Date: 2025-03-16 17:25:54
LastEditors: liguoqiang
LastEditTime: 2025-03-19 17:27:38
Description: 
'''
from typing import Callable
from nicegui import ui
from components import labels, progress

# 显示个人报告窗口
def person_report_dialog() -> ui.dialog:
    with ui.dialog(value=True).props('persistent brightness(40%)') as dialog, \
        ui.card().style('background-color: #f5f5f5; width: 50%; max-width: 50%; height: 90%;') as card:
        with ui.row().classes('w-full items-center place-content-end'):
            ui.button(icon='close', on_click=dialog.close).props('flat round dense').classes('text-red').style('background-color: #f5f5f5;')
        with ui.row().classes('w-full h-2/3 justify-center gap-0 place-content-between'):
            with ui.column().classes('w-1/2 h-full items-center gap-0'):
                with ui.row().classes('w-full place-self-center place-content-start'):
                    labels.bold_xl_black_label('张雨晨')
                with ui.row().classes('w-full mt-2 place-self-center place-content-start'):
                    labels.normal_sm_gray_label('班级')
                    labels.normal_sm_black_label('五年级3班').classes('ml-2')
                with ui.row().classes('w-full place-self-center place-content-start'):
                    labels.normal_sm_gray_label('科目')
                    labels.normal_sm_black_label('数学').classes('ml-2')
                with ui.row().classes('w-full place-self-center place-content-start'):
                    labels.normal_sm_gray_label('任课老师')
                    labels.normal_sm_black_label('张明华老师').classes('ml-2')
                ui.echart({
                    'legend': {'data': ['浅度专注','中度专注','深度专注']},
                    'series': [
                        {
                            'name':'专注时间分布',
                            'type': 'pie',
                            'radius': '40%',
                            'label': {
                                'fontSize': 12,
                                'formatter': '{b}: {c}分钟',
                            },
                            'data': [
                                {'value': 23, 'name': '浅度专注', 'itemStyle': {'color': '#fca5a5'}},
                                {'value': 52, 'name': '中度专注', 'itemStyle': {'color': '#6366f1'}},
                                {'value': 45, 'name': '深度专注', 'itemStyle': {'color': '#25d867'}},
                            ],
                            'emphasis': {
                                'itemStyle': {
                                    'shadowBlur': 10,
                                    'shadowOffsetX': 0,
                                    'shadowColor': 'rgba(0, 0, 0, 0.5)'
                                }
                            }
                        },
                    ]
                }).classes('w-full h-full mt-10 place-self-start')
            with ui.column().classes('w-1/2 h-full items-center gap-2'):
                with ui.row().classes('w-full item-center place-content-start'):
                    ui.label('09:06:12-09:30:59').classes('place-self-center text-xl font-blod text-black')
                    ui.echart(options={
                        'series': [
                            {
                                'type': 'gauge',
                                'radius': '100%',
                                'startAngle': 90,
                                'endAngle': -270,
                                'pointer':{
                                    'show': 0,
                                },
                                'progress': {
                                    'show': 1,
                                    'overlap': 0,
                                    'roundCap': 1,
                                    'clip': 0,
                                    'itemStyle': {
                                        'borderWidth': 0,
                                        'borderColor': '#464646'
                                    }
                                },
                                'axisLine': {
                                    'lineStyle': {
                                        'width': 10
                                    }
                                },
                                'axisTick': {
                                    'show': 0
                                },
                                'axisLabel': {
                                    'show': 0,
                                    'distance': 10
                                },
                                'splitLine': {
                                    'show': 0,
                                    'distance': 0,
                                    'length': 10
                                },
                                'title': {
                                    'fontSize': 12
                                },
                                'detail': {
                                    'valueAnimation': 1,
                                    'formatter': '{value}分',
                                    'fontSize': 10,
                                },
                                'data': [
                                    {
                                        'value': 42,
                                        'title': {
                                            'offsetCenter': ['0%', '0%']
                                        },
                                        'detail': {
                                            'valueAnimation': 1,
                                            'offsetCenter': ['0%', '0%']
                                        }
                                    }
                                ]
                            }
                        ]
                    }).style('width: 50px; height: 50px;')
                progress.show_concentration_progress(19)
                progress.show_position_progress(85)
                progress.show_study_progress(59)
                # ui.label('学习状态详情').classes('w-full mt-5 place-self-start text-xl font-blod text-black')
                ui.echart({
                    'title': {
                        'text': '学习状态详情',
                        'fontSize': 12,
                    },
                    'xAxis': {
                        'type': 'category',
                        'data': ['09:06:12', '09:07:07', '09:08:02', '09:08:57', '09:09:52']
                    },
                    'yAxis': {
                        'type': 'value'
                    },
                    'series': [
                        {
                            'type': 'line',
                            'smooth': 1,
                            'min': 0,
                            'max': 100,
                            'data': [10, 15, 23, 30, 62],
                        },
                    ]
                }).classes('mt-5 place-self-start').style('width: 100%; height: 50%;')
        with ui.row().classes('w-full justify-center gap-0 place-content-between'):
            with ui.column().classes('w-1/3 items-center gap-1 place-content-start'):
                ui.label('深度专注最长时间').classes('w-full place-self-center text-sm text-black')
                ui.label('45分钟').classes('w-full place-self-center text-1g text-black font-bold')
            with ui.column().classes('w-1/3 items-center gap-1 place-content-start'):
                ui.label('专注度最高分').classes('w-full place-self-center text-sm text-black')
                ui.label('98分').classes('w-full place-self-center text-1g text-black font-bold')
            with ui.column().classes('w-1/3 items-center gap-1 place-content-start'):
                ui.label('坐姿不端正时间').classes('w-full place-self-center text-sm text-black')
                ui.label('18分钟').classes('w-full place-self-center text-1g text-black font-bold')
    dialog.open()
    return dialog


# 显示课程监控窗口
def show_course_monitor_dialog(import_students, add_students) -> ui.dialog:
    with ui.dialog(value=True).props('persistent ') as dialog, \
        ui.card().classes('p-10').style('background-color: #f5f5f5; width: 75%; max-width: 75%; height: 100%;'):
        with ui.row().classes('w-full items-center place-content-between'):
            labels.bold_1g_black_label('XX中学智能学习教室')
            with ui.row().classes('items-center place-content-center'):
                labels.bold_1g_black_label('代课老师: 王老师')
                ui.button(icon='close', on_click=dialog.close).props('flat round dense').classes('bg-red-500 text-white')
        with ui.row().classes('w-full item-center place-content-between'):
            labels.bold_sm_black_label('体验班')
            with ui.row().classes('items-center place-content-end'):
                ui.button('批量导入', icon='upload', on_click=import_students).classes('text-black')
                ui.button('添加学生', icon='add', on_click=add_students).classes('text-black')
        for x in('A', 'B', 'C', 'D', 'E', 'F'):
            with ui.row().classes('w-full gap-3 mt-2 item-center place-content-start'):
                ui.label(f'{x}排').classes('text-black font-bold text-sm place-self-center')
                for i in range(8):
                    with ui.card().classes('p-2 gap-2').props('flat bordered').style('width: 120px; height: 90px;'):
                        with ui.row().classes('w-full gap-0 place-content-between'):
                            labels.normal_sm_black_label(f'{x}-{i+1}')
                            ui.icon('circle').classes('text-green-500 w-4 h-4')
                        with ui.row().classes('w-full gap-0 place-content-center'):
                            labels.normal_sm_black_label('刘婷婷')
                        with ui.row().classes('w-full gap-0 place-content-end'):
                            ui.icon('computer').classes('text-gray-300 w-4 h-4')
        with ui.row().classes('w-full gap-1 mt-2 item-center place-content-start'):
            ui.icon('square').classes('text-green-500 w-4 h-4')
            labels.normal_sm_black_label('深度专注')
            ui.icon('square').classes('text-yellow-500 ml-5 w-4 h-4')
            labels.normal_sm_black_label('中度专注')
            ui.icon('square').classes('text-red-500 ml-5 w-4 h-4')
            labels.normal_sm_black_label('浅度专注')
            ui.icon('computer').classes('text-green-500 ml-5 w-4 h-4')
            labels.normal_sm_black_label('设备在线')
            ui.icon('computer').classes('text-gray-500 ml-5 w-4 h-4')
            labels.normal_sm_black_label('设备离线')
        with ui.card().classes('w-full p-5').props('flat'):
            with ui.row().classes('w-full place-content-start'):
                labels.bold_sm_black_label('学习状况:')
            with ui.column().classes('w-full mt-3 place-content-start gap-1'):
                with ui.row().classes('w-full'):
                    labels.normal_sm_gray_label('10:46:05')
                    labels.normal_sm_black_label('刘婷婷同学专注度下降到中度专注')
                    
        
    dialog.open()
    return dialog

#
# 显示确认对话框
#
def make_sure_dialog(message: str, on_ok: Callable) -> ui.dialog:
    with ui.dialog().props('persistent') as dialog, ui.card() \
        .style('background-color: #FFFFFF !important; border-radius: 10px;'):
        ui.label(message).classes('w-full text-[16px] text-[#333333] font-normal')
        with ui.row().classes('w-full place-content-end'):
            ui.button('取消', color=None, on_click=dialog.close) \
                .props('flat') \
                .classes('w-[120px] text-[16px] text-[#888888] font-[400]') \
                .style('background-color: #FFFFFF !important;border-radius: 10px;border: 1px solid #888888;')
            def make_ok():
                try:
                    on_ok()
                    dialog.close()
                except Exception as e:
                    ui.notify(f'操作失败: {str(e)}')
            ui.button('确定', color=None, on_click=make_ok) \
                .props('flat') \
                .classes('w-[120px] text-[16px] text-white font-[400]') \
                .style('background-color: #65B6FF !important; border-radius: 10px')
    dialog.open()
    return dialog

def show_extents_fields_dialog(on_submit: Callable) -> None:
    with ui.dialog(value=True).props('persistent') as dialog, \
        ui.card().classes('p-10').style('background-color: #f5f5f5; width: 30%; max-width: 30%;'):
        ui.label('增加扩展字段').classes('w-full text-[20px] text-[#333333] font-medium')
        with ui.row().classes('w-full mt-1 place-content-start items-center'):
            ui.label('字段名称:').classes('w-[20%] text-[16px] text-[#333333] font-medium')
            field_input = ui.input(placeholder='请输入字段名称').props('rounded-md outlined dense').classes('w-[70%] self-center item-center')
        with ui.row().classes('w-full mt-2 place-content-center items-center'):
            def onOk():
                field_name = field_input.value.strip()
                if not field_name:
                    ui.notify('字段名称不能为空', color='red')
                    return
                on_submit(field_name)
                dialog.close()
            ui.button('提交', on_click=onOk) \
                .props('flat') \
                .classes('w-[120px] text-[16px] text-white font-[400]') \
                .style('background-color: #65B6FF !important; border-radius: 10px')
            ui.button('取消', on_click=dialog.close) \
                .props('flat') \
                .classes('w-[120px] text-[16px] text-[#888888] font-[400]') \
                .style('background-color: #FFFFFF !important;border-radius: 10px;border: 1px solid #888888;')
    dialog.open()