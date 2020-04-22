import os
import re

from argument import parser
from clang.cindex import Index
from multiprocessing import Pool
from persistence import load_components

args = parser.parse_args()
components = load_components()


def get_paths():
    stack = []
    paths = []
    stack.append(args.source)
    # DFS
    while len(stack) > 0:
        prefix = stack.pop(len(stack) - 1)
        for node in os.listdir(prefix):
            child = os.path.join(prefix, node)
            extension = os.path.splitext(child)[-1]
            if os.path.isdir(child):
                stack.append(child)
            elif extension in [".h", ".hpp"]:
                paths.append(child)
    return paths


def fully_qualified(child, path):
    if child.location.file is None:
        return ""
    elif child.location.file.name != path:
        return ""
    else:
        res = fully_qualified(child.semantic_parent, path)
        if res != "":
            return res + "::" + child.spelling
    return child.spelling


def best_matched(path):
    if path in components:
        component = components[path]
    else:
        while True:
            path = path[:path.rindex("/")]
            if path in components:
                component = components[path]
                break
    return component


def find_functions(path):
    functions = dict()
    index = Index.create()
    header = os.path.join(args.source, "rte", "rtebase", "include")
    args_list = [
        "-x", "c++",
        "-I" + args.source, "-I" + header
    ]
    tu = index.parse(path, args_list)
    decl_kinds = [
        "FUNCTION_DECL",
        "CXX_METHOD",
        "CONSTRUCTOR",
        "CONVERSION_FUNCTION"
    ]
    for child in tu.cursor.walk_preorder():
        if child.location.file is not None and \
                child.location.file.name == path and \
                (child.spelling or child.displayname):
            kind = str(child.kind)[str(child.kind).index('.') + 1:]
            if kind in decl_kinds:
                functions[fully_qualified(child, path)] = best_matched(path)
    return functions


def update_functions():
    function_dict = dict()
    # using multi-process
    paths = get_paths()
    pool = Pool(4)
    results = pool.map(find_functions, paths)
    for res in [i for i in results if i]:
        for k in res.keys():
            # special cases
            key = k
            # handle anonymous namespace
            while "::::" in key:
                key = k.replace("::::", "::")
            # remove special characters
            if re.search(r"[^0-9a-zA-Z:_]", key):
                point = re.search(r"[^0-9a-zA-Z:_]", key).span()[0]
                key = key[:point]
            print(key)
            function_dict[key] = res[k]
    pool.close()
    pool.join()
    return function_dict
