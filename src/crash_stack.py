import os
import re

from argument import parser
from symbol import best_matched
from persistence import load_symbols


def find_backtrace(text):
    bt = ""
    # extract source file
    source_dict = dict()
    source_pattern = re.compile(r"[-][\n][ ]+(\d+)[:][ ][^-]+"
                                r"?Source[:][ ](.+)[:]", re.M)
    sources = source_pattern.findall(text)
    for k, v in sources:
        source_dict[k] = v
    # extract method
    method_pattern = re.compile(r"[-][\n][ ]+(\d+)[:][ ](.+)", re.M)
    methods = method_pattern.findall(text)
    for m in methods:
        # processing method
        if " + 0x" in m[1]:
            method = m[1][:m[1].rindex(" + 0x")]
        else:
            method = m[1]
        # merge into a line
        if m[0] in source_dict:
            bt += str(m[0]) + ": " + method + " at " + source_dict[m[0]] + "\n"
        else:
            bt += str(m[0]) + ": " + method + "\n"
    return bt


def find_exception(text):
    ex = ""
    titles = []
    bodies = []
    # extract titles
    title_pattern = re.compile(r"(exception.+)[ ]TID.+[\n]"
                               r"([\S\s]+?exception[ ]throw[ ]location[:])", re.M)
    for t in title_pattern.findall(text):
        title = "\n" + t[0] + "\n" + t[1].lstrip() + "\n"
        titles.append(title)
    # extract bodies
    body_pattern = re.compile(r"(\d+)[:][ ]0x.+[ ]"
                              r"in[ ](.+)[+]0x.+?([ ].+)[:]", re.M)
    whole = body_pattern.findall(text)
    # get break points
    points = []
    for i, b in enumerate(whole):
        if b[0] == "0":
            points.append(i)
    points.append(len(whole) + 1)
    # processing body
    for i in range(len(points) - 1):
        body = ""
        for line in whole[points[i]:points[i+1]]:
            body += line[0] + ": " + line[1] + line[2] + "\n"
        bodies.append(body)
    # merge titles and bodies
    for t, b in zip(titles, bodies):
        ex += t + b
    return ex


def find_stack(text):
    trace = find_backtrace(text)
    # merge exceptions if existing
    if "exception throw location" in text:
        exception = find_exception(text)
        trace += exception
    return trace


def match_component(trace):
    path_pattern = re.compile(r"[ ]at[ ](.+)")
    func_pattern = re.compile(r"\d+[:][\w ]*[ ](.+[^ ])\(")
    # match using source
    if " at " in trace and "/" in trace:
        args = parser.parse_args()
        path = args.source
        for layer in path_pattern.search(trace).group(1).split("/"):
            path = os.path.join(path, layer)
        component = best_matched(path)
    # match using symbol
    elif "(" in trace:
        symbols = load_symbols()
        key = func_pattern.match(trace).group(1)
        if "<" in key:
            key = key[:key.index("<")]
        try:
            component = symbols[key]
        except KeyError:
            component = key
    # unrecognizable component
    else:
        component = re.match(r"\d+[:][ ](.+)", trace).group(1)
    return component


def to_component(trace):
    cnt = 0
    component = ""
    res = "[BACKTRACE]\n"
    # string to list
    trace_list = trace.split("\n")
    # set patterns
    trace_pattern = re.compile(r"\d+[:][ ].+")
    for trace in trace_list:
        # extract backtrace
        if trace_pattern.match(trace):
            com = match_component(trace)
            # update component and cnt
            if com != component:
                res += str(cnt) + ": " + com + "\n"
                component = com
                cnt += 1
        # extract exception
        elif trace.startswith("exception throw location"):
            cnt = 0
            component = ""
            res += "\n[EXCEPTION]\n"
    return res


__all__ = [
    "find_stack",
    "to_component"
]
