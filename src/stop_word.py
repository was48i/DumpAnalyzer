#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import re
import json

from collections import Counter


def get_words(text):
    res = []
    pre_pattern = re.compile(r"[\n](\[CRASH_STACK\][\S\s]+)"
                             r"\[CRASH_REGISTERS\]", re.M)
    stack = pre_pattern.findall(text)
    if not stack:
        return []
    if "exception throw location" in stack[0]:
        ex_pattern = re.compile(r"exception[ ]throw[ ]location:\n"
                                r"[ ]*[\d]:[ ]0x.+[ ]in[ ](.+)[+]", re.M)
        bt_pattern = re.compile(r"[-][\n][ ]+\d+[:][ ](.+)", re.M)
        ex_methods = ex_pattern.findall(stack[0])
        if not ex_methods:
            return []
        bt_methods = bt_pattern.findall(stack[0])
        if "(" in ex_methods[0]:
            key_method = ex_methods[0][:ex_methods[0].index("(")]
        else:
            key_method = ex_methods[0]
        for m in bt_methods:
            if " + 0x" in m:
                method = m[:m.rindex(" + 0x")]
            else:
                method = m
            if "(" in method:
                method = method[:method.index("(")]
            res.append(method)
        try:
            res = res[:res.index(key_method)]
        except ValueError:
            return []
    return res


def read_dumps(bugs):
    res = []
    for bug in bugs:
        path = os.path.join(prefix, str(bug/1000)+"xxx", str(bug))
        for node in os.listdir(path):
            child = os.path.join(path, node)
            extension = os.path.splitext(child)[-1]
            if extension == ".trc":
                print(child)
                try:
                    with open(child, "r") as fp:
                        text = fp.read()
                except IOError:
                    continue
                for word in get_words(text):
                    res.append(word)
    print(Counter(res))


if __name__ == "__main__":
    api_bug_lists_path = os.path.join(os.getcwd(), "json", "api_bug_lists.json")
    try:
        with open(api_bug_lists_path, "r") as f:
            api_bug_lists = json.load(f)
    except FileNotFoundError:
        print("Can't find api_bug_lists, please check!")
    prefix = "/area51/bugzilla"
    read_dumps(api_bug_lists)