import os
import re
import sys
import glob


def find_component(path):
    # read CMakeLists.txt
    with open(path, "r") as fp:
        file_text = fp.read()
    # set patterns
    parent_pattern = re.compile(r"SET_COMPONENT\(\"(.+)?\"\)", re.M)
    child_pattern = re.compile(r"SET_COMPONENT\(\"(.+)?\"([^)]+)\)", re.M)
    # get matching lists
    parents = parent_pattern.findall(file_text)
    children = child_pattern.findall(file_text)
    return parents, children


def update_components(path, components):
    cmk_path = os.path.join(path, "CMakeLists.txt")
    if os.path.exists(cmk_path):
        # get 2 types of component
        parents, children = find_component(cmk_path)
        # save parent component
        for com in parents:
            components[path] = com
        # save child component
        for com in children:
            for node in com[1].split("\n"):
                if node.strip():
                    node_path = path
                    for node_dir in node.strip().split("/"):
                        node_path = os.path.join(node_path, node_dir)
                    # support wild character
                    for wild in glob.iglob(node_path):
                        components[wild] = com[0]
