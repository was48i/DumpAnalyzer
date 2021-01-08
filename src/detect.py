import calculate
import log

from etl import ETL
from knowledge import Knowledge
from process import Process


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
        order_pair, block_pair = [], []
        for test_id in self.test_ids:
            dump = ETL().extract_cdb(test_id)
            processed = Process(dump).internal_process()
            cpnt_order, func_block = Knowledge(processed).add_knowledge()
            order_pair.append(cpnt_order)
            block_pair.append(func_block)
        # output dump comparison
        printer = log.Log()
        calculator = calculate.Calculate(order_pair, block_pair)
        features, len_max, sim = calculator.obtain_feature(), len(max(order_pair, key=len)), calculator.calculate_sim()
        printer.dump_print([order_pair[0], block_pair[0], order_pair[1], block_pair[1]])
        printer.formula_print(features, len_max, sim)
