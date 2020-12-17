import knowledge
import logger

from calculate import Calculate
from functools import reduce
from process import Process
from train import Train


class Detect(object):
    """
    Detect crash dump similarity through the mathematical model.
    """
    def __init__(self, paths):
        self.dump_paths = paths

    def detect_sim(self):
        message = []
        cursor_up = 0
        order_pair = []
        block_pair = []
        for path in self.dump_paths:
            with open(path, "r", encoding="utf-8") as fp:
                dump = fp.read()
            processed = Process(dump).pre_process()
            kdetector = knowledge.Knowledge(processed)
            sequence = kdetector.merge_function()
            cpnt_order, func_block = kdetector.add_knowledge()
            # align the dump length
            length = reduce((lambda x, y: x + y), [len(i[1]) + 1 for i in sequence])
            if cursor_up == 0:
                cursor_up = length
            if length < cursor_up:
                sequence = sequence + [["", []]] * (cursor_up - length)
            message.append(sequence)
            order_pair.append(cpnt_order)
            block_pair.append(func_block)
        # output dump comparison
        printer = logger.Logger()
        features = Train().obtain_feature(order_pair, block_pair)
        len_max = len(max(order_pair, key=len))
        sim = Calculate(features, len_max).calculate_sim()
        printer.dump_print(message, cursor_up)
        printer.formula_print(features, len_max, sim)
