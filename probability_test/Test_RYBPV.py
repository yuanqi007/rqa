import numpy as np

def getRandomResult(args):
    return np.random.choice(args)

c = []
args = np.arange(2)
np.random.shuffle(args)


for i in range(10000):
    c.append(getRandomResult(args))

c = np.asarray(c)
print("%s" % str(c.sum() / len(c)))

