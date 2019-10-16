import sys
import difflib


def format_print(files, lists):
    # get diff
    separator = "\\" if sys.platform == "win32" else "/"
    stack_1 = files[0][files[0].rindex(separator) + 1:]
    stack_2 = files[1][files[1].rindex(separator) + 1:]
    diff = difflib.unified_diff(lists[0].split("\n"), lists[1].split("\n"),
                                fromfile=stack_1, tofile=stack_2, lineterm="")
    # handle the same case
    # try:
    #     next(diff)
    # except StopIteration:
    #     print("\033[1m" + stack_1 + "\033[0m")
    #     for com in lists[0].split("\n"):
    #         print("\033[0;36m" + com + "\033[0m")
    #     print("\033[1m" + stack_2 + "\033[0m")
    #     for com in lists[1].split("\n"):
    #         print("\033[0;36m" + com + "\033[0m")
    # set diff format
    for line in diff:
        if line.startswith("-"):
            if line.startswith("---"):
                print("\033[1m" + line + "\033[0m")
            else:
                line = "-   " + line[line.index("-") + 1:]
                print("\033[0;31m" + line + "\033[0m")
        elif line.startswith("+"):
            if line.startswith("+++"):
                print("\033[1m" + line + "\033[0m")
            else:
                line = "+   " + line[line.index("+") + 1:]
                print("\033[0;32m" + line + "\033[0m")
        elif line.startswith("@@"):
            print("\033[0;36m" + line + "\033[0m")
        else:
            print(line)
    # output similarity
    sim = difflib.SequenceMatcher(None, lists[0], lists[1]).ratio()
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
