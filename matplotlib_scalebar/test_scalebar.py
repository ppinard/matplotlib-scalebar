#!/usr/bin/env python
""" """

# Standard library modules.

# Third party modules.
import matplotlib

matplotlib.use("agg")
import matplotlib.pyplot as plt
from matplotlib.testing.decorators import cleanup
from matplotlib.font_manager import FontProperties

import numpy as np

import pytest

# Local modules.
from matplotlib_scalebar.scalebar import ScaleBar

# Globals and constants variables.


@pytest.fixture
@cleanup
def scalebar():
    fig = plt.figure()
    ax = fig.add_subplot(111)

    data = np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]])
    ax.imshow(data)

    scalebar = ScaleBar(0.5)
    ax.add_artist(scalebar)

    yield scalebar

    plt.draw()


def test_mpl_rcParams_update():
    """
    Test if scalebar params are updated accurately in matplotlib rcParams
    """

    params = {
        "scalebar.length_fraction": 0.2,
        "scalebar.width_fraction": 0.01,
        "scalebar.location": "upper right",
        "scalebar.pad": 0.2,
        "scalebar.border_pad": 0.1,
        "scalebar.sep": 5,
        "scalebar.frameon": True,
        "scalebar.color": "k",
        "scalebar.box_color": "w",
        "scalebar.box_alpha": 1.0,
        "scalebar.scale_loc": "bottom",
        "scalebar.label_loc": "top",
        "scalebar.rotation": "horizontal",
    }
    matplotlib.rcParams.update(params)

    for key, value in params.items():
        assert matplotlib.rcParams[key] == value


def test_scalebar_dx_m(scalebar):
    assert scalebar.get_dx() == pytest.approx(0.5, abs=1e-2)
    assert scalebar.dx == pytest.approx(0.5, abs=1e-2)

    scalebar.set_dx(0.2)
    assert scalebar.get_dx() == pytest.approx(0.2, abs=1e-2)
    assert scalebar.dx == pytest.approx(0.2, abs=1e-2)

    scalebar.dx = 0.1
    assert scalebar.get_dx() == pytest.approx(0.1, abs=1e-2)
    assert scalebar.dx == pytest.approx(0.1, abs=1e-2)


def test_scalebar_length_fraction(scalebar):
    assert scalebar.get_length_fraction() is None
    assert scalebar.length_fraction is None

    scalebar.set_length_fraction(0.2)
    assert scalebar.get_length_fraction() == pytest.approx(0.2, abs=1e-2)
    assert scalebar.length_fraction == pytest.approx(0.2, abs=1e-2)

    scalebar.length_fraction = 0.1
    assert scalebar.get_length_fraction() == pytest.approx(0.1, abs=1e-2)
    assert scalebar.length_fraction == pytest.approx(0.1, abs=1e-2)

    with pytest.raises(ValueError):
        scalebar.set_length_fraction(0.0)

    with pytest.raises(ValueError):
        scalebar.set_length_fraction(1.1)


@pytest.mark.filterwarnings("ignore")
def test_scalebar_height_fraction(scalebar):
    with pytest.deprecated_call():
        assert scalebar.get_height_fraction() is None

    with pytest.deprecated_call():
        assert scalebar.height_fraction is None

    with pytest.deprecated_call():
        scalebar.set_height_fraction(0.2)

    assert scalebar.get_height_fraction() == pytest.approx(0.2, abs=1e-2)
    assert scalebar.height_fraction == pytest.approx(0.2, abs=1e-2)

    with pytest.deprecated_call():
        scalebar.height_fraction = 0.1

    assert scalebar.get_height_fraction() == pytest.approx(0.1, abs=1e-2)
    assert scalebar.height_fraction == pytest.approx(0.1, abs=1e-2)

    with pytest.raises(ValueError), pytest.deprecated_call():
        scalebar.set_height_fraction(0.0)

    with pytest.raises(ValueError), pytest.deprecated_call():
        scalebar.set_height_fraction(1.1)


def test_scalebar_location(scalebar):
    assert scalebar.get_location() is None
    assert scalebar.location is None

    scalebar.set_location("upper right")
    assert scalebar.get_location() == 1
    assert scalebar.location == 1

    scalebar.location = "lower left"
    assert scalebar.get_location() == 3
    assert scalebar.location == 3


def test_scalebar_loc(scalebar):
    assert scalebar.get_loc() is None
    assert scalebar.loc is None

    scalebar.set_location("upper right")
    assert scalebar.get_loc() == 1
    assert scalebar.loc == 1

    scalebar.location = "lower left"
    assert scalebar.get_loc() == 3
    assert scalebar.loc == 3

    scalebar.set_loc("lower right")
    assert scalebar.get_loc() == 4
    assert scalebar.loc == 4

    scalebar.location = "upper left"
    assert scalebar.get_loc() == 2
    assert scalebar.loc == 2

    with pytest.raises(ValueError):
        ScaleBar(1.0, loc="upper right", location="upper left")

    with pytest.raises(ValueError):
        ScaleBar(1.0, loc="upper right", location=2)


def test_scalebar_pad(scalebar):
    assert scalebar.get_pad() is None
    assert scalebar.pad is None

    scalebar.set_pad(4.0)
    assert scalebar.get_pad() == pytest.approx(4.0, abs=1e-2)
    assert scalebar.pad == pytest.approx(4.0, abs=1e-2)

    scalebar.pad = 5.0
    assert scalebar.get_pad() == pytest.approx(5.0, abs=1e-2)
    assert scalebar.pad == pytest.approx(5.0, abs=1e-2)


