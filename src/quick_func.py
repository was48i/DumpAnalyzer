#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import json

from multiprocessing import Pool
from persistence import load_functions

func_dict = load_functions()


def trie_tree(func):
    print(func)
    res = dict()
    key = func
    item_list = [i for i in func.split("::") if i]
    for i, item in enumerate(item_list):
        component_set = set()
        prefix = func[:func.index(item) + len(item)]
        for name in func_dict:
            if name.startswith(prefix):
                flag = 0
                length = len(prefix)
                if len(name) == length:
                    flag = 1
                else:
                    if name[length:length + 2] == "::":
                        flag = 1
                if flag == 1:
                    component_set.add(func_dict[name])
                    if len(component_set) > 1:
                        break
        if len(component_set) == 1:
            key = prefix
            break
    res[key] = func_dict[func]
    return res


def quick_func():
    quick_funcs = dict()
    # using multi-process
    pool = Pool(4)
    results = pool.map(trie_tree, func_dict.keys())
    pool.close()
    pool.join()
    for res in results:
        for k in res.keys():
            quick_funcs[k] = res[k]
    dump_path = os.path.join(os.getcwd(), "json", "quick_functions.json")
    with open(dump_path, "w") as fp:
        json.dump(quick_funcs, fp, indent=4, sort_keys=True)


if __name__ == "__main__":
    quick_func()
