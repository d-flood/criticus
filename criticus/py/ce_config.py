import json
import os
import platform
import subprocess
import webbrowser
from pathlib import Path

from natsort import natsorted


# pylint: disable=no-member
def get_config(fn: str) -> dict | None:
    with open(fn, "r", encoding="utf-8") as f:
        config: dict = json.load(f)
        if not config.get("excluded_witnesses"):
            config["excluded_witnesses"] = []
        return config


def save_config(config: dict, fn: str):
    config["witnesses"] = sort_by_ga(config["witnesses"])
    config["excluded_witnesses"] = sort_by_ga(config["excluded_witnesses"])
    with open(fn, "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=4)


def edit_config(values):
    config = get_config(values["config_fn"])
    if values["name"] != "":
        config["name"] = values["name"]
    if values["basetext"] != "":
        config["base_text"] = values["basetext"]
    save_config(config, values["config_fn"])


def sort_by_ga(wits: list[str]):
    papyri = []
    majuscules = []
    minuscules = []
    lectionaries = []
    editions = []
    for wit in wits:
        if wit.lower().startswith("p"):
            papyri.append(wit)
        elif wit.startswith("0"):
            majuscules.append(wit)
        elif wit[0].isdigit():
            minuscules.append(wit)
        elif wit.lower().startswith("l"):
            lectionaries.append(wit)
        else:
            editions.append(wit)
    return (
        natsorted(papyri)
        + natsorted(majuscules)
        + natsorted(minuscules)
        + natsorted(lectionaries)
        + natsorted(editions)
    )


def remove_from_config(config: dict, key, item_to_remove: str):
    new_list = []
    for wit in config[key]:
        if wit != item_to_remove and wit not in new_list:
            new_list.append(wit)
    config[key] = new_list
    return config


def add_to_config(config: dict, key: str, item_to_add: str):
    if item_to_add not in config[key]:
        config[key].append(item_to_add)
    return config


def delete_selection(values: dict):
    if values["excluded"] == []:
        return
    config = get_config(values["config_fn"])
    for wit in values["excluded"]:
        config = remove_from_config(config, "excluded_witnesses", wit)
    save_config(config, values["config_fn"])


def order_witnesses(config: dict):
    config["witnesses"] = sort_by_ga(config["witnesses"])
    config["excluded_witnesses"] = sort_by_ga(config["excluded_witnesses"])
    return config


def move_selected_witnesses(config: dict, selected: list[str], move_type: str):
    if move_type not in ["exclude", "include"]:
        raise ValueError("move_type must be either 'exclude' or 'include'")

    target_key = "excluded_witnesses" if move_type == "exclude" else "witnesses"
    source_key = "witnesses" if move_type == "exclude" else "excluded_witnesses"

    for wit in selected:
        if wit not in config[target_key]:
            config[target_key].append(wit)
            config = remove_from_config(config, source_key, wit)
    config = order_witnesses(config)
    return config


def delete_selected_witnesses(config: dict, selected: list[str]):
    for wit in selected:
        config = remove_from_config(config, "excluded_witnesses", wit)
    config = order_witnesses(config)
    return config


def start_ce(config_file: str):
    cwd = os.getcwd()
    root_dir = Path(config_file).parent.parent.parent.parent.parent.as_posix()
    print(root_dir)
    os.chdir(root_dir)
    try:
        if platform.system() == "Windows":
            from subprocess import CREATE_NEW_CONSOLE

            subprocess.Popen(
                "start startup.bat", shell=True, creationflags=CREATE_NEW_CONSOLE
            )
            subprocess.Popen(
                "start firefox http://localhost:8080/collation", shell=True
            )
        else:
            subprocess.Popen("bash startup.sh", shell=True)
            webbrowser.get("firefox").open("http:localhost:8080/collation")
    except Exception:
        print("cold not open browser")
    os.chdir(cwd)
    return
