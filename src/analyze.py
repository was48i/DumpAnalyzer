#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import re
import sys
import argparse
from clang.cindex import Config

from output import format_print
from component import update_components
from crash_stack import find_stack, to_component
from persistence import dump_components, dump_symbols


def dfs_repo(root):
    stack = []
    components = dict()
    # symbols = dict()
    symbols = {"ltt::tThrow": "hehe", "ltt::allocator::allocateAligned": "hehe"}
    stack.append(root)
    while len(stack) > 0:
        prefix = stack.pop(len(stack) - 1)
        if os.path.isdir(prefix):
            update_components(prefix, components)
            # update_symbols(prefix, symbols, root=args.source)
            for node in os.listdir(prefix):
                child = os.path.join(prefix, node)
                if os.path.isdir(child):
                    stack.append(child)
    return components, symbols


def pre_process(paths, mode):
    dumps = []
    # set crash stack pattern
    pattern = re.compile(r"[\n](\[CRASH_STACK\][\S\s]+)\[CRASH_REGISTERS\]", re.M)
    for path in paths:
        with open(path, "r") as fp:
            file_text = fp.read()
        stack = pattern.findall(file_text)
        if mode == "ast":
            trace = find_stack(stack[0])
            trace = to_component(trace, root=args.source)
        else:
            trace = find_stack(stack[0])
        dumps.append(trace)
    return dumps


if __name__ == "__main__":
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
        com_dict, sym_dict = dfs_repo(args.source)
        dump_components(com_dict)
        # dump_symbols(sym_dict)
    # output similarity result
    result = pre_process(args.dump, args.mode)
    format_print(args.dump, result)
