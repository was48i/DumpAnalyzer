import configparser
import difflib
import os
import textwrap


class Log(object):
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

    def dump_print(self, message):
        """
        Print a pair of crash dumps in comparison way.
        Args:
            message: Crash dump message to be printed.
        """
        print("\n", end="")
        # print the left part
        cursor_up = 0
        for index in range(len(message[0])):
            blocks = textwrap.fill(" ".join(message[1][index]), width=self.width)
            cursor_up += len(blocks.split("\n")) + 1
            print("\x1b[0;36m{}\x1b[0m".format(message[0][index]))
            print(blocks)
        print("\x1b[{}A".format(cursor_up), end="")
        # print the right part
        cursor_down = 0
        for index in range(len(message[2])):
            blocks = textwrap.fill(" ".join(message[3][index]), width=self.width)
            cursor_down += len(blocks.split("\n")) + 1
            print("\x1b[{}C  |  \x1b[0;36m{}\x1b[0m".format(self.width, message[2][index]))
            for line in blocks.split("\n"):
                print("\x1b[{}C  |  {}".format(self.width, line))
        if cursor_down < cursor_up:
            print("\x1b[{}B".format(cursor_up - cursor_down), end="")

    def formula_print(self, features, len_max, sim):
        """
        Print the formula of similarity calculation.
        Args:
            features: Feature values of position and distance.
            len_max: The longer length of 2 component sequences.
            sim: The similarity result.
        """
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
        print("\n", end="")

    @staticmethod
    def diff_print(message, paths):
        """
        Print crash dump comparison by combined diff format.
        Args:
            message: Crash dump message to be printed.
            paths: The paths of original crash dump pair.
        """
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
        print("\n", end="")
