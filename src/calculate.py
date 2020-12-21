import configparser
import math
import os


class Calculate(object):
    """
    Calculate crash dump similarity through the mathematical model.
    Attributes:
        features: Feature values of position and distance.
        len_max: The longer length of 2 component sequences.
    """
    config = configparser.ConfigParser()
    config_path = os.path.join(os.getcwd(), "config.ini")
    config.read(config_path)
    # Model
    m = config.getfloat("model", "m")
    n = config.getfloat("model", "n")

    def __init__(self, features, length):
        self.features = features
        self.len_max = length

    def calculate_sim(self, m=m, n=n):
        """
        Calculate the crash dump similarity under current parameters.
        Args:
            m: The parameter for component position.
            n: The parameter for component distance.
        Returns:
            sim: The similarity result.
        """
        numerator = 0.0
        denominator = 0.0
        for pos, dist in self.features:
            numerator += math.exp(-m * pos) * math.exp(-n * dist)
        for i in range(self.len_max):
            denominator += math.exp(-m * i)
        sim = numerator / denominator
        return sim
