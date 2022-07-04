import re
from pathlib import Path

from lxml import etree as et

tei_ns = 'http://www.tei-c.org/ns/1.0'
xml_ns = 'http://www.w3.org/XML/1998/namespace'

def get_wits(xml):
    wits = []
    distinct_wits = set()
    for rdg in xml.xpath('//tei:rdg', namespaces={'tei': tei_ns}):
        if not rdg.get('wit'):
            ar = rdg.getnext()
            rdg.getparent().remove(rdg)
            ar.attrib['n'] = 'a'
            ar.attrib.pop('type')
            continue
        for wit in rdg.get('wit').split():
            if wit not in distinct_wits:
                distinct_wits.add(wit)
                wits.append(wit)
    return wits

def add_tei_header(xml, title_stmt: str, publication_stmt: str):
    #Get a List of witness sigla first:
    wits = get_wits(xml)
    #Get the <TEI> element:
    TEI = xml.xpath('//tei:TEI', namespaces={'tei': tei_ns})[0]
    #Append a <teiHeader> element to it:
    teiHeader = et.Element('teiHeader', nsmap={None: tei_ns, 'xml': xml_ns})
    TEI.insert(0, teiHeader)
    #Append a <fileDesc> element to the teiHeader:
    fileDesc = et.Element('fileDesc', nsmap={None: tei_ns, 'xml': xml_ns})
    teiHeader.append(fileDesc)
    #Append a <titleStmt> element to the fileDesc:
    titleStmt = et.Element('titleStmt', nsmap={None: tei_ns, 'xml': xml_ns})
    fileDesc.append(titleStmt)
    #Append a placeholder paragraph to the titleStmt:
    titleStmt_p = et.Element('p', nsmap={None: tei_ns, 'xml': xml_ns})
    titleStmt_p.text = title_stmt
    titleStmt.append(titleStmt_p)
    #Append a <publicationStmt> element to the fileDesc:
    publicationStmt= et.Element('titleStmt', nsmap={None: tei_ns, 'xml': xml_ns})
    fileDesc.append(publicationStmt)
    #Append a placeholder paragraph to the publicationStmt:
    publicationStmt_p = et.Element('p', nsmap={None: tei_ns, 'xml': xml_ns})
    publicationStmt_p.text = publication_stmt
    publicationStmt.append(publicationStmt_p )
    #Append a <sourceDesc> element to the fileDesc:
    sourceDesc = et.Element('sourceDesc', nsmap={None: tei_ns, 'xml': xml_ns})
    fileDesc.append(sourceDesc)
    #Append a <listWit> element to the sourceDesc:
    listWit = et.Element('listWit', nsmap={None: tei_ns, 'xml': xml_ns})
    sourceDesc.append(listWit)
    #Append a <witness> element for each witness we have to the listWit:
    for wit in wits:
        witness = et.Element('witness', nsmap={None: tei_ns, 'xml': xml_ns})
        witness.set('n', wit)
        listWit.append(witness)
    return

def clean_wits(xml):
    for rdg in xml.xpath('//tei:rdg', namespaces={'tei': tei_ns}):
        wits = rdg.get('wit')
        wits = re.sub(r'\([^()]*\)', '', wits)
        rdg.attrib['wit'] = wits

def replace_header(xml):
    TEI = xml.xpath('//tei:TEI', namespaces={'tei': tei_ns})[0]
    header = xml.xpath('//tei:teiHeader', namespaces={'tei': tei_ns})[0]
    TEI.remove(header)
    add_tei_header(xml, 'title', 'publication')

def clean_xml(xml_path: str):
    parser = et.XMLParser(remove_blank_text=True)
    xml = et.parse(xml_path, parser)
    for ab in xml.xpath('//tei:ab', namespaces={'tei': tei_ns}):
        ab.text = ''
    clean_wits(xml)
    replace_header(xml)
    temp = Path('temp_cleaned_xml_open-cbgm').absolute().as_posix()
    xml.write(temp, encoding='utf-8')
    return temp
