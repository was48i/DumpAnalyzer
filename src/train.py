import configparser
import os

from calculate import Calculate
from numpy import arange, array
from pool import MongoConnection
from sklearn.metrics import roc_curve, auc
from utils import DP


class Train(object):
    config = configparser.ConfigParser()
    path = os.path.join(os.getcwd(), "settings.ini")
    config.read(path)
    # MongoDB
    host = config.get("mongodb", "host")
    port = config.getint("mongodb", "port")
    db = config.get("mongodb", "db")
    coll = config.get("mongodb", "coll_data")

    def __init__(self, dataset):
        self.dataset = dataset

    @staticmethod
    def obtain_feature(order_pair, block_pair):
        positions = []
        distances = []
        order_x, order_y = order_pair
        # top first
        len_x, len_y = len(order_x), len(order_y)
        if len_x > len_y:
            indices = DP().lcs_index(order_x[::-1], order_y[::-1])
        else:
            indices = DP().lcs_index(order_x[::-1], order_y[::-1])
        # TODO: need to improve
        index_x, index_y = indices
        position_x = [len_x - i - 1 for i in index_x]
        position_y = [len_y - i - 1 for i in index_y]
        for i, j in zip(position_x, position_y):
            positions.append(max(i, j))
            distances.append(DP().normalized_dist(block_pair[0][i], block_pair[1][j]))
        return list(zip(positions, distances))

    def training(self):
        m_opt = 0.0
        n_opt = 0.0
        auc_max = 0.0
        for m in arange(0.0, 2.1, 0.1):
            for n in arange(0.0, 2.1, 0.1):
                true_label = []
                pred_score = []
                for label, samples in enumerate(self.dataset):
                    for sample in samples:
                        true_label.append(label)
                        with MongoConnection(self.host, self.port) as mongo:
                            collection = mongo.connection[self.db][self.coll]
                            source = collection.find_one({"test_id": sample[0]})
                            target = collection.find_one({"test_id": sample[1]})
                            order_pair = [source["cpnt_order"], target["cpnt_order"]]
                            block_pair = [source["func_block"], target["func_block"]]
                        features = self.obtain_feature(order_pair, block_pair)
                        len_max = len(max(order_pair, key=len))
                        sim = Calculate(features, len_max).calculate_sim()
                        pred_score.append(sim)
                true_label = array(true_label)
                pred_score = array(pred_score)
                fpr, tpr, _ = roc_curve(true_label, pred_score)
                roc_auc = auc(fpr, tpr)
                print("m=%.1f, n=%.1f, AUC=%.3f" % (m, n, roc_auc))
                if roc_auc > auc_max:
                    auc_max = roc_auc
                    m_opt = m
                    n_opt = n
        print(m_opt)
        print(n_opt)
