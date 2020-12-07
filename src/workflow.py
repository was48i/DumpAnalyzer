import configparser
import math
import os
import pymongo
import re
import subprocess


class Workflow(object):
    """
    The whole process of our approach that contains several stages.
    """
    config = configparser.ConfigParser()
    config_path = os.path.join(os.getcwd(), "settings.ini")
    config.read(config_path)
    # Git
    git_dir = config.get("git", "dir")
    # MongoDB
    host = config.get("mongodb", "host")
    port = config.get("mongodb", "port")
    db = config.get("mongodb", "db")
    coll = config.get("mongodb", "coll_cpnt")
    # Model
    stop_source = [i.strip() for i in config.get("model", "stop").split(",")]
    m = config.getfloat("model", "m")
    n = config.getfloat("model", "n")

    @staticmethod
    def pre_process(dump_path):
        result = []
        with open(dump_path, "r", encoding="ISO-8859-1") as fp:
            dump = fp.read()
        # call stack pattern
        stack_pattern = re.compile(r"\n(\[CRASH_STACK][\s\S]+)\[CRASH_REGISTERS]", re.M)
        content = stack_pattern.findall(dump)
        stack = content[0]
        # obtain bt_functions
        bt_pattern = re.compile(r"-\n[ ]*\d+:[ ](.+)[^-]+Source:[ ](.+):", re.M)
        bt_functions = bt_pattern.findall(stack)
        for func_tuple in bt_functions:
            function, path = list(func_tuple)
            # remove offset
            offset_pattern = re.compile(r"([ ]const)*[ ][+][ ]0x.+")
            function = re.sub(offset_pattern, "", function)
            result.append([function, path])
        return result

    def best_matched(self, path):
        """
        Obtain the best matched component from components collection.

        Args:
            path: The path of current header file.

        Returns:
            The best matched component.
        """
        matched = "UNKNOWN"
        client = pymongo.MongoClient(host=self.host, port=int(self.port))
        collection = client[self.db][self.coll]
        result = collection.find_one({"path": path})
        if result:
            matched = result["component"]
        else:
            while "/" in path:
                path = path[:path.rindex("/")]
                result = collection.find_one({"path": path})
                if result:
                    matched = result["component"]
                    break
        return matched

    def add_knowledge(self, processed):
        result = []
        component = ""
        functions = []
        for frame in processed:
            # obtain complete path and source
            if "/" in frame[1]:
                path = self.git_dir + "/" + frame[1]
                source = frame[1][frame[1].rindex("/")+1:]
            else:
                arguments = ["find", self.git_dir, "-name", frame[1]]
                pipe = subprocess.Popen(arguments, stdout=subprocess.PIPE, stdin=subprocess.PIPE)
                stdout, stderr = pipe.communicate()
                path = stdout.decode("utf-8")[:-1]
                source = frame[1]
            # obtain best matched component
            if source in self.stop_source:
                continue
            else:
                if "\n" in path:
                    cur_component = "UNKNOWN"
                else:
                    cur_component = self.best_matched(path)
            # demangle
            if frame[0].startswith("_Z"):
                arguments = ["c++filt", "-p", frame[0]]
                pipe = subprocess.Popen(arguments, stdout=subprocess.PIPE, stdin=subprocess.PIPE)
                stdout, stderr = pipe.communicate()
                frame[0] = stdout.decode("utf-8")[:-1]
            # merge several functions into a component
            if component == "" or cur_component == component:
                component = cur_component
                functions.append(frame[0])
            else:
                result.append([component, functions])
                component = cur_component
                functions = [frame[0]]
        result.append([component, functions])
        return result

    def calculate_sim(self, features, len_max):
        numerator = 0.0
        denominator = 0.0
        for pos, dist in features:
            numerator += math.exp(-self.m * pos) * math.exp(-self.n * dist)
        for i in range(len_max):
            denominator += math.exp(-self.m * i)
        similarity = numerator / denominator
        return similarity
