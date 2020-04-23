#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import json

from multiprocessing import Pool
from persistence import load_functions


def trie_tree(func):
    res = dict()
    print(func)
    key = func
    item_list = func.split("::")
    for i, item in enumerate(item_list):
        component_set = set()
        prefix = func[:func.index(item) + len(item)]
        for name in func_dict:
            if name.startswith(prefix) and name.split("::")[i] == item:
                component_set.add(func_dict[name])
                if len(component_set) > 1:
                    break
        if len(component_set) == 1:
            key = prefix
            break
    res[key] = func_dict[func]
    return res


def quick_func():
    quick_funs = dict()
    pool = Pool(4)
    results = pool.map(trie_tree, func_dict.keys())
    for res in results:
        for k in res.keys():
            quick_funs[k] = res[k]
    dump_path = os.path.join(os.getcwd(), "json", "quick_functions-master.json")
    with open(dump_path, "w") as fp:
        json.dump(quick_funs, fp, indent=4, sort_keys=True)


if __name__ == "__main__":
    func_dict = load_functions()
    quick_func()
