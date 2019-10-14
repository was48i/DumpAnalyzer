import difflib


def format_print(files, lists):
    # get diff
    stack_1 = files[0][files[0].rindex("/") + 1:]
    stack_2 = files[1][files[1].rindex("/") + 1:]
    diff = difflib.unified_diff(lists[0].split("\n"), lists[1].split("\n"),
                                fromfile=stack_1, tofile=stack_2, lineterm="")
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
    difflib.Differ()
    print("+--------------------+")
    print("| Similarity: {:.2%} |".format(sim))
    print("+--------------------+")
