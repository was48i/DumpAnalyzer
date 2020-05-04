#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import re
import json

from workflow import get_name
from collections import Counter


def get_words(text):
    res = []
    prefix = []
    suffix = []
    # set stack pattern
    stack_pattern = re.compile(r"\n(\[CRASH_STACK\][\S\s]+)"
                               r"\[CRASH_REGISTERS\]", re.M)
    stack = stack_pattern.findall(text)
    if not stack:
        return [], []
    ex_flag = "exception throw location"
    if ex_flag in stack[0]:
        # set bt/ex patterns
        bt_pattern = re.compile(r"-\n[ ]*\d+:[ ](.+)[^-]+Symbol:[ ].+"
                                r"([^-]+Source:[ ].+:)*", re.M)
        ex_pattern = re.compile(r"\d+:[ ](.+)[ ]at[ ].+:", re.M)
        # get bt_functions
        bt_functions = bt_pattern.findall(stack[0])
        for func_tuple in bt_functions:
            f = list(func_tuple)
            if " + 0x" in f[0]:
                f[0] = f[0][:f[0].index(" + 0x")]
            bt_name = get_name(f[0])
            res.append(bt_name)
        # get prefix_key and suffix_key
        ex_functions = ex_pattern.findall(stack[0].split(ex_flag)[1])
        if not ex_functions:
            return [], []
        offset_pattern = re.compile(r"([ ]const)*[+]*0x\w+([ ]in[ ])*")
        prefix_func = re.sub(offset_pattern, "", ex_functions[0])
        suffix_func = re.sub(offset_pattern, "", ex_functions[-1])
        prefix_key = get_name(prefix_func)
        suffix_key = get_name(suffix_func)
        try:
            prefix = res[:res.index(prefix_key)]
            suffix = res[res.index(suffix_key) + 1:]
        except ValueError:
            return [], []
    return prefix, suffix


def read_dumps(bugs):
    prefix_words = []
    suffix_words = []
    for bug in bugs:
        path = os.path.join(prefix, str(bug / 1000).zfill(3) + "xxx", str(bug))
        # handle bug_id directory doesn't exist
        try:
            for node in os.listdir(path):
                child = os.path.join(path, node)
                extension = os.path.splitext(child)[-1]
                # only read .trc file
                if extension == ".trc":
                    print(child)
                    try:
                        with open(child, "r") as fp:
                            text = fp.read()
                    except IOError:
                        continue
                    for word in get_words(text)[0]:
                        prefix_words.append(word)
                    for word in get_words(text)[1]:
                        suffix_words.append(word)
        except OSError:
            continue
    # count stop words
    print(Counter(prefix_words))
    print(Counter(suffix_words))


if __name__ == "__main__":
    api_bug_lists_path = os.path.join(os.getcwd(), "json", "api_bug_lists.json")
    try:
        with open(api_bug_lists_path, "r") as f:
            api_bug_lists = json.load(f)
    except FileNotFoundError:
        print("Can not find api_bug_lists, please check.")
    prefix = "/area51/bugzilla"
    read_dumps(api_bug_lists)
