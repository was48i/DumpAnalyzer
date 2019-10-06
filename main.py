#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import re
import glob
import argparse

from clang.cindex import Index
from clang.cindex import Config


def find_comp(path):
    # read file
    with open(path, "r") as f:
        file_text = f.read()
    # set patterns
    pattern_1 = re.compile(r"SET_COMPONENT\(\"(.+)?\"\)", re.M)
    pattern_2 = re.compile(r"SET_COMPONENT\(\"(.+)?\"([^)]+)\)", re.M)
    # get matching lists
    list_1 = pattern_1.findall(file_text)
    list_2 = pattern_2.findall(file_text)
    return list_1, list_2


def fully_qualified(child, path):
    if child.location.file is None:
        return ""
    elif child.location.file.name != path:
        return ""
    else:
        res = fully_qualified(child.semantic_parent, path)
        if res != "":
            return res + "::" + child.spelling
    return child.spelling


def find_func(path):
    res = []
    index = Index.create()
    extra_header = os.path.join(src_path, "rte", "rtebase", "include")
    args_list = ["-x", "c++", "-I" + src_path, "-I" + extra_header]
    tu = index.parse(path, args_list)
    for child in tu.cursor.walk_preorder():
        if child.location.file is not None and child.location.file.name == path:
            text = child.spelling or child.displayname
            if text:
                kind = str(child.kind)[str(child.kind).index('.') + 1:]
                if kind in ["FUNCTION_DECL", "CONSTRUCTOR"]:
                    res.append(fully_qualified(child, path))
    return res


def best_matched(path):
    if path in path_map:
        comp = path_map[path]
    else:
        while True:
            path = path[:path.rindex("/")]
            if path in path_map:
                comp = path_map[path]
                break
    return comp


def dfs_repo(path):
    # check CMakeLists.txt existence
    cur_path = os.path.join(path, "CMakeLists.txt")
    if os.path.exists(cur_path):
        # get 2 types of component
        parent_list, child_list = find_comp(cur_path)
        # save parent component
        for comp in parent_list:
            path_map[path] = comp
        # save child component
        for comp in child_list:
            for node in comp[1].split("\n"):
                if node.strip():
                    # support Windows
                    node_path = path
                    for node_dir in node.strip().split("/"):
                        node_path = os.path.join(node_path, node_dir)
                    # support "*"
                    for wildcard in glob.iglob(node_path):
                        path_map[wildcard] = comp[0]
    # DFS repository
    for node in os.listdir(path):
        child = os.path.join(path, node)
        extension = os.path.splitext(child)
        if os.path.isdir(child):
            dfs_repo(child)
        elif extension[-1] in [".h", ".hpp"]:
            if find_func(child):
                print(find_func(child))
                for func in set(find_func(child)):
                    func_map[func] = best_matched(child)


if __name__ == "__main__":
    src_path = r"/hana"
    path_map = dict()
    func_map = dict()
    # load libclang.so
    lib_path = r"/usr/local/lib"
    if Config.loaded:
        pass
    else:
        Config.set_library_path(lib_path)
    # parse arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("-d1", "--dump1", dest="dump1", help="crash dump file 1")
    parser.add_argument("-d2", "--dump2", dest="dump2", help="crash dump file 2")
    args = parser.parse_args()

    dfs_repo(src_path)

