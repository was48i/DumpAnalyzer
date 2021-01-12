import configparser
import glob
import os
import re
import subprocess

from pool import MongoConnection


class Component:
    """
    Obtain Component-File mapping based on the layered CMakeLists.txt.
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
    git_url = config.get("git", "url")
    git_dir = config.get("git", "dir")

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
            # convert parent component
            if isinstance(cpnt, str):
                result[prefix] = cpnt
        return result

    def update_component(self):
        """
        Obtain Component-File mapping based on the layered CMakeLists.txt and load into database.
        """
        # update source code base
        if os.path.exists(self.git_dir):
            print("Removing from '{}'...".format(self.git_dir))
            cmd = "rm -fr {}".format(self.git_dir)
            subprocess.call(cmd.split(" "))
            print("\x1b[32mSuccessfully removed code base.\x1b[0m")
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
        for key in component_map.keys():
            data = dict()
            data["path"] = key
            data["component"] = component_map[key]
            documents.append(data)
        with MongoConnection(self.host, self.port) as mongo:
            collection = mongo.connection[self.db][self.coll]
            collection.drop()
            collection.insert_many(documents)
        print("\x1b[32mSuccessfully updated Component-File mapping ({}).\x1b[0m".format(len(documents)))

    def best_matched(self, path):
        """
        Query the components collection to obtain the best matched component.
        Args:
            path: A complete path is the stack frame.
        Returns:
            matched: The best matched component.
        """
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
        """
        Verify the validity of path and obtain the matched component.
        Args:
            path: A path in the stack frame.
        Returns:
            matched: A matched component.
        """
        if re.search(r"[^/0-9a-zA-Z._]", path):
            return "UNKNOWN"
        if "/" not in path:
            arguments = ["find", self.git_dir, "-name", path]
            pipe = subprocess.Popen(arguments, stdout=subprocess.PIPE, stdin=subprocess.PIPE)
            stdout, _ = pipe.communicate()
            full_path = stdout.decode("utf-8")[:-1]
        else:
            full_path = "{}/{}".format(self.git_dir, path)
        if not full_path or "\n" in full_path:
            return "UNKNOWN"
        else:
            return self.best_matched(full_path)
