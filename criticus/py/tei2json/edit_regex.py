import codecs

import PySimpleGUI as sg

import criticus.py.edit_settings as es


def unescape_string(text: str):
    return codecs.decode(text, 'unicode-escape')

def update_window(settings: dict, window: sg.Window):
    window['regexes'].update(settings['pre_parse_regex'])
    window['regex'].update('')
    window['replacement'].update('')

def add_regex(values: dict, window: sg.Window):
    settings = es.get_settings()
    regex = unescape_string(values['regex'])
    replacement = unescape_string(values['replacement'])
    settings['pre_parse_regex'].append(
        [regex, replacement]
    )
    update_window(settings, window)
    es.save_settings(settings)

def delete_selected(values: dict, window: sg.Window):
    settings = es.get_settings()
    new_regexes = []
    for reg in settings['pre_parse_regex']:
        if reg in values['regexes']:
            continue
        new_regexes.append(reg)
    settings['pre_parse_regex'] = new_regexes
    update_window(settings, window)
    es.save_settings(settings)

def create_layout(regexes: list = []):
    return [
        [sg.T('Regular Expression: '), sg.I('', key='regex'), sg.T('for'), sg.I('', key='replacement'), sg.B('Add')],
        [sg.Listbox(regexes, select_mode=sg.SELECT_MODE_EXTENDED, key='regexes', expand_x=True, expand_y=True)],
        [sg.B('Delete Selected')],
        [sg.B('Done')]
    ]

def edit_regex(icon):
    settings = es.get_settings()
    layout = create_layout(settings['pre_parse_regex'])

    window = sg.Window('Add/Remove Regular Expressions', layout, icon=icon, resizable=True)

    while True:
        event, values = window.read()
        if event in [sg.WIN_CLOSED, None, 'Done']:
            break
        elif event == 'Add':
            add_regex(values, window)
        elif event == 'Delete Selected':
            delete_selected(values, window)

    window.close()
