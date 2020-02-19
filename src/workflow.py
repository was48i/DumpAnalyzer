import os
import re
import json
import hashlib

from argument import parser
from regex import find_stack
from component import to_component

args = parser.parse_args()
# load stop words
stop_words_path = os.path.join(os.getcwd(), "json", "stop_words.json")
try:
    with open(stop_words_path, "r") as f:
        stop_words = json.load(f)
except FileNotFoundError:
    print("Can't find stop_words, please check!")


def format_dump(path):
    with open(path, "r", encoding="ISO-8859-1") as fp:
        file_text = fp.read()
    res = find_stack(file_text)
    return res


def filter_words(formatted):
    res = ""
    start = 0
    for index, line in enumerate([i for i in formatted.split("\n") if i]):
        # extract symbol
        method = re.match(r"\d+:[ ](.+)", line).group(1)
        if " at " in method:
            method = method[:method.index(" at ")]
        if "(" in method:
            method = method[:method.index("(")]
        if " " in method:
            method = method[method.index(" ") + 1:]
        # apply stop words
        if method not in stop_words and \
                "MemoryManager" not in method and \
                "ltt" not in method and method:
            start = index
            break
    # output filtered stack
    for line in formatted.split("\n")[start:-1]:
        if line == "":
            res += "\n"
        else:
            res += line + "\n"
    return res


def find_key(filtered):
    key = ""
    component = ""
    method_info = []
    # set method info pattern
    pattern = re.compile(r"\d+:[ ](.+)"
                         r"([ ]at[ ].+)*", re.M)
    if not args.ignore:
        # extract exception if exists
        if "exception throw location" in filtered:
            key_part = filtered.split("exception throw location")[1]
            method_info = pattern.findall(key_part)
    # extract backtrace
    if not method_info:
        key_part = filtered.split("exception throw location")[0]
        method_info = pattern.findall(key_part)
    for m_tuple in method_info:
        m = list(m_tuple)
        # get source info
        if m[1]:
            m[1] = m[1][m[1].index(" at ") + 4]
        # remove parameter variable and return type
        if "(" in m[0]:
            m[0] = m[0][:m[0].index("(")]
        if " " in m[0]:
            m[0] = m[0][m[0].index(" ") + 1:]
        if not args.ignore:
            if "MemoryManager" not in m[0] and \
                    "ltt" not in m[0] and m[0]:
                # first component rule
                if component != "" and to_component(m) != component:
                    break
                else:
                    component = to_component(m)
                    key += m[0] + "\n"
        else:
            # ignore stop words
            if component != "" and to_component(m) != component:
                break
            else:
                component = to_component(m)
                key += m[0] + "\n"
    # compare by MD5
    md5 = hashlib.md5()
    message = key
    md5.update(message.encode("utf-8"))
    return key, md5.hexdigest()


__all__ = [
    "format_dump",
    "filter_words",
    "find_key"
]
