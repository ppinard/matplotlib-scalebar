#!/usr/bin/env python
""" """

# Standard library modules.

# Third party modules.
import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt
from matplotlib.testing.decorators import cleanup

import numpy as np

from nose.tools import \
    (assert_equal, assert_almost_equal, assert_is_none, assert_true,
     assert_false, assert_raises)

# Local modules.
from matplotlib_scalebar.scalebar import ScaleBar

# Globals and constants variables.

def create_figure():
    fig = plt.figure()
    ax = fig.add_subplot("111")

    data = np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]])
    ax.imshow(data)

    scalebar = ScaleBar(0.5)
    ax.add_artist(scalebar)

    return fig, ax, scalebar

@cleanup
def test_scalebar_draw():
    create_figure()
    plt.draw()

@cleanup
def test_scalebar_dx_m():
    _fig, _ax, scalebar = create_figure()

    assert_almost_equal(0.5, scalebar.get_dx_m())
    assert_almost_equal(0.5, scalebar.dx_m)

    scalebar.set_dx_m(0.2)
    assert_almost_equal(0.2, scalebar.get_dx_m())
    assert_almost_equal(0.2, scalebar.dx_m)

    scalebar.dx_m = 0.1
    assert_almost_equal(0.1, scalebar.get_dx_m())
    assert_almost_equal(0.1, scalebar.dx_m)

@cleanup
def test_scalebar_length_fraction():
    _fig, _ax, scalebar = create_figure()

    assert_is_none(scalebar.get_length_fraction())
    assert_is_none(scalebar.length_fraction)

    scalebar.set_length_fraction(0.2)
    assert_almost_equal(0.2, scalebar.get_length_fraction())
    assert_almost_equal(0.2, scalebar.length_fraction)

    scalebar.length_fraction = 0.1
    assert_almost_equal(0.1, scalebar.get_length_fraction())
    assert_almost_equal(0.1, scalebar.length_fraction)

    assert_raises(ValueError, scalebar.set_length_fraction, 0.0)
    assert_raises(ValueError, scalebar.set_length_fraction, 1.1)

@cleanup
def test_scalebar_height_fraction():
    _fig, _ax, scalebar = create_figure()

    assert_is_none(scalebar.get_height_fraction())
    assert_is_none(scalebar.height_fraction)

    scalebar.set_height_fraction(0.2)
    assert_almost_equal(0.2, scalebar.get_height_fraction())
    assert_almost_equal(0.2, scalebar.height_fraction)

    scalebar.height_fraction = 0.1
    assert_almost_equal(0.1, scalebar.get_height_fraction())
    assert_almost_equal(0.1, scalebar.height_fraction)

    assert_raises(ValueError, scalebar.set_height_fraction, 0.0)
    assert_raises(ValueError, scalebar.set_height_fraction, 1.1)

@cleanup
def test_scalebar_location():
    _fig, _ax, scalebar = create_figure()

    assert_is_none(scalebar.get_location())
    assert_is_none(scalebar.location)

    scalebar.set_location('upper right')
    assert_equal(1, scalebar.get_location())
    assert_equal(1, scalebar.location)

    scalebar.location = 'lower left'
    assert_equal(3, scalebar.get_location())
    assert_equal(3, scalebar.location)

@cleanup
def test_scalebar_pad():
    _fig, _ax, scalebar = create_figure()

    assert_is_none(scalebar.get_pad())
    assert_is_none(scalebar.pad)

    scalebar.set_pad(4)
    assert_almost_equal(4, scalebar.get_pad())
    assert_almost_equal(4, scalebar.pad)

    scalebar.pad = 5
    assert_almost_equal(5, scalebar.get_pad())
    assert_almost_equal(5, scalebar.pad)

@cleanup
def test_scalebar_border_pad():
    _fig, _ax, scalebar = create_figure()

    assert_is_none(scalebar.get_border_pad())
    assert_is_none(scalebar.border_pad)

    scalebar.set_border_pad(4)
    assert_almost_equal(4, scalebar.get_border_pad())
    assert_almost_equal(4, scalebar.border_pad)

    scalebar.border_pad = 5
    assert_almost_equal(5, scalebar.get_border_pad())
    assert_almost_equal(5, scalebar.border_pad)

@cleanup
def test_scalebar_sep():
    _fig, _ax, scalebar = create_figure()

    assert_is_none(scalebar.get_sep())
    assert_is_none(scalebar.sep)

    scalebar.set_sep(4)
    assert_almost_equal(4, scalebar.get_sep())
    assert_almost_equal(4, scalebar.sep)

    scalebar.sep = 5
    assert_almost_equal(5, scalebar.get_sep())
    assert_almost_equal(5, scalebar.sep)

@cleanup
def test_scalebar_frameon():
    _fig, _ax, scalebar = create_figure()

    assert_is_none(scalebar.get_frameon())
    assert_is_none(scalebar.frameon)

    scalebar.set_frameon(True)
    assert_true(scalebar.get_frameon())
    assert_true(scalebar.frameon)

    scalebar.frameon = False
    assert_false(scalebar.get_frameon())
    assert_false(scalebar.frameon)

if __name__ == '__main__':
    import nose
    import sys

    args = ['-s', '--with-doctest']
    argv = sys.argv
    argv = argv[:1] + args + argv[1:]
    nose.runmodule(argv=argv, exit=False)
