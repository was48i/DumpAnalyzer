import re


def find_component(path):
    # read file
    with open(path, "r") as fp:
        file_text = fp.read()
    # set patterns
    pattern_1 = re.compile(r"SET_COMPONENT\(\"(.+)?\"\)", re.M)
    pattern_2 = re.compile(r"SET_COMPONENT\(\"(.+)?\"([^)]+)\)", re.M)
    # get matching lists
    list_1 = pattern_1.findall(file_text)
    list_2 = pattern_2.findall(file_text)
    return list_1, list_2
