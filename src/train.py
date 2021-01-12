import configparser
import os

from calculate import Calculate
from numpy import arange, array
from pool import MongoConnection
from sample import Sample
from sklearn.metrics import roc_curve, auc


class Train(object):
    """
    Training for parameter tuning which contains data sampling.
    Attributes:
        dataset: The sampled dataset.
    """
    config = configparser.ConfigParser()
    config_path = os.path.join(os.getcwd(), "config.ini")
    config.read(config_path)
    # MongoDB
    host = config.get("mongodb", "host")
    port = config.getint("mongodb", "port")
    db = config.get("mongodb", "db")
    coll = config.get("mongodb", "coll_data")

    def __init__(self):
        self.dataset = Sample().sample_data()

    def predict_score(self, sample, m, n):
        """
        Calculate the predicted score for each sample.
        Args:
            sample: A sample in the dataset.
            m: The parameter for component position.
            n: The parameter for component distance.
        Returns:
            score: The predicted score.
        """
        with MongoConnection(self.host, self.port) as mongo:
            collection = mongo.connection[self.db][self.coll]
            source = collection.find_one({"test_id": sample[0]})
            target = collection.find_one({"test_id": sample[1]})
            order_pair = [source["cpnt_order"], target["cpnt_order"]]
            block_pair = [source["func_block"], target["func_block"]]
        score = Calculate(order_pair, block_pair).calculate_sim(m, n)
        return score

    def draw_curve(self, m, n):
        """
        Obtain basic information for curve drawing.
        Args:
            m: The parameter for component position.
            n: The parameter for component distance.
        Returns:
            The basic information such as fpr, tpr, threshold, ...
        """
        true_label = []
        pred_score = []
        for label, samples in enumerate(self.dataset):
            for sample in samples:
                score = self.predict_score(sample, m, n)
                true_label.append(label)
                pred_score.append(score)
        true_label = array(true_label)
        pred_score = array(pred_score)
        return roc_curve(true_label, pred_score)

    def debugging(self):
        """
        Output debugging information of training.
        """
        threshold = 0.0000
        # obtain optimized parameters
        m = self.config.getfloat("model", "m")
        n = self.config.getfloat("model", "n")
        fpr_list, _, threshold_list = self.draw_curve(m, n)
        for i, fpr in enumerate(fpr_list):
            if fpr > 0:
                threshold = threshold_list[i]
                print("Threshold={:.2%}".format(threshold))
                break
        for label, samples in enumerate(self.dataset):
            for sample in samples:
                score = self.predict_score(sample, m, n)
                if label == 0 and score >= threshold:
                    print("FP: {} {}".format(sample[0], sample[1]))
                if label == 1 and score < threshold:
                    print("FN: {} {}".format(sample[0], sample[1]))

    def training(self):
        """
        Training for parameter tuning which contains data sampling.
        """
        m_opt = 0.0
        n_opt = 0.0
        auc_max = 0.0
        print("Start parameter tuning...")
        for m in arange(0.0, 2.1, 0.1):
            for n in arange(0.0, 2.1, 0.1):
                fpr, tpr, _ = self.draw_curve(m, n)
                roc_auc = auc(fpr, tpr)
                print("m=%.1f, n=%.1f, AUC=%.3f" % (m, n, roc_auc))
                if roc_auc > auc_max:
                    m_opt = m
                    n_opt = n
                    auc_max = roc_auc
        print("\x1b[32mm_opt=%.1f, n_opt=%.1f, AUC_MAX=%.3f\x1b[0m" % (m_opt, n_opt, auc_max))
        # update model parameters
        self.config.set("model", "m", "%.1f" % m_opt)
        self.config.set("model", "n", "%.1f" % n_opt)
        self.config.write(open(self.config_path, "w"))
        self.debugging()
