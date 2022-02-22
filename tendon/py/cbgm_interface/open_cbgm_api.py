import json
from pathlib import Path

import platform
operating_system = platform.system()

if operating_system == 'Windows':
    from subprocess import Popen, CREATE_NEW_CONSOLE, check_output
else:
    from subprocess import Popen, check_output
import os

# pylint: disable=import-error
import tendon.py.custom_popups as cp
import tendon.py.edit_settings as es

def get_system_specific_command(command, new_console: bool):
    if operating_system == 'Windows':
        if new_console:
            p = Popen(command, creationflags=CREATE_NEW_CONSOLE)
        else:
            p = Popen(command)
    else:
        command = command.replace(".exe", "")
        command = command.replace('\\', '/')
        p = Popen(command, shell=True)
    return p

def get_system_output_command(command):
    if operating_system == 'Windows':
        return command
    command = command.replace('\\', '/')
    command = command.replace(".exe", "")
    return command

def parse_user_input(values: dict):
    settings = es.get_settings()
    db = Path(f'{settings["cbgm_main_dir"]}/db/{values["new_db_name"]}.db').as_posix().replace('/', '\\')
    cx = Path(values['xml_file']).as_posix().replace('/', '\\')
    script = Path(f"{settings['cbgm_main_dir']}/populate_db.exe").as_posix().replace('/', '\\')
    command = f'"{script}"'
    if values['threshold']:
        for threshold in values['threshold_input'].strip().split(', '):
            command = f'{command} -t {threshold}'
    if values['trivial']:
        for t in values['trivial_input'].strip().split(', '):
            command = f'{command} -z {t}'
    if values['exclude']:
        for e in values['exclude_input'].strip().split(', '):
            command = f'{command} -Z {e}'
    if values['merge_split']:
        command = f'{command} --merge-splits'
    if values['classic']:
        command = f'{command} --classic'
    return f'{command} "{cx}" "{db}"'

def check_db_dir(cbgm_main_dir: str):
    db_dir = Path(f'{cbgm_main_dir}/db')
    if not db_dir.is_dir():
        db_dir.mkdir()
    if db_dir.is_dir():
        return True
    else:
        return False

def populate_db(values: dict):
    if not check_db_dir(values['cbgm_main_dir']):
        cp.ok('There was an unanticipated problem making a folder\n\
in which to save databases.')
        return
    command = parse_user_input(values)
    p = get_system_specific_command(command, new_console=True)
    p.wait()

def get_all_dbs():
    settings = es.get_settings()
    try:
        db_dir = f"{settings['cbgm_main_dir']}/db"
        db_dir = Path(db_dir)
        databases = [x.as_posix().split('/')[-1] for x in db_dir.iterdir() if x.as_posix().endswith('.db')]
        if databases is None or databases == []:
            databases = ['']
    except:
        databases = ['']
    return databases

def delete_db(values):
    settings = es.get_settings()
    db_dir = f"{settings['cbgm_main_dir']}/db"
    db_dir = Path(db_dir)
    for db in values['db_listbox']:
        for f in db_dir.iterdir():
            if f.as_posix().endswith(db):
                try:
                    os.remove(f.as_posix())
                except Exception as e:
                    # print(f'HEADS UP: {e}')
                    cp.ok(f'There was a problem deleting\n{f.as_posix()}\nbecause: {e}', 'Just a small problem')

def parse_compare_input(values):
    settings = es.get_settings()
    script = Path(f'''{settings['cbgm_main_dir']}/compare_witnesses.exe''').as_posix().replace('/', '\\')
    db = Path(f'{settings["cbgm_main_dir"]}/db/{values["selected_db"]}').as_posix().replace('/', '\\')
    command = f'"{script}" -f json "{db}" {values["wit_to_compare"]}'
    for wit in values['wits_to_compare'].strip().split(', '):
        command = f'{command} {wit}'
    return command

def compare_wits(values):
    command = parse_compare_input(values)
    command = get_system_output_command(command)
    try:
        text = check_output(command, shell=True)
    except:
        return None
    text = text.decode()
    text = text.replace('Opening database...', '')
    text = text.replace('Retrieving witness list...', '')
    text = text.replace('Retrieving genealogical relationships for primary witness...', '')
    text = text.replace('Closing database...', '')
    text = text.replace('Database closed.', '')
    text = text.replace('Writing to cout...', '')
    text = text.strip()
    return json.loads(text)

def csv_comparison(values, output_fn):
    output_fn = Path(output_fn).as_posix().replace('/', '\\')
    settings = es.get_settings()
    script = Path(f'''{settings['cbgm_main_dir']}/compare_witnesses.exe''').as_posix().replace('/', '\\')
    db = Path(f'{settings["cbgm_main_dir"]}/db/{values["selected_db"]}').as_posix().replace('/', '\\')
    command = f'"{script}" -f csv -o "{output_fn}" "{db}" {values["wit_to_compare"]}'
    for wit in values['wits_to_compare'].strip().split(', '):
        command = f'{command} {wit}'
    p = get_system_specific_command(command, new_console=False)
    p.wait()
    if Path(output_fn).is_file():
        return True
    else:
        return False

def view_plain_text(values):
    settings = es.get_settings()
    script = Path(f'''{settings['cbgm_main_dir']}/compare_witnesses.exe''').as_posix().replace('/', '\\')
    db = Path(f'{settings["cbgm_main_dir"]}/db/{values["selected_db"]}').as_posix().replace('/', '\\')
    command = f'"{script}" "{db}" {values["wit_to_compare"]}'
    for wit in values['wits_to_compare'].strip().split(', '):
        command = f'{command} {wit}'
    command = get_system_output_command(command)
    text = check_output(command, shell=True)
    text = text.decode()
    text = text.replace('Opening database...', '')
    text = text.replace('Retrieving witness list...', '')
    text = text.replace('Retrieving genealogical relationships for primary witness...', '')
    text = text.replace('Closing database...', '')
    text = text.replace('Database closed.', '')
    text = text.replace('Writing to cout...', '')
    text = text.strip()
    return text
