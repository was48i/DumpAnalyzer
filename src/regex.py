import re


def find_component(path):
    # read CMakeLists.txt
    with open(path, "r") as fp:
        file_text = fp.read()
    # set patterns
    pattern_1 = re.compile(r"SET_COMPONENT\(\"(.+)?\"\)", re.M)
    pattern_2 = re.compile(r"SET_COMPONENT\(\"(.+)?\"([^)]+)\)", re.M)
    # get matching lists
    list_1 = pattern_1.findall(file_text)
    list_2 = pattern_2.findall(file_text)
    return list_1, list_2


def find_backtrace(text):
    bt = ""
    # extract source file
    source_dict = dict()
    source_pattern = re.compile(r"[-][\n][ ]+(\d+)[:][ ][\S\s]+"
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
    body_pattern = re.compile(r"(\d+)[:][ ]0x.+[ ]in[ ](.+)[+]0x.+"
                              r"?([ ].+)[:]", re.M)
    whole = body_pattern.findall(text)
    # get break points
    points = []
    for i, b in enumerate(whole):
        if b[0] == "0":
            points.append(i)
    points.append(len(whole) + 1)
    # get lines of body
    for i in range(len(points) - 1):
        body = ""
        for line in whole[points[i]:points[i+1]]:
            body += line[0] + ": " + line[1] + line[2] + "\n"
        bodies.append(body)
    # merge titles and bodies
    for t, b in zip(titles, bodies):
        ex += t + b
    return ex


def find_stacktrace(text):
    trace = find_backtrace(text)
    # merge exceptions if existing
    if "exception throw location" in text:
        exception = find_exception(text)
        trace += exception
    return trace
