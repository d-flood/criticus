import pathlib
from types import FunctionType
import platform

import PySimpleGUIQt as sg 
from tendon.py.txt2json.window_text_to_json import txt_to_json
import tendon.py.edit_settings as es
from tendon.py.combine_xml import combine_xml_files_interface as combine_xml
from tendon.py.md2tei.MarkdownTEI import md_to_tei
from tendon.py.tei2json.tei2json_ui import tei_to_json
from tendon.py.reformat_collation.reformat_xml_ui import start_reformat_ui as reform
from tendon.py.serve_tei_transcriptions.serve_tei_tx_ui import serve_tei_tx

#pylint: disable=no-member

def open_new_window(function: FunctionType, window: sg.Window, main_dir, font, icon, include_main_dir=False):
    window.hide()
    stay_open = True
    while stay_open:
        if include_main_dir:
            stay_open = function(main_dir, font, icon)
        else:
            stay_open = function(font, icon)
    window.un_hide()

def main():
    sg.LOOK_AND_FEEL_TABLE['Parchment'] = {'BACKGROUND': '#FFE9C6',
                                        'TEXT': '#533516',
                                        'INPUT': '#EAC8A3',
                                        'TEXT_INPUT': '#2F1B0A',
                                        'SCROLL': '#B39B73',
                                        'BUTTON': ('white', '#C55741'),
                                        'PROGRESS': ('#01826B', '#D0D0D0'),
                                        'BORDER': 3, 'SLIDER_DEPTH': 0, 'PROGRESS_DEPTH': 0,
                                        }
    sg.theme('Parchment')
    main_dir = pathlib.Path(__file__).parent.as_posix()
    if platform.system() == 'Windows':
        icon = f'{main_dir}/resources/tendon.ico'
        font = ('Cambria', 12)
    else:
        icon = f'{main_dir}/resources/tendon.png'
        font = ('Cambria', 14)
    layout = [
        [sg.Button('               Plain Text to JSON               ', key='txt_to_json')],
        [sg.Button('Markdown to TEI', key='md_to_tei')],
        [sg.Button('TEI to JSON', key='tei_to_json')],
        [sg.Button('Combine Collation Files', key='combine_verses')],
        [sg.Button('Reformat Collation File', key='reformat_xml')],
        [sg.Button('View TEI Transcriptions', key='tei_server')],
        [sg.Stretch(), sg.Button('Close'), sg.Stretch()]
    ]
    window = sg.Window('Tendon v0.2', layout, font=font, icon=icon)
    while True:
        event, _ = window.read()

        if event in [sg.WIN_CLOSED, None, 'Close']:
            break

        elif event == 'txt_to_json':
            open_new_window(txt_to_json, window, main_dir, font, icon)

        elif event == 'combine_verses':
            open_new_window(combine_xml, window, main_dir, font, icon, include_main_dir=True)

        elif event == 'md_to_tei':
            open_new_window(md_to_tei, window, main_dir, font, icon)

        elif event == 'tei_to_json':
            open_new_window(tei_to_json, window, main_dir, font, icon)

        elif event == 'reformat_xml':
            open_new_window(reform, window, main_dir, font, icon)

        elif event == 'tei_server':
            open_new_window(serve_tei_tx, window, main_dir, font, icon, include_main_dir=True)

    window.close()
