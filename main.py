#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import re

source_dir = "/Users/hyang/workspace/hana"


def dfs_dir(path):
    with open(path + "/CMakeLists.txt") as file:
        component_pattern = re.compile(r"SET_COMPONENT\(.*?\)", re.S)
        directory_pattern = re.compile(r"ADD_SUBDIRECTORY\(.*?\)", re.S)
        dir_list = []
        for directory in directory_pattern.findall(file.read()):
            dir_list.append(re.split(r"[(\")]+", directory)[1])
        print(dir_list)
        path_dir = dict()
        for component in component_pattern.findall(file.read()):
            if component.split("\"")[2] == ")":
                for node in dir_list:
                    path_dir[path + "/" + node] = component.split("\"")[1]
            else:
                for node in component.split("\"")[2].split("\n"):
                    if re.search(r"\w", node):
                        path_dir[path + "/" + node] = component.split("\"")[1]
        for node in dir_list:
            child_node = path + "/" + node
            dfs_dir(child_node)


if __name__ == '__main__':
    dfs_dir(source_dir)
