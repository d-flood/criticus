import traceback

from lxml import etree as et

from criticus.py.reformat_collation.clean_wits import remove_redundant_correctors
from criticus.py.reformat_collation.differentiate_subreading_ids import (
    differentiate_subreading_ids as diff_ids,
)
from criticus.py.reformat_collation.itsee_to_open_cbgm import reformat_xml

# pylint: disable=no-member


def fix_NCNames(xml_fn):
    """lxml throws a syntax eror when the id attribute is set to a number, even though it is a string.
    The Collation Editor is allowing invalid XML to be created, I guess"""
    fixed = "temp_repaired_xml"
    with open(xml_fn, "r", encoding="utf-8") as f:
        xml = f.read()
    xml = xml.replace('xml:id="1', 'xml:id="I')
    xml = xml.replace('xml:id="2', 'xml:id="II')
    xml = xml.replace('xml:id="3', 'xml:id="III')
    with open(fixed, "w", encoding="utf-8") as f:
        f.write(xml)
    return fixed


def convert(
    xml_input_file: str, save_path: str, title_stmt: str, publication_stmt: str
):
    invalid_ncnames = False
    if not xml_input_file:
        return {
            "type": "warning",
            "modal_text": "Browse to select an XML collation file to convert",
        }
    try:
        try:
            xml_fn = reformat_xml(xml_input_file, title_stmt, publication_stmt)
        except et.XMLSyntaxError:
            invalid_ncnames = True
            xml_fn = fix_NCNames(xml_input_file)
            try:
                xml_fn = reformat_xml(xml_fn, title_stmt, publication_stmt)
            except Exception:
                return {
                    "type": "fail",
                    "modal_text": "There are invalid NCNames in this XML file. Criticus tried and failed to fix them. This is usually caused by an attribute 'xml:id' with a number for a value.",
                    "error_text": traceback.format_exc(),
                }
        xml = diff_ids(xml_fn)
        xml.write(save_path, encoding="utf-8", xml_declaration=True, pretty_print=True)
        modal_text = "XML Collation File was successfully reformatted and saved!"
        if invalid_ncnames:
            modal_text += "<br> Invalid NCNames were found and fixed."
        return {
            "type": "success",
            "modal_text": modal_text,
        }
    except Exception:
        return {
            "type": "fail",
            "modal_text": "Failed to reformat XML file. Check that the input file name is correct and that this is the output of the ITSEE Collation Editor. Detailed error below:",
            "error_text": traceback.format_exc(),
        }


def clean_wits(xml_input_file: str, save_path: str):
    try:
        xml = remove_redundant_correctors(xml_input_file)
    except Exception:
        return {
            "type": "fail",
            "modal_text": "Failed to clean witnesses in the collation file. Check that the input file name is correct and that this is the output of the ITSEE Collation Editor. Detailed error below:",
            "error_text": traceback.format_exc(),
        }
    xml.write(save_path, encoding="utf-8", xml_declaration=True, pretty_print=True)
    return {
        "type": "success",
        "modal_text": "Witnesses were successfully cleaned and the new file saved!",
    }
