#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import re
import sys
import glob
import argparse
from clang.cindex import Config

from symbol import find_symbol
from format import format_print
from regex import find_component, find_stacktrace
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
                    node_path = path
                    separator = "\\" if sys.platform == "win32" else "/"
                    for node_dir in node.strip().split(separator):
                        node_path = os.path.join(node_path, node_dir)
                    # support wild character
                    for wild in glob.iglob(node_path):
                        components[wild] = com[0]
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
            separator = "\\" if sys.platform == "win32" else "/"
            path = path[:path.rindex(separator)]
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


def to_component(trace):
    cnt = 0
    component = ""
    res = "[BACKTRACE]\n"
    # string to list
    trace_list = trace.split("\n")
    # set patterns
    trace_pattern = re.compile(r"\d+[:][ ](.+)")
    path_pattern = re.compile(r"[ ]at[ ](.+)")
    func_pattern = re.compile(r"\d+[:][\w ]*[ ](.+[^ ])\(")
    for trace in trace_list:
        # extract backtrace
        if trace_pattern.match(trace):
            # match component
            if " at " in trace and "/" in trace:
                path = args.source
                for path_dir in path_pattern.search(trace).group(1).split("/"):
                    path = os.path.join(path, path_dir)
                com = best_matched(path)
            elif "(" in trace:
                key = func_pattern.match(trace).group(1)
                if "<" in key:
                    key = key[:key.index("<")]
                com = symbols[key]
            else:
                com = trace_pattern.match(trace).group(1)
            # update component and cnt
            if com != component:
                res += str(cnt) + ": " + com + "\n"
                component = com
                cnt += 1
        # extract exception
        elif trace.startswith("exception throw location"):
            cnt = 0
            component = ""
            res += "\n[EXCEPTION]\n"
    return res


def pre_process(paths, mode):
    dumps = []
    # set crash stack pattern
    pattern = re.compile(r"[\n](\[CRASH_STACK\][\S\s]+)\[CRASH_REGISTERS\]", re.M)
    for path in paths:
        with open(path, "r") as fp:
            file_text = fp.read()
        stack = pattern.findall(file_text)
        if mode == "ast":
            trace = find_stacktrace(stack[0])
            trace = to_component(trace)
        else:
            trace = find_stacktrace(stack[0])
        dumps.append(trace)
    return dumps


if __name__ == "__main__":
    components = dict()
    # symbols = dict()
    symbols = {"ltt::tThrow": "hehe", "ltt::allocator::allocateAligned": "hehe"}
    # load libclang.so
    lib_path = r"C:\LLVM\bin" if sys.platform == "win32" else "/usr/local/lib"
    if Config.loaded:
        pass
    else:
        Config.set_library_path(lib_path)
    # parse arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("-m", "--mode", default="ast", choices=["ast", "csi"],
                        help="select the mode of analysis")
    parser.add_argument("-u", "--update", nargs="?", const=True,
                        help="update components or not")
    # support Windows
    if sys.platform == "win32":
        parser.add_argument("-d", "--dump", nargs=2, default=[r"data\bt_dump_1.trc", r"data\bt_dump_2.trc"],
                            help="pass crash dump files")
        parser.add_argument("-s", "--source", nargs="?", default=r"C:\hana",
                            help="source code path")
    else:
        parser.add_argument("-d", "--dump", nargs=2, default=["data/bt_dump_1.trc", "data/bt_dump_2.trc"],
                            help="pass crash dump files")
        parser.add_argument("-s", "--source", nargs="?", default="/hana",
                            help="source code path")
    args = parser.parse_args()
    # update components or not
    if args.update:
        update_components(args.source)
        dump_components(components)
    else:
        components = load_components()
    # output similarity result
    result = pre_process(args.dump, args.mode)
    format_print(args.dump, result)
