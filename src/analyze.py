#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import re
import sys

from clang.cindex import Config
from multiprocessing import Pool

from symbol import *
from component import *
from crash_stack import *

from argument import parser
from output import format_print
from persistence import dump_components, dump_symbols


def update_components(root):
    queue = []
    components = dict()
    queue.append(root)
    while len(queue) > 0:
        prefix = queue.pop(0)
        cmk_path = os.path.join(prefix, "CMakeLists.txt")
        if os.path.exists(cmk_path):
            # get 2 types of component
            parents, children = find_component(cmk_path)
            # save parent component
            for com in parents:
                components[prefix] = com
            # save child component
            child_dict = get_child(children, prefix)
            for child in child_dict:
                components[child] = child_dict[child]
        for node in os.listdir(prefix):
            child = os.path.join(prefix, node)
            if os.path.isdir(child):
                queue.append(child)
    return components


def update_symbols(root):
    symbols = dict()
    # update symbols using multi-process
    paths = get_paths(root)
    pool = Pool(4)
    results = pool.map(find_symbol, paths)
    for res in [i for i in results if i]:
        for k in res:
            symbols[k] = res[k]
    pool.close()
    pool.join()
    return symbols


def pre_process(paths, mode):
    dumps = []
    # set crash stack pattern
    pattern = re.compile(r"[\n](\[CRASH_STACK\][\S\s]+)"
                         r"\[CRASH_REGISTERS\]", re.M)
    for path in paths:
        with open(path, "r") as fp:
            file_text = fp.read()
        stack = pattern.findall(file_text)
        if mode == "ast":
            trace = find_stack(stack[0])
            trace = to_component(trace)
        else:
            trace = find_stack(stack[0])
        dumps.append(trace)
    return dumps


if __name__ == "__main__":
    # load libclang.so
    lib_path = r"C:\LLVM\bin" if sys.platform == "win32" else "/usr/local/lib"
    if not Config.loaded:
        Config.set_library_path(lib_path)
    # parse arguments
    args = parser.parse_args()
    if args.update:
        # create json directory
        json_path = os.path.join(os.getcwd(), "json")
        if not os.path.exists(json_path):
            os.makedirs(json_path)
        # get and save json
        com_dict = update_components(args.source)
        dump_components(com_dict)
        sym_dict = update_symbols(args.source)
        dump_symbols(sym_dict)
    # output similarity result
    result = pre_process(args.dump, args.mode)
    format_print(args.dump, result)
