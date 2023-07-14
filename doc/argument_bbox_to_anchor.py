from pathlib import Path
import matplotlib.pyplot as plt
from matplotlib_scalebar.scalebar import ScaleBar

fig, ax = plt.subplots()

scalebar = ScaleBar(
    1,
    "cm",
    length_fraction=0.25,
    bbox_to_anchor=(0.5, 0.5),
    bbox_transform=ax.transAxes,
    location="lower left",
    label="lower left",
    box_color="0.8",
)
ax.add_artist(scalebar)

scalebar = ScaleBar(
    1,
    "cm",
    length_fraction=0.25,
    bbox_to_anchor=(0.5, 0.5),
    bbox_transform=ax.transAxes,
    location="upper right",
    label="upper right",
    box_color="0.8",
)
ax.add_artist(scalebar)

outdir = Path(__file__).parent.resolve()
fig.savefig(outdir / "argument_bbox_to_anchor.png", dpi=60, bbox_inches="tight")
