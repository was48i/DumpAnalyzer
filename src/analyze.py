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


def pre_process(paths):
    sections = []
    pattern = re.compile(r"[\n](\[CRASH_STACK\][\S\s]+)\[CRASH_REGISTERS\]", re.M)
    for path in paths:
        with open(path, "r") as fp:
            file_text = fp.read()
        stack = pattern.findall(file_text)
        if "exception throw location" in stack[0]:
            section = find_exception(stack[0])
        else:
            section = find_backtrace(stack[0])
        sections.append(section)
    return sections


def find_exception(text):
    res = []
    title_pattern = re.compile(r"exception.*TID.*exception throw location:\n", re.M | re.S)
    body_pattern = re.compile(r"\d+:[ ]0x\w+[ ]in.*[+0x].*[:]", re.M)
    titles = title_pattern.findall(text)
    bodies = body_pattern.findall(text)
    for t, b in titles, bodies:
        res.append(t + b)
    return res


def find_backtrace(text):
    res = []
    # extract source file
    source_dict = dict()
    source_pattern = re.compile(r"[-][\n][ ]+(\d+)[:][ ][^\n]+[\S\s]+?Source[:][ ](.*)[:]", re.M)
    sources = source_pattern.findall(text)
    for k, v in sources:
        source_dict[k] = v
    # extract function
    function_pattern = re.compile(r"[-][\n][ ]+(\d+)[:][ ](.*)", re.M)
    functions = function_pattern.findall(text)
    for func in functions:
        if " + 0x" in func[1]:
            sym = func[1][:func[1].rindex("+") - 1]
        else:
            sym = func[1]
        # merge into a line
        res.append(sym + " at " + source_dict[func[0]])
    return res


def format_print(lists, mode):
    total = len(lists[0]) + len(lists[1])
    equal = len([i for i in lists[0] if i in lists[1]]) * 2

    print("Similarity: {:.2%}".format(equal / total))


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
                        default=["./data/bt_dump_1.trc", "./data/bt_dump_2.trc"], help="pass crash dump files")
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

    # format_print(pre_process(args.dump), args.mode)
    pre_process(args.dump)
