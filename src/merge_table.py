#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import json


def load_orange():
    load_path = os.path.join(os.getcwd(), "json", "quick_functions-orange.json")
    try:
        with open(load_path, "r") as fp:
            component_dict = json.load(fp)
    except FileNotFoundError:
        print("Can not find component dict, please update.")
        return dict()
    else:
        return component_dict


def load_master():
    load_path = os.path.join(os.getcwd(), "json", "quick_functions-master.json")
    try:
        with open(load_path, "r") as fp:
            component_dict = json.load(fp)
    except FileNotFoundError:
        print("Can not find component dict, please update.")
        return dict()
    else:
        return component_dict


def merge_tables(function_dict):
    dump_path = os.path.join(os.getcwd(), "json", "quick_functions_merge.json")
    with open(dump_path, "w") as fp:
        json.dump(function_dict, fp, indent=4, sort_keys=True)


if __name__ == "__main__":
    orange_dict = load_orange()
    master_dict = load_master()
    res = orange_dict
    for m_key in master_dict:
        if m_key not in orange_dict:
            res[m_key] = master_dict[m_key]
        else:
            if master_dict[m_key] != orange_dict[m_key]:
                res[m_key] = master_dict[m_key]
            else:
                continue
    merge_tables(res)
