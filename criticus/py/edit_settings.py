import json
from pathlib import Path
import sys

if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'): # shipped app
    main_dir = Path(sys.executable).parent.joinpath('resources').as_posix()
else: # dev
    main_dir = Path(__file__).parent.parent.joinpath('resources').as_posix()


def get_settings():
    try:
        with open(f'{main_dir}/settings.json', 'r') as f:
            settings = json.load(f)
        _ = (
            settings['ce_repo_dir'],
            settings['tx_dir'],
            settings['ce_output_dir'],
            settings['markdown_tx_dir'],
            settings['converted_markdown_tx_dir'],
            settings['tei_dir'],
            settings['combined_xml_dir'],
            settings['reformatted_xml_dir'],
            settings['ce_config_fn'],
            settings['txt_from_json_dir'],
            settings['plain_text_dir'],
            settings['cbgm_main_dir'],
            settings['cbgm_cx_dir'],
            settings['pre_parse_regex'],
            settings['custom_template_path'],
            settings['wits_separator'],
            ) 
    except:
        settings = {
            'ce_repo_dir': '',
            'tx_dir': '',
            'ce_output_dir': '',
            'markdown_tx_dir': '',
            'converted_markdown_tx_dir': '',
            'tei_dir': '',
            'combined_xml_dir': '',
            'reformatted_xml_dir': '',
            'ce_config_fn': '',
            'txt_from_json_dir': '',
            'plain_text_dir': '',
            'cbgm_main_dir': '',
            'cbgm_cx_dir': '',
            'pre_parse_regex': [],
            'export_docx_folder': '',
            'text_wits_separator': ' // ',
            'rdg_n_text_separator': '\t',
            'wits_separator': '',
            'words_per_line': 10,
            'text_bold': False,
            'custom_template_path': '',
        }
        save_settings(settings)
    return settings

def save_settings(settings: dict):
    with open(f'{main_dir}/settings.json', 'w') as f:
        json.dump(settings, f, indent=4)

def edit_settings(setting_key: str, value):
    settings = get_settings()
    settings[setting_key] = value
    save_settings(settings)
