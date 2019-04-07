import numpy as np


def roll_dice(d, size):
    return np.random.randint(1, d + 1, size=size)
