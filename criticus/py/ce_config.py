import json
import os
from pathlib import Path
import platform
import subprocess
from typing import Dict, List
import webbrowser

from natsort import natsorted
import PySimpleGUI as sg

import criticus.py.edit_settings as es

# pylint: disable=no-member
def get_config(fn = None) -> dict:
    if not fn:
        settings = es.get_settings()
        fn = settings['ce_config_fn']
    try:
        with open(fn, 'r', encoding='utf-8') as c:
            config = json.load(c)
            if not config.get('excluded_witnesses'):
                config['excluded_witnesses'] = []
            return config
    except:
        sg.popup_quick_message('No config file found.\nBrowse for the Config File')
        return {}

def save_config(config: dict, fn: str):
    config['witnesses'] = sort_by_ga(config['witnesses'])
    config['excluded_witnesses'] = sort_by_ga(config['excluded_witnesses'])
    with open(fn, 'w', encoding='utf-8') as f:
        json.dump(config, f, ensure_ascii=False, indent=4)

def layout():
    settings = es.get_settings()
    i_size = (30, 1)
    config = get_config()
    if platform.system() == 'Windows':
        launch_ce = sg.B('Start Collation Editor')
    else:
        # launch_ce = sg.T('')
        launch_ce = sg.B('Start Collation Editor')

    settings_frame = [
        [sg.T('Project Title'), sg.I(config.get('name', ''), size=i_size, key='name')],
        [sg.T('Basetext'), sg.I(config.get('base_text', ''), size=i_size, key='basetext')],
        [sg.T('Included'), sg.Listbox(config.get('witnesses', []), select_mode=sg.LISTBOX_SELECT_MODE_EXTENDED, key='witnesses', expand_x=True, expand_y=True)],
        [sg.B('Add Witness', bind_return_key=True), sg.I('', key='wit_to_add'), sg.T(''), sg.B('Move to Excluded')],
        [sg.T('Excluded'), sg.Listbox(config.get('excluded_witnesses', []), select_mode=sg.LISTBOX_SELECT_MODE_EXTENDED, key='excluded', expand_x=True, expand_y=True)],
        [sg.B('Move to Included'), sg.B('Delete Selected')]
    ]

    return [
        [sg.T('Collation Config File'), sg.I(settings['ce_config_fn'], key='config_fn'), sg.FileBrowse(file_types=(('JSON Files', '*.json'),)), sg.B('Update')],
        [sg.Frame('Collation Configuration', settings_frame, border_width=4, expand_x=True, expand_y=True)],
        [launch_ce, sg.T(''), sg.B('Done', key='exit')],
    ]

def edit_config(values):
    config = get_config(values['config_fn'])
    if values['name'] != '':
        config['name'] = values['name']
    if values['basetext'] != '':
        config['base_text'] = values['basetext']
    save_config(config, values['config_fn'])
    sg.popup_quick_message('Configuration File Updated')

def sort_by_ga(wits: List[str]):
    papyri = []
    majuscules = []
    minuscules = []
    lectionaries = []
    editions = []
    for wit in wits:
        if wit.lower().startswith('p'):
            papyri.append(wit)
        elif wit.startswith('0'):
            majuscules.append(wit)
        elif wit[0].isdigit():
            minuscules.append(wit)
        elif wit.lower().startswith('l'):
            lectionaries.append(wit)
        else:
            editions.append(wit)
    return natsorted(papyri) + natsorted(majuscules) + natsorted(minuscules) + natsorted(lectionaries) + natsorted(editions)
  
def remove_from_config(config: dict, key, item_to_remove: str):
    new_list = []
    for wit in config[key]:
        if wit != item_to_remove and wit not in new_list:
            new_list.append(wit)
    config[key] = new_list
    return config

def update_window(window: sg.Window, values):
    config = get_config(values['config_fn'])
    if not config:
        return
    window['name'].update(config['name'])
    window['basetext'].update(config['base_text'])
    window['witnesses'].update(config['witnesses'])
    window['excluded'].update(config['excluded_witnesses'])
    window['wit_to_add'].update('')

def add_witness(values, window):
    if values['wit_to_add'] == '':
        return
    if values['config_fn'] == '':
        return
    config = get_config(values['config_fn'])
    try:
        config['witnesses'].append(values['wit_to_add'])
    except:
        sg.popup_quick_message('Are you sure that is the right config.json file?\nIt did not work.')
        return
    config = remove_from_config(config, 'excluded_witnesses', values['wit_to_add'])
    save_config(config, values['config_fn'])
    update_window(window, values)

def remove_witnesses(values, window):
    if values['witnesses'] == []:
        return
    config = get_config(values['config_fn'])
    for wit in values['witnesses']:
        if wit not in config['excluded_witnesses']:
            config['excluded_witnesses'].append(wit)
        config = remove_from_config(config, 'witnesses', wit)
    save_config(config, values['config_fn'])
    update_window(window, values)

def include_selected(values: dict, window: sg.Window):
    if values['excluded'] == []:
        return
    config = get_config(values['config_fn'])
    for wit in values['excluded']:
        config['witnesses'].append(wit)
        config = remove_from_config(config, 'excluded_witnesses', wit)
    save_config(config, values['config_fn'])
    update_window(window, values)

def delete_selection(window: sg.Window, values: dict):
    if values['excluded'] == []:
        return
    config = get_config(values['config_fn'])
    for wit in values['excluded']:
        config = remove_from_config(config, 'excluded_witnesses', wit)
    save_config(config, values['config_fn'])
    update_window(window, values)

def start_ce(values):
    if values['config_fn'] == '':
        return
    cwd = os.getcwd()
    root_dir = Path(values['config_fn']).parent.parent.parent.parent.parent.as_posix()
    print(root_dir)
    os.chdir(root_dir)
    try:
        if platform.system() == 'Windows':
            from subprocess import CREATE_NEW_CONSOLE
            subprocess.Popen('start startup.bat', shell=True, creationflags=CREATE_NEW_CONSOLE)
            subprocess.Popen('start firefox http://localhost:8080/collation', shell=True)
        else:
            subprocess.Popen('bash startup.sh', shell=True)
            webbrowser.get('firefox').open('http:localhost:8080/collation')
    except:
        print('cold not open browser')
    os.chdir(cwd)
    return

def configure_ce(font, icon):
    window = sg.Window('Configure Collation Editor', layout(), font=font, icon=icon, resizable=True)
    while True:
        event, values = window.read()
        if event in [None, sg.WINDOW_CLOSED, 'exit']:
            break
        elif event == 'Update':
            if values['config_fn'] == '':
                continue
            try:
                edit_config(values)
                update_window(window, values)
            except:
                sg.popup_quick_message('Are you sure that is the right config.json file?\nIt did not work.')
            es.edit_settings('ce_config_fn', values['config_fn'])
        elif event == 'Add Witness':
            add_witness(values, window)
        elif event == 'Move to Excluded':
            remove_witnesses(values, window)
        elif event == 'Start Collation Editor':
            start_ce(values)
        elif event == 'Move to Included':
            include_selected(values, window)
        elif event == 'Delete Selected':
            delete_selection(window, values)
    window.close()
    return False
