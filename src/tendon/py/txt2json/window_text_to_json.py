from pathlib import Path
import PySimpleGUIQt as sg
import tendon.py.edit_settings as es
from tendon.py.txt2json.convert_text_to_json import convert_text_to_json as t2j

#pylint: disable=no-member
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
    if ((values['all_verses_in_file'] is False and values['range_of_verses'] is False) 
    or (values['manual'] is False and values['auto'] is False) 
    or values['output_dir_input'] in ['', None]):
       window['convert_dir'].update(disabled=True) 
       window['convert_file'].update(disabled=True)
    else:
        window['convert_dir'].update(disabled=False) 
        window['convert_file'].update(disabled=False)

def convert_file(values: dict):
    settings = es.get_settings()
    filename = sg.popup_get_file('', no_window=True, default_path=settings['tx_dir'], file_types=(('Plain Text Files', '*.txt'),))
    if filename:
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
        sg.popup_ok('Done!', title='Text File Converted')

def convert_dir(values: dict):
    settings = es.get_settings()
    folder = sg.popup_get_folder('', no_window=True, default_path=settings['tx_dir'])
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
        sg.popup_ok('Done!', title='Text File Converted')


def txt_to_json(font: tuple, icon):
    settings = es.get_settings()
    frame_prepare_all_or_rage = [
        [sg.Radio('All verses in file ', group_id='all_or_range', key='all_verses_in_file', enable_events=True)],
        [sg.Radio('Range of verses ', group_id='all_or_range', key='range_of_verses', enable_events=True),
                sg.T('From'), sg.Input(key='range_from', disabled=True), sg.T('To'), sg.Input(key='range_to', disabled=True)],
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
        [sg.Button('Convert File', key='convert_file', disabled=True), 
                sg.Button('Convert Directory', key='convert_dir', disabled=True)],
        [sg.T('Output Directory '), sg.Input(default_text=settings['ce_repo_dir'], disabled=True, key='output_dir_input'), sg.Button('Browse')]
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
            convert_file(values)

        elif event == 'convert_dir':
            convert_dir(values)

    window.close()
    return False
