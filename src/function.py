import os
import re
import sys

from argument import parser
from clang.cindex import Index
from multiprocessing import Pool
from persistence import load_components, dump_functions

args = parser.parse_args()
components = load_components()


def get_files(dir_path):
    stack = []
    paths = []
    stack.append(dir_path)
    # DFS
    while len(stack) > 0:
        prefix = stack.pop(len(stack) - 1)
        for node in os.listdir(prefix):
            cur_path = os.path.join(prefix, node)
            extension = os.path.splitext(cur_path)[-1]
            if not os.path.isdir(cur_path):
                if extension in [".h", ".hpp"]:
                    paths.append(cur_path)
            else:
                stack.append(cur_path)
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
    # remove prefix
    path = path[len(args.source) + 1:]
    # support Win
    if sys.platform == "win32":
        path = path.replace("\\", "/")
    # match component
    if path in components:
        component = components[path]
    else:
        while True:
            if "/" in path:
                path = path[:path.rindex("/")]
                if path in components:
                    component = components[path]
                    break
            else:
                if path in components:
                    component = components[path]
                    break
                else:
                    component = "UNKNOWN"
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
        "DESTRUCTOR",
        "CONVERSION_FUNCTION"
    ]
    for child in tu.cursor.walk_preorder():
        if child.location.file is not None and child.location.file.name == path and \
           (child.spelling or child.displayname):
            kind = str(child.kind)[str(child.kind).index('.') + 1:]
            if kind in decl_kinds:
                key = fully_qualified(child, path)
                functions[key] = best_matched(path)
    return functions


def multi_process(paths):
    function_dict = dict()
    # using multi-process
    pool = Pool(4)
    results = pool.map(find_functions, paths)
    pool.close()
    pool.join()
    for res in [i for i in results if i]:
        for k in res.keys():
            key = k
            # handle anonymous namespace
            while "::::" in key:
                key = key.replace("::::", "::")
            # remove special characters
            if re.search(r"[^0-9a-zA-Z:_~]", key):
                point = re.search(r"[^0-9a-zA-Z:_~]", key).span()[0]
                key = key[:point]
            print(key)
            function_dict[key] = res[k]
    return function_dict


def update_functions():
    result = dict()
    # apply map reduce
    for loc in os.listdir(args.source):
        cur_path = os.path.join(args.source, loc)
        if os.path.isdir(cur_path):
            paths = get_files(cur_path)
            # update functions by directory
            if paths:
                result.update(multi_process(paths))
    dump_functions(result)
