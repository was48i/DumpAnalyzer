from calculate import Calculate
from etl import ETL
from log import Log
from knowledge import Knowledge
from process import Process


class Detect:
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
        order_pair, block_pair = [], []
        for test_id in self.test_ids:
            dump = ETL().extract_cdb(test_id)
            processed = Process(dump).internal_process()
            cpnt_order, func_block = Knowledge(processed).add_knowledge()
            message.extend([cpnt_order, func_block])
            order_pair.append(cpnt_order)
            block_pair.append(func_block)
        # output dump comparison
        Log().dump_print(message)
        Calculate(order_pair, block_pair).calculate_sim(debug=True)
