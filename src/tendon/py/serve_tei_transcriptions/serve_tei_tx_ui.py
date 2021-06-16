import PySimpleGUIQt as sg 
import tendon.py.edit_settings as es
from pathlib import Path
import os
import threading

from tendon.py.serve_tei_transcriptions.serve_tei import launch_tei_viewer as launch

# pylint: disable=no-member
def layout(settings: dict):
    tei_repo_frame = [
        [sg.I(settings['tei_dir'], key='tei_folder'), 
         sg.FolderBrowse(initial_folder=settings['tei_dir'])]
    ]
    return [
        [sg.B('Exit', key='exit'), sg.Stretch()],
        [sg.Frame('TEI Transcription Folder', tei_repo_frame)],
        [sg.B('Launch TEI Transcription Viewer', key='launch')]
    ]

def set_initial_dir(tei_dir: str):
    tei_dir = Path(tei_dir).as_posix()
    es.edit_settings('tei_dir', tei_dir)

def kill_server(httpd):
    httpd.shutdown()
    print('server stopped')

def serve_tei_tx(main_dir):
    settings = es.get_settings()
    window = sg.Window('Launch TEI Transcription Viewer', layout(settings))
    httpd = None
    while True:
        event, values = window.read()

        if event in ['exit', sg.WINDOW_CLOSED, None]:
            if httpd:
                threading.Thread(target=kill_server, args=[httpd]).start()
            break

        elif event == 'launch':
            if values['tei_folder'] == '':
                continue
            try:
                tei_dir = Path(values['tei_folder'])
            except:
                continue
            if tei_dir.is_file():
                tei_dir = tei_dir.parent.as_posix()
            else:
                tei_dir = tei_dir.as_posix()
            set_initial_dir(tei_dir)
            httpd = launch(tei_dir, main_dir)
            window['launch'].update(disabled=True)
    
    window.close()
    os.chdir(main_dir)
    return False