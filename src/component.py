from utils import *


class Component(object):
    """
    Obtain Component-File mapping based on the layered CMakeLists.txt.
    """
    config = configparser.ConfigParser()
    path = os.path.join(os.getcwd(), "settings.ini")
    config.read(path)
    # Git
    url = config.get("git", "url")
    directory = config.get("git", "dir")
    # MongoDB
    host = config.get("mongodb", "host")
    port = config.get("mongodb", "port")
    database = config.get("mongodb", "db")
    collection = config.get("mongodb", "coll_cpnt")

    def __init__(self):
        # clone source code
        cmd = "git clone --branch master --depth 1 {} {}".format(self.url, self.directory)
        subprocess.call(cmd.split(" "))

    def update_component(self):
        """
        Obtain Component-File mapping based on the layered CMakeLists.txt.
        """
        component_mapping = dict()
        queue = [self.directory]
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
        # insert documents
        client = pymongo.MongoClient(host=self.host, port=int(self.port))
        collection = client[self.database][self.collection]
        collection.drop()
        documents = []
        for key in component_mapping:
            data = dict()
            data["path"] = key
            data["component"] = component_mapping[key]
            documents.append(data)
        collection.insert_many(documents)
