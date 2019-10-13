#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import re
import glob
import difflib
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


def pre_process(paths, mode):
    dumps = []
    pattern = re.compile(r"[\n](\[CRASH_STACK\][\S\s]+)\[CRASH_REGISTERS\]", re.M)
    for path in paths:
        with open(path, "r") as fp:
            file_text = fp.read()
        stack = pattern.findall(file_text)
        if mode == "ast":
            trace = find_trace(stack[0])
            pass
        else:
            trace = find_trace(stack[0])
        dumps.append(trace)
    return dumps


def find_exception(text):
    ex = ""
    titles = []
    bodies = []
    title_pattern = re.compile(r"(exception.+)[ ]TID.+[\n]"
                               r"([\S\s]+?exception[ ]throw[ ]location[:])", re.M)
    for t in title_pattern.findall(text):
        title = t[0] + "\n" + \
                t[1].lstrip() + "\n"
        titles.append(title)
    body_pattern = re.compile(r"(\d+)[:][ ]0x.+[ ]in[ ](.+)[+]0x.+"
                              r"?([ ].+)[:]", re.M)
    body_list = body_pattern.findall(text)
    body = body_list[0][0] + ": " + body_list[0][1] + body_list[0][2] + "\n"
    for b in body_list:
        if b[0] == "0":
            bodies.append(body)
            body = ""
        body += b[0] + ": " + b[1] + b[2] + "\n"


def find_backtrace(text):
    bt = ""
    # extract source file
    source_dict = dict()
    source_pattern = re.compile(r"[-][\n][ ]+(\d+)[:][ ][\S\s]+"
                                r"?Source[:][ ](.+)[:]", re.M)
    sources = source_pattern.findall(text)
    for k, v in sources:
        source_dict[k] = v
    # extract method
    method_pattern = re.compile(r"[-][\n][ ]+(\d+)[:][ ](.+)", re.M)
    methods = method_pattern.findall(text)
    for m in methods:
        # processing method
        if " + 0x" in m[1]:
            method = m[1][:m[1].rindex(" + 0x")]
        else:
            method = m[1]
        # merge into a line
        if m[0] in source_dict:
            bt += str(m[0]) + ": " + method + " at " + source_dict[m[0]] + "\n"
        else:
            bt += str(m[0]) + ": " + method + "\n"
    return bt


def find_trace(text):
    # trace = find_backtrace(text)
    if "exception throw location" in text:
        body_pattern = re.compile(r"(\d+)[:][ ]0x.+[ ]in[ ](.+)[+]0x.+?([ ].+)[:]", re.M)
        titles = body_pattern.findall(text)
        print(titles)
    # return trace


def format_print(lists):
    # get diff
    stack_1 = args.dump[0][args.dump[0].rindex("/") + 1:]
    stack_2 = args.dump[1][args.dump[1].rindex("/") + 1:]
    diff = difflib.unified_diff(lists[0].split("\n"), lists[1].split("\n"),
                                fromfile=stack_1, tofile=stack_2, lineterm="")
    # set diff format
    for line in diff:
        if line.startswith("-"):
            if line.startswith("---"):
                print("\033[1m" + line + "\033[0m")
            else:
                line = "-   " + line[line.index("-") + 1:]
                print("\033[0;31m" + line + "\033[0m")
        elif line.startswith("+"):
            if line.startswith("+++"):
                print("\033[1m" + line + "\033[0m")
            else:
                line = "+   " + line[line.index("+") + 1:]
                print("\033[0;32m" + line + "\033[0m")
        elif line.startswith("@@"):
            print("\033[0;36m" + line + "\033[0m")
        else:
            print(line)
    # output similarity
    sim = difflib.SequenceMatcher(None, lists[0], lists[1]).ratio()
    difflib.Differ()
    print("+--------------------+")
    print("| Similarity: {:.2%} |".format(sim))
    print("+--------------------+")


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
    parser.add_argument("-d", "--dump", nargs=2, default=["./data/bt_dump_1.trc", "./data/bt_dump_2.trc"],
                        help="pass crash dump files")
    parser.add_argument("-m", "--mode", default="ast", choices=["ast", "csi"],
                        help="select the mode of analysis")
    parser.add_argument("-u", "--update", nargs="?", const=True,
                        help="update components or not")
    parser.add_argument("-s", "--source", nargs="?", default="/hana",
                        help="source code path")
    args = parser.parse_args()
    # update components or not
    if args.update:
        update_components(args.source)
        dump_components(components)
    else:
        components = load_components()

    # result = pre_process(args.dump, args.mode)
    # format_print(result)
    with open("/Users/hyang/Downloads/777_1.trc", "r") as fp:
        file_text = fp.read()
    find_trace(file_text)
