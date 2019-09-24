#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import re
import clang.cindex
import argparse
from clang.cindex import Config


def find_component(path):
    with open(path) as file:
        file_text = file.read()
    com_pattern_1 = re.compile(r"SET_COMPONENT\(\"(.+)?\"\)", re.M)
    com_pattern_2 = re.compile(r"SET_COMPONENT\(\"(.+)?\"([^)]+)\)", re.M)
    com_list_1 = com_pattern_1.findall(file_text)
    com_list_2 = com_pattern_2.findall(file_text)
    return com_list_1, com_list_2


def long_match(target):
    match = ""
    for k in [k for k, v in path_map.items()]:
        if target.startwith(k):
            if match:
                if len(k) > len(match):
                    match = k
            else:
                match = k
    return match


def dump_node(node, deep):
    text = node.spelling or node.displayname
    kind = str(node.kind)[str(node.kind).index('.') + 1:]
    print('{} {}'.format(kind, text))
    for i in [c for c in node.get_children() if c.location.file.name == file_path]:
        if str(i.kind)[str(i.kind).index('.') + 1:] in ["NAMESPACE", "FUNCTION_DECL", "CLASS_DECL", "CONSTRUCTOR"]:
            dump_node(i, deep + 1)


def find_symbol(path):
    index = clang.cindex.Index.create()
    headers = ["-x", "c++", "-I" + args.source, "-I" + args.source + "/rtebase/include"]
    tu = index.parse(path, headers)
    dump_node(tu.cursor, 0)


def dfs_repo(path):
    cur_path = os.path.join(path, "CMakeLists.txt")
    if os.path.exists(cur_path):
        parent_list, child_list = find_component(cur_path)
        for com in parent_list:
            path_map[path] = com
        for com in child_list:
            for node in com[1].split("\n"):
                if re.search(r"\w", node):
                    path_map[os.path.join(path, node.strip(")").strip())] = com[0]
    for node in os.listdir(path):
        child_node = os.path.join(path, node)
        extension = os.path.splitext(child_node)
        if os.path.isdir(child_node):
            dfs_repo(child_node)
        elif extension[-1] in [".cc", ".cpp"]:
            find_symbol(child_node)


if __name__ == "__main__":
    Config.set_compatibility_check(False)
    Config.set_library_path(r"/usr/local/lib")
    parser = argparse.ArgumentParser()
    parser.add_argument("-s", dest="source", help="source code path")
    args = parser.parse_args()
    repo_path = args.source
    path_map = dict()
    # dfs_repo(repo_path)
    file_path = r"/Users/hyang/workspace/hana/ptime/query/sqlscript/util/planviz_scope.h"
    find_symbol(file_path)
