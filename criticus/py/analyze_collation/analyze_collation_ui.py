import PySimpleGUI as sg

from criticus.py.analyze_collation.find_agreements import find_agreements


def layout():
    return [
        [sg.Text('XML Collation File'), sg.Input(key='xml_file', expand_x=True), sg.FileBrowse(file_types=(('XML Files', '*.xml'),))],
        [sg.Text('All of:'), sg.Input('', k='all', expand_x=True)],
        [sg.Text('Any of:'), sg.Input('', k='any', expand_x=True)],
        [sg.Text('None of:'), sg.Input('', k='none', expand_x=True)],
        [sg.Multiline(k='output', expand_y=True, expand_x=True)],
        [sg.Button('Find Agreements', k='go', expand_x=True), sg.Button('Close')]
    ]

def main(font: tuple, icon):
    window = sg.Window('Find Agreements', layout(), font=font, icon=icon, resizable=True)
    while True:
        event, values = window.read()

        if event in [sg.WIN_CLOSE_ATTEMPTED_EVENT, sg.WINDOW_CLOSED, None, 'Close']:
            break

        elif event == 'go':
            result = find_agreements(values)
            if result:
                output = '\n'.join(result)
                window['output'].update(value=output)
    
    window.close()
    return
