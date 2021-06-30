import json
from pathlib import Path
import re

from natsort import natsorted
import PySimpleGUIQt as sg

import tendon.py.edit_settings as es

# pylint: disable=no-member
def json_to_plain_text(json_dir: str):
    files = Path(json_dir).glob('**/*.json')
    files = [f.as_posix() for f in files]
    files = natsorted(files)
    lines = []
    for verse in files:
        try:
            with open(verse, 'r', encoding='utf-8') as f:
                tx = json.load(f)
            lines.append(f"{tx['context']} {tx['plain_text']}")
        except:
            print(f'Did not open {verse}')
    text = '\n'.join(lines)
    return text

def simplify_ref(text: str, icon):
    text = re.sub(r'B[0-9]+K', 'K', text)
    text = text.splitlines()

    chapters = []
    new_lines = []
    skipped_lines = []

    for line in text:
        try:
            ch = re.search(r'K[0-9]+V', line).group(0)
        except:
            print(f'Did not find a reference on this line:\n{line}')
            skipped_lines.append(line)
            continue
        ch = ch.replace('V', '')
        ch_num = ch.replace('K', '')
        if ch_num not in chapters:
            chapters.append(ch_num)
            new_lines.append(f'\nCHAPTER {ch_num}\n')
        new_lines.append(line)

    text = '\n'.join(new_lines)
    text = re.sub(r'K.+V', '', text)

    if len(skipped_lines) > 0:
        skipped_lines = '\n'.join(skipped_lines)
        sg.popup_ok(f'''The following lines were skipped because a reference was not found:
{skipped_lines}''', title='Some lines skipped', icon=icon)

    return text

def get_text_from_json_files(font, icon):
    settings = es.get_settings()
    folder = sg.popup_get_folder(
        'Select a folder containing the target JSON files', 
        title='Plain Text from JSON',
        default_path=settings['txt_from_json_dir'],
        icon=icon, initial_folder=settings['txt_from_json_dir'],
        font=font
        )
    if not folder:
        return
    folder = Path(folder).as_posix()
    es.edit_settings('txt_from_json_dir', folder)
    text = json_to_plain_text(folder)
    text = simplify_ref(text, icon)
    save_fn = sg.popup_get_file(
        '', title='Save Plain Text', save_as=True, no_window=True, 
        file_types=(('Plain Text Files', '*.txt'),),
        initial_folder=settings['plain_text_dir'],
        font=font
        )
    if not save_fn:
        return
    save_fn = Path(save_fn).as_posix()
    save_fn_setting = Path(save_fn).parent.as_posix()
    es.edit_settings('plain_text_dir', save_fn_setting)
    with open(save_fn, 'w', encoding='utf-8') as f:
        f.write(text)
    sg.popup_ok(f'Plain text was extracted from JSON files \
and saved to\n{save_fn}', title='Success!', icon=icon, font=font)
