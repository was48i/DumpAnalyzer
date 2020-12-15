from calculate import Calculate
from functools import reduce
from knowledge import Knowledge
from logger import Logger
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
            sequence = Knowledge(processed).merge_function()
            # align the dump length
            length = reduce((lambda x, y: x + y), [len(i[1]) + 1 for i in sequence])
            if cursor_up == 0:
                cursor_up = length
            if length < cursor_up:
                sequence = sequence + [["", []]] * (cursor_up - length)
            message.append(sequence)
            cpnt_order, func_block = Knowledge(processed).add_knowledge()
            order_pair.append(cpnt_order)
            block_pair.append(func_block)
        # output dump comparison
        Logger().dump_print(message, cursor_up)
        features = Train().obtain_feature(order_pair, block_pair)
        len_max = len(max(order_pair, key=len))
        sim = Calculate(features, len_max).calculate_sim()
        Logger().formula_print(features, len_max, sim)
