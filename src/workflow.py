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
    # set crash stack pattern
    pattern = re.compile(r"\n(\[CRASH_STACK\][\S\s]+)"
                         r"\[CRASH_REGISTERS\]", re.M)
    with open(path, "r", encoding="ISO-8859-1") as fp:
        file_text = fp.read()
    stack = pattern.findall(file_text)
    res = find_stack(stack[0])
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
        # get break point
        if method not in stop_words and \
                "ltt" not in method and \
                "std" not in method and \
                "::" in method:
            start = index
            break
    # cut off exception part
    for line in [i for i in formatted.split("\n") if i][start:]:
        if line.startswith("exception"):
            break
        res += line + "\n"
    return res


def find_key(backtrace):
    key = ""
    component = ""
    # set method info pattern
    pattern = re.compile(r"\d+:[ ](.+)"
                         r"([ ]at[ ].+)*", re.M)
    method_info = pattern.findall(backtrace)
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
        # apply stop words
        if m[0] not in stop_words and "ltt" not in m[0]:
            # first component rule
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
