import codecs
from pathlib import Path

import PySimpleGUI as sg

import criticus.py.edit_settings as es
import criticus.py.custom_popups as cp
from criticus.py.export_to_docx.xml_to_docx import export_xml_to_docx
from criticus.py import edit_settings as es


def unescape_string(text: str):
    return codecs.decode(text, 'unicode-escape')

def validate_form(values):
    for value in values:
        if values[value] == '':
            print(f'{values[value]=}')
            cp.ok('Please fill in all input fields', 'No Blanks, Please')
            return
        return True

def update_settings(settings: dict, values: dict):
    settings['text_wits_separator'] = unescape_string(values['text_wits_separator'])
    settings['rdg_n_text_separator'] = unescape_string(values['rdg_n_text_separator'])
    settings['wits_separator'] = unescape_string(values['wits_separator'])
    settings['words_per_line'] = values[ 'words_per_line']
    settings['text_bold'] = values['text_bold']
    settings['reformatted_xml_dir'] = Path(values['xml_filename']).parent.as_posix()
    es.save_settings(settings)

def export(settings, values: dict, collapse_regularized: bool = False, use_custom_template: bool = None, add_suffix: bool = False):
    if not validate_form(values):
        return
    update_settings(settings, values)
    # try:
    saved_file = export_xml_to_docx(values['xml_filename'], collapse_regularized, use_custom_template, add_suffix)
    if saved_file:
        cp.ok(f'Collation exported to {saved_file}', 'Success!')
    # except Exception as e:
    #     cp.ok(f'{e}', 'Failed to Export')

def layout(settings: dict):
    custom_template_path = es.get_settings()['custom_template_path']
    if  custom_template_path != '':
        template_parent = Path(custom_template_path).parent.as_posix()
    else:
        template_parent = None

    options_frame = [
        [
            sg.Checkbox('Use Custom Template', key='use_custom_template', enable_events=True), sg.Input(custom_template_path, key='custom_template_path', disabled=True), sg.FileBrowse(initial_folder=template_parent)
        ],
        [
            sg.T('Reading Text and Witnesses Separator: '), 
            sg.I(settings.get('text_wits_separator', ' // '), key='text_wits_separator')
        ],
        [
            sg.T('Reading ID and Reading Text Separator: '),
            sg.I(settings.get('rdg_n_text_separator', '\t'), key='rdg_n_text_separator')
        ],
        [
            sg.T('Witnesses Separator: '),
            sg.I(settings.get('wits_separator', '\t'), key='wits_separator')
        ],
        [
            sg.T('Basetext Words Per Line: '), 
            sg.Spin([i for i in range(1, 20)], initial_value=settings.get('words_per_line', 10), key='words_per_line')
        ],
        [
            sg.Check('Make Reading Text Bold', default=settings.get('text_bold', False), key='text_bold')
        ],
        [
            sg.Checkbox('Collapse regularized readings to parent reading', key='collapse_regularized'),
            sg.Checkbox('Add "r" suffix to each witness moved to its parent reading', key='add_r_suffix')
        ]
    ]
    return [
        [
            sg.T('Collation File: '), 
            sg.I('', key='xml_filename'), 
            sg.FileBrowse(file_types=(('XML Files', '*.xml'),), initial_folder=settings.get('reformatted_xml_dir'))
        ],
        [
            sg.Frame('Export Options', options_frame)
        ],
        [
            sg.Button('Export'), sg.Button('Close')
        ]
    ]

def export_to_docx(font, icon):
    settings = es.get_settings()
    window = sg.Window('Export Collation to DOCX', layout(settings), icon=icon, font=font)
    while True:
        event, values = window.read()
        if event in [None, sg.WIN_CLOSED, 'Close']:
            break
        elif event == 'Export' and not values['use_custom_template']:
            export(settings, values, values['collapse_regularized'], None, values['add_r_suffix'])

        elif event == 'Export' and values['use_custom_template'] is True and values['custom_template_path'] != '':
            export(settings, values, values['collapse_regularized'], values['custom_template_path'], values['add_r_suffix'])
            es.edit_settings('custom_template_path', values['custom_template_path'])

        elif event == 'use_custom_template':
            window['custom_template_path'].update(disabled=not values['use_custom_template'])
    window.close()
