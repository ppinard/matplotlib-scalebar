import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cbook as cbook
from matplotlib_scalebar.scalebar import ScaleBar

with cbook.get_sample_data("s1045.ima.gz") as dfile:
    im = np.frombuffer(dfile.read(), np.uint16).reshape((256, 256))

fig, ax = plt.subplots()
ax.axis("off")

ax.imshow(im, cmap="gray", extent=[0, 20.48, 0, 20.48])

scalebar = ScaleBar(1, "cm", length_fraction=0.25)
ax.add_artist(scalebar)

fig.savefig("argument_dx.png", dpi=60, bbox_inches="tight")
