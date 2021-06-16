from copy import deepcopy
import os
from lxml import etree as et

from natsort import natsorted
import PySimpleGUIQt as sg

import tendon.py.edit_settings as es

#pylint: disable=no-member
def okay_popup(message: str, title: str, icon):
    layout = [[sg.Text(message, pad=(10, 10))],
        [sg.Button('Okay')]]
    popup = sg.Window(title, layout, icon=icon)
    popup.read()
    popup.close()

def get_verse_file(f, output_dir):
    parser = et.XMLParser(remove_blank_text=True, recover=True)
    tree = et.parse(f'{output_dir}/{f}', parser=parser)
    root = tree.getroot()
    ns = root.nsmap
    all_ab_elems = root.findall('ab', ns)
    return deepcopy(all_ab_elems)

def combine_verses(starting_string: str, output_dir, main_dir):
    tree = et.parse(f'{main_dir}/resources/template.xml')
    root = tree.getroot()
    files = os.listdir(output_dir)
    files = natsorted(files)
    for f in files:
        if f.startswith(starting_string):
            all_ab_elems = get_verse_file(f, output_dir)
            for ab in all_ab_elems:
                root.append(ab)
    return tree

def combine_xml_files_interface(main_dir, icon=None):
    settings = es.get_settings()
    layout = [
        [sg.Text('Select the folder that contains the individual XML files to be combined')],
        [sg.Text('Folder:'), sg.Input(settings['ce_output_dir'], key='output_dir'), sg.FolderBrowse(initial_folder=settings['ce_output_dir'])],
        [sg.Text('Combine all files that start with:'), sg.Stretch(), sg.Input('', key='starts_with')],
        [sg.Button('Combine XML Files'), sg.Button('Cancel')]
    ]
    window = sg.Window('Combine XML Files', layout, icon=icon)
    while True:
        event, values = window.read()
        if event in [sg.WINDOW_CLOSED, 'Cancel']:
            window.close()
            return None
        elif event == 'Combine XML Files':
            if values['output_dir'] == '' or values['starts_with'] == '':
                sg.popup_quick_message('First select a folder and at least one "starts with" character')
                continue
            try:
                tree = combine_verses(values['starts_with'], values['output_dir'], main_dir)
                es.edit_settings('ce_output_dir', values['output_dir'])
            except:
                okay_popup('Failed to combine files.\n\
Double-check that the selected folder contains XML files and that\n\
these match the given "starts with" characters', 'Bummer', icon)
                continue
            saved_name = sg.popup_get_file('', no_window=True, file_types=(("XML Files", "*.xml"),), save_as=True, initial_folder=values['output_dir'])
            tree.write(saved_name, encoding='utf-8', xml_declaration=True)
            settings['ce_output_dir'] = values['output_dir']
            okay_popup(f'Files have been combined and saved to {saved_name}', 'Combined!', icon)
            window.close()
            return False
