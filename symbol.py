import os

from clang.cindex import Index
from component import components

src_path = r"/hana"
symbols = dict()


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


def find_symbol(path):
    symbol = []
    index = Index.create()
    extra_header = os.path.join(src_path,
                                "rte", "rtebase", "include")
    args_list = ["-x", "c++",
                 "-I" + src_path, "-I" + extra_header]
    tu = index.parse(path, args_list)
    decl_kinds = ["FUNCTION_DECL",
                  "CXX_METHOD",
                  "CONSTRUCTOR",
                  "CONVERSION_FUNCTION"]
    for child in tu.cursor.walk_preorder():
        if child.location.file is not None and child.location.file.name == path:
            text = child.spelling or child.displayname
            if text:
                kind = str(child.kind)[str(child.kind).index('.') + 1:]
                if kind in decl_kinds:
                    symbol.append(fully_qualified(child, path))
    return symbol


def best_matched(path):
    if path in components:
        com = components[path]
    else:
        while True:
            path = path[:path.rindex("/")]
            if path in components:
                com = components[path]
                break
    return com


def update_symbols(path):
    for node in os.listdir(path):
        child = os.path.join(path, node)
        extension = os.path.splitext(child)
        if os.path.isdir(child):
            update_symbols(child)
        elif extension[-1] in [".h", ".hpp"]:
            if find_symbol(child):
                for sym in set(find_symbol(child)):
                    symbols[sym] = best_matched(child)