def test_scalebar_border_pad(scalebar):
    assert scalebar.get_border_pad() is None
    assert scalebar.border_pad is None

    scalebar.set_border_pad(4)
    assert scalebar.get_border_pad() == pytest.approx(4.0, abs=1e-2)
    assert scalebar.border_pad == pytest.approx(4.0, abs=1e-2)

    scalebar.border_pad = 5
    assert scalebar.get_border_pad() == pytest.approx(5.0, abs=1e-2)
    assert scalebar.border_pad == pytest.approx(5.0, abs=1e-2)


def test_scalebar_sep(scalebar):
    assert scalebar.get_sep() is None
    assert scalebar.sep is None

    scalebar.set_sep(4)
    assert scalebar.get_sep() == pytest.approx(4.0, abs=1e-2)
    assert scalebar.sep == pytest.approx(4.0, abs=1e-2)

    scalebar.sep = 5
    assert scalebar.get_sep() == pytest.approx(5.0, abs=1e-2)
    assert scalebar.sep == pytest.approx(5.0, abs=1e-2)


def test_scalebar_frameon(scalebar):
    assert scalebar.get_frameon() is None
    assert scalebar.frameon is None

    scalebar.set_frameon(True)
    assert scalebar.get_frameon()
    assert scalebar.frameon

    scalebar.frameon = False
    assert not scalebar.get_frameon()
    assert not scalebar.frameon


def test_scalebar_font_properties(scalebar):
    assert isinstance(scalebar.get_font_properties(), FontProperties)
    assert isinstance(scalebar.font_properties, FontProperties)

    scalebar.set_font_properties(dict(family="serif", size=9))
    assert scalebar.font_properties.get_family() == ["serif"]
    assert scalebar.font_properties.get_size() == 9

    scalebar.font_properties = dict(family="sans serif", size=12)
    assert scalebar.font_properties.get_family() == ["sans serif"]
    assert scalebar.font_properties.get_size() == 12

    with pytest.raises(ValueError):
        scalebar.set_font_properties(2.0)

    with pytest.raises(ValueError):
        scalebar.font_properties = 2.0


def test_matplotlibrc(scalebar):
    matplotlib.rcParams["scalebar.box_color"] = "r"


def test_scalebar_fixed_value(scalebar):
    assert scalebar.get_fixed_value() is None
    assert scalebar.fixed_value is None

    scalebar.set_fixed_value(0.2)
    assert scalebar.get_fixed_value() == pytest.approx(0.2, abs=1e-2)
    assert scalebar.fixed_value == pytest.approx(0.2, abs=1e-2)

    scalebar.fixed_value = 0.1
    assert scalebar.get_fixed_value() == pytest.approx(0.1, abs=1e-2)
    assert scalebar.fixed_value == pytest.approx(0.1, abs=1e-2)


def test_scalebar_fixed_units(scalebar):
    assert scalebar.get_fixed_units() is None
    assert scalebar.fixed_units is None

    scalebar.set_fixed_units("m")
    assert scalebar.get_fixed_units() == "m"
    assert scalebar.fixed_units == "m"

    scalebar.fixed_units = "um"
    assert scalebar.get_fixed_units() == "um"
    assert scalebar.fixed_units == "um"


def test_scale_formatter(scalebar):
    scalebar.dx = 1
    scalebar.units = "m"
    _length, value, units = scalebar._calculate_best_length(10)

    assert scalebar.scale_formatter(value, units) == "5 m"

    scalebar.scale_formatter = lambda *_: "test"
    assert scalebar.scale_formatter(value, units) == "test"

    scalebar.scale_formatter = lambda value, unit: "{} {}".format(unit, value)
    assert scalebar.scale_formatter(value, units) == "m 5"


def test_label_formatter(scalebar):
    scalebar.dx = 1
    scalebar.units = "m"
    _length, value, units = scalebar._calculate_best_length(10)

    with pytest.deprecated_call():
        assert scalebar.label_formatter(value, units) == "5 m"

    with pytest.deprecated_call():
        scalebar.label_formatter = lambda *_: "test"
        assert scalebar.label_formatter(value, units) == "test"

    with pytest.deprecated_call():
        scalebar.label_formatter = lambda value, unit: "{} {}".format(unit, value)
        assert scalebar.label_formatter(value, units) == "m 5"


@pytest.mark.parametrize("rotation", ["horizontal", "vertical"])
def test_rotation(scalebar, rotation):
    assert scalebar.get_rotation() is None
    assert scalebar.rotation is None

    scalebar.set_rotation(rotation)
    assert scalebar.get_rotation() == rotation
    assert scalebar.rotation == rotation

    with pytest.raises(ValueError):
        scalebar.set_rotation("h")


def test_warnings():
    with pytest.warns(None) as record:
        fig = plt.figure()
        ax = fig.add_subplot(111)

        data = np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]])
        ax.imshow(data)

        scalebar = ScaleBar(0.5)
        ax.add_artist(scalebar)

        plt.draw()

    assert len(record) == 0, "Warnings: " + ",".join(
        f"{repr(w.message)}" for w in record
    )
