import figures
from skimage import data, io, draw
import matplotlib.pyplot as plt
rect = figures.Rectangle()
can = io.imread("input/unnamed.png")
can[rect.draw()] = (255,0,0)
plt.imshow(can)
plt.show()