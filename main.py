#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import re


def dfs_repo(path):
    if os.path.exists(os.path.join(path, "CMakeLists.txt")):
        with open(os.path.join(path, "CMakeLists.txt")) as file:
            com_pattern = re.compile(r"SET_COMPONENT\(\".*?\".*?\)", re.S)
            com_list = com_pattern.findall(file.read())
            if com_list:
                for com in com_list:
                    if com.split("\"")[2] == ")":
                        for node in os.listdir(path):
                            path_map[os.path.join(path, node)] = com.split("\"")[1]
                    else:
                        for node in com.split("\"")[2].split("\n"):
                            if re.search(r"\w", node):
                                path_map[os.path.join(path, node.strip())] = com.split("\"")[1]
    for node in os.listdir(path):
        child_node = os.path.join(path, node)
        if os.path.isdir(child_node):
            dfs_repo(child_node)


if __name__ == '__main__':
    path_map = dict()
    # repository = "/Users/hyang/workspace/hana"
    repository = "C:\\Users\\I516697\\workspace\\hana"
    dfs_repo(repository)
