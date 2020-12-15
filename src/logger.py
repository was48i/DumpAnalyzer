import configparser
import os


class Logger(object):
    """
    Print a few messages for the specific feature.
    """
    config = configparser.ConfigParser()
    config_path = os.path.join(os.getcwd(), "config.ini")
    config.read(config_path)
    # Log
    width = config.getint("log", "width")
    # Model
    m = config.getfloat("model", "m")
    n = config.getfloat("model", "n")

    def dump_print(self, message, cursor_up):
        print("\n", end="")
        # print the left part
        for msg in message[0]:
            component, functions = msg
            print("\x1b[0;36m" + component + "\x1b[0m")
            for func in functions:
                print(func[:self.width])
        # print the right part
        print("\x1b[{}A".format(cursor_up), end="")
        for msg in message[1]:
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
        if features:
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
        else:
            print("Similarity = 0.00%")
