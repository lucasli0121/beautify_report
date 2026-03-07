from dataclasses import dataclass
from nicegui import ui,events, app, run
from components import inputs, tables,cards
from typing import Optional
from datetime import datetime
from utils import global_vars as g
from dao.tax_approval_dao import TaxApprovalDao

@dataclass
class SearchCondition:
    select_year: str = ""
search_condition = SearchCondition()

async def show_tax_brief_stat_page():
    with ui.row().classes('w-full h-[80px] px-[20px] mt-0 place-content-start') \
        .style('background-color: #FFFFFF !important; border-radius: 10px;'):
        with ui.row().classes('h-full items-center'):
            curyear = datetime.now().year
            years_value = [f'{year}年' for year in range(curyear, 2020, -1)]
            inputs.selection_w40(years_value, years_value[0], False, None) \
                .bind_value_to(search_condition, 'select_year')
        with ui.row().classes('h-full items-center'):
            ui.button('刷新', icon='img:/static/images/refresh@2x.png', on_click=on_search) \
                .classes('w-25 rounded-md text-white') \
                .style('background-color: #6C96FB !important')
            
    out_grid_columns = 13*6 + 2
    with ui.row().classes('w-full px-[20px] mt-2 place-content-start flex flex-col') \
        .style('height: calc(100dvh - 80px); background-color: #FFFFFF !important; border-radius: 10px;'):
        with ui.scroll_area().classes('w-full h-full flex-1') \
            .style('background-color: #FFFFFF !important; border-radius: 10px; overflow-x: auto;'):
            app.storage.client['tax_brief_grid'] = ui.grid(columns=out_grid_columns).classes('w-full h-full gap-0 items-center')\
                .style('grid-template-columns: repeat(80,60px)')
    await on_search()
                        
            

