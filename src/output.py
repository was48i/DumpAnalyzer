import os
import difflib
import Levenshtein
import prettytable as pt

from argument import parser


def same_print(text):
    for stack in text:
        print("\033[0;36m" + stack[0] + "\033[0m")
        for com in stack[1].split("\n"):
            print(com)


def diff_print(text):
    for line in text:
        if line.startswith("---") or line.startswith("+++"):
            print("\033[1m" + line + "\033[0m")
        elif line.startswith("-"):
            print("\033[0;31m" + line + "\033[0m")
        elif line.startswith("+"):
            print("\033[0;32m" + line + "\033[0m")
        elif line.startswith("@@"):
            print("\033[0;36m" + line + "\033[0m")
        else:
            print(line)


def sim_print(text_1, text_2):
    sim = Levenshtein.ratio(text_1, text_2)
    # do alignment
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


def format_print(lists):
    # get diff
    args = parser.parse_args()
    stack_1 = os.path.basename(args.dump[0])
    stack_2 = os.path.basename(args.dump[1])
    diff = difflib.unified_diff(lists[0].split("\n"), lists[1].split("\n"),
                                fromfile=stack_1, tofile=stack_2, lineterm="")
    # handle the same situation
    if lists[0] == lists[1]:
        same_print([(stack_1, lists[0]), (stack_2, lists[1])])
    # formatted print
    diff_print(diff)
    sim_print(lists[0], lists[1])


def stats_print(metrics):
    tb = pt.PrettyTable()
    # insert metrics
    precision, recall, f1 = metrics
    tb.add_column("Precision", precision)
    tb.add_column("Recall", recall)
    tb.add_column("F1 Score", f1)
    print(tb)


def flow_print(results):
    step_1, step_2, step_3 = results
    # follow 4 steps to output
    print("\033[0;32m" + "I. Format Dump File" + "\033[0m")
    print(step_1)
    print("\033[0;32m" + "II. Filter Stop Words" + "\033[0m")
    print(step_2)
    print("\033[0;32m" + "III. Add HANA Knowledge" + "\033[0m")
    for func_info in step_3:
        print("\033[0;36m" + func_info[0] + "\033[0m")
        for name in func_info[1].split("\n"):
            print(name)


__all__ = [
    "format_print",
    "stats_print",
    "flow_print"
]
