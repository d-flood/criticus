from lib2to3.pytree import convert
from pathlib import Path
import platform
import PySimpleGUI as sg
import criticus.py.edit_settings as es
from criticus.py.txt2json.convert_text_to_json import convert_text_to_json as t2j
from criticus.py.txt2json.convert_text_to_json import convert_single_verse_to_json as t2j_single

#pylint: disable=no-member
def disable_reference_and_text(window: sg.Window, switch: bool, values):
    window['single_ref'].update(disabled=switch)
    window['single_text'].update(disabled=switch)
    disable_buttons(window, values)

def disable_from_and_to(window: sg.Window, switch: bool, values):
    window['range_from'].update(disabled=switch)
    window['range_to'].update(disabled=switch)
    disable_buttons(window, values)
    
def disable_siglum_and_prefix(window: sg.Window, switch: bool, values):
    window['siglum_input'].update(disabled=switch)
    window['ref_prefix_input'].update(disabled=switch)
    disable_buttons(window, values)

def browse_for_output_dir(window: sg.Window, output_dir):
    window['output_dir_input'].update(output_dir)
    es.edit_settings('ce_repo_dir', output_dir)

def disable_buttons(window: sg.Window, values: dict):
    if (all([values['all_verses_in_file'] is False, values['range_of_verses'] is False, values['single_verse'] is False])
    or (values['manual'] is False and values['auto'] is False) 
    or values['output_dir_input'] in ['', None]):
       window['convert_dir'].update(disabled=True) 
       window['convert_file'].update(disabled=True)
    else:
        window['convert_dir'].update(disabled=False) 
        window['convert_file'].update(disabled=False)
        window['convert_text'].update(disabled=False)

def convert_file(values: dict, icon):
    settings = es.get_settings()
    filename = sg.popup_get_file('', no_window=True, initial_folder=settings['tx_dir'], file_types=(('Plain Text Files', '*.txt'),))
    if not filename:
        return
    f = Path(filename)
    f = f.parent.absolute().as_posix()
    es.edit_settings('tx_dir', f)
    t2j(
        filename, output_dir=values['output_dir_input'], 
        convert_all=values['all_verses_in_file'],
        reference_prefix=values['ref_prefix_input'],
        auto=values['auto'], verse_from=values['range_from'],
        verse_to=values['range_to'], siglum=values['siglum_input']
    )
    sg.popup_ok('Done!', title='Text File Converted', icon=icon)

def convert_dir(values: dict, icon):
    settings = es.get_settings()
    folder = sg.popup_get_folder('', no_window=True, initial_folder=settings['tx_dir'], icon=icon)
    if folder:
        es.edit_settings('tx_dir', folder)
        folder = Path(folder)
        for f in folder.iterdir():
            if f.name.endswith('.txt'):
                t2j(
                    f, 
                    output_dir=values['output_dir_input'], 
                    convert_all=True,
                    reference_prefix=values['ref_prefix_input'],
                    auto=values['auto'], 
                    verse_from=values['range_from'],
                    verse_to=values['range_to'], 
                    siglum=values['siglum_input']
                )
        sg.popup_ok('Done!', title='Text File Converted', icon=icon)


def txt_to_json(font: tuple, icon):
    settings = es.get_settings()
    if platform.system() == 'Windows':
        space = sg.T('')
        output_folder_elem = sg.Input(default_text=settings['ce_repo_dir'], disabled=True, key='output_dir_input')
    else:
        space = sg.T('               ')
        output_folder_elem = sg.Input(default_text=settings['ce_repo_dir'], disabled=True, key='output_dir_input', size=(30, 1))
        
    frame_prepare_all_or_rage = [
        [sg.Radio('All verses in file ', group_id='all_or_range', key='all_verses_in_file', enable_events=True)],
        [sg.Radio('Range of verses ', group_id='all_or_range', key='range_of_verses', enable_events=True),
                sg.T('From'), sg.Input(key='range_from', disabled=True), sg.T('To'), sg.Input(key='range_to', disabled=True)],
        [sg.Radio('Single Verse ', group_id='all_or_range', key='single_verse', enable_events=True), 
            sg.T('Reference'), sg.Input(key='single_ref', size=(10, 1), disabled=True),
            sg.T('Text'), sg.Input(key='single_text', disabled=True, expand_x=True)],
    ]
    frame_ref_format = [
        [sg.Radio('Manual ', group_id='ref_prefix', enable_events=True, key='manual'), 
                sg.T('Siglum'), sg.Input(key='siglum_input', disabled=True), 
                sg.T('Unit prefix'), sg.Input(key='ref_prefix_input', disabled=True)],
        [sg.Radio('Auto from file name ', group_id='ref_prefix', enable_events=True, key='auto')],
    ]

    win_txt_to_json = [
        [sg.Button('Back', key='exit'), sg.Stretch()],
        [sg.Frame('Units to Convert', frame_prepare_all_or_rage)],
        [sg.Frame('Transcription Info', frame_ref_format)],
        [sg.T('Output Directory '), output_folder_elem, sg.Button('Browse')],
        [sg.Button('Convert File', key='convert_file', disabled=True), space,
                sg.Button('Convert Directory', key='convert_dir', disabled=True),
                sg.Button('Convert Text', key='convert_text', disabled=True)],
    ]

    window = sg.Window('Convert Plain Text to JSON', win_txt_to_json, font=font, icon=icon)

###########################################################
###########################################################

    while True:
        event, values = window.read()

        if event == sg.WIN_CLOSED:
            break

        elif event == 'range_of_verses':
            disable_from_and_to(window, False, values)

        elif event == 'all_verses_in_file':
            disable_from_and_to(window, True, values)

        elif event == 'single_verse':
            disable_reference_and_text(window, False, values)

        elif event == 'auto':
            disable_siglum_and_prefix(window, True, values)

        elif event == 'manual':
            disable_siglum_and_prefix(window, False, values)

        elif event == 'exit':
            break

        elif event == 'Browse':
            output_dir = sg.popup_get_folder('', no_window=True, default_path=settings['ce_repo_dir'])
            browse_for_output_dir(window, output_dir)

        elif event == 'convert_file':
            convert_file(values, icon)

        elif event == 'convert_dir':
            convert_dir(values, icon)

        elif event == 'convert_text':
            t2j_single(values)
            sg.popup_ok('Done!', title='Text File Converted', icon=icon)

    window.close()
    return False
