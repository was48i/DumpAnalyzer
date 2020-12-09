import configparser
import os

from functools import reduce


class Log(object):
    """
    Print a few messages for the specific feature.
    """
    config = configparser.ConfigParser()
    config_path = os.path.join(os.getcwd(), "settings.ini")
    config.read(config_path)
    # Log
    width = config.getint("log", "width")
    # Model
    m = config.getfloat("model", "m")
    n = config.getfloat("model", "n")

    def dump_print(self, message):
        print("\n", end="")
        dump_x, dump_y = message
        len_left = reduce((lambda x, y: x + y), [len(i[1]) + 1 for i in dump_x])
        len_right = reduce((lambda x, y: x + y), [len(i[1]) + 1 for i in dump_y])
        len_max = max(len_left, len_right)
        # align the dump length
        if len_left < len_max:
            dump_x = dump_x + [["", []]] * (len_max - len_left)
        if len_right < len_max:
            dump_y = dump_y + [["", []]] * (len_max - len_right)
        # print the left part
        for msg in dump_x:
            component, functions = msg
            if component != "":
                print("\x1b[0;36m" + component + "\x1b[0m")
                for func in functions:
                    print(func[:self.width])
            else:
                print("")
        # print the right part
        print("\x1b[{}A".format(len_max), end="")
        for msg in dump_y:
            component, functions = msg
            if component != "":
                print("\x1b[{}C".format(self.width + 2), end="")
                print("|  " + "\x1b[0;36m" + component + "\x1b[0m")
                for func in functions:
                    print("\x1b[{}C".format(self.width + 2), end="")
                    print("|  " + func[:self.width])
            else:
                print("\x1b[{}C".format(self.width + 2), end="")
                print("|  ")

    def formula_print(self, features, len_max, sim):
        print("\n", end="")
        numerator = ""
        denominator = ""
        # obtain numerator
        for pos, dist in features:
            numerator += "e^-{}*{}*".format(self.m, pos) + "e^-%.1f*%.4f + " % (self.n, dist)
        numerator = numerator[:-3]
        # obtain denominator
        for i in range(len_max):
            denominator += "e^-{}*{} + ".format(self.m, i)
        denominator = denominator[:-3]
        print("             " + numerator)
        print("Similarity = {} = {:.2%}".format("-" * len(numerator), sim))
        print("             " + denominator)
