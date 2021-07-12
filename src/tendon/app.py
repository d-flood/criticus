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
from tendon.py.ce_config import configure_ce
from tendon.py.txt_from_json import get_text_from_json_files
from tendon.py.cbgm_interface.open_cbgm_ui import open_cbgm_ui

__version = '0.10'
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
    bs = (32, 2)
    sg.LOOK_AND_FEEL_TABLE['Parchment'] = {'BACKGROUND': '#FFE9C6',
                                        'TEXT': '#533516',
                                        'INPUT': '#EAC8A3',
                                        'TEXT_INPUT': '#2F1B0A',
                                        'SCROLL': '#B39B73',
                                        'BUTTON': ('white', '#C55741'),
                                        'PROGRESS': ('#01826B', '#D0D0D0'),
                                        'BORDER': 1, 'SLIDER_DEPTH': 0, 'PROGRESS_DEPTH': 0,
                                        }
    sg.theme('Parchment')
    main_dir = pathlib.Path(__file__).parent.as_posix()
    if platform.system() == 'Windows':
        icon = f'{main_dir}/resources/tendon.ico'
        font = ('Cambria', 11)
        open_cbgm = [sg.B('open-cbgm Interface', key='open-cbgm', size=bs)]
    else:
        icon = f'{main_dir}/resources/tendon.png'
        font = ('Arial', 12)
        open_cbgm = []
    layout = [
        [sg.Button('Plain Text to JSON', key='txt_to_json', size=bs)],
        [sg.Button('Get Plain Text from JSON', key='json_to_txt', size=bs)],
        [sg.Button('Markdown to TEI', key='md_to_tei', size=bs)],
        [sg.Button('TEI to JSON', key='tei_to_json', size=bs)],
        [sg.Button('Combine Collation Files', key='combine_verses', size=bs)],
        [sg.Button('Reformat Collation File', key='reformat_xml', size=bs)],
        [sg.Button('View TEI Transcriptions', key='tei_server', size=bs)],
        [sg.Button('Configure Collation Editor', key='ce_config', size=bs)],
        open_cbgm,
        [sg.Stretch(), sg.Button('Close', pad=(None, 20)), sg.Stretch()]
    ]
    window = sg.Window(f'Tendon v{__version}', layout, font=font, icon=icon)
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

        elif event == 'ce_config':
            open_new_window(configure_ce, window, main_dir, font, icon)

        elif event == 'json_to_txt':
            open_new_window(get_text_from_json_files, window, main_dir, font, icon)

        elif event == 'open-cbgm':
            open_new_window(open_cbgm_ui, window, main_dir, font, icon)

    window.close()
