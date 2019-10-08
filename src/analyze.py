#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import re
import glob
import argparse
from clang.cindex import Config

from symbol import find_symbol
from component import find_component
from persistence import dump_components, load_components


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


def update_symbols(path):
    for node in os.listdir(path):
        child = os.path.join(path, node)
        extension = os.path.splitext(child)
        if os.path.isdir(child):
            update_symbols(child)
        elif extension[-1] in [".h", ".hpp"]:
            if find_symbol(child, args.source):
                for sym in set(find_symbol(child, args.source)):
                    symbols[sym] = best_matched(child)


def ast_compare():
    pass


def csi_compare(paths):
    dump_list = []
    pattern = re.compile(r"[ ]+[-]+\n[ ]+\d+[:][ ]([^(\n ]+)", re.M)
    for path in paths:
        with open(path, "r") as fp:
            file_text = fp.read()
        sym_list = pattern.findall(file_text)
        dump_list.append(sym_list)

    total = len(dump_list[0]) + len(dump_list[1])
    equal = len([i for i in dump_list[0] if i in dump_list[1]]) * 2

    print("Similarity: {:.2%}".format(equal / total))


def format_print():
    pass


if __name__ == "__main__":
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
    parser.add_argument("-d", "--dump", nargs=2,
                        default=["./data/bt_1.dmp", "./data/bt_2.dmp"], help="pass crash dump files")
    parser.add_argument("-m", "--mode", default="ast",
                        choices=["ast", "csi"], help="select the mode of analysis")
    parser.add_argument("-u", "--update", nargs="?", const=True,
                        help="update components or not")
    parser.add_argument("-s", "--source", nargs="?",
                        help="source code path")
    args = parser.parse_args()
    # update components or not
    if args.update:
        update_components(args.source)
        dump_components(components)
    else:
        components = load_components()
    # analyze mode
    if args.mode == "ast":
        ast_compare()
    else:
        csi_compare(args.dump)
