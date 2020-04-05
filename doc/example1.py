import matplotlib.pyplot as plt
import matplotlib.cbook as cbook
from matplotlib_scalebar.scalebar import ScaleBar

plt.figure()
image = plt.imread(cbook.get_sample_data("grace_hopper.png"))
plt.imshow(image)
scalebar = ScaleBar(0.2)  # 1 pixel = 0.2 meter
plt.gca().add_artist(scalebar)
plt.savefig("example1.png")
