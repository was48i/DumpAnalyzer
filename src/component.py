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
    child_dict = dict()
    for com in children:
        for node in [i for i in com[1].split("\n") if i.strip()]:
            node_path = prefix
            for node_dir in node.strip().split("/"):
                node_path = os.path.join(node_path, node_dir)
            # support wild character
            for wild in glob.iglob(node_path):
                child_dict[wild] = com[0]
    return child_dict


def update_components(path, components):
    cmk_path = os.path.join(path, "CMakeLists.txt")
    if os.path.exists(cmk_path):
        # get 2 types of component
        parents, children = find_component(cmk_path)
        # save parent component
        for com in parents:
            components[path] = com
        # save child component
        child_dict = get_child(children, path)
        for child in child_dict:
            components[child] = child_dict[child]


__all__ = [
    "find_component",
    "update_components"
]
