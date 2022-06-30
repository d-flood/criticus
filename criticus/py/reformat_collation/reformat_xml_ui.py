from pathlib import Path

from lxml import etree as et
import PySimpleGUI as sg

from criticus.py.reformat_collation.itsee_to_open_cbgm import reformat_xml
from criticus.py.reformat_collation.differentiate_subreading_ids import differentiate_subreading_ids as diff_ids
from criticus.py.reformat_collation.clean_wits import remove_redundant_correctors
import criticus.py.edit_settings as es
import criticus.py.custom_popups as cp

# pylint: disable=no-member
def layout(settings: dict):
    titlestmt_tip = '''E.g. "Collation of Romans with Emphasis on Lectionary Witnesses"'''
    pub_tip = '''E.g. "This is an open access work licensed under a Creative Commons Attribution 4.0 International license."'''
    input_frame = [
        [sg.I('', key='xml_input_file'), sg.FileBrowse(initial_folder=settings['combined_xml_dir'], file_types=(('XML Files', '*.xml'), ))]
    ]
    return [
        [sg.Frame('Combined Collation File', input_frame)],
        [sg.T('Collation Title:'), sg.Input('untitled', key='title_stmt', expand_x=True, tooltip=titlestmt_tip)],
        [sg.T('Publication Statement:'), sg.Input('unspecified', key='publication_stmt', expand_x=True, tooltip=pub_tip)],
        [sg.B('Convert', key='convert'), sg.B('Cancel', key='exit'), sg.Stretch(), sg.B('Remove Redundant Correctors', k='clean_wits')],
        ]

def set_initial_dirs(combined_xml_dir: str, reformatted_xml_dir: str):
    combined_xml_dir = Path(combined_xml_dir).parent.as_posix()
    reformatted_xml_dir = Path(reformatted_xml_dir).parent.as_posix()
    es.edit_settings('combined_xml_dir', combined_xml_dir)
    es.edit_settings('reformatted_xml_dir', reformatted_xml_dir)

def fix_NCNames(xml_fn):
    '''lxml throws a syntax eror when the id attribute is set to a number, even though it is a string.
    The Collation Editor is allowing invalid XML to be created, I guess'''
    fixed = 'temp_repaired_xml'
    with open(xml_fn, 'r', encoding='utf-8') as f:
        xml = f.read()
    xml = xml.replace('xml:id="1', 'xml:id="I')
    xml = xml.replace('xml:id="2', 'xml:id="II')
    xml = xml.replace('xml:id="3', 'xml:id="III')
    with open(fixed, 'w', encoding='utf-8') as f:
        f.write(xml)
    return fixed

def convert(values, settings):
    if values['xml_input_file'] == '':
        sg.popup_quick_message('Browse to select an XML collation file to convert')
        return
    try:
        try:
            xml_fn = reformat_xml(values['xml_input_file'], values['title_stmt'], values['publication_stmt'])
        except et.XMLSyntaxError:
            sg.popup_quick_message('file contains invalid NCNames, attempting to repair...')
            xml_fn = fix_NCNames(values['xml_input_file'])
            try:
                xml_fn = reformat_xml(xml_fn, values['title_stmt'], values['publication_stmt'])
            except Exception as e:
                cp.ok(f'There are invalid elements or attributes in this XML file.\nError: {e}',
                'Failed to Reformat')
                return
        xml = diff_ids(xml_fn)
        cp.ok('XML Collation File was successfully reformatted!\n\
You will now be prompted to save the converted file.', title='Success!')
        fn_to_save = sg.popup_get_file('', no_window=True, save_as=True, file_types=(('XML Files', '*.xml'),), initial_folder=settings['reformatted_xml_dir'])
        if not fn_to_save:
            return
        xml.write(fn_to_save, encoding='utf-8', xml_declaration=True, pretty_print=True)
    except Exception as e:
        cp.ok(f'Failed to reformat XML file.\n\
Check that the input file name is correct and that\n\
this is the output of the ITSEE Collation Editor.\n\
Error: {e}', title='Bummer...')
        return
    set_initial_dirs(values['xml_input_file'], fn_to_save)


def clean_wits(values: dict, settings: dict):
    if values['xml_input_file'] == '':
        sg.popup_quick_message('Browse to select an XML collation file to convert')
        return
    try:
        xml = remove_redundant_correctors(values['xml_input_file'])
    except Exception as e:
        cp.ok(f'Failed to clean wits.\n{e}', 'Bummer')
        return
    cp.ok('Witnesses in the collation file have been saved, ready to save.', 'Cleaned!')
    fn_to_save = sg.popup_get_file('', no_window=True, save_as=True, file_types=(('XML Files', '*.xml'),), initial_folder=settings['reformatted_xml_dir'])
    if not fn_to_save:
        return
    try:
        xml.write(fn_to_save, encoding='utf-8', xml_declaration=True, pretty_print=True)
        cp.ok(f'Collation was saved to\n{fn_to_save}', 'Saved!')
    except Exception as e:
        cp.ok(f'Could not write the file to disk.\n{e}', 'Bummer')
        return
    set_initial_dirs(values['xml_input_file'], fn_to_save)

def start_reformat_ui(font: tuple, icon):
    settings = es.get_settings()
    window = sg.Window('Reformat XML Collation File', layout(settings), font=font, icon=icon)

    while True:
        event, values = window.read()

        if event in ['exit', sg.WINDOW_CLOSED, None]:
            break

        elif event == 'convert':
            convert(values, settings)

        elif event == 'clean_wits':
            clean_wits(values, settings)

    window.close()
    return False