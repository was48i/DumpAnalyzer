import configparser
import pymongo

from clang.cindex import Index
from clang.cindex import Config
from multiprocessing import Pool
from utils import *


class Function(object):
    """
     Obtain File-Function mapping through Python bindings for Clang.
    """
    config = configparser.ConfigParser()
    path = os.path.join(os.getcwd(), "settings.ini")
    config.read(path)
    # Git
    directory = config.get("git", "dir")
    # Mongo
    host = config.get("mongo", "host")
    port = config.get("mongo", "port")
    database = config.get("mongo", "db")
    collection = config.get("mongo", "coll_func")

    def __init__(self):
        # load libclang.so
        lib_path = "/usr/local/lib"
        if not Config.loaded:
            Config.set_library_path(lib_path)

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
        collection = client[self.database][self.collection]
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

    def find_function(self, path):
        """
        Obtain all fully qualified names from the current header file.

        Args:
            path: The path of current header file.

        Returns:
            All fully qualified names in the header file.
        """
        result = dict()
        index = Index.create()
        cpnt = self.best_matched(path)
        # remove it when include dependencies resolved
        header = os.path.join(self.directory, "rte", "rtebase", "include")
        args_list = ["-x", "c++", "-I" + self.directory, "-I" + header]
        tu = index.parse(path, args_list)
        decl_kinds = ["FUNCTION_DECL", "CXX_METHOD", "CONSTRUCTOR", "DESTRUCTOR", "CONVERSION_FUNCTION"]
        for node in tu.cursor.walk_preorder():
            if node.location.file is not None and node.location.file.name == path and node.spelling:
                kind = str(node.kind)[str(node.kind).index('.')+1:]
                if kind in decl_kinds:
                    key = fully_qualified(node, path)
                    result[key] = cpnt
        return result

    def multi_process(self, paths):
        """
        Use multi-process to parse functions in the header file.

        Args:
            paths: All header file's paths in the code base.

        Returns:
            Function parsing result from the code base.
        """
        result = dict()
        # using multi-process
        pool = Pool(40)
        functions = pool.map(self.find_function, paths)
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
        for node in os.listdir(self.directory):
            cur_path = os.path.join(self.directory, node)
            if os.path.isdir(cur_path):
                print(cur_path)
                # update functions by directory
                headers = header_path(cur_path)
                if headers:
                    function_mapping.update(self.multi_process(headers))
        # insert documents
        client = pymongo.MongoClient(host=self.host, port=int(self.port))
        collection = client[self.database][self.collection]
        collection.drop()
        documents = []
        for key in function_mapping:
            data = dict()
            data["function"] = key
            data["component"] = function_mapping[key]
            documents.append(data)
        collection.insert_many(documents)
        # remove source code
        print("Removing from '{}'...".format(self.directory))
        cmd = "rm -fr {}".format(self.directory)
        subprocess.call(cmd.split(" "))
