from pathlib import Path

import PySimpleGUIQt as sg
#pylint: disable=import-error
# pylint: disable=no-member
import tendon.py.edit_settings as es 
import tendon.py.cbgm_interface.open_cbgm_api as oc
import tendon.py.custom_popups as cp


def validate_user_input(values: dict):
    if values['xml_file'] == '':
        cp.ok('Select a Collation file with which to populate the new database.', 'Forget something?')
        return
    elif not Path(values['xml_file']).is_file() or not values['xml_file'].endswith('.xml'):
        cp.ok('The given XML Collation file could not be opened or does not exist.', 'Cannot Open File')
        return
    if values['new_db_name'] == '':
        cp.ok('Enter a name for the new database', 'Forget something?')
        return
    if values['threshold'] and values['threshold_input'] == '':
        cp.ok('You have enabled readings threshold without providing\nthe threshold number.', 'Forget something?')
        return
    elif values['threshold']:
        try:
            int(values['threshold_input'])
        except:
            cp.ok('The reads threshold must be an integer', 'Bad Input')
            return
    if values['trivial'] and values['trivial_input'] == '':
        cp.ok('You have enabled "Treat as Trivial" without designating\nwhich reading types to trivialize.', 'Forget something?')
        return
    if values['exclude'] and values['exclude_input'] == '':
        cp.ok('You have chosen to "Exclude" reading type(s) without designating\nthe types to be excluded.', 'Forget something?')
        return
    return True

def validate_compare_inputs(values):
    if values['selected_db'] in ['', [], None]:
        return
    if values['wit_to_compare'] == '':
        cp.ok('Enter a witness to which others are compared.', 'Forget something?')
        return
    if values['compare_some'] and values['wits_to_compare'] == '':
        cp.ok('You have chosen to compare select witnesses without designating\nthose witnesses.', 'Forget something?')
        return
    return True

def populate_new_database(values, window: sg.Window):
    if not validate_user_input(values):
        return
    es.edit_settings('cbgm_main_dir', values['cbgm_main_dir'])
    es.edit_settings('cbgm_cx_dir', Path(values['xml_file']).parent.as_posix())
    oc.populate_db(values)
    window['db_listbox'].update(oc.get_all_dbs())
    window['selected_db'].update(oc.get_all_dbs())

def delete_selected(values, window):
    if values['db_listbox'] == []:
        return
    oc.delete_db(values)
    window['db_listbox'].update(oc.get_all_dbs())
    window['selected_db'].update(oc.get_all_dbs())

def compare_witnesses(values, window):
    if not validate_compare_inputs(values):
        return
    table = oc.compare_wits(values)
    display_table = []
    for row in table['rows']:
        r = []
        for item in ['id', 'dir', 'pass', 'eq', 'perc', 'prior', 'posterior']:
            r.append(str(row[item]))
        display_table.append(r)
    window['table'].update(values=display_table)
    return display_table

def save_as_csv(values, settings):
    output_fn = sg.popup_get_file(
        '', save_as=True, file_types=(('CSV Files', '*.csv'),),
        no_window=True, initial_folder=settings['cbgm_main_dir'])
    if not output_fn:
        return
    result = oc.csv_comparison(values, output_fn)
    if result:
        cp.ok(f'The CSV file was saved to\n{output_fn}', 'Success!')
    else:
        cp.ok('CSV file was not saved.', 'Bummer')

def view_plain_text(values):
    text = oc.view_plain_text(values)
    cp.textbox(text, 'open-cbgm text output')

def manage_db_tab_layout(settings: dict):
    w = (25, 1)
    xml_file_frame = [
        [sg.T('Select XML Collation File: ', size=w), sg.I('', key='xml_file'), sg.FileBrowse(file_types=(('XML Files', '*.xml'),), initial_folder=settings['cbgm_cx_dir'])],
        [sg.T('New Database Name: ', size=w), sg.I('', key='new_db_name')],
        [sg.Checkbox('Readings Threshold: ', key='threshold', size=w), sg.I('', key='threshold_input')],
        [sg.Checkbox('Treat as Trivial: ', key='trivial', size=w), sg.I('', key='trivial_input')],
        [sg.Checkbox('Exclude: ', key='exclude', size=w), sg.I('', key='exclude_input')],
        [sg.Checkbox('Merge Split Attestations', key='merge_split')],
        [sg.T('Rules: '), sg.Radio('Standard', 'rules', default=True, key='standard'), sg.Radio('Classic', 'rules', key='classic')],
        [sg.B('Populate Database')]
    ]
    dbs_frame = [
        [sg.Listbox(oc.get_all_dbs(), select_mode=sg.SELECT_MODE_EXTENDED, key='db_listbox')],
        [sg.B('Delete Selected')]
    ]
    return [
        [sg.T('open-cbgm binaries folder: '), sg.I(settings['cbgm_main_dir'], key='cbgm_main_dir'), sg.FolderBrowse(initial_folder=settings['cbgm_main_dir'])],
        [sg.Frame('Populate New Database', xml_file_frame)],
        [sg.Frame('All Databases', dbs_frame)],
    ]
def compare_wits_tab_layout(settings: dict):
    headings = ['Witness', 'Direction', 'Passages', 'Agreement', 'Percentage', 'Prior', 'Posterior']
    return [
        [sg.T('Select a Database'), sg.Combo(oc.get_all_dbs(), readonly=True, key='selected_db')],
        [sg.T('Compare Witnesses to: '), sg.I('', key='wit_to_compare')],
        [sg.Radio('Compare All Witnesses', 'compare', default=True, key='compare_all')],
        [sg.Radio('Compare only these: ', 'compare', key='compare_some'), sg.I('', key='wits_to_compare')],
        [sg.B('Compare', bind_return_key=True)],
        [sg.Table([['','','','','','','',]], headings=headings, key='table')],
        [sg.B('Save as CSV'), sg.B('View Plain Text')],
    ]

def layout(settings):
    return [
        [sg.B('Back', key='exit'), sg.Stretch()],
        [sg.TabGroup([[sg.Tab('Manage Databases', manage_db_tab_layout(settings)), sg.Tab('Compare Witnesses', compare_wits_tab_layout(settings))]])]
    ]

def open_cbgm_ui(font, icon):
    settings = es.get_settings()
    window = sg.Window('open-cbgm Interface', layout(settings), font=font, icon=icon)

    while True:
        event, values = window.read()
        if event in [sg.WINDOW_CLOSED, None, 'exit']:
            break

        elif event == 'Populate Database':
            populate_new_database(values, window)

        elif event == 'Delete Selected':
            delete_selected(values, window)

        elif event == 'Compare':
            compare_witnesses(values, window)

        elif event == 'Save as CSV':
            save_as_csv(values, settings)

        elif event == 'View Plain Text':
            view_plain_text(values)

    window.close()
    return False
