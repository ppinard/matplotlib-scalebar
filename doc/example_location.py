import matplotlib.pyplot as plt
from matplotlib_scalebar.scalebar import ScaleBar

plt.figure()
plt.gca().add_artist(
    ScaleBar(
        0.5,
        label="scale_loc=top, label_loc=top",
        scale_loc="top",
        label_loc="top",
        location="upper right",
    )
)
plt.gca().add_artist(
    ScaleBar(
        0.5,
        label="scale_loc=bottom, label_loc=top",
        scale_loc="bottom",
        label_loc="top",
        location="lower right",
    )
)

plt.gca().add_artist(
    ScaleBar(
        0.5,
        label="scale_loc=top, label_loc=bottom",
        scale_loc="top",
        label_loc="bottom",
        location="upper left",
    )
)
plt.gca().add_artist(
    ScaleBar(
        0.5,
        label="scale_loc=bottom, label_loc=bottom",
        scale_loc="bottom",
        label_loc="bottom",
        location="lower left",
    )
)

plt.savefig("example_location.png")
