import configparser
import os
import re
import subprocess

from component import Component


class Knowledge(object):
    """
    Add component knowledge and obtain cpnt_order, func_block for calculation.
    Attributes:
        processed: Processed crash dump composed of function and path.
    """
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

    @staticmethod
    def unboxing(function):
        """
        Extract the required part of function and divide it into blocks.
        Args:
            function: A original function name.
        Returns:
            Function blocks composed of class, namespace, ...
        """
        blocks = []
        # handle anonymous namespace
        if "(anonymous namespace)::" in function:
            function = function.replace("(anonymous namespace)::", "")
        if "::(anonymous namespace)" in function:
            function = function.replace("::(anonymous namespace)", "")
        if "(" in function:
            function = function[:function.index("(")]
        if "<" in function:
            function = function[:function.index("<")]
        if re.match(r"^[a-z]+[ ]", function):
            function = function[function.index(" ") + 1:]
        # remove special characters
        if re.search(r"[^0-9a-zA-Z:_~]", function):
            point = re.search(r"[^0-9a-zA-Z:_~]", function).span()[0]
            function = function[:point]
        for block in function.split("::"):
            blocks.append(block)
        return blocks

    def process_frame(self, frame):
        """
        Process stack frame and obtain component and function information.
        Args:
            frame: A original stack frame.
        Returns:
            A component with function information which the current frame belongs to.
        """
        function, path = frame
        word = path[path.rindex("/") + 1:] if "/" in path else path
        if word in self.stop_words:
            return "", ""
        else:
            component = Component().to_component(path)
            if component == "UNKNOWN":
                return "", ""
            # demangle
            if function.startswith("_Z"):
                arguments = ["c++filt", "-p", function]
                pipe = subprocess.Popen(arguments, stdout=subprocess.PIPE, stdin=subprocess.PIPE)
                stdout, _ = pipe.communicate()
                function = stdout.decode("utf-8")[:-1]
            function = self.unboxing(function)
            return component, function

    def add_knowledge(self):
        """
        Add component knowledge and obtain cpnt_order, func_block for calculation.
        Returns:
            The cpnt_order and func_block for calculation.
        """
        cpnt_order = []
        func_block = []
        for frame in self.processed:
            component, function = self.process_frame(frame)
            if component == "":
                continue
            # obtain cpnt_order and func_block
            if not cpnt_order:
                cpnt_order = [component]
                func_block = [function]
            else:
                if component != cpnt_order[-1]:
                    cpnt_order.append(component)
                    func_block.append(function)
                else:
                    func_block[-1].extend(function)
        return cpnt_order, func_block
