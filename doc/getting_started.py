import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cbook as cbook
from matplotlib_scalebar.scalebar import ScaleBar

# Load image
with cbook.get_sample_data("s1045.ima.gz") as dfile:
    im = np.frombuffer(dfile.read(), np.uint16).reshape((256, 256))

# Create subplot
fig, ax = plt.subplots()
ax.axis("off")

# Plot image
ax.imshow(im, cmap="gray")

# Create scale bar
scalebar = ScaleBar(0.08, "cm", length_fraction=0.25)
ax.add_artist(scalebar)

fig.savefig("getting_started.png", dpi=60, bbox_inches="tight")
