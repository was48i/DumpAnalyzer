import os
import sys

from argument import parser
from clang.cindex import Index
from persistence import load_components


args = parser.parse_args()
components = load_components()


def get_paths(root):
    stack = []
    paths = []
    stack.append(root)
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
        com = components[path]
    else:
        while True:
            slash = "\\" if sys.platform == "win32" else "/"
            path = path[:path.rindex(slash)]
            if path in components:
                com = components[path]
                break
    return com


def find_symbol(path):
    symbol = dict()
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
                symbol[fully_qualified(child, path)] = best_matched(path)
    return symbol


__all__ = [
    "get_paths",
    "best_matched",
    "find_symbol"
]
