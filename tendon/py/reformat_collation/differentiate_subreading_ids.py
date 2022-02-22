from lxml import etree as et

def differentiate_subreading_ids(xml_filename) -> et._ElementTree:
    ns = '{http://www.tei-c.org/ns/1.0}'
    parser = et.XMLParser(remove_blank_text=True)
    xml = et.parse(xml_filename, parser=parser)
    root = xml.getroot()
    for ab in root:
        for app in ab:
            n_num = 1
            for elem in app:
                if elem.tag == f'{ns}rdg' and 'r' in elem.get('n'):
                    elem.attrib['n'] = f'{elem.get("n")}{n_num}'
                    n_num += 1
                elif elem.tag == f'{ns}note': # this is a <note> element
                    for child in elem: # this is a <note> child
                        if child.tag == f'{ns}graph':
                            node_num = 1
                            for node in child:
                                if node.tag == f'{ns}node':
                                    if 'r' in node.get('n'):
                                        distinct_attrib = f'{node.get("n")}{node_num}'
                                        node.attrib['n'] = distinct_attrib
                                        arc = et.Element('arc')
                                        arc.attrib['from'] = distinct_attrib[0]
                                        arc.attrib['to'] = distinct_attrib
                                        node.getparent().append(arc)
                                        node_num += 1
    # xml.write(xml_filename, encoding='utf8')
    return xml
