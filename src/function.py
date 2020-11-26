import configparser
import subprocess

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
    git_directory = config.get("git", "directory")

    def __init__(self):
        # load libclang.so
        lib_path = "/usr/local/lib"
        if not Config.loaded:
            Config.set_library_path(lib_path)

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
        cpnt = best_matched(file)
        # remove it when include dependencies resolved
        header = os.path.join(self.git_directory, "rte", "rtebase", "include")
        args_list = ["-x", "c++", "-I" + self.git_directory, "-I" + header]
        tu = index.parse(file, args_list)
        decl_kinds = ["FUNCTION_DECL", "CXX_METHOD", "CONSTRUCTOR", "DESTRUCTOR", "CONVERSION_FUNCTION"]
        for node in tu.cursor.walk_preorder():
            if node.location.file is not None and node.location.file.name == file and node.spelling:
                kind = str(node.kind)[str(node.kind).index('.')+1:]
                if kind in decl_kinds:
                    key = fully_qualified(node, file)
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
        for node in os.listdir(self.git_directory):
            cur_path = os.path.join(self.git_directory, node)
            if os.path.isdir(cur_path):
                print(cur_path)
                # update functions by directory
                headers = get_header(cur_path)
                if headers:
                    function_mapping.update(self.multi_process(headers))
        dump_function(function_mapping)
        # remove source code
        print("Removing from '{}'...".format(self.git_directory))
        cmd = "rm -fr {}".format(self.git_directory)
        subprocess.call(cmd.split(" "))
