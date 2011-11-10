from interpolation import *
from numpy import *
from matplotlib.pyplot import *

x = linspace(0, 1, 100)
y = [quadratic(i, 1) for i in x]
plot(x, y) # call Matplotlib plotting function
show()
