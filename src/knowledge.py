import configparser
import os
import re
import subprocess

from component import Component


class Knowledge(object):
    config = configparser.ConfigParser()
    config_path = os.path.join(os.getcwd(), "config.ini")
    config.read(config_path)
    # MongoDB
    host = config.get("mongodb", "host")
    port = config.getint("mongodb", "port")
    db = config.get("mongodb", "db")
    coll = config.get("mongodb", "coll_cpnt")
    # Git
    git_dir = config.get("git", "dir")
    # Stop
    stop_words = config.get("stop", "words")

    def __init__(self, processed):
        self.processed = processed

    def process_frame(self, frame):
        function, path = frame
        word = path[path.rindex("/") + 1:] if "/" in path else path
        if word not in self.stop_words:
            component = Component().to_component(path)
            # demangle
            if function.startswith("_Z"):
                arguments = ["c++filt", "-p", function]
                pipe = subprocess.Popen(arguments, stdout=subprocess.PIPE, stdin=subprocess.PIPE)
                stdout, _ = pipe.communicate()
                function = stdout.decode("utf-8")[:-1]
            return component, function
        else:
            return "", ""

    @staticmethod
    def unboxing(function):
        blocks = []
        if "(" in function:
            function = function[:function.index("(")]
        if "<" in function:
            function = function[:function.index("<")]
        if re.match(r"^[a-z]+[ ]", function):
            function = function[function.index(" ") + 1:]
        for block in function.split("::"):
            blocks.append(block)
        return blocks

    def add_knowledge(self):
        cpnt_order = []
        func_block = []
        for frame in self.processed:
            component, function = self.process_frame(frame)
            if not component:
                continue
            # obtain cpnt_order and func_block
            if cpnt_order:
                if component != cpnt_order[-1]:
                    cpnt_order.append(component)
                    func_block.append(self.unboxing(function))
                else:
                    func_block[-1].extend(self.unboxing(function))
            else:
                cpnt_order = [component]
                func_block = [self.unboxing(function)]
        return cpnt_order, func_block

    def merge_function(self):
        result = []
        component = ""
        functions = []
        for frame in self.processed:
            cur_component, function = self.process_frame(frame)
            if not cur_component:
                continue
            # merge several functions into a component
            if component != "" and cur_component != component:
                result.append([component, functions])
                component = cur_component
                functions = [function]
            else:
                component = cur_component
                functions.append(function)
        result.append([component, functions])
        return result
