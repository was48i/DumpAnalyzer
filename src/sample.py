import bugzilla
import configparser
import os

from pool import MongoConnection
from itertools import combinations
from random import sample
from utils import UnionFind


class Sample(object):
    config = configparser.ConfigParser()
    path = os.path.join(os.getcwd(), "config.ini")
    config.read(path)
    # MongoDB
    host = config.get("mongodb", "host")
    port = config.getint("mongodb", "port")
    db = config.get("mongodb", "db")
    coll = config.get("mongodb", "coll_data")
    # Bugzilla
    url = config.get("bugzilla", "url")
    key = config.get("bugzilla", "key")

    def bug_map(self):
        bug_map = dict()
        # obtain bug_id/test_id mapping
        with MongoConnection(self.host, self.port) as mongo:
            collection = mongo.connection[self.db][self.coll]
            dataset = collection.find()
        for data in dataset:
            bug_id, test_id = data["bug_id"], data["test_id"]
            if bug_id not in bug_map:
                bug_map[bug_id] = [test_id]
            else:
                bug_map[bug_id].append(test_id)
        return bug_map

    def union_map(self, bug_list):
        # obtain bug_id/group_id mapping
        pairs = []
        bzapi = bugzilla.Bugzilla(self.url, api_key=self.key, sslverify=False)
        for bug_id in bug_list:
            bug = bzapi.getbug(bug_id)
            if bug.dupe_of and bug.dupe_of in bug_list:
                pairs.append([bug_id, bug.dupe_of])
        uf = UnionFind(len(bug_list))
        for pair in pairs:
            uf.unite(bug_list.index(pair[0]), bug_list.index(pair[1]))
        uf.id = [uf.find(i) for i in uf.id]
        union_map = dict(zip(bug_list, uf.id))
        return union_map

    def group_data(self):
        groups = []
        bug_map = self.bug_map()
        union_map = self.union_map(list(bug_map))
        # test_id grouping
        for union_id in set(union_map.values()):
            group = []
            for k, v in union_map.items():
                if v == union_id:
                    group.extend(bug_map[k])
            if len(group) > 1:
                groups.append(group)
        return groups

    def sample_data(self):
        print("Start data sampling...\n")
        positives = []
        negatives = []
        groups = self.group_data()
        for group in groups:
            positives.extend(list(combinations(group, 2)))
        while True:
            group_x, group_y = sample(groups, 2)
            negatives.append((sample(group_x, 1)[0], sample(group_y, 1)[0]))
            if len(negatives) == len(positives):
                break
        print("There are {} negative samples and {} positive samples.\n".format(len(negatives), len(positives)))
        return [negatives, positives]
