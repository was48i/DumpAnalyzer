#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import re


def dfs_repo(path):
    if os.path.exists(os.path.join(path, "CMakeLists.txt")):
        with open(os.path.join(path, "CMakeLists.txt")) as file:
            file_text = file.read()

            com_pattern_1 = re.compile(r"SET_COMPONENT\(\"(.+)?\"\)", re.M)
            com_pattern_2 = re.compile(r"SET_COMPONENT\(\"(.+)?\"([^)]+)\)", re.M)

            com_list_1 = com_pattern_1.findall(file_text)
            com_list_2 = com_pattern_2.findall(file_text)

        for com in com_list_1:
            path_map[path] = com
        for com in com_list_2:
            for node in com[1].split("\n"):
                if re.search(r"\w", node):
                    path_map[os.path.join(path, node.strip())] = com[0]

    for node in os.listdir(path):
        child_node = os.path.join(path, node)
        if os.path.isdir(child_node):
            dfs_repo(child_node)


if __name__ == '__main__':
    path_map = dict()
    repo_path = "/Users/hyang/workspace/hana"
    dfs_repo(repo_path)
