import configparser
import math
import os

from utils import DP


class Calculate(object):
    """
    Calculate crash dump similarity through the mathematical model.
    Attributes:
        order_pair: The component order information within crash dump pair.
        block_pair: The function block information within crash dump pair.
    """
    config = configparser.ConfigParser()
    config_path = os.path.join(os.getcwd(), "config.ini")
    config.read(config_path)
    # Model
    m = config.getfloat("model", "m")
    n = config.getfloat("model", "n")

    def __init__(self, order_pair, block_pair):
        self.order_pair = order_pair
        self.block_pair = block_pair

    def obtain_feature(self):
        """
        Obtain the features used for calculation through dump pair information.
        Returns:
            The features used for calculation.
        """
        positions, distances = [], []
        pos_x, pos_y = DP().lcs_position(self.order_pair[0], self.order_pair[1])
        for i, j in zip(pos_x, pos_y):
            positions.append(max(i, j))
            distances.append(DP().normalized_dist(self.block_pair[0][i], self.block_pair[1][j]))
        return list(zip(positions, distances))

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
        for pos, dist in self.obtain_feature():
            numerator += math.exp(-m * pos) * math.exp(-n * dist)
        for i in range(len(max(self.order_pair, key=len))):
            denominator += math.exp(-m * i)
        sim = numerator / denominator
        return sim
