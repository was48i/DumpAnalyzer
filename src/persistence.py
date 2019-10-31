import os
import json


def dump_components(com_dict):
    dump_path = os.path.join(os.getcwd(), "json", "components.json")
    with open(dump_path, "w") as fp:
        json.dump(com_dict, fp, indent=4, sort_keys=True)


def dump_symbols(sym_dict):
    dump_path = os.path.join(os.getcwd(), "json", "symbols.json")
    with open(dump_path, "w") as fp:
        json.dump(sym_dict, fp, indent=4, sort_keys=True)


def load_components():
    load_path = os.path.join(os.getcwd(), "json", "components.json")
    try:
        with open(load_path, "r") as fp:
            com_dict = json.load(fp)
    except FileNotFoundError:
        print("We don't have component dict, need to update!")
        return dict()
    else:
        return com_dict


def load_symbols():
    load_path = os.path.join(os.getcwd(), "json", "symbols.json")
    try:
        with open(load_path, "r") as fp:
            sym_dict = json.load(fp)
    except FileNotFoundError:
        print("We don't have symbol dict, need to update!")
        return dict()
    else:
        return sym_dict


__all__ = [
    "dump_components",
    "dump_symbols",
    "load_components",
    "load_symbols"
]
