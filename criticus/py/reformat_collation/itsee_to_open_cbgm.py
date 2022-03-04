"""
Many thanks to Joey McCollum, from whose code this was slightly adapted. 
(https://github.com/jjmccollum/itsee-to-open-cbgm)
It was downloaded on June 1, 2020

The only modification I have made occurs in the main function:
This script is now a module that is called from a main application 
instead of a standalone command line utility.
"""

"""MIT License

Copyright (c) 2020 Joey McCollum

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import re
from lxml import etree as et

"""
XML namespaces
"""
xml_ns = 'http://www.w3.org/XML/1998/namespace'
tei_ns = 'http://www.tei-c.org/ns/1.0'

"""
Book index to SBL book abbreviation Dictionary
"""
books_by_n = {
    'B01': 'Matt',
    'B02': 'Mark',
    'B03': 'Luke',
    'B04': 'John', 
    'B05': 'Acts',
    'B06': 'Rom',
    'B07': '1 Cor',
    'B08': '2 Cor', 
    'B09': 'Gal',
    'B10': 'Eph',
    'B11': 'Phil',
    'B12': 'Col',
    'B13': '1 Thess',
    'B14': '2 Thess',
    'B15': '1 Tim',
    'B16': '2 Tim',
    'B17': 'Titus',
    'B18': 'Phlm',
    'B19': 'Heb',
    'B20': 'Jas', 
    'B21': '1 Pet',
    'B22': '2 Pet', 
    'B23': '1 John',
    'B24': '2 John', 
    'B25': '3 John', 
    'B26': 'Jude',
    'B27': 'Rev'
}

"""
Returns a List of all witness IDs encountered in the input XML tree.
"""
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

"""
Adds a <teiHeader> with appropriate subelements as the first child of the input XML's <TEI> element.
The <listWit> element in particular is needed for the open-cbgm library.
"""
def add_tei_header(xml):
    #Get a List of witness sigla first:
    wits = get_wits(xml)
    #Get the <TEI> element:
    TEI = xml.xpath('//tei:TEI', namespaces={'tei': tei_ns})[0]
    #Append a <teiHeader> element to it:
    teiHeader = et.Element('teiHeader', nsmap={None: tei_ns, 'xml': xml_ns})
    TEI.insert(0, teiHeader)
    #Append a <sourceDesc> element to the teiHeader:
    sourceDesc = et.Element('sourceDesc', nsmap={None: tei_ns, 'xml': xml_ns})
    teiHeader.append(sourceDesc)
    #Append a <listWit> element to the sourceDesc:
    listWit = et.Element('listWit', nsmap={None: tei_ns, 'xml': xml_ns})
    sourceDesc.append(listWit)
    #Append a <witness> element for each witness we have to the listWit:
    for wit in wits:
        witness = et.Element('witness', nsmap={None: tei_ns, 'xml': xml_ns})
        witness.set('n', wit)
        listWit.append(witness)
    return

"""
Strips the input XML of all <wit> elements.
(These elements are not needed, as the "wit" attribute of their parent <rdg> element 
contains the same information.)
"""
def strip_wit_subelements(xml):
    for wit in xml.xpath('//tei:wit', namespaces={'tei': tei_ns}):
        wit.getparent().remove(wit)
    return

"""
Strips the input XML of every <app> element without "from" and "to" elements 
(i.e, superfluous apparatus elements used to describe which witnesses are lacunose for entire verses).
"""
def strip_unitless_apps(xml):
    for app in xml.xpath('//tei:app[not(@from) and not(@to)]', namespaces={'tei': tei_ns}):
        app.getparent().remove(app)
    return

"""
Converts escaped Unicode character codes for combining underdots to the corresponding characters.
"""
def unescape_underdots(xml):
    for rdg in xml.xpath('//tei:lem|//tei:rdg', namespaces={'tei': tei_ns}):
        if rdg.text is not None and '&amp;#803;' in rdg.text:
            rdg.text = rdg.text.replace('&amp;#803;', '\u0323')
    return

"""
Strips the text from all <lem> and <rdg> elements in the input XML that have type="om".
"""
def strip_om_text(xml):
    for rdg in xml.xpath('//tei:lem[@type="om"]|//tei:rdg[@type="om"]', namespaces={'tei': tei_ns}):
        rdg.text = None
    return

"""
Replaces <app> elements having only one reading in the input XML with <seg> elements containing that reading.
"""
def sub_segs_for_apps(xml):
    for app in xml.xpath('//tei:app', namespaces={'tei': tei_ns}):
        rdgs = app.xpath('tei:rdg', namespaces={'tei': tei_ns})
        if len(rdgs) == 1:
            seg = et.Element('seg', nsmap={None: tei_ns, 'xml': xml_ns})
            seg.text = rdgs[0].text
            app.getparent().replace(app, seg)
    return

"""
Under each <app> element in the input XML, 
adds a <note> element containing a variation unit label, 
a default connectivity value, and a local stemma without edges.
"""
def add_app_notes(xml):
    for app in xml.xpath('//tei:app', namespaces={'tei': tei_ns}):
        #First, get the "n", "from", and "to" attributes of this apparatus:
        app_n = app.get('n')
        app_from = app.get('from')
        app_to = app.get('to')
        #Then get a List of its reading numbers:
        rdg_ids = []
        for rdg in app.xpath('tei:rdg', namespaces={'tei': tei_ns}):
            if rdg.get('n') is not None:
                rdg_ids.append(rdg.get('n'))
        #Add a <note> element as the last child of the <app> element:
        note = et.Element('note', nsmap={None: tei_ns, 'xml': xml_ns})
        app.append(note)
        #Then add a <label> element under the note, if one can be constructed from the attributes of the apparatus:
        match = re.match('(B\d+)(K\d+)(V\d+)', app_n)
        if match is not None:
            book_n = match.groups()[0]
            chapter_n = match.groups()[1]
            verse_n = match.groups()[2]
            label_text = books_by_n[book_n] + ' ' + chapter_n[1:] + ':' + verse_n[1:] 
            if app_from is not None:
                label_text += '/' + app_from
            if app_to is not None and app_to != app_from:
                label_text += '-' + app_to
            label = et.Element('label', nsmap={None: tei_ns, 'xml': xml_ns})
            label.text = label_text
            note.append(label)
        #Then add a <fs> element under the note:
        fs = et.Element('fs', nsmap={None: tei_ns, 'xml': xml_ns})
        note.append(fs)
        #Then add an <f> element for the "connectivity" feature under the feature set:
        f = et.Element('f', nsmap={None: tei_ns, 'xml': xml_ns})
        f.set('name', 'connectivity')
        fs.append(f)
        #Then add a <numeric> element under the feature with the default connectivity value:
        numeric = et.Element('numeric', nsmap={None: tei_ns, 'xml': xml_ns})
        numeric.set('value', '10')
        f.append(numeric)
        #Then add a <graph> element under the note:
        graph = et.Element('graph', nsmap={None: tei_ns, 'xml': xml_ns})
        graph.set('type', 'directed')
        note.append(graph)
        #Then, add a <node> element for each reading under the graph:
        for rdg_id in rdg_ids:
            node = et.Element('node', nsmap={None: tei_ns, 'xml': xml_ns})
            node.set('n', rdg_id)
            graph.append(node)
    return


def reformat_xml(input_addr):
    output_addr = 'temp_xml_collation_file'
    parser = et.XMLParser(remove_blank_text=True)
    xml = et.parse(input_addr, parser)
    add_tei_header(xml)
    strip_wit_subelements(xml)
    strip_unitless_apps(xml)
    strip_om_text(xml)
    sub_segs_for_apps(xml)
    add_app_notes(xml)
    xml.write(output_addr, encoding='utf-8', xml_declaration=True, pretty_print=True)
    return output_addr
    