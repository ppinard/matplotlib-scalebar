import matplotlib.pyplot as plt
import matplotlib.cbook as cbook
from matplotlib_scalebar.scalebar import ScaleBar, IMPERIAL_LENGTH

plt.figure()
image = plt.imread(cbook.get_sample_data("grace_hopper.png"))
plt.imshow(image)
scalebar = ScaleBar(0.02, "ft", IMPERIAL_LENGTH, fixed_value=48.0, fixed_units="in")
plt.gca().add_artist(scalebar)
plt.savefig("example3.png")
