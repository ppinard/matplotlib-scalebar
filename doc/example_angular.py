import numpy as np
import matplotlib.pyplot as plt
from matplotlib_scalebar.scalebar import ScaleBar

delta = 0.025
x = y = np.arange(-3.0, 3.0, delta)
X, Y = np.meshgrid(x, y)
Z1 = np.exp(-(X**2) - Y**2)
Z2 = np.exp(-((X - 1) ** 2) - (Y - 1) ** 2)
Z = (Z1 - Z2) * 2

fig, axes = plt.subplots(1, 3, figsize=(9, 3))

for ax, dx in zip(axes, [delta, delta / 60, delta / 3600]):
    ax.imshow(Z)

    scalebar = ScaleBar(dx, "deg", dimension="angle")
    ax.add_artist(scalebar)

    ax.set_title("dx = {:.6f}deg".format(dx))

fig.savefig("example_angular.png")
