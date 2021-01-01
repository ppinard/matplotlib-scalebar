import matplotlib.pyplot as plt
from matplotlib_scalebar.scalebar import ScaleBar

fig, ax = plt.subplots(figsize=(3, 2.8))
ax.axis("off")

scalebar = ScaleBar(
    1,
    "cm",
    length_fraction=0.75,
    width_fraction=0.05,
    scale_loc="bottom",
    label="scale_loc=bottom",
    location="upper center",
    box_color="0.8",
    pad=0.5,
)
ax.add_artist(scalebar)

scalebar = ScaleBar(
    1,
    "cm",
    length_fraction=0.75,
    width_fraction=0.05,
    scale_loc="right",
    label="scale_loc=right",
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
    scale_loc="top",
    label="scale_loc=top",
    location="lower center",
    box_color="0.8",
    pad=0.5,
)
ax.add_artist(scalebar)

fig.savefig("argument_scale_loc.png", dpi=100, bbox_inches="tight")
