#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import re
import json


def data_storage(dump_list):
    prefix = "/data/hyang/dataset"
    # set stack pattern
    pattern = re.compile(r"\n\[CRASH_STACK\][\S\s]+\[CRASH_REGISTERS\]", re.M)
    for index, dump_set in enumerate(dump_list):
        # create subdirectory
        set_path = os.path.join(prefix, str(index))
        os.makedirs(set_path)
        # write to dump file
        for i, path in enumerate(dump_set):
            try:
                with open(path, "r") as fp:
                    file_text = fp.read()
            except IOError:
                continue
            stack = pattern.findall(file_text)
            if not stack:
                continue
            with open(os.path.join(set_path, "dump_" + str(i)), "w") as fp:
                fp.write(stack[0])


if __name__ == "__main__":
    dump_unions_path = os.path.join(os.getcwd(), "json", "dump_unions.json")
    try:
        with open(dump_unions_path, "r") as f:
            dump_unions = json.load(f)
    except FileNotFoundError:
        print("Can't find dump_unions, please check!")
    data_storage(dump_unions)
