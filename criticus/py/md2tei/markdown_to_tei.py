import lxml.etree as et
from markdown import Markdown
from criticus.py.md2tei.md_tei_extension import TEI, postprocess_xml, preprocess_md, postprocess_markup # pylint: disable=import-error


def convert_md_to_tei(md_file, xml_file, plain: bool, lines: bool):
    M = Markdown(extensions=['attr_list', TEI(), 'markdown_del_ins'])
    with open(md_file, 'r', encoding='utf-8') as file:
        md = file.read()

    md = preprocess_md(md)
    markup = M.convert(md)
    markup = postprocess_markup(markup)

    parser = et.XMLParser(remove_blank_text=True, encoding='UTF-8')
    xml = et.fromstring(markup, parser)
    xml = postprocess_xml(xml)

    xml = xml.getroottree()
    if plain:
        xml.write(xml_file, encoding='utf-8')
    elif lines:
        xml_str = et.tostring(xml, encoding='unicode')
        xml_str = xml_str.replace('\n', '')
        xml_str = xml_str.replace('<pb', '\n<pb')
        xml_str = xml_str.replace('<lb', '\n    <lb')
        with open(xml_file, 'w', encoding='utf-8') as f:
            f.write(xml_str)
    else:
        et.indent(xml, '    ')
        xml.write(xml_file, encoding='utf-8', pretty_print=True)
