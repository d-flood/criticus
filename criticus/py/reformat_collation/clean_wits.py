import re

from lxml import etree as et


def clean_wits(wits: list[str]) -> str:
    cleaned_wits = list(wits)
    for wit in wits:
        if 'c' not in wit:
            continue
        first_hand = re.sub(r'c1|c2|c3|c4|c5|c', '', wit)
        if first_hand in wits:
            cleaned_wits.remove(wit)
    return ' '.join(cleaned_wits)


def remove_redundant_correctors(input_addr: str):
    tei_ns = 'http://www.tei-c.org/ns/1.0'

    parser = et.XMLParser(remove_blank_text=True)
    xml = et.parse(input_addr, parser)
    for rdg in xml.xpath('//tei:rdg', namespaces={'tei': tei_ns}):
        wits = rdg.get('wit').split()
        cleaned_wits = clean_wits(wits)
        rdg.attrib['wit'] = cleaned_wits
    return xml