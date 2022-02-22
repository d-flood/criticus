import json
import lxml.etree as et

import PySimpleGUI as sg

from criticus.py.tei2json.to_json import verse_to_dict, save_tx
from criticus.py.tei2json.from_tei import (get_file, pre_parse_cleanup,
                      add_underdot_to_unclear_letters,
                      parse, remove_unclear_tags,
                      tei_ns, get_verse_as_tuple)
import criticus.py.custom_popups as cp
# pylint: disable=no-member
#########
def get_siglum_from_user() -> str:
    msg = '''criticus could not find the siglum.
Please enter a witness ID: '''
    layout = [[sg.T(msg)],
              [sg.I('', key='siglum')],
              [sg.B('Submit')]]
    window = sg.Window('Provide a Siglum', layout)
    siglum = ''
    while True:
        event, values = window.read()
        if event in [None, sg.WINDOW_CLOSED]:
            siglum = values['siglum']
            break
        elif event == 'Submit' and values['siglum'] != '':
            siglum = values['siglum']
            break
    window.close()
    return siglum
#########

def get_siglum(root: et._Element) -> str:
    titles = root.xpath('//tei:title', namespaces={'tei': tei_ns})
    for title in titles:
        if title.get('n'):
            siglum = title.get('n')
            siglum = siglum.replace('-ns', '')
            break
    else:
        siglum = ''
        while siglum == '':
            siglum = get_siglum_from_user()
    return siglum

def get_hands(root: et._Element) -> list:
    rdgs = root.xpath('//tei:rdg', namespaces={'tei': tei_ns})
    hands = []
    for rdg in rdgs:
        if rdg.get('hand') and rdg.get('hand') not in hands:
            hands.append(rdg.get('hand'))
    if hands == []:
        hands = ['firsthand']
    return hands

def tei_to_json(tei: str, output_dir, single_verse: str):
    text = get_file(tei)
    text = pre_parse_cleanup(text)
    parsed, root = parse(text)
    if not parsed:
        cp.ok(f'Failed to parse XML. See error:\n{root}', title='Bummer...')
        return False
    add_underdot_to_unclear_letters(root)
    text = et.tostring(root, encoding='unicode')
    text = remove_unclear_tags(text)
    _, root = parse(text)
    hands = get_hands(root)
    siglum = get_siglum(root)
    output_dir = f'{output_dir}/{siglum}'
    metadata = {'id': siglum, 'siglum': siglum}
    verses = root.xpath(f'//tei:ab', namespaces={'tei': tei_ns})
    for verse in verses:
        ref = verse.get('n')
        if single_verse != '' and single_verse != ref:
            continue
        witnesses = get_verse_as_tuple(verse, hands=hands)
        verse_as_dict = verse_to_dict(siglum, ref, witnesses)
        save_tx(verse_as_dict, ref, output_dir)
    if output_dir:
        f = f'{output_dir}/metadata.json'
    else:
        f = 'metadata.json'
    with open(f, 'w', encoding='utf-8') as file:
        json.dump(metadata, file, ensure_ascii=False)
    return True
