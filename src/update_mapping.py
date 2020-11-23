import configparser
import glob
import json
import os
import re
import subprocess

from clang.cindex import Config
from clang.cindex import Index
from multiprocessing import Pool


class UpdateMapping(object):
    """
    Use CMake + Clang to achieve the conversion from function to component.
    """
    def __init__(self):
        # clone source code
        config = configparser.ConfigParser()
        path = os.path.join(os.getcwd(), "settings.ini")
        config.read(path)
        git_url = config.get("URL", "git_url")
        cmd = "git clone --branch master --depth 1 " + git_url + " temp"
        subprocess.call(cmd.split(" "))
        # load libclang.so
        lib_path = "/usr/lib"
        if not Config.loaded:
            Config.set_library_path(lib_path)

    @staticmethod
    def find_component(path):
        """
        Obtain parent/child components from a CMakeLists.txt.

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

    @staticmethod
    def dump_component(mapping):
        """
        Dump component mapping to JSON format.
        """
        dump_path = os.path.join(os.getcwd(), "json", "components.json")
        with open(dump_path, "w") as fp:
            json.dump(mapping, fp, indent=4, sort_keys=True)

    def update_component(self):
        """
        Obtain Component-File mapping based on the layered CMakeLists.txt.
        """
        component_mapping = dict()
        queue = ["temp"]
        # BFS
        while len(queue) > 0:
            prefix = queue.pop(0)
            cmk_path = os.path.join(prefix, "CMakeLists.txt")
            if os.path.exists(cmk_path):
                components = self.find_component(cmk_path)
                component_mapping.update(self.convert_path(components, prefix))
            for node in os.listdir(prefix):
                item = os.path.join(prefix, node)
                if os.path.isdir(item):
                    queue.append(item)
        # create a directory if not exist
        json_path = os.path.join(os.getcwd(), "json")
        if not os.path.exists(json_path):
            os.makedirs(json_path)
        self.dump_component(component_mapping)

    @staticmethod
    def get_header(dir_path):
        """
        Obtain all header files in the current directory.

        Args:
            dir_path: The dictionary to be processed.

        Returns:
            All header files in the directory.
        """
        headers = []
        stack = [dir_path]
        # DFS
        while len(stack) > 0:
            prefix = stack.pop(len(stack) - 1)
            for node in os.listdir(prefix):
                cur_path = os.path.join(prefix, node)
                extension = os.path.splitext(cur_path)[-1]
                if not os.path.isdir(cur_path):
                    if extension in [".h", ".hpp"]:
                        headers.append(cur_path)
                else:
                    stack.append(cur_path)
        return headers

    @staticmethod
    def load_component():
        """
        Load component JSON to mapping.
        """
        load_path = os.path.join(os.getcwd(), "json", "components.json")
        with open(load_path, "r") as fp:
            component_mapping = json.load(fp)
        return component_mapping

    def best_matched(self, path):
        """
        Obtain the best matched component.

        Args:
            path: The path of current header file.

        Returns:
            The best matched component.
        """
        result = "UNKNOWN"
        components = self.load_component()
        if path in components:
            result = components[path]
        else:
            while "/" in path:
                path = path[:path.rindex("/")]
                if path in components:
                    result = components[path]
                    break
        return result

    def fully_qualified(self, node, path):
        """
        Obtain fully qualified name recursively.

        Args:
            node: A node in abstract syntax tree.
            path: The path of current header file.

        Returns:
            The fully qualified name that belongs to the node.
        """
        if node.location.file is None:
            return ""
        elif node.location.file.name != path:
            return ""
        else:
            res = self.fully_qualified(node.semantic_parent, path)
            if res != "":
                return res + "::" + node.spelling
        return node.spelling

    @staticmethod
    def dump_function(mapping):
        """
        Dump function mapping to JSON format.
        """
        dump_path = os.path.join(os.getcwd(), "json", "functions.json")
        with open(dump_path, "w") as fp:
            json.dump(mapping, fp, indent=4, sort_keys=True)

    def find_function(self, file):
        """
        Obtain all fully qualified names in the current header file.

        Args:
            file: The path of current header file.

        Returns:
            All fully qualified names in the header file.
        """
        result = dict()
        index = Index.create()
        cpnt = self.best_matched(file)
        # remove it when include dependencies resolved
        header = os.path.join("temp", "rte", "rtebase", "include")
        args_list = [
            "-x", "c++",
            "-I" + "temp", "-I" + header
        ]
        tu = index.parse(file, args_list)
        decl_kinds = [
            "FUNCTION_DECL",
            "CXX_METHOD",
            "CONSTRUCTOR",
            "DESTRUCTOR",
            "CONVERSION_FUNCTION"
        ]
        for node in tu.cursor.walk_preorder():
            if node.location.file is not None and node.location.file.name == file and node.spelling:
                kind = str(node.kind)[str(node.kind).index('.')+1:]
                if kind in decl_kinds:
                    key = self.fully_qualified(node, file)
                    result[key] = cpnt
        return result

    def multi_process(self, files):
        """
        Use multi-process to parse functions in the header file.

        Args:
            files: All header files in the source code.

        Returns:
            Function parsing result in the source code.
        """
        result = dict()
        # using multi-process
        pool = Pool(40)
        functions = pool.map(self.find_function, files)
        pool.close()
        pool.join()
        for func in [i for i in functions if i]:
            for k in func.keys():
                key = k
                # handle anonymous namespace
                while "::::" in key:
                    key = key.replace("::::", "::")
                # remove special characters
                if re.search(r"[^0-9a-zA-Z:_~]", key):
                    point = re.search(r"[^0-9a-zA-Z:_~]", key).span()[0]
                    key = key[:point]
                result[key] = func[k]
        return result

    def update_function(self):
        """
        Obtain File-Function mapping through Python bindings for Clang and complete the conversion.
        """
        function_mapping = dict()
        for node in os.listdir("temp"):
            cur_path = os.path.join("temp", node)
            if os.path.isdir(cur_path):
                print(cur_path)
                # update functions by directory
                headers = self.get_header(cur_path)
                if headers:
                    function_mapping.update(self.multi_process(headers))
        self.dump_function(function_mapping)

    def update_mapping(self):
        """
        Combine update_component and update_function and remove temporary source code.
        """
        self.update_component()
        self.update_function()
        # remove source code
        print("Removing from 'temp'...")
        cmd = "rm -fr temp"
        subprocess.call(cmd.split(" "))
