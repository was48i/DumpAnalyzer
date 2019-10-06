#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import re
import json
import glob
import argparse

from clang.cindex import Index
from clang.cindex import Config


def find_component(path):
    # read file
    with open(path, "r") as fp:
        file_text = fp.read()
    # set patterns
    pattern_1 = re.compile(r"SET_COMPONENT\(\"(.+)?\"\)", re.M)
    pattern_2 = re.compile(r"SET_COMPONENT\(\"(.+)?\"([^)]+)\)", re.M)
    # get matching lists
    list_1 = pattern_1.findall(file_text)
    list_2 = pattern_2.findall(file_text)
    return list_1, list_2


def fully_qualified(child, path):
    if child.location.file is None:
        return ""
    elif child.location.file.name != path:
        return ""
    else:
        res = fully_qualified(child.semantic_parent, path)
        if res != "":
            return res + "::" + child.spelling
    return child.spelling


def find_symbol(path):
    symbol = []
    index = Index.create()
    extra_header = os.path.join(src_path, "rte", "rtebase", "include")
    args_list = ["-x", "c++", "-I" + src_path, "-I" + extra_header]
    tu = index.parse(path, args_list)
    decl_kinds = ["FUNCTION_DECL", "CXX_METHOD", "CONSTRUCTOR", "CONVERSION_FUNCTION"]
    for child in tu.cursor.walk_preorder():
        if child.location.file is not None and child.location.file.name == path:
            text = child.spelling or child.displayname
            if text:
                kind = str(child.kind)[str(child.kind).index('.') + 1:]
                if kind in decl_kinds:
                    symbol.append(fully_qualified(child, path))
    return symbol


def best_matched(path):
    if path in components:
        com = components[path]
    else:
        while True:
            path = path[:path.rindex("/")]
            if path in components:
                com = components[path]
                break
    return com


def update_components(path):
    # check CMakeLists.txt existence
    cmk_path = os.path.join(path, "CMakeLists.txt")
    if os.path.exists(cmk_path):
        # get 2 types of component
        parent_list, child_list = find_component(cmk_path)
        # save parent component
        for com in parent_list:
            components[path] = com
        # save child component
        for com in child_list:
            for node in com[1].split("\n"):
                if node.strip():
                    # support Windows
                    node_path = path
                    for node_dir in node.strip().split("/"):
                        node_path = os.path.join(node_path, node_dir)
                    # support "*"
                    for wildcard in glob.iglob(node_path):
                        components[wildcard] = com[0]
    # DFS repository
    for node in os.listdir(path):
        child = os.path.join(path, node)
        if os.path.isdir(child):
            update_components(child)


def update_symbols(path):
    for node in os.listdir(path):
        child = os.path.join(path, node)
        extension = os.path.splitext(child)
        if os.path.isdir(child):
            update_symbols(child)
        elif extension[-1] in [".h", ".hpp"]:
            if find_symbol(child):
                for sym in set(find_symbol(child)):
                    symbols[sym] = best_matched(child)


def dump_components(com_dict):
    dump_path = os.path.join(os.getcwd(), "components.json")
    with open(dump_path, "w") as fp:
        json.dump(com_dict, fp, sort_keys=True, indent=4)


def dump_symbols(sym_dict):
    dump_path = os.path.join(os.getcwd(), "symbols.json")
    with open(dump_path, "a") as fp:
        json.dump(sym_dict, fp, sort_keys=True, indent=4)


def load_components():
    load_path = os.path.join(os.getcwd(), "components.json")
    try:
        with open(load_path, "r") as fp:
            com_dict = json.load(fp)
    except FileNotFoundError:
        print("We don't have component dict, need to update!")
        return dict()
    else:
        return com_dict


def load_symbols():
    load_path = os.path.join(os.getcwd(), "symbols.json")
    try:
        with open(load_path, "r") as fp:
            sym_dict = json.load(fp)
    except FileNotFoundError:
        print("We don't have symbol dict, need to update!")
        return dict()
    else:
        return sym_dict


if __name__ == "__main__":
    src_path = r"/hana"
    components = dict()
    symbols = dict()
    # load libclang.so
    lib_path = r"/usr/local/lib"
    if Config.loaded:
        pass
    else:
        Config.set_library_path(lib_path)
    # parse arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("-u", "--update", nargs="?", const=True, help="update components or not")
    args = parser.parse_args()
    # update components or not
    if args.update:
        update_components(src_path)
        dump_components(components)
    else:
        components = load_components()

    update_symbols(r"/hana/ptime/query/sqlscript/util")

