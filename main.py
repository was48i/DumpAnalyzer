#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import re
import argparse
from clang.cindex import Index
from clang.cindex import Config


def find_component(path):
    with open(path) as file:
        file_text = file.read()
    com_pattern_1 = re.compile(r"SET_COMPONENT\(\"(.+)?\"\)", re.M)
    com_pattern_2 = re.compile(r"SET_COMPONENT\(\"(.+)?\"([^)]+)\)", re.M)
    com_list_1 = com_pattern_1.findall(file_text)
    com_list_2 = com_pattern_2.findall(file_text)
    return com_list_1, com_list_2


def long_match(path):
    component = "UNKNOWN"
    if path in path_map:
        component = path_map[path]
    else:
        for i in range(1, len(path)):
            if path[:-i] in path_map:
                component = path_map[path[:-i]]
    return component


def split_str(deep, text):
    global prefix
    global pre_deep
    if deep == 1:
        prefix = text
        symbol_list.append(prefix)
        pre_deep = deep
    else:
        if deep > pre_deep:
            symbol_list[-1] = symbol_list[-1] + "::" + text
            pre_deep = deep
        else:
            symbol_list.append(prefix + "::" + text)
            pre_deep = deep


def dump_node(node, path, deep):
    for child in node.get_children():
        if child.location.file is not None and child.location.file.name == path:
            text = child.spelling or child.displayname
            if text:
                kind = str(child.kind)[str(child.kind).index('.') + 1:]
                if kind in ["NAMESPACE", "FUNCTION_DECL", "CLASS_DECL", "CONSTRUCTOR"]:
                    split_str(deep, text)
                    dump_node(child, path, deep + 1)
    return symbol_list


def find_symbol(path):
    index = Index.create()
    header = os.path.join(args.source, "rte", "rtebase", "include")
    args_list = ["-x", "c++", "-I" + args.source, "-I" + header]
    tu = index.parse(path, args_list)
    return dump_node(tu.cursor, path, 1)


def dfs_repo(path):
    cur_path = os.path.join(path, "CMakeLists.txt")
    if os.path.exists(cur_path):
        parent_list, child_list = find_component(cur_path)
        for com in parent_list:
            path_map[path] = com
        for com in child_list:
            for node in com[1].split("\n"):
                for node_path in node.strip().split("/"):
                    if node_path:
                        tmp = os.path.join(path, node_path)
                        path_map[tmp] = com[0]
    for node in os.listdir(path):
        child_node = os.path.join(path, node)
        extension = os.path.splitext(child_node)
        if os.path.isdir(child_node):
            dfs_repo(child_node)
        elif extension[-1] in [".h", ".hpp"]:
            pass
            # print(child_node)
            # for symbol in find_symbol(child_node):
            #     symbol_map[symbol] = path_map[long_match(child_node)]


if __name__ == "__main__":
    libclangPath = r"C:\Program Files\LLVM\bin"
    if Config.loaded:
        pass
    else:
        Config.set_library_path(libclangPath)

    parser = argparse.ArgumentParser()
    parser.add_argument("-s", "--source", dest="source", help="source code path")
    args = parser.parse_args()

    repo_path = args.source
    path_map = dict()
    symbol_map = dict()
    prefix = ""
    pre_deep = 0
    symbol_list = []
    dfs_repo(repo_path)
    print(path_map)
    # file_path = r"C:\Users\I516697\workspace\hana\ptime\query\sqlscript\util\planviz_scope.h"
    # for symbol in find_symbol(file_path):
    #     symbol_map[symbol] = path_map[long_match(file_path)]
    # print(symbol_map)
    # print(path_map)
    # print(file_path)
    # print(long_match(file_path))
