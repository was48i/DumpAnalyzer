import configparser
import glob
import os
import pymongo
import re
import subprocess


def find_component(path):
    """
    Obtain parent/child components from a CMakeLists.txt path.

    Args:
        path: A CMakeLists.txt path.

    Returns:
        Parent and its children.
    """
    with open(path, "r") as fp:
        content = fp.read()
    parent_pattern = re.compile(r'SET_COMPONENT\("(.+)"\)', re.M)
    child_pattern = re.compile(r'SET_COMPONENT\("(.+)"\n([^)]+)\)', re.M)
    parent = parent_pattern.findall(content)
    children = child_pattern.findall(content)
    return parent + children


def convert_path(components, prefix):
    """
    Obtain the file path for corresponding component.
    Args:
        components: Parent component or child component list.
        prefix: The current prefix of CMakeLists.txt.
    Returns:
        Component-File mapping.
    """
    result = dict()
    for cpnt in components:
        # convert parent component
        if isinstance(cpnt, str):
            result[prefix] = cpnt
            continue
        # convert child component
        if isinstance(cpnt, tuple):
            for item in [i.strip() for i in cpnt[1].split("\n") if i.strip()]:
                path = prefix
                for layer in item.split("/"):
                    path = os.path.join(path, layer)
                # wild character
                for wild in glob.iglob(path):
                    result[wild] = cpnt[0]
            continue
    return result


def header_path(dir_path):
    """
    Obtain all header file's paths in the current directory.

    Args:
        dir_path: The dictionary to be processed.

    Returns:
        All header file's paths in the directory.
    """
    headers = []
    stack = [dir_path]
    # DFS
    while len(stack) > 0:
        prefix = stack.pop(len(stack) - 1)
        for node in os.listdir(prefix):
            cur_path = os.path.join(prefix, node)
            extension = os.path.splitext(cur_path)[-1]
            if not os.path.isdir(cur_path):
                if extension in [".h", ".hpp"]:
                    headers.append(cur_path)
            else:
                stack.append(cur_path)
    return headers


def fully_qualified(node, path):
    """
    Obtain fully qualified name recursively.

    Args:
        node: A node in abstract syntax tree.
        path: The path of current header file.

    Returns:
        The fully qualified name that belongs to the node.
    """
    if node.location.file is None:
        return ""
    elif node.location.file.name != path:
        return ""
    else:
        res = fully_qualified(node.semantic_parent, path)
        if res != "":
            return res + "::" + node.spelling
    return node.spelling


def valid_function(func):
    # demangle
    arguments = ["c++filt", "-p"]
    if func.startswith("_Z"):
        arguments.extend([func])
        pipe = subprocess.Popen(arguments, stdout=subprocess.PIPE, stdin=subprocess.PIPE)
        stdout, stderr = pipe.communicate()
        func = stdout.decode("utf-8")[:-1]
    # handle anonymous namespace
    if "::(anonymous namespace)" in func:
        func = func.replace("::(anonymous namespace)", "")
    if "(anonymous namespace)::" in func:
        func = func.replace("(anonymous namespace)::", "")
    # remove parameter variable
    if "(" in func:
        func = func[:func.index("(")]
    # remove template
    if "<" in func:
        func = func[:func.index("<")]
    # remove return type
    if re.match(r"^[a-z]+[ ]", func):
        func = func[func.index(" ")+1:]
    if not re.match(r"^[_a-zA-Z]", func):
        return ""
    else:
        return func


def best_matched(path):
    """
    Obtain the best matched component from components collection.

    Args:
        path: The path of current header file.

    Returns:
        The best matched component.
    """
    config = configparser.ConfigParser()
    config_path = os.path.join(os.getcwd(), "settings.ini")
    config.read(config_path)
    # MongoDB
    host = config.get("mongodb", "host")
    port = config.get("mongodb", "port")
    database = config.get("mongodb", "db")
    collection = config.get("mongodb", "coll_func")

    matched = "UNKNOWN"
    client = pymongo.MongoClient(host=host, port=int(port))
    collection = client[database][collection]
    result = collection.find_one({"path": path})
    if result:
        matched = result["component"]
    else:
        while "/" in path:
            path = path[:path.rindex("/")]
            result = collection.find_one({"path": path})
            if result:
                matched = result["component"]
                break
    return matched
