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
    print("Can not find stop_words, please check.")


def valid_function(func):
    # demangling
    args = ["c++filt", "-p"]
    if func.startswith("_Z"):
        args.extend([func])
        pipe = subprocess.Popen(args, stdout=subprocess.PIPE, 
                                stdin=subprocess.PIPE)
        stdout, stderr = pipe.communicate()
        func = stdout.decode("utf-8")[:-1]
    # remove parameter variable
    if "(" in func:
        func = func[:func.index("(")]
    # remove template
    if "<" in func:
        func = func[:func.index("<")]
    # remove return type
    if re.match(r"^[a-z]+[ ]", func):
        func = func[func.index(" ") + 1:]
    if not re.match(r"^[_a-zA-Z]", func):
        return ""
    else:
        return func


def extract_backtrace(text):
    bt = "[BACKTRACE]\n"
    bt_pattern = re.compile(r"-\n[ ]*\d+:[ ](.+)"
                            r"([^-]+Source:[ ].+:)*", re.M)
    bt_functions = bt_pattern.findall(text)
    for func_tuple in bt_functions:
        func_info = list(func_tuple)
        # merge into a line
        if " + 0x" in func_info[0]:
            func_info[0] = func_info[0][:func_info[0].index(" + 0x")]
        # get valid function name
        name = valid_function(func_info[0])
        if name == "":
            continue
        if func_info[1]:
            func_info[1] = func_info[1][func_info[1].index("Source: ") + 8:-1]
            if "/" in func_info[1]:
                bt += name + " at " + func_info[1] + "\n"
            else:
                bt += name + "\n"
        else:
            bt += name + "\n"
    return bt


def extract_exception(text):
    ex = "[EXCEPTION]\n"
    ex_pattern = re.compile(r"\d+:[ ](.+[+].+[ ]at[ ].+):", re.M)
    # handle exception without source
    ex_pattern_sp = re.compile(r"\d+:[ ](.+[+].+)[ ]", re.M)
    ex_functions = ex_pattern.findall(text)
    if not ex_functions:
        ex_functions = ex_pattern_sp.findall(text)
    for line in ex_functions:
        # remove offset if exists
        offset_pattern = re.compile(r"([ ]const)*[+]*0x\w+([ ]in[ ])*")
        func_info = re.sub(offset_pattern, "", line)
        source = ""
        # handle special exception
        if " at " in func_info:
            f_name = func_info[:func_info.index(" at ")]
            source = func_info[func_info.index(" at ") + 4:]
        else:
            f_name = func_info
        # get valid function name
        name = valid_function(f_name)
        if name == "":
            continue
        if "/" in source:
            ex += name + " at " + source + "\n"
        else:
            ex += name + "\n"
    return ex


def format_dump(path):
    res = ""
    with open(path, "r", encoding="ISO-8859-1") as fp:
        file_text = fp.read()
    # set stack pattern
    stack_pattern = re.compile(r"\n(\[CRASH_STACK\][\s\S]+)"
                               r"\[CRASH_REGISTERS\]", re.M)
    stack = stack_pattern.findall(file_text)
    # backtrace function
    bt_header = "-> Symbolic stack backtrace <-"
    ex_header = "-> Pending exceptions (possible root cause) <-"
    ex_part, bt_part = stack[0].split(bt_header)
    bt = extract_backtrace(bt_part)
    res += bt
    # merge exception function if exists
    if ex_header in ex_part:
        # extract the first exception
        ex_location = "exception throw location:"
        if ex_location in ex_part:
            first_ex = ex_part.split(ex_location)[1]
            ex = extract_exception(first_ex)
            res += ex
    return res


def filter_word(formatted):
    res = ""
    if "[EXCEPTION]\n" in formatted:
        key_part = formatted.split("[EXCEPTION]\n")[1]
        if key_part:
            res = key_part
    else:
        key_part = formatted[formatted.index("[BACKTRACE]\n") + 12:]
        if key_part:
            start = 0
            end = len([i for i in key_part.split("\n") if i])
            prefix_words, suffix_words = stop_words
            # get start/end
            for i, func in enumerate([i for i in key_part.split("\n") if i]):
                if " at " in func:
                    func = func[:func.index(" at ")]
                if func not in prefix_words:
                    start += i
                    break
            for i, func in enumerate([i for i in key_part.split("\n") if i][::-1]):
                if " at " in func:
                    func = func[:func.index(" at ")]
                if func not in suffix_words:
                    end -= i
                    break
            for line in [i for i in key_part.split("\n") if i][start:end]:
                res += line + "\n"
            res = res
    return res


def add_knowledge(filtered):
    res = []
    component = ""
    func_content = ""
    for func_info in [i for i in filtered.split("\n") if i]:
        if " at " in func_info:
            name = func_info[:func_info.index(" at ")]
            source = func_info[func_info.index(" at ") + 4:]
            func = [name, source]
        else:
            func = [func_info, ""]
        if component != "" and to_component(func) != component:
            res.append([component, func_content[:-1]])
            component = to_component(func)
            func_content = ""
            func_content += func[0] + "\n"
        else:
            component = to_component(func)
            func_content += func[0] + "\n"
    res.append([component, func_content[:-1]])
    return res
