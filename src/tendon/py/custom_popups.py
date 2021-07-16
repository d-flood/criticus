from pathlib import Path
import platform

import PySimpleGUIQt as sg

# pylint: disable=no-member
op_os = platform.system()

def get_icon():
    tendon_dir = Path(__file__).parent.parent.as_posix()
    return f'{tendon_dir}/resources/tendon.ico'

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
    if op_os == 'Windows':
        size = (1200, 400)
    else:
        size = (800, 400)
    layout = [
        [sg.Multiline(text, font=('Courier', 10), size_px=size)],
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
    