#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import re
import sys

from regex import *
from output import *
from argument import *
from workflow import *
from statistics import *

from clang.cindex import Config
from symbol import update_symbols
from component import update_components
from persistence import dump_components, dump_symbols


def pre_process():
    dumps = []
    # set crash stack pattern
    pattern = re.compile(r"\n(\[CRASH_STACK\][\S\s]+)"
                         r"\[CRASH_REGISTERS\]", re.M)
    for path in args.dump:
        with open(path, "r", encoding="ISO-8859-1") as fp:
            file_text = fp.read()
        stack = pattern.findall(file_text)
        trace = find_stack(stack[0])
        dumps.append(trace)
    return dumps


if __name__ == "__main__":
    args = parser.parse_args()
    # load libclang.so
    lib_path = r"C:\LLVM\bin" if sys.platform == "win32" else "/usr/local/lib"
    if not Config.loaded:
        Config.set_library_path(lib_path)
    # data validation
    if args.stats:
        stats_print(validate())
    # show workflow
    elif args.workflow:
        format_res = format_dump()
        filter_res = filter_words(format_res)
        rule_res = find_key(filter_res)[0]
        hash_res = find_key(filter_res)[1]
        flow_print([format_res, filter_res, rule_res, hash_res])
    # text similarity
    else:
        result = pre_process()
        format_print(result)
    # create directory if necessary
    if args.update:
        json_path = os.path.join(os.getcwd(), "json")
        if not os.path.exists(json_path):
            os.makedirs(json_path)
        # store components/symbols
        com_dict = update_components(args.source)
        dump_components(com_dict)
        sym_dict = update_symbols(args.source)
        dump_symbols(sym_dict)
