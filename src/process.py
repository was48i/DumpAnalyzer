import re


class Process(object):
    def __init__(self, dump):
        self.dump = dump

    def pre_process(self):
        result = []
        # call stack pattern
        stack_pattern = re.compile(r"\n(\[CRASH_STACK][\s\S]+)\[CRASH_REGISTERS]", re.M)
        content = stack_pattern.findall(self.dump)
        stack = content[0]
        # backtrace pattern
        pattern = re.compile(r"-\n[ ]*\d+:[ ](.+)[^-]+Source:[ ](.+):", re.M)
        frames = pattern.findall(stack)
        for frame in frames:
            function, path = frame
            # remove offset
            offset_pattern = re.compile(r"([ ]const)*[ ][+][ ]0x\w+")
            function = re.sub(offset_pattern, "", function)
            result.append([function, path])
        return result

    def internal_process(self):
        result = []
        ex_header = "exception throw location:"
        if ex_header in self.dump:
            self.dump = self.dump.split(ex_header)[0]
        pattern = re.compile(r"^\d+:[ ](.+)[ ]at[ ](.+)", re.M)
        frames = pattern.findall(self.dump)
        for frame in frames:
            function, path = frame
            result.append([function, path])
        return result
