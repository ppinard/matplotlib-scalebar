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
    0.0315,
    "in",
    dimension="imperial-length",
    length_fraction=0.25,
    bbox_to_anchor=(0.5, 0.5),
    bbox_transform=ax.transAxes,
    location="center",
)
ax.add_artist(scalebar)

scalebar = ScaleBar(
    0.0315,
    "in",
    dimension="imperial-length",
    length_fraction=0.25,
    bbox_to_anchor=(1.0, 1.0),
    bbox_transform=ax.transAxes,
    location="upper right",
)
ax.add_artist(scalebar)

fig.savefig("argument_bbox_to_anchor.png", dpi=60, bbox_inches="tight")
