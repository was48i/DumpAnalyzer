import os
import re
import sys
import glob

from argument import parser
from function import best_matched
from persistence import load_functions

args = parser.parse_args()
functions = load_functions()


def find_components(path):
    # read CMakeLists.txt
    with open(path, "r") as fp:
        file_text = fp.read()
    # set patterns
    parent_pattern = re.compile(r'SET_COMPONENT\("(.+)"\)', re.M)
    child_pattern = re.compile(r'SET_COMPONENT\("(.+)"\n([^)]+)\)', re.M)
    # get matching lists
    parents = parent_pattern.findall(file_text)
    children = child_pattern.findall(file_text)
    return parents, children


def get_child(children, prefix):
    child = dict()
    for component in children:
        for node in [i.strip() for i in component[1].split("\n") if i.strip()]:
            path = prefix
            for layer in node.split("/"):
                path = os.path.join(path, layer)
            # support wild character
            for wild in glob.iglob(path):
                child[wild] = component[0]
    return child


def to_component(func_info):
    name, source = func_info
    raw = name
    # get component by source
    if source:
        component = best_matched(source)
    # get component by name
    else:
        if name in functions:
            component = functions[name]
        else:
            while True:
                if "::" in name:
                    name = name[:name.rindex("::")]
                    if name in functions:
                        component = functions[name]
                        break
                else:
                    if name in functions:
                        component = functions[name]
                        break
                    else:
                        component = raw
                        break
    return component


def update_components():
    queue = []
    component_dict = dict()
    queue.append(args.source)
    # BFS
    while len(queue) > 0:
        prefix = queue.pop(0)
        cmk_path = os.path.join(prefix, "CMakeLists.txt")
        if os.path.exists(cmk_path):
            # get 2 types of component
            parents, children = find_components(cmk_path)
            # save parent component
            for component in parents:
                key = prefix[len(args.source):]
                if sys.platform == "win32":
                    key = key.replace("\\", "/")
                if key:
                    key = key[1:]
                    print(key)
                    component_dict[key] = component
            # save child component
            child_dict = get_child(children, prefix)
            for child in child_dict:
                key = child[len(args.source):]
                if sys.platform == "win32":
                    key = key.replace("\\", "/")
                if key:
                    key = key[1:]
                    print(key)
                    component_dict[key] = child_dict[child]
        for node in os.listdir(prefix):
            child = os.path.join(prefix, node)
            if os.path.isdir(child):
                queue.append(child)
    return component_dict
