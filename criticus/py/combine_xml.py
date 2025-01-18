import os
from copy import deepcopy

from lxml import etree as et
from natsort import natsorted

import criticus.py.reformat_collation.itsee_to_open_cbgm as itoc

# pylint: disable=no-member


def get_verse_file(f, output_dir):
    parser = et.XMLParser(remove_blank_text=True, recover=True)
    tree = et.parse(f"{output_dir}/{f}", parser=parser)
    root = tree.getroot()
    ns = root.nsmap
    all_ab_elems = root.findall("ab", ns)
    return deepcopy(all_ab_elems)


def combine_verses(
    starting_string: str,
    input_dir: str,
    base_dir: str,
    already_formatted: bool,
    title_stmt: str,
    publication_stmt: str,
):
    tree = et.parse(f"{base_dir}/resources/template.xml")
    root = tree.getroot()
    files = os.listdir(input_dir)
    files = natsorted(files)
    failed = []
    for f in files:
        if f.startswith(starting_string):
            try:
                all_ab_elems = get_verse_file(f, input_dir)
                for ab in all_ab_elems:
                    root.append(ab)
            except Exception as e:
                failed.append(f"{f}: {e}")
    if already_formatted:
        itoc.add_tei_header(tree, title_stmt, publication_stmt)
    return tree, failed


def combine_xml_files(
    input_dir: str,
    starts_with: str,
    base_dir: str,
    save_path: str,
    already_reformatted: bool = False,
    title_stmt: str = "untitled",
    publication_stmt: str = "unspecified",
) -> et._Element:
    if not input_dir or not starts_with:
        raise ValueError("Output directory and starts_with prefix are required")

    tree, failed = combine_verses(
        starts_with,
        input_dir,
        base_dir,
        already_reformatted,
        title_stmt,
        publication_stmt,
    )

    if save_path:
        tree.write(save_path, encoding="utf-8", xml_declaration=True)

    return tree, failed
