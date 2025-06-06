from queue import Queue
from nicegui import ui, app
import threading as thread
from components import tables, cards, inputs
from dao.person_report_dao import PersonReportDao, get_person_report_by_student_id
from dao.company_dao import CourseDao
from dao.progress_value import ProgressValue
from utils.make_png import generate_png

download_progress_value = ProgressValue(0.0)

def show_person_report_page(course_id: int, id: int) -> None:
    course_dao = CourseDao()
    course_dao.id = course_id
    status, result = course_dao.get_course_by_id()
    if status != 200:
        ui.notify(f'获取课程信息失败, {result}')
        return
    app.storage.user['course_dao'] = course_dao
    status, report_result = get_person_report_by_student_id(id)
    if status != 200:
        ui.notify(f'获取个人报告信息失败, {report_result}')
        return
    if isinstance(report_result, PersonReportDao):
        person_report_dao : PersonReportDao = report_result
        app.storage.user["person_report_dao"] = person_report_dao
    with ui.column().classes('w-full gap-0 mt-0 p-[15px] items-center place-content-start') \
        .style('background-color: #FFFFFF !important; border-radius: 10px;'):
        with ui.row().classes('w-full gap-0 items-center place-content-between'):
            with ui.row().classes('items-center place-content-start gap-0'):
                ui.icon('square').classes('text-[#65B6FF] w-[6px] h-[20px]')
                ui.label('赵雨晨').classes('ml-2 font-bold text-[#333333] text-[18px]') \
                    .bind_text_from(app.storage.user["person_report_dao"], 'student_name')
                ui.label('>').classes('ml-2 text-[#888888] text-[18px]')
                # inputs.input_search_w40('搜索学生', on_enterkey=lambda e: ui.notify(e))
            with ui.row().classes('items-center place-content-end'):
                ui.button('打印', icon='img:/static/images/printer@2x.png', on_click=print_person_report) \
                    .classes('w-25 rounded-md text-white') \
                    .style('background-color: #27CACA !important; border-radius: 6px;')
                app.storage.client['download_button'] = ui.button('下载', icon='img:/static/images/download@2x.png', on_click=download_person_report) \
                    .classes('w-25 rounded-md text-white') \
                    .style('background-color: #65B6FF !important; border-radius: 6px;')
                download_progress_ui = ui.circular_progress(value=0.0, min=0.0, max=1.0, show_value=True) \
                    .classes('w-[30px] h-[30px]') \
                    .style('color: #65B6FF !important; background-color: #FFFFFF !important; border-radius: 50% !important;')
                download_progress_ui.bind_value_from(download_progress_value, 'value')
                app.storage.client['download_progress_ui'] = download_progress_ui
                app.storage.client['download_progress_ui'].visible = False
        with ui.row().classes('w-full mt-2 items-center place-content-start'):
            ui.icon('img:/static/images/group_student@2x.png').classes('w-[40px] h-[40px]')
            ui.label('一(4)班').classes('ml-2 text-[#333333] text-[14px]') \
                .bind_text_from(app.storage.user["course_dao"], 'classes')
        with ui.row().classes('w-full mt-2 gap-0 items-center place-content-start'):
            ui.icon('img:/static/images/subject@2x.png').classes('w-[40px] h-[40px]')
            ui.label('科目').classes('ml-2 text-[#888888] text-[14px]')
            ui.label('数学').classes('ml-2 text-[#008DFF] text-[14px]') \
                .bind_text_from(app.storage.user["course_dao"], 'subject')
            ui.icon('img:/static/images/teacher@2x.png').classes('ml-5 w-[40px] h-[40px]')
            ui.label('任课老师').classes('ml-2 text-[#888888] text-[14px]')
            ui.label('张明华').classes('ml-2 text-[#008DFF] text-[14px]') \
                .bind_text_from(app.storage.user["course_dao"], 'teacher')
            ui.icon('img:/static/images/student@2x.png').classes('ml-5 w-[40px] h-[40px]')
            ui.label('学生人数').classes('ml-2 text-[#888888] text-[14px]')
            ui.label('46').classes('ml-2 text-[#008DFF] text-[14px]') \
                .bind_text_from(app.storage.user["course_dao"], 'student_num')
            ui.label('人').classes('ml-2 text-[#008DFF] text-[14px]')
            ui.icon('img:/static/images/calendar_2@2x.png').classes('ml-5 w-[40px] h-[40px]')
            ui.label('开始时间').classes('ml-2 text-[#888888] text-[14px]')
            ui.label('2024-01-08 08:00').classes('ml-2 text-[#008DFF] text-[14px]') \
                .bind_text_from(app.storage.user["course_dao"], 'begin_time')
            ui.icon('img:/static/images/course_time_long@2x.png').classes('ml-5 w-[40px] h-[40px]')
            ui.label('课程时长').classes('ml-2 text-[#888888] text-[14px]')
            ui.label('45').classes('ml-2 text-[#008DFF] text-[14px]') \
                .bind_text_from(app.storage.user["course_dao"], 'duration')
            ui.label('分钟').classes('ml-2 text-[#008DFF] text-[14px]')
    with ui.row().classes('w-full h-[150px] gap-0 mt-3 items-center justify-between'):
        with ui.card().classes('h-full p-2 items-center gap-0') \
            .props('flat no-shadow') \
            .style('background-color: #FFFFFF !important; border-radius: 10px; width: 29% !important;'):
            with ui.row().classes('size-full gap-0 items-center place-content-around') \
                .style('background-color: #E2F2FF !important; border-radius: 4px;'):
                with ui.column().classes('h-full gap-0 items-center place-content-center'):
                    ui.label('深度专注总时长').classes('text-[#333333] text-[18px]')
                    with ui.row().classes('gap-0 items-center place-content-center'):
                        ui.label('30').classes('text-[#333333] text-[30px]') \
                            .bind_text_from(app.storage.user["person_report_dao"], 'deep_concentration_total_time')
                        ui.label('分钟').classes('text-[#333333] text-[30px]')
                ui.icon('img:/static/images/total_time_long@2x.png').classes('w-[70px] h-[70px]')
        with ui.card().classes('w-1/4 h-full p-2 items-center gap-0') \
            .props('flat no-shadow') \
            .style('background-color: #FFFFFF !important; border-radius: 10px; width: 29% !important;'):
            with ui.row().classes('size-full gap-0 items-center place-content-around') \
                .style('background-color: #F1F2FF !important; border-radius: 4px;'):
                with ui.column().classes('h-full gap-0 items-center place-content-center'):
                    ui.label('深度专注最长时间').classes('text-[#333333] text-[18px]')
                    with ui.row().classes('gap-0 items-center place-content-center'):
                        ui.label('10').classes('text-[#333333] text-[30px]') \
                            .bind_text_from(app.storage.user["person_report_dao"], 'deep_concentration_max_time')
                        ui.label('分钟').classes('text-[#333333] text-[30px]')
                ui.icon('img:/static/images/max_time_long@2x.png').classes('w-[70px] h-[70px]')
        with ui.card().classes('w-1/4 h-full p-2 items-center gap-0') \
            .props('flat no-shadow') \
            .style('background-color: #FFFFFF !important; border-radius: 10px; width: 29% !important;'):
            with ui.row().classes('size-full gap-0 items-center place-content-around') \
                .style('background-color: #E8F9EA !important; border-radius: 4px;'):
                with ui.column().classes('h-full gap-0 items-center place-content-center'):
                    ui.label('坐姿不端正时间').classes('text-[#333333] text-[18px]')
                    with ui.row().classes('gap-0 items-center place-content-center'):
                        ui.label('5').classes('text-[#333333] text-[30px]') \
                            .bind_text_from(app.storage.user["person_report_dao"], 'posture_not_correct_time')
                        ui.label('分钟').classes('text-[#333333] text-[30px]')
                ui.icon('img:/static/images/inposture_time_long@2x.png').classes('w-[70px] h-[70px]')
    with ui.row().classes('w-full h-[400px] gap-0 mt-3 items-center justify-between'):
        with ui.column().classes('gap-0 p-[15px] items-center') \
            .style('background-color: #FFFFFF !important; border-radius: 10px; width: 30% !important; height: 100% !important;'):
            ui.label('专注度分布').classes('w-full font-bold text-[16px] text-[#333333]')
            with ui.row().classes('w-full mt-2 items-center place-content-start'):
                ui.icon('square').classes('text-[#65B6FF] w-4 h-4')
                ui.label('深度专注').classes('ml-1 text-[#333333] text-[12px]')
                ui.icon('square').classes('text-[#4D82FB] w-4 h-4 ml-5')
                ui.label('中专注度').classes('ml-1 text-[#333333] text-[12px]')
                ui.icon('square').classes('text-[#FFA137] w-4 h-4 ml-5')
                ui.label('浅专注度').classes('ml-1 text-[#333333] text-[12px]')
            low_concentration_time = app.storage.user["person_report_dao"].person_concentration.low_concentration_time
            mid_concentration_time = app.storage.user["person_report_dao"].person_concentration.mid_concentration_time
            deep_concentration_time = app.storage.user["person_report_dao"].person_concentration.deep_concentration_time
            with ui.card().classes('w-full mt-2 flex-1').props('flat no-shadow'):
                ui.echart({
                    'series': [
                        {
                            'type': 'pie',
                            'radius': ['30%', '60%'],
                            'label': {
                                'fontSize': 12,
                                'formatter': '{b}: {c}分钟',
                            },
                            'data': [
                                {'value': low_concentration_time, 'name': '浅度专注', 'itemStyle': {'color': '#FFA137'}},
                                {'value': mid_concentration_time, 'name': '中度专注', 'itemStyle': {'color': '#4D82FB'}},
                                {'value': deep_concentration_time, 'name': '深度专注', 'itemStyle': {'color': '#65B6FF'}},
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
                }).classes('w-full h-full')
        with ui.column().classes('gap-0 p-[15px] items-center') \
            .style('background-color: #FFFFFF !important; border-radius: 10px; width: 30% !important; height: 100% !important;'):
            with ui.row().classes('w-full h-[55px] items-center place-content-between'):
                ui.label('学习记录').classes('font-bold text-[16px] text-[#333333] self-center')
                # ui.echart(options={
                #     'series': [
                #         {
                #             'type': 'gauge',
                #             'radius': '100%',
                #             'startAngle': 90,
                #             'endAngle': -270,
                #             'pointer':{
                #                 'show': 0,
                #             },
                #             'progress': {
                #                 'show': 1,
                #                 'overlap': 0,
                #                 'roundCap': 1,
                #                 'clip': 0,
                #                 'itemStyle': {
                #                     'borderWidth': 0,
                #                     'borderColor': '#71B4FF'
                #                 }
                #             },
                #             'axisLine': {
                #                 'lineStyle': {
                #                     'width': 10
                #                 }
                #             },
                #             'axisTick': {
                #                 'show': 0
                #             },
                #             'axisLabel': {
                #                 'show': 0,
                #                 'distance': 10
                #             },
                #             'splitLine': {
                #                 'show': 0,
                #                 'distance': 0,
                #                 'length': 10
                #             },
                #             'title': {
                #                 'fontSize': 12
                #             },
                #             'detail': {
                #                 'valueAnimation': 1,
                #                 'formatter': '{value}分',
                #                 'fontSize': 10,
                #             },
                #             'data': [
                #                 {
                #                     'value': 42,
                #                     'title': {
                #                         'offsetCenter': ['0%', '0%']
                #                     },
                #                     'detail': {
                #                         'valueAnimation': 1,
                #                         'offsetCenter': ['0%', '0%']
                #                     }
                #                 }
                #             ]
                #         }
                #     ]
                # }).classes('w-[50px] h-[50px] self-center')
            focus_score = app.storage.user["person_report_dao"].study_score.focus_score
            posture_score = app.storage.user["person_report_dao"].study_score.posture_score
            with ui.card().classes('w-full mt-2 flex-1').props('flat no-shadow'):
                ui.echart({
                    'tooltip': {
                        'trigger': 'axis',
                        'axisPointer': {
                            'type': 'shadow'
                        }
                    },
                    'grid': {
                        'left': '3%',
                        'right': '4%',
                        'top': '3%',
                        'bottom': '3%',
                        'containLabel': 1
                    },
                    'xAxis': {
                        'data': ['学习专注度', '坐姿管理'],
                        'axisLabel': {
                            'inside': 0,
                            'color': '#333333',
                            'fontSize': 14,
                        },
                        'axisTick': {
                            'show': 0
                        },
                        'axisLine': {
                            'show': 0,
                            'color': '#65B6FF'
                        },
                    },
                    'yAxis': {
                        'axisLabel': {
                            'inside': 0,
                            'color': '#333333',
                            'fontSize': 14,
                        },
                        'axisTick': {
                            'show': 0
                        },
                        'axisLine': {
                            'show': 0,
                        },
                        'type': 'value',
                        'max': 100
                    },
                    
                    'series': [
                        {
                            'type': 'bar',
                            'barWidth': '30%',
                            'showBackground': 1,
                            'itemStyle': {
                                'color': {
                                    'type': 'linear',
                                    'x': 0,
                                    'y': 0,
                                    'x2': 0,
                                    'y2': 1,
                                    'colorStops': [
                                        { 'offset': 0, 'color': '#D9EDFF' },
                                        { 'offset': 1, 'color': '#65B6FF' }
                                    ],
                                }
                            },
                            'data': [focus_score, posture_score]
                        }
                    ]
                }).classes('w-full h-full p-0 gap-0')
        app.storage.user["person_report_dao"].person_flow_state.sort(key=lambda x: x.start_time)
        flow_time_data = [app.storage.user["person_report_dao"].person_flow_state[i].start_time for i in range(len(app.storage.user["person_report_dao"].person_flow_state))]
        flow_state_data = [app.storage.user["person_report_dao"].person_flow_state[i].flow_state for i in range(len(app.storage.user["person_report_dao"].person_flow_state))]
        with ui.column().classes('gap-0 p-[15px] items-center') \
            .style('background-color: #FFFFFF !important; border-radius: 10px; width: 30% !important; height: 100% !important;'):
                ui.label('学习状态详情').classes('font-bold text-[16px] text-[#333333] place-self-start')
                with ui.card().classes('w-full mt-2 flex-1').props('flat no-shadow'):
                    ui.echart({
                        'tooltip': {
                            'trigger': 'axis',
                            'axisPointer': {
                                'type': 'shadow'
                            }
                        },
                        'grid': {
                            'left': '3%',
                            'right': '4%',
                            'top': '3%',
                            'bottom': '3%',
                            'containLabel': 1
                        },
                        'xAxis': {
                            'axisTick': {
                                'show': 0
                            },
                            'type': 'category',
                            'data': flow_time_data
                        },
                        'yAxis': {
                            'type': 'value'
                        },
                        'series': [
                            {
                                'type': 'line',
                                'stack': 'Total',
                                'areaStyle': {},
                                'smooth': 1,
                                'min': 0,
                                'max': 100,
                                'data': flow_state_data,
                            },
                        ]
                    }).classes('w-full h-full')
        

@ui.page('/person_report/{course_id}/{student_id}')
def report_page(course_id: int, student_id: int):
    show_person_report_page(course_id, student_id)

def print_person_report() ->None:
    ui.notify('打印个人报告')

download_status_queue = Queue[int]()

def download_person_report() ->None:
    if 'download_progress_ui' in app.storage.client:
        app.storage.client['download_progress_ui'].visible = True
    if 'download_button' in app.storage.client:
        app.storage.client['download_button'].visible = False
    student_id = app.storage.user["person_report_dao"].student_id
    course_id = app.storage.user['course_dao'].id
    student_name = app.storage.user["person_report_dao"].student_name
    url = f"http://localhost:8083/person_report/{course_id}/{student_id}"
    outfile = f'./static/{student_name}_report.png'
    download_progress_value.set_value(0.0)
    def check_download_queue():
        if not download_status_queue.empty():
            value = download_status_queue.get()
            if isinstance(value, int):
                if value == 10:
                    download_progress_value.set_value(1.0)
                    if 'download_progress_ui' in app.storage.client:
                        app.storage.client['download_progress_ui'].visible = False
                    if 'download_button' in app.storage.client:
                        app.storage.client['download_button'].visible = True
                    if 'download_timer' in app.storage.client:
                        app.storage.client['download_timer'].cancel()
                    ui.download(outfile, f'{student_name}_report.png')
                    ui.notify(f'{student_name}报告下载完成')
                else:
                    v = value / 10
                    download_progress_value.set_value(v)
                
            else:
                ui.notify('课程报告下载失败')
                if 'download_progress_ui' in app.storage.client:
                    app.storage.client['download_progress_ui'].visible = False
                if 'download_button' in app.storage.client:
                    app.storage.client['download_button'].visible = True
                if 'download_timer' in app.storage.client:
                    app.storage.client['download_timer'].cancel()
    if 'download_timer' in app.storage.client:
        app.storage.client['download_timer'].cancel()
    app.storage.client['download_timer'] = ui.timer(1, callback=check_download_queue, immediate=True)
    app.storage.client['download_timer'].activate()
    thr = thread.Thread(target=generate_png, args=(url, outfile, download_status_queue))
    thr.start()