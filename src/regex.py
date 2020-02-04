import re


def find_backtrace(text):
    bt = ""
    # extract method and file
    bt_pattern = re.compile(r"-\n[ ]+(\d+:[ ].+)[ ][+]"
                            r"([^-]+?Source:[^:]+:)*", re.M)
    bt_methods = bt_pattern.findall(text)
    for m_tuple in bt_methods:
        m = list(m_tuple)
        # merge into a line
        if m[1]:
            m[1] = m[1][m[1].index("Source: ") + 8:-1]
            bt += m[0] + " at " + m[1] + "\n"
        else:
            bt += m[0] + "\n"
    return bt


def find_exception(text):
    ex = ""
    # extract headers
    headers = []
    header_pattern = re.compile(r"(exception.+)[ ]TID.+\n"
                                r"([\S\s]+?exception[ ]throw[ ]location:)",
                                re.M)
    for h in header_pattern.findall(text):
        header = "\n" + h[0] + "\n" + h[1].lstrip() + "\n"
        headers.append(header)
    # extract bodies
    bodies = []
    body_pattern = re.compile(r"(\d+:[ ])0x.+[ ]in[ ]"
                              r"(.+)[+]0x(.+)", re.M)
    whole = body_pattern.findall(text)
    # get break points
    points = []
    for i, b in enumerate(whole):
        if b[0] == whole[0][0]:
            points.append(i)
    points.append(len(whole) + 1)
    # processing body
    for i in range(len(points) - 1):
        body = ""
        for line_tuple in whole[points[i]:points[i + 1]]:
            line = list(line_tuple)
            # merge into a line
            if " at " in line[2]:
                line[2] = line[2][line[2].index(" at "):line[2].index(":")]
                body += line[0] + line[1] + line[2] + "\n"
            else:
                body += line[0] + line[1] + "\n"
        bodies.append(body)
    # merge header and body
    for h, b in zip(headers, bodies):
        ex += h + b
    return ex


def find_stack(text):
    trace = find_backtrace(text)
    # merge exceptions if exist
    if "exception throw location" in text:
        exception = find_exception(text)
        trace += exception
    return trace


__all__ = [
    "find_backtrace",
    "find_stack"
]
