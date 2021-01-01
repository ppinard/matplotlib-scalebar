import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch
from matplotlib_scalebar.scalebar import ScaleBar


fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(16, 4))

for ax in [ax1, ax2, ax3]:
    ax.xaxis.set_visible(False)
    ax.yaxis.set_visible(False)

    scalebar = ScaleBar(
        1,
        "cm",
        width_fraction=0.05,
        location="center left",
        label="label",
        box_color="0.8",
        pad=5,
        border_pad=2,
        font_properties={"size": "xx-large"},
        fixed_value=2,
        fixed_units="mm",
    )
    ax.add_artist(scalebar)

# Names
ax1.annotate(
    "label",
    (0.4, 0.6),
    (0.65, 0.65),
    arrowprops={"arrowstyle": "->", "connectionstyle": "arc3,rad=0.1", "lw": 3},
    fontsize=20,
    zorder=7,
)
ax1.annotate(
    "scale bar",
    (0.42, 0.5),
    (0.65, 0.5),
    arrowprops={"arrowstyle": "->", "connectionstyle": "arc3,rad=0.0", "lw": 3},
    fontsize=20,
    zorder=7,
)
ax1.annotate(
    "scale",
    (0.4, 0.42),
    (0.65, 0.35),
    arrowprops={"arrowstyle": "->", "connectionstyle": "arc3,rad=-0.1", "lw": 3},
    fontsize=20,
    zorder=7,
)
ax1.annotate(
    "box",
    (0.3, 0.75),
    (0.4, 0.9),
    arrowprops={"arrowstyle": "->", "connectionstyle": "arc3,rad=0.1", "lw": 3},
    fontsize=20,
    zorder=7,
)

# Fractions
patch = FancyArrowPatch(
    (0.19, 0.3), (0.405, 0.3), arrowstyle="|-|,widthA=6,widthB=6", zorder=7, lw=2
)
ax2.add_patch(patch)
ax2.annotate(
    "length",
    (0.3, 0.25),
    (0.5, 0.05),
    arrowprops={"arrowstyle": "->", "connectionstyle": "arc3,rad=-0.3", "lw": 3},
    fontsize=20,
    zorder=7,
)

patch = FancyArrowPatch(
    (0.45, 0.46), (0.45, 0.54), arrowstyle="|-|,widthA=6,widthB=6", zorder=7, lw=2
)
ax2.add_patch(patch)
ax2.annotate(
    "width",
    (0.5, 0.5),
    (0.65, 0.5),
    arrowprops={"arrowstyle": "->", "connectionstyle": "arc3", "lw": 3},
    fontsize=20,
    zorder=7,
)

# Pad
patch = FancyArrowPatch(
    (0.45, 0.44), (0.45, 0.485), arrowstyle="|-|,widthA=6,widthB=6", zorder=7, lw=2
)
ax3.add_patch(patch)
patch = FancyArrowPatch(
    (0.45, 0.52), (0.45, 0.565), arrowstyle="|-|,widthA=6,widthB=6", zorder=7, lw=2
)
ax3.add_patch(patch)
ax3.annotate(
    "sep",
    (0.47, 0.465),
    (0.65, 0.5),
    arrowprops={"arrowstyle": "->", "connectionstyle": "arc3,rad=-0.1", "lw": 3},
    fontsize=20,
    zorder=7,
)
ax3.annotate(
    "sep",
    (0.47, 0.545),
    (0.65, 0.5),
    arrowprops={"arrowstyle": "->", "connectionstyle": "arc3,rad=0.1", "lw": 3},
    fontsize=20,
    zorder=7,
)

patch = FancyArrowPatch(
    (0.0, 0.1), (0.065, 0.1), arrowstyle="|-|,widthA=6,widthB=6", zorder=7, lw=2
)
ax3.add_patch(patch)
ax3.annotate(
    "border pad",
    (0.08, 0.1),
    (0.2, 0.05),
    arrowprops={"arrowstyle": "->", "connectionstyle": "arc3", "lw": 3},
    fontsize=20,
    zorder=7,
)

patch = FancyArrowPatch(
    (0.065, 0.9), (0.19, 0.9), arrowstyle="|-|,widthA=6,widthB=6", zorder=7, lw=2
)
ax3.add_patch(patch)
ax3.annotate(
    "pad",
    (0.22, 0.9),
    (0.35, 0.9),
    arrowprops={"arrowstyle": "->", "connectionstyle": "arc3", "lw": 3},
    fontsize=20,
    zorder=7,
)

plt.tight_layout(pad=2)

fig.savefig("nomenclature.png", dpi=60)
