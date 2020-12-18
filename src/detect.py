import logger

from calculate import Calculate
from etl import ETL
from functools import reduce
from knowledge import Knowledge
from process import Process
from train import Train


class Detect(object):
    """
    Detect crash dump similarity through the mathematical model.
    Attributes:
        test_ids: A pair of test IDs that has crash failures.
    """
    def __init__(self, ids):
        self.test_ids = ids

    def detect_sim(self):
        """
        Detect crash dump similarity and output the comparison result.
        """
        message = []
        order_pair = []
        block_pair = []
        for test_id in self.test_ids:
            dump = ETL().extract_cdb(test_id)
            processed = Process(dump).internal_process()
            cpnt_order, func_block = Knowledge(processed).add_knowledge()
            message.extend([cpnt_order, func_block])
            order_pair.append(cpnt_order)
            block_pair.append(func_block)
        # output dump comparison
        printer = logger.Logger()
        features = Train().obtain_feature(order_pair, block_pair)
        len_max = len(max(order_pair, key=len))
        sim = Calculate(features, len_max).calculate_sim()
        printer.dump_print(message)
        printer.formula_print(features, len_max, sim)
