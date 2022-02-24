import PySimpleGUI as sg 



#pylint: disable=no-member
def pc_layout():
    bs = (32, 2)

    layout = [
        # [sg.Menu(menu)],
        [sg.Button('Plain Text to JSON', key='txt_to_json', size=bs)],
        [sg.Button('Get Plain Text from JSON', key='json_to_txt', size=bs)],
        [sg.Button('Markdown to TEI', key='md_to_tei', size=bs)],
        [sg.Button('TEI to JSON', key='tei_to_json', size=bs)],
        [sg.Button('Combine Collation Files', key='combine_verses', size=bs)],
        [sg.Button('Reformat Collation File', key='reformat_xml', size=bs)],
        [sg.Button('View TEI Transcriptions', key='tei_server', size=bs)],
        [sg.Button('Configure Collation Editor', key='ce_config', size=bs)],
        [sg.Button('open-cbgm Interface', key='open-cbgm', size=bs)],
        [sg.Button('Export Collation to DOCX', key='export_to_docx', size=bs)],
        [sg.Stretch(), sg.Button('Close', pad=(20, 20), size=(20, 2)), sg.Stretch()]
    ]
    return layout
