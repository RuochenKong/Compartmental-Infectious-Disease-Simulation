import numpy as np
import numpy.random
import random

rand = None

def init_random(seed):
    global rand
    rand = random.Random(seed)
    numpy.random.seed(seed)


def test_random():
    arr = [int(np.random.poisson(30)) for _ in range(10)]
    arr2 = [rand.randint(0, 100) for _ in range(10)]
    return arr+arr2
def main(seed):
    init_random(seed)

    print(test_random())