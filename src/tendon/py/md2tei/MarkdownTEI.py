from pathlib import Path

import PySimpleGUIQt as sg 

import tendon.py.edit_settings as es
from tendon.py.md2tei.markdown_to_tei import convert_md_to_tei as md2tei

# pylint: disable=no-member
def okay_popup(msg: str, title: str):
    window = sg.Window(title, [[sg.T(msg)], [sg.B('OKAY')]])
    window.read()
    window.close()

def bummer():
    okay_popup('The Markdown file failed to convert. Talk to David about it.', 'Bummer...')

def yay(output_file):
    msg = f'Yay! The Markdown transcription was converted and saved to\n{output_file}'
    okay_popup(msg, 'Yay!')

def set_initial_dirs(input_file, output_file):
    if input_file:
        initial_dir = Path(input_file).parent.as_posix()
        es.edit_settings('markdown_tx_dir', initial_dir)
    if output_file:
        output_dir = Path(output_file).parent.as_posix()
        es.edit_settings('converted_markdown_tx_dir', output_dir)

def convert(settings, values):
    output_file = sg.popup_get_file('', no_window=True, save_as=True, file_types=(('XML File', '*.xml'), ), initial_folder=settings['converted_markdown_tx_dir'])
    set_initial_dirs(values['md_input'], output_file)
    md2tei(values['md_input'], output_file, values['plain'], values['lines'])
    return output_file

def layout(settings):
    plain_tip = 'smaller file size; not very human-readable'
    lines_tip = 'break lines according to transcription'
    pretty_tip = 'pretty print'
    radio_frame = [
        [sg.Radio('Do not add extra whitespace', 'format', tooltip=plain_tip, key='plain')],
        [sg.Radio('Keep transcription lines', 'format', tooltip=lines_tip, key='lines')],
        [sg.Radio('Pretty Print', 'format', tooltip=pretty_tip, key='pretty', default=True)],
    ]
    io_frame = [
        [sg.I('', key='md_input'), sg.FileBrowse('Browse', file_types=(('Markdown Files', '*.md'),), initial_folder=settings['markdown_tx_dir'])]
    ]
    return [
        [sg.Button('<- Back to Tendon', key='exit'), sg.Stretch()],
        [sg.Frame('XML TEI Output Format', radio_frame)],
        [sg.Frame('Markdown File', io_frame)],
        [sg.B('Convert Markdown to TEI', key='convert')]
    ]

def md_to_tei(font: tuple):
    settings = es.get_settings()
    L = layout(settings)
    window = sg.Window('MarkdownTEI', L, font=font)

    while True:
        event, values = window.read()
        if event in [sg.WINDOW_CLOSED, 'exit']:
            break
        elif event == 'convert' and values['md_input'] != '':
            try:
                output_file = convert(settings, values)
                yay(output_file)
            except:
                bummer()
    window.close()
    return False
