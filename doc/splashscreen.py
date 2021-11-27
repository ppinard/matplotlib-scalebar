import matplotlib.pyplot as plt
from matplotlib_scalebar.scalebar import ScaleBar
import requests
from PIL import Image
from io import BytesIO

r = requests.get("https://upload.wikimedia.org/wikipedia/commons/a/a4/Misc_pollen.jpg")
im = Image.open(BytesIO(r.content))

fig = plt.figure(figsize=(4, 4 / 1.3125))
ax = fig.add_axes([0.0, 0.0, 1.0, 1.0])

ax.imshow(im, "gray")

# According to Wikipedia, "the bean shaped grain in the bottom left corner is about 50 μm long."
scalebar = ScaleBar(
    50 / 144, "um", location="lower right", width_fraction=0.02, border_pad=1, pad=0.5
)
ax.add_artist(scalebar)

ax.xaxis.set_visible(False)
ax.yaxis.set_visible(False)

fig.savefig("splashscreen.png")
