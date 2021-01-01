import matplotlib.pyplot as plt
from matplotlib_scalebar.scalebar import ScaleBar

fig, ax = plt.subplots(figsize=(3, 2.8))
ax.axis("off")

scalebar = ScaleBar(
    1,
    "cm",
    length_fraction=0.25,
    width_fraction=0.05,
    label="length_fraction=0.25",
    location="upper center",
    box_color="0.8",
    pad=0.5,
)
ax.add_artist(scalebar)

scalebar = ScaleBar(
    1,
    "cm",
    length_fraction=0.5,
    width_fraction=0.05,
    label="length_fraction=0.5",
    location="center",
    box_color="0.8",
    pad=0.5,
)
ax.add_artist(scalebar)

scalebar = ScaleBar(
    1,
    "cm",
    length_fraction=0.75,
    width_fraction=0.05,
    label="length_fraction=0.75",
    location="lower center",
    box_color="0.8",
    pad=0.5,
)
ax.add_artist(scalebar)

fig.savefig("argument_length_fraction.png", dpi=100, bbox_inches="tight")
