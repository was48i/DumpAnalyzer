import os
import re
import glob

from argument import parser
from symbol import best_matched
from persistence import load_symbols

args = parser.parse_args()
symbols = load_symbols()


def find_components(path):
    # read CMakeLists.txt
    with open(path, "r") as fp:
        file_text = fp.read()
    # set patterns
    parent_pattern = re.compile(r'SET_COMPONENT\("(.+)"\)', re.M)
    child_pattern = re.compile(r'SET_COMPONENT\("(.+)"\n[^)]+\)', re.M)
    # get matching lists
    parents = parent_pattern.findall(file_text)
    children = child_pattern.findall(file_text)
    return parents, children


def get_child(children, prefix):
    child = dict()
    for com in children:
        for node in filter(lambda x: x.strip() is not None, com[1].split("\n")):
            path = prefix
            for layer in node.strip().split("/"):
                path = os.path.join(path, layer)
            # support wild character
            for wild in glob.iglob(path):
                child[wild] = com[0]
    return child


def to_component(method_info):
    method, source = method_info
    # get component by source
    if "/" in source:
        path = args.source
        for layer in source.split("/"):
            path = os.path.join(path, layer)
        component = best_matched(path)
    # get component by symbol
    else:
        try:
            component = symbols[method]
        except KeyError:
            component = method
    return component


def update_components(root):
    queue = []
    component_dict = dict()
    queue.append(root)
    # do BFS
    while len(queue) > 0:
        prefix = queue.pop(0)
        cmk_path = os.path.join(prefix, "CMakeLists.txt")
        if os.path.exists(cmk_path):
            # get 2 types of component
            parents, children = find_components(cmk_path)
            # save parent component
            for com in parents:
                component_dict[prefix] = com
            # save child component
            child_dict = get_child(children, prefix)
            for child in child_dict:
                component_dict[child] = child_dict[child]
        for node in os.listdir(prefix):
            child = os.path.join(prefix, node)
            if os.path.isdir(child):
                queue.append(child)
    return component_dict


__all__ = [
    "to_component",
    "update_components"
]
