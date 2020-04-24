import os
import json


def dump_components(component_dict):
    dump_path = os.path.join(os.getcwd(), "json", "components-master.json")
    with open(dump_path, "w") as fp:
        json.dump(component_dict, fp, indent=4, sort_keys=True)


def dump_functions(function_dict):
    dump_path = os.path.join(os.getcwd(), "json", "functions-master.json")
    with open(dump_path, "w") as fp:
        json.dump(function_dict, fp, indent=4, sort_keys=True)


def load_components():
    load_path = os.path.join(os.getcwd(), "json", "components-master.json")
    try:
        with open(load_path, "r") as fp:
            component_dict = json.load(fp)
    except FileNotFoundError:
        print("Can not find component dict, please update.")
        return dict()
    else:
        return component_dict


def load_functions():
    load_path = os.path.join(os.getcwd(), "json", "quick_functions-master.json")
    try:
        with open(load_path, "r") as fp:
            function_dict = json.load(fp)
    except FileNotFoundError:
        print("Can not find function dict, please update.")
        return dict()
    else:
        return function_dict