async def on_search() -> None:
    if 'tax_brief_grid' not in app.storage.client:
        return
    app.storage.client['tax_brief_grid'].clear()
    result, company_info = g.query_company_name_company()
    if result is False:
        ui.notify('查询公司信息失败')
        return
    with app.storage.client['tax_brief_grid']:
        ui.label('').classes('col-span-2 text-lx font-bold')
        ui.label('年度合计').classes('col-span-6 flex justify-center text-lx font-bold border p-1 border-gray-300')
        for i in range(1, 13):
            ui.label(f'{i}月').classes('col-span-6 flex justify-center text-lx font-bold border p-1 border-gray-300')
        ui.label('').classes('col-span-2 text-lx font-bold')
        for i in range(1, 14):
            ui.label('增值税').classes('text-sm flex justify-center font-normal border-l border-b p-1 border-gray-300')
            ui.label('附加').classes('text-sm flex justify-center font-normal border-b p-1 border-gray-300')
            ui.label('印花税').classes('text-sm flex justify-center font-normal border-b p-1 border-gray-300')
            ui.label('所得税').classes('text-sm flex justify-center font-normal border-b p-1 border-gray-300')
            ui.label('其他税').classes('text-sm flex justify-center font-normal border-b p-1 border-gray-300')
            ui.label('合计').classes('text-sm flex justify-center font-normal border-r border-b p-1 border-gray-300')
        def do_search() -> tuple[bool, list[dict], str]:
            rows = []
            for company in company_info.values():
                if company.brief_name is None or len(company.brief_name) == 0:
                    continue
                company_dict = {company.brief_name:{}}
                year_dict = {'year_tax_value': 0.0, 'year_attach_value': 0.0, 'year_stamp_value': 0.0, 'year_income_value': 0.0, 'year_other_value': 0.0, 'year_total_value': 0.0}
                month_dict = {}
                for i in range(1, 13):
                    month_dict[f'{i}'] = {'month_tax_value': 0.0, 'month_attach_value': 0.0, 'month_stamp_value': 0.0, 'month_income_value': 0.0, 'month_other_value': 0.0, 'month_total_value': 0.0}
                    result, tax_values = g.my_db.query_tax_approval_by_period_date(company.id, f'{search_condition.select_year[:-1]}-{i:02d}')
                    if result and tax_values and len(tax_values) > 0:
                        for tax_value in tax_values:
                            dao = TaxApprovalDao()
                            dao.from_db(tax_value)
                            
                            match dao.tax_type:
                                case '增值税':
                                    month_dict[f'{i}']['month_tax_value'] += dao.paid_in_money
                                case '地方教育附加':
                                    month_dict[f'{i}']['month_attach_value'] += dao.paid_in_money
                                case '教育费附加':
                                    month_dict[f'{i}']['month_attach_value'] += dao.paid_in_money
                                case '城市维护建设税':
                                    month_dict[f'{i}']['month_attach_value'] += dao.paid_in_money
                                case '印花税':
                                    month_dict[f'{i}']['month_stamp_value'] += dao.paid_in_money
                                case '企业所得税':
                                    month_dict[f'{i}']['month_income_value'] += dao.paid_in_money
                                case _:
                                    month_dict[f'{i}']['month_other_value'] += dao.paid_in_money
                            month_dict[f'{i}']['month_total_value'] += dao.paid_in_money
                        year_dict['year_tax_value'] += month_dict[f'{i}']['month_tax_value']
                        year_dict['year_attach_value'] += month_dict[f'{i}']['month_attach_value']
                        year_dict['year_stamp_value'] += month_dict[f'{i}']['month_stamp_value']
                        year_dict['year_income_value'] += month_dict[f'{i}']['month_income_value']
                        year_dict['year_other_value'] += month_dict[f'{i}']['month_other_value']
                        year_dict['year_total_value'] += month_dict[f'{i}']['month_total_value']
                values = {'company': company, 'year_dict': year_dict}
                for i in range(1, 13):
                    values[f'month_dict_{i}'] = month_dict[f'{i}']
                company_dict[company.brief_name] = values
                rows.append(company_dict)
            return True, rows, ''
            
        refresh_dialog = g.show_refresh_process("统计中，请稍候")
        success, rows, message = await run.io_bound(do_search)
        if not success:
            ui.notify(message or '查询记录失败')
        refresh_dialog.close()
        for row in rows:
            for company_name, values in row.items():
                ui.label(company_name).classes('col-span-2 text-sm flex justify-center font-normal border-r border-b p-1 border-gray-300')
                year_dict = values['year_dict']
                year_tax_value = year_dict['year_tax_value']
                year_attach_value = year_dict['year_attach_value']
                year_stamp_value = year_dict['year_stamp_value']
                year_income_value = year_dict['year_income_value']
                year_other_value = year_dict['year_other_value']
                year_total_value = year_dict['year_total_value']
                year_tax_value_label = ui.label('').classes('text-xs flex justify-center font-normal border-l border-b p-1 border-gray-300')
                year_attach_value_label = ui.label('').classes('text-xs flex justify-center font-normal border-b p-1 border-gray-300')
                year_stamp_value_label = ui.label('').classes('text-xs flex justify-center font-normal border-b p-1 border-gray-300')
                year_income_value_label = ui.label('').classes('text-xs flex justify-center font-normal border-b p-1 border-gray-300')
                year_other_value_label = ui.label('').classes('text-xs flex justify-center font-normal border-b p-1 border-gray-300')
                year_total_value_label = ui.label('').classes('text-xs flex justify-center font-normal border-r border-b p-1 border-gray-300')
                year_tax_value_label.set_text(g.format_currency(year_tax_value))
                year_attach_value_label.set_text(g.format_currency(year_attach_value))
                year_stamp_value_label.set_text(g.format_currency(year_stamp_value))
                year_income_value_label.set_text(g.format_currency(year_income_value))
                year_other_value_label.set_text(g.format_currency(year_other_value))
                year_total_value_label.set_text(g.format_currency(year_total_value))
                for i in range(1, 13):
                    month_dict = values[f'month_dict_{i}']
                    month_tax_value_label = ui.label('').classes('text-xs flex justify-center font-normal border-l border-b p-1 border-gray-300')
                    month_attach_value_label = ui.label('').classes('text-xs flex justify-center font-normal border-b p-1 border-gray-300')
                    month_stamp_value_label = ui.label('').classes('text-xs flex justify-center font-normal border-b p-1 border-gray-300')
                    month_income_value_label = ui.label('').classes('text-xs flex justify-center font-normal border-b p-1 border-gray-300')
                    month_other_value_label = ui.label('').classes('text-xs flex justify-center font-normal border-b p-1 border-gray-300')
                    month_total_value_label = ui.label('').classes('text-xs flex justify-center font-normal border-r border-b p-1 border-gray-300')
            
                    month_tax_value_label.set_text(g.format_currency(month_dict['month_tax_value']))
                    month_attach_value_label.set_text(g.format_currency(month_dict['month_attach_value']))
                    month_stamp_value_label.set_text(g.format_currency(month_dict['month_stamp_value']))
                    month_income_value_label.set_text(g.format_currency(month_dict['month_income_value']))
                    month_other_value_label.set_text(g.format_currency(month_dict['month_other_value']))
                    month_total_value_label.set_text(g.format_currency(month_dict['month_total_value']))
