import os
import difflib


def same_print(text):
    for stack in text:
        # print title
        print("\033[1m" + stack[0] + "\033[0m")
        # print body
        for com in stack[1].split("\n"):
            print("\033[0;36m" + com + "\033[0m")


def diff_print(text):
    for line in text:
        if line.startswith("---") or line.startswith("+++"):
            print("\033[1m" + line + "\033[0m")
        elif line.startswith("-"):
            line = "-   " + line[line.index("-") + 1:]
            print("\033[0;31m" + line + "\033[0m")
        elif line.startswith("+"):
            line = "+   " + line[line.index("+") + 1:]
            print("\033[0;32m" + line + "\033[0m")
        elif line.startswith("@@"):
            print("\033[0;36m" + line + "\033[0m")
        else:
            print(line)


def sim_print(text_1, text_2):
    sim = difflib.SequenceMatcher(None, text_1, text_2).ratio()
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


def format_print(files, lists):
    # get diff
    stack_1 = os.path.basename(files[0])
    stack_2 = os.path.basename(files[1])
    diff = difflib.unified_diff(lists[0].split("\n"), lists[1].split("\n"),
                                fromfile=stack_1, tofile=stack_2, lineterm="")
    # handle the same situation
    if lists[0] == lists[1]:
        same_print([(stack_1, lists[0]), (stack_2, lists[1])])
    # formatted print
    diff_print(diff)
    sim_print(lists[0], lists[1])
