import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cbook as cbook
from matplotlib_scalebar.scalebar import ScaleBar

with cbook.get_sample_data("s1045.ima.gz") as dfile:
    im = np.frombuffer(dfile.read(), np.uint16).reshape((256, 256))

fig, ax = plt.subplots()
ax.axis("off")

ax.imshow(im, cmap="gray")

scalebar = ScaleBar(
    0.08, "cm", pad=1.0, border_pad=1.0, sep=10.0, frameon=True, length_fraction=0.25
)
ax.add_artist(scalebar)

fig.savefig("argument_pad.png", dpi=60, bbox_inches="tight")
