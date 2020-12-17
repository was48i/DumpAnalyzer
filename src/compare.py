import re

from logger import Logger


class Compare(object):
    """
    Compare original crash dumps and display with combined diff format.
    Attributes:
        dump_paths: The paths of crash dumps.
    """
    def __init__(self, paths):
        self.dump_paths = paths

    @staticmethod
    def find_backtrace(stack):
        """
        Obtain the backtrace part of call stack.
        Args:
            stack: A call stack text.
        Returns:
            The backtrace part.
        """
        backtrace = ""
        pattern = re.compile(r"-\n[ ]*(\d+:[ ].+)([^-]+Source:[ ].+:)*", re.M)
        frames = pattern.findall(stack)
        for frame in frames:
            function, source = frame
            # remove offset
            offset_pattern = re.compile(r"([ ]const)*[ ][+][ ]0x\w+")
            function = re.sub(offset_pattern, "", function)
            # merge into a line
            if source:
                source = source[source.index("Source: ") + 8:-1]
                backtrace += "{} at {}\n".format(function, source)
            else:
                backtrace += "{}\n".format(function)
        return backtrace

    @staticmethod
    def find_exception(stack):
        """
        Obtain the exception part of call stack.
        Args:
            stack: A call stack text.
        Returns:
            The exception part.
        """
        exception = ""
        # extract headers
        headers = []
        header_pattern = re.compile(r"(^exception.+no[.].+)\n([\s\S]+?exception[ ]throw[ ]location:)", re.M)
        for header in header_pattern.findall(stack):
            header = "\n{}\n{}\n".format(header[0], header[1].strip())
            headers.append(header)
        # obtain break points
        points = []
        line_pattern = re.compile(r"(\d+:[ ].+[ ]at[ ].+):", re.M)
        lines = line_pattern.findall(stack)
        for index, line in enumerate(lines):
            if line[:line.index(":")] == lines[0][0]:
                points.append(index)
        points.append(len(lines))
        # extract bodies
        bodies = []
        for index in range(len(points) - 1):
            body = ""
            for line in lines[points[index]:points[index + 1]]:
                # remove offset
                offset_pattern = re.compile(r"([ ]const)*[+]*0x\w+([ ]in[ ])*")
                line = re.sub(offset_pattern, "", line)
                body += "{}\n".format(line)
            bodies.append(body)
        # merge header and body
        for header, body in zip(headers, bodies):
            exception += header + body
        return exception

    def compare_dump(self):
        """
        Obtain the call stack part of crash dump and output comparison result.
        """
        message = []
        # call stack pattern
        stack_pattern = re.compile(r"\n(\[CRASH_STACK][\s\S]+)\[CRASH_REGISTERS]", re.M)
        for path in self.dump_paths:
            with open(path, "r", encoding="utf-8") as fp:
                dump = fp.read()
            content = stack_pattern.findall(dump)
            stack = content[0]
            backtrace = self.find_backtrace(stack)
            message.append(backtrace)
            # append exception if exists
            ex_header = "exception throw location:"
            if ex_header in stack:
                exception = self.find_exception(stack)
                message[-1] += exception
        Logger().diff_print(message, self.dump_paths)
