from nicegui import ui

def normal_sm_black_label(text) -> ui.label:
    return ui.label(text).classes('font-normal text-sm text-black')

def normal_sm_gray_label(text) ->ui.label:
    return ui.label(text).classes('font-normal text-sm text-gray-400')

def bold_sm_black_label(text) -> ui.label:
    return ui.label(text).classes('font-bold text-sm text-black')

def normal_1g_black_label(text) -> ui.label:
    return ui.label(text).classes('font-normal text-1g text-black')
def bold_1g_black_label(text) -> ui.label:
    return ui.label(text).classes('font-bold text-1g text-black')
def bold_xl_black_label(text) -> ui.label:
    return ui.label(text).classes('font-bold text-xl text-black')