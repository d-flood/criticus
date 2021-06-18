import platform

import PySimpleGUIQt as sg

import tendon.py.edit_settings as es

from tendon.py.tei2json.tei_to_json import tei_to_json as t2j

# pylint: disable=no-member
def get_siglum_from_user(msg: str, title: str, icon) -> str:
    layout = [[sg.T(msg)], [sg.I('', key='input')], [sg.B('Submit')]]
    window = sg.Window(title, layout, icon=icon)
    siglum = ''
    while True:
        event, values = window.read()
        if event in [None, sg.WIN_CLOSED]:
            break
        elif event == 'Submit' and values['input'] != '':
            siglum = values['input']
            break
    window.close()
    return siglum

def get_space(s: str):
    return sg.T('          ')

def no_space():
    return sg.T('')

def layout(settings: dict):
    if platform.system() == 'Windows':
        space = no_space
    else:
        space = get_space
    input_frame = [
        [sg.I('', key='tei_input'), sg.FileBrowse(initial_folder=settings['tei_dir'], file_types=(('XML Files', '*.xml'), ))],
        [sg.Radio('Convert All Verses', 'all_or_one', key='all', enable_events=True)],
        [sg.Radio('Convert One Verse ', 'all_or_one', key='one', enable_events=True), sg.T('Reference'), sg.I('', key='single_ref', disabled=True, enable_events=True)]
    ]
    output_frame = [
        [sg.I(settings['ce_repo_dir'], key='output_dir'), sg.FolderBrowse(initial_folder=settings['ce_repo_dir'])]
    ]
    return [
        [sg.Frame('TEI Transcription File', input_frame)],
        [sg.Frame('Output Folder', output_frame)],
        [sg.B('Convert', disabled=True, key='convert'), space(), sg.B('Cancel', key='exit')]
        ]

def popup(msg: str, title: str):
    window = sg.Window(title, [[sg.T(msg)], [sg.B('OKAY')]])
    while True:
        event, _ = window.read()
        if event in ['OKAY', sg.WINDOW_CLOSED, None]:
            break
    window.close()

def save_settings(values):
    es.edit_settings('tei_dir', values['tei_input'])
    es.edit_settings('ce_repo_dir', values['output_dir'])

def enable_ui_elems(values: dict, window: sg.Window):
    if values['one'] is True:
        window['single_ref'].update(disabled=False)
    else:
        window['single_ref'].update(disabled=True)
        window['single_ref'].update('')
    if ((values['all'] is False and values['one'] is False)
    or (values['one'] is True and values['single_ref'] == '')):
        window['convert'].update(disabled=True)
    else:
        window['convert'].update(disabled=False)

def tei_to_json(font: tuple, icon):
    settings = es.get_settings()
    window = sg.Window('Convert TEI to JSON', layout(settings), font=font, icon=icon)

    while True:
        event, values = window.read()

        if event in [sg.WIN_CLOSED, 'exit', None]:
            break

        elif event in ['all', 'one', 'single_ref']:
            enable_ui_elems(values, window)

        elif event == 'convert':
            if values['tei_input'] == '' or values['output_dir'] == '':
                continue
            else:
                save_settings(values)
                # try:
                t2j(values['tei_input'], values['output_dir'], single_verse=values['single_ref'])
                popup(f'JSON transcription files saved to {values["output_dir"]}', 'Success!')
                print('success!')
                # except:
                #     print('conversion failed')
                #     popup('Conversion failed. Talk to David', 'Bummer...')

    window.close()
    return False
