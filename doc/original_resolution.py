import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cbook as cbook
from matplotlib_scalebar.scalebar import ScaleBar

# Load image
with cbook.get_sample_data("s1045.ima.gz") as dfile:
    arr = np.frombuffer(dfile.read(), np.uint16).reshape((256, 256))

# Create figure
dpi = 200
fig = plt.figure(
    figsize=(arr.shape[1] / dpi, arr.shape[0] / dpi), frameon=False, dpi=dpi
)

ax = fig.add_axes([0.0, 0.0, 1.0, 1.0])
ax.set_axis_off()

ax.imshow(arr)

scalebar = ScaleBar(100, "nm", length_fraction=0.25, location="lower right")
ax.add_artist(scalebar)

fig.savefig("original_resolution.png", dpi=dpi)
