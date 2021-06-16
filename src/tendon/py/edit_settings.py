import json


def get_settings():
    try:
        with open('settings.json', 'r') as f:
            settings = json.load(f)
    except:
        settings = {
            'ce_repo_dir': '',
            'tx_dir': '',
            'ce_output_dir': '',
            'markdown_tx_dir': '',
            'converted_markdown_tx_dir': '',
            'tei_dir': '',
            'combined_xml_dir': '',
            'reformatted_xml_dir': ''
        }
        save_settings(settings)
    return settings

def save_settings(settings: dict):
    with open('settings.json', 'w') as f:
        json.dump(settings, f, indent=4)

def edit_settings(setting_key: str, value):
    settings = get_settings()
    settings[setting_key] = value
    save_settings(settings)
