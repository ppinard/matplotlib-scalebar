import matplotlib.pyplot as plt
import matplotlib.cbook as cbook
from matplotlib_scalebar.scalebar import ScaleBar, IMPERIAL_LENGTH

plt.figure()
image = plt.imread(cbook.get_sample_data("grace_hopper.png"))
plt.imshow(image)
scalebar = ScaleBar(0.02, "ft", IMPERIAL_LENGTH)  # 1 pixel = 0.02 feet
plt.gca().add_artist(scalebar)
plt.savefig("example2.png")
