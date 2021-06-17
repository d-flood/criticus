import json
from pathlib import Path
from typing import Dict, List
import tendon.py.edit_settings as es


def get_file(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        text = f.readlines()
    return text

def get_info_from_filename(filename):
    filename = filename.split('/')[-1]
    f = filename.split('_')
    siglum = f[0]
    reference_prefix = f[1].replace('.txt', '')
    return siglum, reference_prefix

def format_reference(line: List[str], reference_prefix: str):
    if reference_prefix[-1].isdigit():
        seperator = '.'
    else:
        seperator = ''
    verse = line.pop(0)
    reference = verse.replace(':', '.')
    reference = f'{reference_prefix}{seperator}{reference}'
    return line, reference, verse

def convert_this_line(verse: str, verse_from, verse_to) -> bool:
    if verse.replace(':', '.') in [verse_from.replace(':', '.'), verse_to.replace(':', '.')]:
        return True
    else:
        return False

def build_token(word: str, index: str, siglum: str) -> dict:
    return {
        'index': index,
        'siglum': siglum,
        'reading': siglum,
        'original': word,
        'rule_match': [word],
        't': word
    }

def build_witneses(siglum: str, tokens: List[dict]):
    return [{
        'id': siglum,
        'tokens': tokens
    }]

def build_json(siglum, reference, witnesses: List[dict], line: list):
    return {
        'id': siglum,
        '_id': siglum,
        'transcription': siglum,
        'transcription_siglum': siglum,
        'siglum': siglum,
        'context': reference,
        'n': reference,
        'text': ' '.join(line),
        'witnesses': witnesses
    }

def make_tokens(line, siglum) -> List[dict]:
    tokens = []
    for i, word in enumerate(line, 1):
        index = f'{i*2}'
        token = build_token(word, index, siglum)
        tokens.append(token)
    return tokens

def save_json(to_save: dict, reference: str, output_dir: str, siglum: str):
    with open(f'{output_dir}/{siglum}/{reference}.json', 'w', encoding='utf-8') as f:
        json.dump(to_save, f, ensure_ascii=False, indent=4)

def save_metadata(siglum, output_dir):
    metadata = {'_id': siglum, 'siglum': siglum, 'id': siglum}
    with open(f'{output_dir}/{siglum}/metadata.json', 'w', encoding='utf-8') as f:
        json.dump(metadata, f, ensure_ascii=False)

def construct_json_transcription(line: List[str], reference: str, siglum: str, output_dir):
    tokens = make_tokens(line, siglum)
    witnesses = build_witneses(siglum, tokens)
    complete_json = build_json(siglum, reference, witnesses, line)
    save_json(complete_json, reference, output_dir, siglum)

def check_and_save_dirs(output_dir, siglum):
    output_dir = Path(f'{output_dir}/{siglum}')
    if not output_dir.exists():
        Path.mkdir(output_dir, parents=True)
    output_dir = output_dir.parent.absolute().as_posix()
    es.edit_settings('output_dir', output_dir)

def convert_text_to_json(
    filename, output_dir, convert_all: bool,
    reference_prefix: str, auto: bool, verse_from: str=None, 
    verse_to: str=None, siglum: str=None
    ):
    check_and_save_dirs(output_dir, siglum)
    save_metadata(siglum, output_dir)  
    text = get_file(filename)
    if auto:
        siglum, reference_prefix = get_info_from_filename(filename)
    capture = False
    for line in text:
        line = line.split()
        if len(line) > 2 and line[0][0].isdigit() and line[0][-1].isdigit(): # check that line contains a reference and a text unit and is not a heading
            line, reference, verse = format_reference(line, reference_prefix)

            if not convert_all and verse_to != verse_from: # handle a range of text units to convert
                if convert_this_line(verse, verse_from, verse_to):
                    capture = not capture
                    construct_json_transcription(line, reference, siglum, output_dir)
                elif capture:
                    construct_json_transcription(line, reference, siglum, output_dir)

            elif not convert_all and verse_from == verse_to: # handle a single text unit
                if convert_this_line(verse, verse_from, verse_to):
                    construct_json_transcription(line, reference, siglum, output_dir)

            else:
                construct_json_transcription(line, reference, siglum, output_dir) # handle all text units


# convert_text_to_json(filename, output_dir, convert_all, reference_prefix, auto=False, verse_from=verse_from, verse_to=verse_to, siglum=siglum)
