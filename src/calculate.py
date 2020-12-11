import configparser
import math
import os


class Calculate(object):
    config = configparser.ConfigParser()
    config_path = os.path.join(os.getcwd(), "settings.ini")
    config.read(config_path)
    # Model
    m = config.getfloat("model", "m")
    n = config.getfloat("model", "n")

    def __init__(self, features, length):
        self.features = features
        self.length = length

    def calculate_sim(self):
        numerator = 0.0
        denominator = 0.0
        for pos, dist in self.features:
            numerator += math.exp(-self.m * pos) * math.exp(-self.n * dist)
        for i in range(self.length):
            denominator += math.exp(-self.m * i)
        sim = numerator / denominator
        return sim
