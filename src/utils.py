import glob
import json
import os
import re


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


def dump_component(mapping):
    """
    Dump component mapping to JSON format.
    """
    dump_path = os.path.join(os.getcwd(), "json", "components.json")
    with open(dump_path, "w") as fp:
        json.dump(mapping, fp, indent=4, sort_keys=True)


def get_header(dir_path):
    """
    Obtain all header files in the current directory.

    Args:
        dir_path: The dictionary to be processed.

    Returns:
        All header files in the directory.
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


def load_component():
    """
    Load component JSON to mapping.
    """
    load_path = os.path.join(os.getcwd(), "json", "components.json")
    with open(load_path, "r") as fp:
        component_mapping = json.load(fp)
    return component_mapping


def best_matched(path):
    """
    Obtain the best matched component.

    Args:
        path: The path of current header file.

    Returns:
        The best matched component.
    """
    result = "UNKNOWN"
    components = load_component()
    if path in components:
        result = components[path]
    else:
        while "/" in path:
            path = path[:path.rindex("/")]
            if path in components:
                result = components[path]
                break
    return result


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


def dump_function(mapping):
    """
    Dump function mapping to JSON format.
    """
    dump_path = os.path.join(os.getcwd(), "json", "functions.json")
    with open(dump_path, "w") as fp:
        json.dump(mapping, fp, indent=4, sort_keys=True)
