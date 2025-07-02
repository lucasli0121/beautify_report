from nicegui import ui,app
from components import inputs
from dao.company_dao import CompanyDao
from utils import global_vars as g

def show_invoice_title_page() -> None:
    result, company_info = g.query_company_name_company()
    if result is False:
        ui.notify('查询公司信息失败')
        return
    options = list(company_info.keys())  # 获取所有公司名称
    def on_change(value):
        if value in company_info:
            company_dao = company_info[value]
            company_list = [company_dao]
            on_search(company_list)

    with ui.row().classes('w-full h-[60px] px-[20px] py-[10px] place-content-start items-center') \
        .style('background-color: #FFFFFF !important; border-radius: 10px;'):
        inputs.selection_w80(options, None, need_input=True, on_change=on_change)
    app.storage.client['invoice_title_card'] = ui.card().classes('w-full h-full px-[20px] mt-2 place-content-start gap-0')
    on_search(list(company_info.values()))
    

def on_search(company_list: list[CompanyDao]) -> None:
    if 'invoice_title_card' not in app.storage.client:
        return
    invoice_title_card: ui.card = app.storage.client['invoice_title_card']
    invoice_title_card.clear()
    invoice_title_card.update()
    with invoice_title_card:
        for company_dao in company_list:
            if not isinstance(company_dao, CompanyDao):
                continue
            with ui.row().classes('w-full px-[20px] py-[10px] mt-2 place-content-between gap-0 items-center') \
                .style('background-color: #F4F9FD !important; border-radius: 10px;'):
                with ui.column().classes('w-full items-center'):
                    with ui.row().classes('w-full items-center justify-start gap-2'):
                        ui.label('名称').classes('text-[16px] text-[#333333] font-medium')
                        ui.label('name').classes('text-[16px] text-[#333333] font-medium') \
                            .bind_text_from(company_dao, 'name')
                    with ui.row().classes('w-full items-center justify-start gap-2'):
                        ui.label('地址').classes('text-[16px] text-[#333333] font-medium')
                        ui.label('address').classes('text-[16px] text-[#333333] font-medium') \
                            .bind_text_from(company_dao, 'address')
                    with ui.row().classes('w-full items-center justify-start gap-2'):
                        ui.label('税号').classes('text-[16px] text-[#333333] font-medium')
                        ui.label('tax_no').classes('text-[16px] text-[#333333] font-medium') \
                            .bind_text_from(company_dao, 'tax_no')
                    with ui.row().classes('w-full items-center justify-start gap-2'):
                        ui.label('联系人').classes('wtext-[16px] text-[#333333] font-medium')
                        ui.label('phone').classes('text-[16px] text-[#333333] font-medium') \
                            .bind_text_from(company_dao, 'contacts')
                    with ui.row().classes('w-full items-center justify-start gap-2'):
                        ui.label('电话').classes('text-[16px] text-[#333333] font-medium')
                        ui.label('phone').classes('text-[16px] text-[#333333] font-medium') \
                            .bind_text_from(company_dao, 'phone')