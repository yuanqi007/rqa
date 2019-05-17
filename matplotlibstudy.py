import numpy as np
import matplotlib.pyplot as plt

x = np.linspace(-1,1,50)
y = 2*x + 1

plt.figure()
plt.plot(x,y)
plt.show()