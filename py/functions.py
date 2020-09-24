import json
from tkinter import *
from tkinter import ttk

def set_tab_on_start(main_dir, transcription_tab, prepare_json_tab, collation_tab):

    with open(f'{main_dir}/py/settings.json', 'r') as settings_file:
        settings_file = json.load(settings_file)
        pass

    if settings_file['tab_on_start'] == 'transcription':
        return transcription_tab
    elif settings_file['tab_on_start'] == 'prepare_json':
        return prepare_json_tab
    elif settings_file['tab_on_start'] == 'collation':
        return collation_tab
    else:
        return transcription_tab