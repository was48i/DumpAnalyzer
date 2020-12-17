import configparser
import difflib
import os


class Logger(object):
    """
    Print a few messages for the specific feature.
    """
    config = configparser.ConfigParser()
    config_path = os.path.join(os.getcwd(), "config.ini")
    config.read(config_path)
    # Model
    m = config.getfloat("model", "m")
    n = config.getfloat("model", "n")
    # Log
    width = config.getint("log", "width")

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
            print("Similarity = {} = {:.2%}".format("-" * max(len(numerator), len(denominator)), sim))
            print("             " + denominator)
        else:
            print("Similarity = 0.00%")

    @staticmethod
    def diff_print(message, paths):
        print("\n", end="")
        diff = difflib.unified_diff(message[0].split("\n"), message[1].split("\n"),
                                    fromfile=os.path.basename(paths[0]), tofile=os.path.basename(paths[1]),
                                    lineterm="")
        for line in diff:
            if line.startswith("---") or line.startswith("+++"):
                print("\x1b[1m" + line + "\x1b[0m")
            elif line.startswith("-"):
                print("\x1b[0;31m" + line + "\x1b[0m")
            elif line.startswith("+"):
                print("\x1b[0;32m" + line + "\x1b[0m")
            elif line.startswith("@@"):
                print("\x1b[0;36m" + line + "\x1b[0m")
            else:
                print(line)
        # handle the same situation
        if message[0] == message[1]:
            for line in message[0].split("\n"):
                print(line)
