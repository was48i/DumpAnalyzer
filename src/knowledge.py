import configparser
import os
import subprocess

from pool import MongoConnection


class Knowledge(object):
    config = configparser.ConfigParser()
    config_path = os.path.join(os.getcwd(), "settings.ini")
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

    @staticmethod
    def execute_shell(arguments):
        pipe = subprocess.Popen(arguments, stdout=subprocess.PIPE, stdin=subprocess.PIPE)
        stdout, stderr = pipe.communicate()
        return stdout.decode("utf-8")[:-1]

    def complete_path(self, path):
        if "/" in path:
            file = path[path.rindex("/")+1:]
            path = self.git_dir + "/" + path
        else:
            file = path
            arguments = ["find", self.git_dir, "-name", path]
            path = self.execute_shell(arguments)
        return file, path

    def best_matched(self, path):
        matched = "UNKNOWN"
        with MongoConnection(self.host, self.port) as mongo:
            collection = mongo.connection[self.db][self.coll]
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
            function, path = frame
            file, path = self.complete_path(path)
            # obtain best matched component
            if file in self.stop_words:
                continue
            else:
                if "\n" in path:
                    cur_component = "UNKNOWN"
                else:
                    cur_component = self.best_matched(path)
            # demangle
            if function.startswith("_Z"):
                arguments = ["c++filt", "-p", function]
                function = self.execute_shell(arguments)
            # merge several functions into a component
            if component == "" or cur_component == component:
                component = cur_component
                functions.append(function)
            else:
                result.append([component, functions])
                component = cur_component
                functions = [function]
        result.append([component, functions])
        return result
