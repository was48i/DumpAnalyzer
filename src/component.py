import configparser
import glob
import os
import re
import subprocess

from pool import MongoConnection


class Component(object):
    """
    Obtain Component-File mapping based on the layered CMakeLists.txt.
    """
    config = configparser.ConfigParser()
    path = os.path.join(os.getcwd(), "config.ini")
    config.read(path)
    # Git
    git_url = config.get("git", "url")
    git_dir = config.get("git", "dir")
    # MongoDB
    host = config.get("mongodb", "host")
    port = config.getint("mongodb", "port")
    db = config.get("mongodb", "db")
    coll = config.get("mongodb", "coll_cpnt")

    @staticmethod
    def find_component(path):
        """
        Obtain parent/child components from a CMakeLists.txt path.

        Args:
            path: A CMakeLists.txt path.

        Returns:
            Parent and its children.
        """
        with open(path, "r") as fp:
            content = fp.read()
        parent_pattern = re.compile(r'SET_COMPONENT\("(.+)"\)', re.M)
        child_pattern = re.compile(r'SET_COMPONENT\("(.+)"\n([^)]+)\)', re.M)
        parent = parent_pattern.findall(content)
        children = child_pattern.findall(content)
        return parent + children

    @staticmethod
    def convert_path(components, prefix):
        """
        Obtain the file path for corresponding component.
        Args:
            components: Parent component or child component list.
            prefix: The current prefix of CMakeLists.txt.
        Returns:
            Component-File mapping.
        """
        result = dict()
        for cpnt in components:
            # convert parent component
            if isinstance(cpnt, str):
                result[prefix] = cpnt
                continue
            # convert child component
            if isinstance(cpnt, tuple):
                for item in [i.strip() for i in cpnt[1].split("\n") if i.strip()]:
                    path = prefix
                    for layer in item.split("/"):
                        path = os.path.join(path, layer)
                    # wild character
                    for wild in glob.iglob(path):
                        result[wild] = cpnt[0]
                continue
        return result

    def update_component(self):
        """
        Obtain Component-File mapping based on the layered CMakeLists.txt.
        """
        # update source code base
        if os.path.exists(self.git_dir):
            print("Removing from '{}'...".format(self.git_dir))
            cmd = "rm -fr {}".format(self.git_dir)
            subprocess.call(cmd.split(" "))
        cmd = "git clone --branch master --depth 1 {} {}".format(self.git_url, self.git_dir)
        subprocess.call(cmd.split(" "))
        component_map = dict()
        queue = [self.git_dir]
        # BFS
        while len(queue) > 0:
            prefix = queue.pop(0)
            cmk_path = os.path.join(prefix, "CMakeLists.txt")
            if os.path.exists(cmk_path):
                components = self.find_component(cmk_path)
                component_map.update(self.convert_path(components, prefix))
            for node in os.listdir(prefix):
                item = os.path.join(prefix, node)
                if os.path.isdir(item):
                    queue.append(item)
        # insert documents
        documents = []
        for key in component_map:
            data = dict()
            data["path"] = key
            data["component"] = component_map[key]
            documents.append(data)
        with MongoConnection(self.host, self.port) as mongo:
            collection = mongo.connection[self.db][self.coll]
            collection.drop()
            collection.insert_many(documents)
        print("Component-File mapping is successfully updated.")

    def best_matched(self, path):
        matched = "UNKNOWN"
        with MongoConnection(self.host, self.port) as mongo:
            collection = mongo.connection[self.db][self.coll]
            data = collection.find_one({"path": path})
            if not data:
                while "/" in path:
                    path = path[:path.rindex("/")]
                    data = collection.find_one({"path": path})
                    if data:
                        matched = data["component"]
                        break
            else:
                matched = data["component"]
        return matched

    def to_component(self, path):
        if "/" not in path:
            arguments = ["find", self.git_dir, "-name", path]
            pipe = subprocess.Popen(arguments, stdout=subprocess.PIPE, stdin=subprocess.PIPE)
            stdout, stderr = pipe.communicate()
            full_path = stdout.decode("utf-8")[:-1]
        else:
            full_path = "{}/{}".format(self.git_dir, path)
        if "\n" not in full_path:
            return self.best_matched(full_path)
        else:
            return "UNKNOWN"
