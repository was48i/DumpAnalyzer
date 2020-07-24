#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import re
import json

from collections import Counter
from workflow import vaild_function


def break_point(funcs):
    name = ""
    for line in funcs:
        # remove offset if exists
        offset_pattern = re.compile(r"([ ]const)*[+]*0x\w+([ ]in[ ])*")
        func_info = re.sub(offset_pattern, "", line)
        if " at " in func_info:
            f_name = func_info[:func_info.index(" at ")]
        else:
            f_name = func_info
        # get vaild function name
        name = vaild_function(f_name)
        if name == "":
            continue
        else:
            break
    return name


def stop_word(text):
    prefix = []
    suffix = []
    # call stack pattern
    stack_pattern = re.compile(r"\n(\[CRASH_STACK\][\s\S]+)"
                               r"\[CRASH_REGISTERS\]", re.M)
    content = stack_pattern.findall(text)
    if not content:
        return [], []
    else:
        stack = content[0]
    # extract stop word if ex exists
    ex_location = "exception throw location:"
    if ex_location in stack:
        # get bt_functions
        bt_pattern = re.compile(r"-\n[ ]*\d+:[ ](.+)"
                                r"([^-]+Source:[ ].+:)*", re.M)
        bt_functions = bt_pattern.findall(stack)
        bt_result = []
        for func_tuple in bt_functions:
            f = list(func_tuple)
            if " + 0x" in f[0]:
                f[0] = f[0][:f[0].index(" + 0x")]
            # get vaild function name
            bt_name = vaild_function(f[0])
            if bt_name == "":
                continue
            bt_result.append(bt_name)
        # get ex_functions
        ex_pattern = re.compile(r"\d+:[ ](.+[+].+)[ ]at[ ].+:", re.M)
        ex_pattern_sp = re.compile(r"\d+:[ ](.+[+].+)[ ]", re.M)
        first_ex = stack.split(ex_location)[1]
        ex_functions = ex_pattern.findall(first_ex)
        if not ex_functions:
            ex_functions = ex_pattern_sp.findall(first_ex)
        prefix_point = break_point(ex_functions)
        suffix_point = break_point(ex_functions[::-1])
        # prefix_key/suffix_key
        try:
            prefix = bt_result[:bt_result.index(prefix_point)]
            suffix = bt_result[bt_result.index(suffix_point) + 1:]
        except ValueError:
            return [], []
    return prefix, suffix


def load_dumps(bugs):
    prefix_words = []
    suffix_words = []
    for bug in bugs:
        path = os.path.join(bugzilla_prefix, str(bug / 1000).zfill(3) + "xxx", str(bug))
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
                    prefix, suffix = stop_word(text)
                    for word in prefix:
                        prefix_words.append(word)
                    for word in suffix:
                        suffix_words.append(word)
        except OSError:
            continue
    # count stop words
    print(Counter(prefix_words))
    print(Counter(suffix_words))


if __name__ == "__main__":
    bugzilla_prefix = "/area51/bugzilla"
    api_bug_lists_path = os.path.join(os.getcwd(), "json", "api_bug_lists.json")
    try:
        with open(api_bug_lists_path, "r") as f:
            api_bug_lists = json.load(f)
    except FileNotFoundError:
        print("Can not find api_bug_lists, please check.")
    load_dumps(api_bug_lists)
