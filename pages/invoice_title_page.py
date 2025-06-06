from nicegui import ui, app


def show_invoice_title_page() -> None:
    company_dao = app.storage.user['company_dao']
    if company_dao is None :
        ui.notify('请先选择公司')
        return
    with ui.row().classes('w-full h-full px-[20px] mt-0 place-content-between gap-0') \
        .style('background-color: #F4F9FD !important; border-radius: 10px;'):
        with ui.column().classes('w-full h-full items-center'):
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
                ui.label('tex_id').classes('text-[16px] text-[#333333] font-medium') \
                    .bind_text_from(company_dao, 'tex_id')
            with ui.row().classes('w-full items-center justify-start gap-2'):
                ui.label('联系人').classes('wtext-[16px] text-[#333333] font-medium')
                ui.label('phone').classes('text-[16px] text-[#333333] font-medium') \
                    .bind_text_from(company_dao, 'contacts')
            with ui.row().classes('w-full items-center justify-start gap-2'):
                ui.label('电话').classes('text-[16px] text-[#333333] font-medium')
                ui.label('phone').classes('text-[16px] text-[#333333] font-medium') \
                    .bind_text_from(company_dao, 'phone')
            