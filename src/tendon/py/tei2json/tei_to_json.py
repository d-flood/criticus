import json
import lxml.etree as et

from tendon.py.tei2json.to_json import verse_to_dict, save_tx
from tendon.py.tei2json.from_tei import (get_file, pre_parse_cleanup,
                      add_underdot_to_unclear_letters,
                      parse, remove_unclear_tags,
                      tei_ns, get_verse_as_tuple)

def tei_to_json(tei: str, output_dir, single_verse: str):
    text = get_file(tei)
    text = pre_parse_cleanup(text)
    root = parse(text)
    add_underdot_to_unclear_letters(root)
    text = et.tostring(root, encoding='unicode')
    text = remove_unclear_tags(text)
    root = parse(text)
    # write_xml(root)
    hands = ['firsthand', 'corrector']
    siglum = root.xpath('//tei:title', namespaces={'tei': tei_ns})[0].get('n')
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
