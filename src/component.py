import os
import re
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


def get_child(children, prefix):
    child = dict()
    for com in children:
        for node in [i for i in com[1].split("\n") if i.strip()]:
            node_path = prefix
            for node_dir in node.strip().split("/"):
                node_path = os.path.join(node_path, node_dir)
            # support wild character
            for wild in glob.iglob(node_path):
                child[wild] = com[0]
    return child


__all__ = [
    "find_component",
    "get_child"
]
