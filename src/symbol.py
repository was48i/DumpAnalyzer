import os
from clang.cindex import Index


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


def find_symbol(path, repo):
    symbol = []
    index = Index.create()
    header = os.path.join(repo, "rte", "rtebase", "include")
    args_list = ["-x", "c++",
                 "-I" + repo, "-I" + header]
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
