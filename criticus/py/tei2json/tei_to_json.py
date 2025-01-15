import json

import lxml.etree as et

from criticus.py.tei2json.from_tei import (
    add_underdot_to_unclear_letters,
    get_file,
    get_verse_as_tuple,
    parse,
    pre_parse_cleanup,
    remove_unclear_tags,
    tei_ns,
)
from criticus.py.tei2json.to_json import save_tx, verse_to_dict

# pylint: disable=no-member
#########


def get_siglum(root: et._Element, siglum: str | None) -> str | None:
    if siglum:
        return siglum
    titles = root.xpath("//tei:title", namespaces={"tei": tei_ns})
    for title in titles:
        if title.get("n"):
            siglum = title.get("n")
            siglum = siglum.replace("-ns", "")
            return siglum
    return None


def get_hands(root: et._Element) -> list:
    rdgs = root.xpath("//tei:rdg", namespaces={"tei": tei_ns})
    hands = []
    for rdg in rdgs:
        if rdg.get("hand") and rdg.get("hand") not in hands:
            hands.append(rdg.get("hand"))
    if hands == []:
        hands = ["firsthand"]
    return hands


def tei_to_json(
    tei_file_path: str,
    output_dir: str,
    single_verse: str,
    siglum_suffix: str,
    regexes,
    siglum: str = None,
):
    text = get_file(tei_file_path)
    text = pre_parse_cleanup(text, regexes)
    if isinstance(text, tuple):
        return text[1]
    parsed, root = parse(text)
    if not parsed:
        return f"Failed to parse XML. See error:\n{root}"
    add_underdot_to_unclear_letters(root)
    text = et.tostring(root, encoding="unicode")
    text = remove_unclear_tags(text)
    _, root = parse(text)
    hands = get_hands(root)
    siglum = get_siglum(root, siglum)
    if not siglum:
        return "No siglum found in TEI file. It may work to provide one and try again, or this may be an indication that the TEI file is not formatted correctly."
    if siglum_suffix:
        siglum = f"{siglum}-{siglum_suffix}"
    output_dir = f"{output_dir}/{siglum}"
    metadata = {"id": siglum, "siglum": siglum}
    verses = root.xpath("//tei:ab", namespaces={"tei": tei_ns})
    for verse in verses:
        ref = verse.get("n")
        if single_verse and single_verse != ref:
            continue
        witnesses = get_verse_as_tuple(verse, hands=hands)
        verse_as_dict = verse_to_dict(siglum, ref, witnesses)
        save_tx(verse_as_dict, ref, output_dir)
    if output_dir:
        f = f"{output_dir}/metadata.json"
    else:
        f = "metadata.json"
    with open(f, "w", encoding="utf-8") as file:
        json.dump(metadata, file, ensure_ascii=False)
    return True
