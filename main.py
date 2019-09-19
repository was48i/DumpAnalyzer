#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import re


def find_component(file_path):
    with open(file_path) as file:
        file_text = file.read()
    com_pattern_1 = re.compile(r"SET_COMPONENT\(\"(.+)?\"\)", re.M)
    com_pattern_2 = re.compile(r"SET_COMPONENT\(\"(.+)?\"([^)]+)\)", re.M)
    com_list_1 = com_pattern_1.findall(file_text)
    com_list_2 = com_pattern_2.findall(file_text)
    return com_list_1, com_list_2


def find_symbol(file_path):
    pass


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
            header_1 = extension[0] + '.h'
            header_2 = extension[0] + '.hpp'
            for header in [header_1, header_2]:
                if os.path.exists(header):
                    find_symbol(header)


if __name__ == '__main__':
    path_map = dict()
    symbol_map = dict()
    # repo_path = "/Users/hyang/workspace/hana"
    repo_path = "C:\\Users\\I516697\\workspace\\hana"
    dfs_repo(repo_path)
