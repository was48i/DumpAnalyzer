import os
import re
import json
import subprocess

from argument import parser
from component import to_component

args = parser.parse_args()
# load stop words
stop_words_path = os.path.join(os.getcwd(), "json", "stop_words.json")
try:
    with open(stop_words_path, "r") as f:
        stop_words = json.load(f)
except FileNotFoundError:
    print("Can't find stop_words, please check!")


def demangle(name):
    args = ["c++filt", "-p"]
    args.extend([name])
    pipe = subprocess.Popen(args, stdout=subprocess.PIPE, 
                            stdin=subprocess.PIPE)
    stdout, stderr = pipe.communicate()
    return stdout.decode("utf-8")[:-1]


def get_name(func):
    while "(" in func:
        func = func[:func.rindex("(")]
    if "<" in func:
        func = func[:func.index("<")]
    if re.match(r"^[a-z]+[ ]", func):
        func = func[func.index(" ") + 1:]
    return func


def extract_backtrace(text):
    bt = "[BACKTRACE]\n"
    bt_pattern = re.compile(r"-\n[ ]*\d+:[ ](.+)[^-]+Symbol:[ ].+"
                            r"([^-]+Source:[ ].+:)*", re.M)
    bt_functions = bt_pattern.findall(text)
    for func_tuple in bt_functions:
        f = list(func_tuple)
        # merge into a line
        if " + 0x" in f[0]:
            f[0] = f[0][:f[0].index(" + 0x")]
        name = get_name(f[0])
        if f[1]:
            f[1] = f[1][f[1].index("Source: ") + 8:-1]
            if "/" in f[1]:
                bt += name + " at " + f[1] + "\n"
            else:
                bt += name + "\n"
        else:
            bt += name + "\n"
    return bt


def extract_exception(text):
    ex = "[EXCEPTION]\n"
    ex_pattern = re.compile(r"\d+:[ ](.+)([ ]at[ ].+:)*", re.M)
    ex_functions = ex_pattern.findall(text)
    for func_info in ex_functions:
        f = list(func_info)
        # remove offset if exists
        offset_pattern = re.compile(r"([ ]const)*[+]*0x\w+([ ]in[ ])*")
        f[0] = re.sub(offset_pattern, "", f[0])
        name = get_name(f[0])
        if f[1]:
            f[1] = f[1][f[1].index(" at ") + 4:-1]
        if "/" in f[1]:
            ex += name + " at " + f[1] + "\n"
        else:
            ex += name + "\n"
    return ex


def format_dump(path):
    res = ""
    with open(path, "r", encoding="ISO-8859-1") as fp:
        file_text = fp.read()
    # set stack pattern
    stack_pattern = re.compile(r"\n(\[CRASH_STACK\][\S\s]+)"
                               r"\[CRASH_REGISTERS\]", re.M)
    stack = stack_pattern.findall(file_text)
    # backtrace function
    bt = extract_backtrace(stack[0])
    res += bt
    # merge exception function if exists
    ex_start = "exception throw location"
    ex_end = "exception type information"
    bt_key = "----> Symbolic stack backtrace <----"
    if ex_start in stack[0]:
        key_part = stack[0].split(ex_start)[1]
        if ex_end in key_part:
            key_part = key_part.split(ex_end)[0]
        else:
            key_part = key_part.split(bt_key)[0]
        ex = extract_exception(key_part)
        res += ex
    return res[:-1]


def filter_word(formatted):
    res = ""
    if "[EXCEPTION]\n" in formatted:
        key_part = formatted.split("[EXCEPTION]\n")[1][:-1]
        if key_part:
            res = key_part
    else:
        key_part = formatted[formatted.index("[BACKTRACE]\n") + 12:-1]
        if key_part:
            start = 0
            for i, func in enumerate(key_part.split("\n")):
                if " at " in func:
                    func = func[:func.index(" at ")]
                # filter stop words
                if func not in stop_words:
                    start = i
                    break
            for line in key_part.split("\n")[start:]:
                res += line + "\n"
            res = res[:-1]
    return res


def add_knowledge(filtered):
    res = []
    component = ""
    func_content = ""
    for func_info in filtered.split("\n"):
        if " at " in func_info:
            name = func_info[:func_info.index(" at ")]
            source = func_info[func_info.index(" at ") + 4:]
            f = [name, source]
        else:
            f = [func_info, ""]
        if component != "" and to_component(f) != component:
            res.append([component, func_content[:-1]])
            component = to_component(f)
            func_content = ""
            func_content += f[0] + "\n"
        else:
            component = to_component(f)
            func_content += f[0] + "\n"
    res.append([component, func_content[:-1]])
    return res


__all__ = [
    "format_dump",
    "filter_word",
    "add_knowledge"
]
