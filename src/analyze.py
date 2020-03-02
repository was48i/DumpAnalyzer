#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys

from argument import parser
from statistics import validate
from clang.cindex import Config
from symbol import update_symbols
from component import update_components
from persistence import dump_components, dump_symbols
from output import stats_print, flow_print, format_print
from workflow import format_dump, filter_words, find_key


if __name__ == "__main__":
    args = parser.parse_args()
    # load libclang.so
    lib_path = r"C:\LLVM\bin" if sys.platform == "win32" else "/usr/lib"
    if not Config.loaded:
        Config.set_library_path(lib_path)
    # data validation
    if args.stats:
        stats_print(validate())
    # show workflow
    elif args.workflow:
        format_res = format_dump(args.workflow[0])
        filter_res = filter_words(format_res)
        rule_res = find_key(filter_res)[0]
        hash_res = find_key(filter_res)[1]
        flow_print([format_res, filter_res, rule_res, hash_res])
    # text similarity
    else:
        result = []
        for path in args.dump:
            if not args.order:
                result.append(format_dump(path))
            else:
                result.append(find_key(filter_words(format_dump(path)))[0])
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
