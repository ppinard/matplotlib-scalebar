""" """

# Standard library modules.

# Third party modules.
import pytest

# Local modules.
from matplotlib_scalebar.dimension import (
    SILengthDimension,
    SILengthReciprocalDimension,
    ImperialLengthDimension,
    PixelLengthDimension,
    _LATEX_MU,
)

# Globals and constants variables.


@pytest.mark.parametrize(
    "dim,value,units,expected_value,expected_units",
    [
        (SILengthDimension(), 2000, "m", 2.0, "km"),
        (SILengthDimension(), 200, "m", 200, "m"),
        (SILengthDimension(), 0.02, "m", 2.0, "cm"),
        (SILengthDimension(), 0.01, "m", 1.0, "cm"),
        (SILengthDimension(), 0.002, "m", 2, "mm"),
        (SILengthDimension(), 0.001, "m", 1, "mm"),
        (SILengthDimension(), 0.009, "m", 9, "mm"),
        (SILengthDimension(), 2e-7, "m", 200, "nm"),
        (ImperialLengthDimension(), 18, "in", 1.5, "ft"),
        (ImperialLengthDimension(), 120, "in", 3.333, "yd"),
        (ImperialLengthDimension(), 10000, "ft", 1.8939, "mi"),
        (SILengthReciprocalDimension(), 0.02, "1/m", 20.0, "1/km"),
        (SILengthReciprocalDimension(), 0.002, "1/m", 2.0, "1/km"),
        (PixelLengthDimension(), 2000, "px", 2.0, "kpx"),
        (PixelLengthDimension(), 200, "px", 200.0, "px"),
        (PixelLengthDimension(), 0.02, "px", 0.02, "px"),
        (PixelLengthDimension(), 0.001, "px", 0.001, "px"),
    ],
)
def test_calculate_preferred(dim, value, units, expected_value, expected_units):
    value, units = dim.calculate_preferred(value, units)
    assert value == pytest.approx(expected_value, abs=1e-3)
    assert units == expected_units


@pytest.mark.parametrize(
    "dim,units,expected",
    [
        (SILengthDimension(), "cm", "cm"),
        (SILengthDimension(), u"\u00b5m", _LATEX_MU + "m"),
        (SILengthReciprocalDimension(), "1/cm", "cm$^{-1}$"),
        (SILengthReciprocalDimension(), u"1/\u00b5m", _LATEX_MU + "m$^{-1}$"),
    ],
)
def test_to_latex(dim, units, expected):
    assert dim.to_latex(units) == expected


@pytest.mark.parametrize(
    "dim,value,units,newunits,expected_value",
    [
        (SILengthDimension(), 2, "cm", "um", 2e4),
        (SILengthDimension(), 2, "um", "cm", 2e-4),
        (PixelLengthDimension(), 2, "kpx", "px", 2000),
        (PixelLengthDimension(), 2, "px", "kpx", 2e-3),
    ],
)
def test_convert(dim, value, units, newunits, expected_value):
    value = dim.convert(value, units, newunits)
    assert value == pytest.approx(expected_value, abs=1e-6)
