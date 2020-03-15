#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys

from argument import parser
from regex import find_stack
from statistics import validate
from clang.cindex import Config
from symbol import update_symbols
from component import update_components
from persistence import dump_components, dump_symbols
from output import stats_print, flow_print, format_print
from workflow import format_dump, filter_word, add_knowledge


if __name__ == "__main__":
    args = parser.parse_args()
    # load libclang.so
    lib_path = r"C:\LLVM\bin" if sys.platform == "win32" else "/usr/lib"
    if not Config.loaded:
        Config.set_library_path(lib_path)
    # data evaluation
    if args.stats:
        stats_print(validate())
    # show workflow
    elif args.workflow:
        step_1 = format_dump(args.workflow[0])
        step_2 = filter_word(step_1)
        step_3 = add_knowledge(step_2)
        flow_print([step_1, step_2, step_3])
    # compare dump
    else:
        result = []
        for path in args.dump:
            result.append(find_stack(path))
        format_print(result)
    # update components/symbols
    if args.update:
        # create directory if doesn't exist
        json_path = os.path.join(os.getcwd(), "json")
        if not os.path.exists(json_path):
            os.makedirs(json_path)
        # store components/symbols
        com_dict = update_components(args.source)
        dump_components(com_dict)
        sym_dict = update_symbols(args.source)
        dump_symbols(sym_dict)
