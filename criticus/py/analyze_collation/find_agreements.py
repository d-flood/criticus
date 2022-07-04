from lxml import etree as et
from criticus.py import custom_popups as cp

def all_wits_included(wits: list, _all: str):
    if _all == '':
        return False
    _all = _all.replace(',', '').replace('.', '').split()
    for wit in _all:
        if wit not in wits:
            return False
    else:
        return True

def any_wits_included(wits: list, _any: str):
    if _any == '':
        return False
    _any = _any.replace(',', '').replace('.', '').split()
    for wit in _any:
        if wit in wits:
            return True
    else:
        False

def no_wits_included(wits: list, _none: str):
    if _none == '':
        return False
    _none = _none.replace(',', '').replace('.', '').split()
    for wit in _none:
        if wit in wits:
            return False
    else:
        return True

def make_string(rdg):
    app = rdg.getparent()
    if app.get('from') == app.get('to'):
        app_unit = app.get('from')
    else:
        app_unit = f"{app.get('from')}-{app.get('to')}"
    app_to_append = f"{app.get('n')} #{app_unit}\t{rdg.get('n')}"
    return app_to_append

def find_agreements(values: dict):
    if values['xml_file'] == '':
        cp.ok('Select an XML file')
        return
    if values['all'] == '' and values['any'] == '' and values['none'] == '':
        cp.ok('Please fill in at least one field', 'Form Incomplete')
        return
    tei_ns = 'http://www.tei-c.org/ns/1.0'
    agreements = []
    parser = et.XMLParser(remove_blank_text=True)
    try:
        xml = et.parse(values['xml_file'], parser)
    except Exception as e:
        cp.ok(f'Failed to parse XML\n{e}', 'Bummer')
        return
    try:
        for rdg in xml.xpath('//tei:rdg', namespaces={'tei': tei_ns}):
            wits = rdg.get('wit').split()
            if values['all'] != '':
                if not all_wits_included(wits, values['all']):
                    continue
            if values['any'] != '':
                if not any_wits_included(wits, values['any']):
                    continue
            if values['none'] != '':
                if not no_wits_included(wits, values['none']):
                    continue
            agreements.append(make_string(rdg))
            
    except Exception as e:
        cp.ok(f'Something unexpected was in or not in this file\n{e}', 'Bummer')
        return
    
    number = f'Total: {len(agreements)}'
    agreements.insert(0, number)
    return agreements