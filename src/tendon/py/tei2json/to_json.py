import json
from pathlib import Path
from typing import List

def regularize_word(word: str):
    word = word.replace('\u0323', '')
    word = word.replace('[', '')
    word = word.replace(']', '')
    return word

def words_to_tokens(words: list, siglum: str, ):
    tokens = []
    gap_before = False
    gap_after = False
    for i, word in enumerate(words, start=1):
        gap_after = False
        gap_before = False
        if f"___{word.replace('___', '')}" == word:
            gap_before = True
            word = word.replace('___', '')
        elif f"{word.replace('___', '')}___" == word:
            gap_after = True
            word = word.replace('___', '')
        regularized = regularize_word(word)
        token = {'index': f'{i*2}',
                 'siglum': siglum,
                 'reading': siglum,
                 'original': word,
                 'rule_match': [regularized],
                 't': regularized}
        if gap_after:
            token['gap_after'] = True
        if gap_before:
            token['gap_before'] = True
        tokens.append(token)
    return tokens


def dictify_witnesses(witness: tuple, siglum):
    if witness[0] != 'firsthand':
        corrector = witness[0].replace('corrector', 'c')
        siglum = f'{siglum}{corrector}'
    return {
        'id': siglum,
        'tokens': words_to_tokens(witness[1], siglum)
    }

def dictify_transcription(siglum: str, ref: str, plain_tx: str, witnesses: List[dict]) -> dict:
    return {
        'id': f'{siglum}_{ref}',
        'transcription': siglum,
        'transcription_siglum': siglum,
        'siglum': siglum,
        'context': ref, 
        'n': ref,
        'plain_text': plain_tx,
        'witnesses': witnesses
    }

def save_tx(transcription: dict, filename: str, output_dir: str):
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)
    output_dir = output_path.as_posix()
    fn = f'{output_dir}/{filename}.json'
    with open(fn, 'w', encoding='utf-8') as file:
        json.dump(transcription, file, ensure_ascii=False, indent=4)

def verse_to_dict(siglum: str, ref: str, witnesses: List[tuple]) -> dict:
    wits = []
    plain = ' '.join(witnesses[0][1]).replace('___', '')
    for witness in witnesses:
        wits.append(dictify_witnesses(witness, siglum))
    transcription = dictify_transcription(siglum, ref, plain, wits)
    return transcription
