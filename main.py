#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import re
import clang.cindex
from clang.cindex import Config
Config.set_compatibility_check(False)
Config.set_library_path(r"C:\Program Files\LLVM\bin")


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
    global temp_str
    global flag
    global prefix
    # kind = str(node.kind)[str(node.kind).index('.') + 1:]
    if deep == 0:
        pass
    elif deep == 1:
        if temp_str:
            symbol_list.append(temp_str)
        temp_str = ""
        temp_str = temp_str + text
        prefix = temp_str
    elif deep > 1 and deep > flag:
        temp_str = temp_str + "::" + text
        flag = deep
    else:
        temp_str = prefix + "::" + text
    print(temp_str)
    # temp_str += '{} {}'.format(indent, text)
    for i in [c for c in node.get_children() if c.location.file.name == file_path]:
        if str(i.kind)[str(i.kind).index('.') + 1:] in ["NAMESPACE", "FUNCTION_DECL", "CLASS_DECL", "CONSTRUCTOR"]:
            dump_node(i, deep + 1)


def find_symbol(path):
    index = clang.cindex.Index.create()
    tu = index.parse(path, ["-x", "c++", "-IC:\\Users\\I516697\\workspace\\hana",
                            "-IC:\\Users\\I516697\\workspace\\hana\\rte\\rtebase\\include"])
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


if __name__ == '__main__':
    path_map = dict()
    symbol_map = dict()
    symbol_list = []
    temp_str = ""
    flag = 0
    prefix = ""
    # repo_path = "/Users/hyang/workspace/hana"
    repo_path = r"C:\Users\I516697\workspace\hana"
    # dfs_repo(repo_path)
    file_path = r"C:\Users\I516697\workspace\hana\ptime\query\sqlscript\util\planviz_scope.h"
    find_symbol(file_path)
    print(symbol_list)
