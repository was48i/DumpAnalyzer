import os
import difflib
import Levenshtein

from argument import parser

args = parser.parse_args()


def hana_print(result):
    print("\n", end="")
    # get delimiter position
    max_pos = 0
    for func_info in result[0]:
        cur_pos = len(max(func_info[1].split("\n")))
        if cur_pos > max_pos:
            max_pos = cur_pos
    # get dump lengths
    length = []
    for dump in result:
        cnt = 0
        for func_info in dump:
            cnt += len([i for i in func_info[1].split("\n") if i])
        cnt += len(dump)
        length.append(cnt)
    # comparision output
    for func_info in result[0]:
        print("\x1b[0;36m" + func_info[0] + "\x1b[0m")
        for name in [i for i in func_info[1].split("\n") if i]:
            print(name)
    print("\x1b[%dA" % length[0], end="")
    for func_info in result[1]:
        print("\x1b[%dC" % max_pos, end="")
        print("  |  ", end="")
        print("\x1b[0;36m" + func_info[0] + "\x1b[0m")
        for name in [i for i in func_info[1].split("\n") if i]:
            print("\x1b[%dC" % max_pos, end="")
            print("  |  ", end="")
            print(name)
    # complete delimiters
    if length[0] > length[1]:
        for i in range(length[0] - length[1]):
            print("\x1b[%dC" % max_pos, end="")
            print("  |")
    print("\n", end="")


def formula_print(results, parameters):
    numerator = ""
    denominator = ""
    m_pos, n_sim, threshold = parameters
    sim, above_item, below_item = results
    # merge numerator and denominator
    if above_item:
        numerator = "e^" + "-%.1f*%d" % (m_pos, above_item[0][0]) + "*" + \
                    "e^" + "-%.1f*(1-%.4f)" % (n_sim, above_item[0][1])
        for i in above_item[1:]:
            numerator += " + " + "e^" + "-%.1f*%d" % (m_pos, i[0]) + \
                         "*" + "e^" + "-%.1f*(1-%.4f)" % (n_sim, i[1])
    if below_item:
        denominator = "e^" + "-%.1f*%d" % (m_pos, 0)
        for i in range(1, below_item):
            denominator += " + " + "e^" + "-%.1f*%d" % (m_pos, i)
    # beautiful output
    max_length = max(len(numerator), len(denominator))
    indent = round(abs(len(numerator) - len(denominator)) / 2)
    print("\n", end="")
    if len(numerator) >= len(denominator):
        denominator = " " * indent + denominator
    else:
        if numerator:
            numerator = " " * indent + numerator
        else:
            numerator = " " * indent + "0"
    print("             " + numerator)
    print("Similarity = " + "-" * max_length + " = {:.2%}".format(sim))
    print("             " + denominator)
    print("\n", end="")
    if sim >= threshold:
        print("{:.2%} >= {:.2%}, ".format(sim, threshold), end="")
        print("\x1b[0;32mDUPLICATE\x1b[0m")
    else:
        print("{:.2%} < {:.2%}, ".format(sim, threshold), end="")
        print("\x1b[0;31mDISTINCT\x1b[0m")
    print("\n", end="")


def diff_print(lists, files):
    print("\n", end="")
    # handle the same situation
    if lists[0] == lists[1]:
        for line in lists[0].split("\n"):
            print(line)
    # print diff
    diff = difflib.unified_diff(lists[0].split("\n"), lists[1].split("\n"),
                                fromfile=files[0], tofile=files[1], lineterm="")
    for line in diff:
        if line.startswith("---") or line.startswith("+++"):
            print("\x1b[1m" + line + "\x1b[0m")
        elif line.startswith("-"):
            print("\x1b[0;31m" + line + "\x1b[0m")
        elif line.startswith("+"):
            print("\x1b[0;32m" + line + "\x1b[0m")
        elif line.startswith("@@"):
            print("\x1b[0;36m" + line + "\x1b[0m")
        else:
            print(line)


def sim_print(text_1, text_2):
    sim = Levenshtein.ratio(text_1, text_2)
    if sim < 0.1:
        print("+-------------------+")
        print("| Similarity: {:.2%} |".format(sim))
        print("+-------------------+")
    elif sim < 1.0:
        print("+--------------------+")
        print("| Similarity: {:.2%} |".format(sim))
        print("+--------------------+")
    else:
        print("+---------------------+")
        print("| Similarity: {:.2%} |".format(sim))
        print("+---------------------+")
    print("\n", end="")


def format_print(lists):
    stack_1 = os.path.basename(args.dump[0])
    stack_2 = os.path.basename(args.dump[1])
    diff_print(lists, [stack_1, stack_2])
    sim_print(lists[0], lists[1])
