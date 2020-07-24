#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys

from argument import parser
from regex import find_stack
from clang.cindex import Config
from function import update_functions
from component import update_components
from output import hana_print, formula_print, format_print
from workflow import pre_process, add_knowledge, calculate_sim


if __name__ == "__main__":
    args = parser.parse_args()
    # load libclang.so
    lib_path = r"C:\LLVM\bin" if sys.platform == "win32" else "/usr/lib"
    if not Config.loaded:
        Config.set_library_path(lib_path)
    # show AST workflow
    if args.workflow:
        # hana_print
        step_1 = []
        for dump in args.workflow:
            step_1.append(add_knowledge(pre_process(dump)))
        hana_print(step_1)
        # formula print
        m_pos = 0.4
        n_sim = 1.9
        threshold = 0.3104
        parameters = [m_pos, n_sim, threshold]
        step_2 = calculate_sim(args.workflow, m_pos, n_sim)
        formula_print(step_2, parameters)
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
