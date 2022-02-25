from pathlib import Path
import platform
from turtle import back

import PySimpleGUI as sg

# pylint: disable=no-member
op_os = platform.system()

def get_icon():
    criticus_dir = Path(__file__).parent.parent.as_posix()
    return f'{criticus_dir}/resources/criticus.ico'

def ok(msg, title):
    layout = [[sg.T(msg)],
              [sg.B('Ok')]]
    window = sg.Window(title, layout, icon=get_icon())
    window.read()
    window.close()

def yes_cancel(msg, title):
    layout = [[sg.T(msg)],
              [sg.B('Yes'), sg.T(''), sg.B('Cancel')]]
    window = sg.Window(title, layout, icon=get_icon())
    event, _ = window.read()
    window.close()
    if event == 'Yes':
        return True
    else:
        return False

def textbox(text, title):
    # if op_os == 'Windows':
    #     size = (1200, 400)
    # else:
    #     size = (800, 400)
    layout = [
        [sg.Multiline(text, font=('Courier', 10))],
        [sg.B('Done')]
        ]
    window = sg.Window(title, layout, icon=get_icon())
    window.read()
    window.close()

def listbox(message: str, items: list, title: str):
    layout = [[sg.T(message)],
              [sg.Listbox(items)],
              [sg.B('Ok')]]
    window = sg.Window(title, layout, icon=get_icon())
    window.read()
    window.close()

def mac_win_cmd(text: str, title: str, mac_cmd: str, win_cmd: str):
    layout = [
        [sg.T(text)],
        [sg.T('MacOS:', size=(10, 1)), sg.Input(mac_cmd, readonly=True, disabled_readonly_background_color='#000000', disabled_readonly_text_color='#ffffff')],
        [sg.T('Windows:', size=(10, 1)), sg.Input(win_cmd, readonly=True, disabled_readonly_background_color='#000000', disabled_readonly_text_color='#ffffff')],
        [sg.Stretch(), sg.Button('Ok', size=(5, 1)), sg.Stretch()],
    ]
    window = sg.Window(title, layout, icon=get_icon())
    window.read()
    window.close()
    