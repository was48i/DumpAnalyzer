from calculate import Calculate
from etl import ETL
from knowledge import Knowledge
from log import Log
from process import Process
from utils import DP


class Detect(object):
    """
    Detect crash dump similarity through the mathematical model.
    """
    def __init__(self, paths):
        self.dump_paths = paths

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

    def detect_sim(self):
        message = []
        order_pair = []
        block_pair = []
        for path in self.dump_paths:
            with open(path, "r", encoding="ISO-8859-1") as fp:
                dump = fp.read()
            processed = Process(dump).pre_process()
            sequence = Knowledge().add_knowledge(processed)
            message.append(sequence)
            cpnt_order, func_block = ETL().serialize(sequence)
            order_pair.append(cpnt_order)
            block_pair.append(func_block)
        # output dump comparison
        Log().dump_print(message)
        features = self.obtain_feature(order_pair, block_pair)
        len_max = len(max(order_pair, key=len))
        sim = Calculate(features, len_max).calculate_sim()
        Log().formula_print(features, len_max, sim)
