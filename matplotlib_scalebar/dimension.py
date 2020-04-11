""""""

# Standard library modules.
from __future__ import division, unicode_literals
from operator import itemgetter
import bisect

# Third party modules.

# Local modules.

# Globals and constants variables.
_PREFIXES_FACTORS = {
    "Y": 1e24,
    "Z": 1e21,
    "E": 1e18,
    "P": 1e15,
    "T": 1e12,
    "G": 1e9,
    "M": 1e6,
    "k": 1e3,
    "d": 1e-1,
    "c": 1e-2,
    "m": 1e-3,
    "\u00b5": 1e-6,
    "u": 1e-6,
    "n": 1e-9,
    "p": 1e-12,
    "f": 1e-15,
    "a": 1e-18,
    "z": 1e-21,
    "y": 1e-24,
}
_LATEX_MU = "$\\mathrm{\\mu}$"


class _Dimension(object):
    def __init__(self, base_units, latexrepr=None):
        self._base_units = base_units
        self._units = {base_units: 1.0}

        if latexrepr is None:
            latexrepr = base_units
        self._latexrepr = {base_units: latexrepr}

    def add_units(self, units, factor, latexrepr=None):
        """
        Add new possible units.

        :arg units: units
        :type units: :class:`str`

        :arg factor: multiplication factor to convert new units into base units
        :type factor: :class:`float`

        :arg latexrepr: LaTeX representation of units (if ``None``, use *units)
        :type latexrepr: :class:`str`
        """
        if units in self._units:
            raise ValueError("%s already defined" % units)
        if factor == 1:
            raise ValueError("Factor cannot be equal to 1")
        if latexrepr is None:
            latexrepr = units

        self._units[units] = factor
        self._latexrepr[units] = latexrepr

    def is_valid_units(self, units):
        return units in self._units and units in self._latexrepr

    def calculate_preferred(self, value, units):
        if units not in self._units:
            raise ValueError("Unknown units: %s" % units)
        base_value = value * self._units[units]

        units_factor = sorted(self._units.items(), key=itemgetter(1))
        factors = [item[1] for item in units_factor]
        index = bisect.bisect_right(factors, base_value)

        if index:
            newunits, factor = units_factor[index - 1]
            return base_value / factor, newunits

        else:
            return value, units

    def convert(self, value, units, newunits):
        """
        Converts a value expressed in certain *units* to a new units.
        """
        return value * self._units[units] / self._units[newunits]

    def to_latex(self, units):
        if units not in self._latexrepr:
            raise ValueError("Unknown units: %s" % units)
        return self._latexrepr[units]

    def create_label(self, value, latexrepr):
        return "{} {}".format(value, latexrepr)

    @property
    def base_units(self):
        return self._base_units


class SILengthDimension(_Dimension):
    def __init__(self):
        super().__init__("m")
        for prefix, factor in _PREFIXES_FACTORS.items():
            latexrepr = None
            if prefix == "\u00b5" or prefix == "u":
                latexrepr = _LATEX_MU + "m"
            self.add_units(prefix + "m", factor, latexrepr)


class SILengthReciprocalDimension(_Dimension):
    def __init__(self):
        super().__init__("1/m", "m$^{-1}$")
        for prefix, factor in _PREFIXES_FACTORS.items():
            latexrepr = "{0}m$^{{-1}}$".format(prefix)
            if prefix == "\u00b5" or prefix == "u":
                latexrepr = _LATEX_MU + "m$^{-1}$"
            self.add_units("1/{0}m".format(prefix), 1 / factor, latexrepr)


class ImperialLengthDimension(_Dimension):
    def __init__(self):
        super().__init__("ft")
        self.add_units("th", 1 / 12000)
        self.add_units("in", 1 / 12)
        self.add_units("yd", 3)
        self.add_units("ch", 66)
        self.add_units("fur", 660)
        self.add_units("mi", 5280)
        self.add_units("lea", 15840)


class PixelLengthDimension(_Dimension):
    def __init__(self):
        super().__init__("px")
        for prefix, factor in _PREFIXES_FACTORS.items():
            if factor < 1:
                continue
            self.add_units(prefix + "px", factor)


class AngleDimension(_Dimension):
    def __init__(self):
        super().__init__("deg", "$^\\circ$")
        self.add_units("'", 1 / 60, "$^\\prime$")
        self.add_units("''", 1 / 3600, "$^{\\prime\\prime}$")

    def create_label(self, value, latexrepr):
        # Overriden to remove space between value and units.
        return "{}{}".format(value, latexrepr)
