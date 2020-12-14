import configparser
import math
import os


class Calculate(object):
    config = configparser.ConfigParser()
    config_path = os.path.join(os.getcwd(), "config.ini")
    config.read(config_path)
    # Model
    m = config.getfloat("model", "m")
    n = config.getfloat("model", "n")

    def __init__(self, features, length):
        self.features = features
        self.length = length

    def calculate_sim(self, m=m, n=n):
        numerator = 0.0
        denominator = 0.0
        for pos, dist in self.features:
            numerator += math.exp(-m * pos) * math.exp(-n * dist)
        for i in range(self.length):
            denominator += math.exp(-m * i)
        sim = numerator / denominator
        return sim
