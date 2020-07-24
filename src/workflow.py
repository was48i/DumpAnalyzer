import os
import re
import json
import subprocess
import numpy as np

from lcs_dp import lcs_dp
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


def vaild_function(func):
    # demangle
    arguments = ["c++filt", "-p"]
    if func.startswith("_Z"):
        arguments.extend([func])
        pipe = subprocess.Popen(arguments, stdout=subprocess.PIPE,
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


def extract_exception(text):
    ex = ""
    # get ex_functions
    ex_pattern = re.compile(r"\d+:[ ](.+[+].+[ ]at[ ].+):", re.M)
    ex_pattern_sp = re.compile(r"\d+:[ ](.+[+].+)[ ]", re.M)
    ex_functions = ex_pattern.findall(text)
    if not ex_functions:
        ex_functions = ex_pattern_sp.findall(text)
    for line in ex_functions:
        # remove offset if exists
        offset_pattern = re.compile(r"([ ]const)*[+]*0x\w+([ ]in[ ])*")
        func_info = re.sub(offset_pattern, "", line)
        # handle exception without source
        source = ""
        if " at " in func_info:
            f_name = func_info[:func_info.index(" at ")]
            source = func_info[func_info.index(" at ") + 4:]
        else:
            f_name = func_info
        # get vaild function name
        name = vaild_function(f_name)
        if name == "":
            continue
        # combine function and source
        if "/" in source:
            ex += name + " at " + source + "\n"
        else:
            ex += name + "\n"
    return ex


def extract_backtrace(text):
    bt = ""
    bt_pattern = re.compile(r"-\n[ ]*\d+:[ ](.+)"
                            r"([^-]+Source:[ ].+:)*", re.M)
    bt_functions = bt_pattern.findall(text)
    for func_tuple in bt_functions:
        func_info = list(func_tuple)
        # merge into a line
        if " + 0x" in func_info[0]:
            func_info[0] = func_info[0][:func_info[0].index(" + 0x")]
        # get vaild function name
        name = vaild_function(func_info[0])
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


def filter_position(stacks, words):
    position = 0
    for i, func in enumerate(stacks):
        if " at " in func:
            func = func[:func.index(" at ")]
        if func not in words:
            position = i
            break
    return position


def pre_process(path):
    result = ""
    with open(path, "r", encoding="ISO-8859-1") as fp:
        file_text = fp.read()
    # call stack pattern
    stack_pattern = re.compile(r"\n(\[CRASH_STACK\][\s\S]+)"
                               r"\[CRASH_REGISTERS\]", re.M)
    content = stack_pattern.findall(file_text)
    if not content:
        return ""
    else:
        stack = content[0]
    # extract exception firstly
    ex_location = "exception throw location:"
    if ex_location in stack:
        first_ex = stack.split(ex_location)[1]
        result = extract_exception(first_ex)
    # need to filter bt by stop_words
    if result == "":
        bt_result = extract_backtrace(stack)
        bt_list = [i for i in bt_result.split("\n") if i]
        prefix_words, suffix_words = stop_words
        start = filter_position(bt_list, prefix_words)
        end = len(bt_list) - filter_position(bt_list[::-1], suffix_words)
        for line in bt_list[start:end]:
            result += line + "\n"
    return result


def add_knowledge(processed):
    result = []
    component = ""
    func_content = ""
    for func_info in [i for i in processed.split("\n") if i]:
        if " at " in func_info:
            name = func_info[:func_info.index(" at ")]
            source = func_info[func_info.index(" at ") + 4:]
            func = [name, source]
        else:
            func = [func_info, ""]
        if component != "" and to_component(func) != component:
            result.append([component, func_content[:-1]])
            component = to_component(func)
            func_content = ""
            func_content += func[0] + "\n"
        else:
            component = to_component(func)
            func_content += func[0] + "\n"
    result.append([component, func_content[:-1]])
    return result


def edit_distance(src, tgt):
    m = len(src)
    n = len(tgt)
    dp = [[i + j for j in range(n + 1)] for i in range(m + 1)]
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if src[i - 1] == tgt[j - 1]:
                d = 0
            else:
                d = 1
            dp[i][j] = min(dp[i - 1][j] + 1, dp[i][j - 1] + 1,
                           dp[i - 1][j - 1] + d)
    sum = m + n
    return (sum - dp[m][n]) / sum


def calculate_sim(paths, m, n):
    sim = 0.0
    # prepare items for calculation
    cpnt_list = []
    func_list = []
    for path in paths:
        info = add_knowledge(pre_process(path))
        cpnt_list.append([i[0] for i in info])
        func_list.append([i[1] for i in info])
    # calculate similarity
    above_sum = 0.0
    below_sum = 0.0
    # apply LCS
    lcs, x_pos, y_pos = lcs_dp(cpnt_list)
    above_item = []
    for i, com in enumerate(lcs):
        pos = max(x_pos[i], y_pos[i])
        # apply edit distance by element
        src_list = re.split("\n|::", func_list[0][x_pos[i]])
        tgt_list = re.split("\n|::", func_list[1][y_pos[i]])
        component_sim = edit_distance(src_list, tgt_list)
        # used for output
        above_item.append([pos, component_sim])
        above_sum += np.exp(-m * pos) * np.exp(-n * (1 - component_sim))
    below_item = max(len(cpnt_list[0]), len(cpnt_list[1]))
    for i in range(below_item):
        below_sum += np.exp(-m * i)
    sim = above_sum / below_sum
    return sim, above_item, below_item
