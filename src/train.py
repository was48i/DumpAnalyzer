import configparser
import os

from calculate import Calculate
from component import Component
from etl import ETL
from numpy import arange, array
from pool import MongoConnection
from sample import Sample
from sklearn.metrics import roc_curve, auc
from utils import DP


class Train(object):
    config = configparser.ConfigParser()
    path = os.path.join(os.getcwd(), "config.ini")
    config.read(path)
    # MongoDB
    host = config.get("mongodb", "host")
    port = config.getint("mongodb", "port")
    db = config.get("mongodb", "db")
    coll = config.get("mongodb", "coll_data")

    @staticmethod
    def obtain_feature(order_pair, block_pair):
        positions = []
        distances = []
        order_x, order_y = order_pair
        # top first
        pos_x, pos_y = DP().lcs_position(order_x[::-1], order_y[::-1])
        for i, j in zip(pos_x, pos_y):
            positions.append(max(i, j))
            distances.append(DP().normalized_dist(block_pair[0][i], block_pair[1][j]))
        return list(zip(positions, distances))

    def predict_score(self, sample, m, n):
        with MongoConnection(self.host, self.port) as mongo:
            collection = mongo.connection[self.db][self.coll]
            source = collection.find_one({"test_id": sample[0]})
            target = collection.find_one({"test_id": sample[1]})
            order_pair = [source["cpnt_order"], target["cpnt_order"]]
            block_pair = [source["func_block"], target["func_block"]]
        features = self.obtain_feature(order_pair, block_pair)
        len_max = len(max(order_pair, key=len))
        score = Calculate(features, len_max).calculate_sim(m, n)
        return score

    def training(self):
        m_opt = 0.0
        n_opt = 0.0
        auc_max = 0.0
        # knowledge updating
        Component().update_component()
        # dump crawling
        ETL().load()
        # data sampling
        dataset = Sample().sample_data()
        print("Start parameter tuning...\n")
        for m in arange(0.0, 2.1, 0.1):
            for n in arange(0.0, 2.1, 0.1):
                true_label = []
                pred_score = []
                for label, samples in enumerate(dataset):
                    for sample in samples:
                        true_label.append(label)
                        pred_score.append(self.predict_score(sample, m, n))
                true_label = array(true_label)
                pred_score = array(pred_score)
                fpr, tpr, _ = roc_curve(true_label, pred_score)
                roc_auc = auc(fpr, tpr)
                print("m=%.1f, n=%.1f, AUC=%.3f" % (m, n, roc_auc))
                if roc_auc > auc_max:
                    auc_max = roc_auc
                    m_opt = m
                    n_opt = n
        print("{:.1}".format(m_opt))
        print("{:.1}".format(n_opt))
