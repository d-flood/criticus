from enum import unique
from lxml import etree as et

def version_rdgs(elem: et._Element, regularized: dict):
    if elem.get('n') in regularized:
        regularized[elem.get('n')] += 1
    else:
        regularized[elem.get('n')] = 1
    unique_name = f'{elem.get("n")}{regularized[elem.get("n")]}'
    elem.attrib['n'] = unique_name
    return regularized, unique_name

def differentiate_subreading_ids(xml_filename) -> et._ElementTree:
    ns = '{http://www.tei-c.org/ns/1.0}'
    parser = et.XMLParser(remove_blank_text=True)
    xml = et.parse(xml_filename, parser=parser)
    root = xml.getroot()
    for ab in root:
        for app in ab:
            regularized = {}
            for elem in app:
                if elem.tag == f'{ns}rdg' and 'r' in elem.get('n'):
                    regularized, _ = version_rdgs(elem, regularized)

                elif elem.tag == f'{ns}note': # this is a <note> element
                    for child in elem: # this is a <note> child
                        if child.tag == f'{ns}graph':
                            regularized = {}
                            for node in child:
                                if node.tag == f'{ns}node':
                                    if 'r' in node.get('n'):
                                        regularized, distinct_attrib = version_rdgs(node, regularized)
                                        # distinct_attrib = f'{node.get("n")}{node_num}'
                                        # node.attrib['n'] = distinct_attrib
                                        arc = et.Element('arc')
                                        arc.attrib['from'] = distinct_attrib[0]
                                        arc.attrib['to'] = distinct_attrib
                                        node.getparent().append(arc)
    # xml.write(xml_filename, encoding='utf8')
    return xml
