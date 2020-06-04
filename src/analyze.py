#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys

from argument import parser
from regex import find_stack
from clang.cindex import Config
from function import update_functions
from component import update_components
from output import flow_print, format_print
from workflow import format_dump, filter_word, add_knowledge


if __name__ == "__main__":
    args = parser.parse_args()
    # load libclang.so
    lib_path = r"C:\LLVM\bin" if sys.platform == "win32" else "/usr/lib"
    if not Config.loaded:
        Config.set_library_path(lib_path)
    # show AST workflow
    if args.workflow:
        step_1 = []
        step_2 = []
        step_3 = []
        for dump in args.workflow:
            step_1.append(format_dump(dump))
            step_2.append(filter_word(format_dump(dump)))
            step_3.append(add_knowledge(filter_word(format_dump(dump))))
        flow_print([step_1, step_2, step_3])
    # comparing based on CSI
    if args.dump:
        result = []
        for path in args.dump:
            result.append(find_stack(path))
        format_print(result)
    # update components/functions
    if args.update:
        # create directory if doesn't exist
        json_path = os.path.join(os.getcwd(), "json")
        if not os.path.exists(json_path):
            os.makedirs(json_path)
        # store components/functions
        update_components()
        update_functions()
