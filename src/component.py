import configparser
import subprocess

from utils import *


class Component(object):
    """
    Obtain Component-File mapping based on the layered CMakeLists.txt.
    """
    config = configparser.ConfigParser()
    path = os.path.join(os.getcwd(), "settings.ini")
    config.read(path)
    git_url = config.get("git", "url")
    git_directory = config.get("git", "directory")

    def __init__(self):
        # clone source code
        cmd = "git clone --branch master --depth 1 {} {}".format(self.git_url, self.git_directory)
        subprocess.call(cmd.split(" "))

    def update_component(self):
        """
        Obtain Component-File mapping based on the layered CMakeLists.txt.
        """
        component_mapping = dict()
        queue = [self.git_directory]
        # BFS
        while len(queue) > 0:
            prefix = queue.pop(0)
            cmk_path = os.path.join(prefix, "CMakeLists.txt")
            if os.path.exists(cmk_path):
                components = find_component(cmk_path)
                component_mapping.update(convert_path(components, prefix))
            for node in os.listdir(prefix):
                item = os.path.join(prefix, node)
                if os.path.isdir(item):
                    queue.append(item)
        # create a directory if not exist
        json_path = os.path.join(os.getcwd(), "json")
        if not os.path.exists(json_path):
            os.makedirs(json_path)
        dump_component(component_mapping)
