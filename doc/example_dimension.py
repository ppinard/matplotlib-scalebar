import matplotlib.pyplot as plt
from matplotlib_scalebar.scalebar import ScaleBar
from matplotlib_scalebar.dimension import _Dimension, _PREFIXES_FACTORS, _LATEX_MU


class TimeDimension(_Dimension):
    def __init__(self):
        super().__init__("s")
        for prefix, factor in _PREFIXES_FACTORS.items():
            latexrepr = None
            if prefix == "\u00b5" or prefix == "u":
                latexrepr = _LATEX_MU + "s"
            self.add_units(prefix + "s", factor, latexrepr)


plt.figure()
plt.gca().add_artist(
    ScaleBar(5, units="ms", dimension=TimeDimension(), location="lower right")
)

plt.savefig("example_dimension.png")
