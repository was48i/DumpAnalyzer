import sys

from argument import parser
from persistence import load_components

args = parser.parse_args()
components = load_components()


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
    # remove root directory
    if args.source in path:
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
