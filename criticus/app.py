from pathlib import Path
from types import FunctionType
import platform
import sys

import PySimpleGUI as sg 

from criticus.py.txt2json.window_text_to_json import txt_to_json
from criticus.py.combine_xml import combine_xml_files_interface as combine_xml
from criticus.py.md2tei.MarkdownTEI import md_to_tei
from criticus.py.tei2json.tei2json_ui import tei_to_json
from criticus.py.reformat_collation.reformat_xml_ui import start_reformat_ui as reform
from criticus.py.serve_tei_transcriptions.serve_tei_tx_ui import serve_tei_tx
from criticus.py.ce_config import configure_ce
from criticus.py.txt_from_json import get_text_from_json_files
from criticus.main_layout import main_layout
from criticus.py.export_to_docx.xml_to_docx_ui import export_to_docx
from criticus.py.check_for_updates import check_for_update
from criticus.py.analyze_collation.analyze_collation_ui import main as analyze

# if platform.system() == 'Windows':
from criticus.py.cbgm_interface.open_cbgm_ui import open_cbgm_ui

__version__ = '0.37.2'
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

def get_actual_dir():
    '''Since PyInstaller unpacks modules into a virtual 
    directory, this is required to get the actual absolute 
    path of the main directory both for dev and frozen states.'''
    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'): # shipped app
        return Path(sys.executable).parent.as_posix()
    else: # dev
        return Path(__file__).parent.as_posix()

def main():
    main_dir = get_actual_dir()
    sg.set_options(dpi_awareness=True)
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
    if platform.system() == 'Windows':
        icon = f'{main_dir}/resources/criticus.ico'
        font = ('Cambria', 11)
    else:
        icon = f'{main_dir}/resources/criticus.png'
        font = ('Arial', 11)
    window = sg.Window(f'Criticus v{__version__}', main_layout(), font=font, icon=icon, debugger_enabled=False)
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

        elif event == 'export_to_docx':
            open_new_window(export_to_docx, window, main_dir, font, icon)

        elif event == 'analyze_collation':
            open_new_window(analyze, window, main_dir, font, icon)

        elif event == 'Check for Updates':
            check_for_update(__version__)

    window.close()
