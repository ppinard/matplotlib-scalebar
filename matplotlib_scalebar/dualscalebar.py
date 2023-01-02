"""
Artist for matplotlib to display a scale / micron bar.

Example::

   >>> fig = plt.figure()
   >>> ax = fig.add_axes([0.0, 0.0, 1.0, 1.0])
   >>> ax.imshow(...)
   >>> scalebar = ScaleBar(0.2)
   >>> ax.add_artist(scalebar)
   >>> plt.show()

The following parameters are available for customization in the matplotlibrc:
    - scalebar.length_fraction
    - scalebar.height_fraction
    - scalebar.location
    - scalebar.pad
    - scalebar.border_pad
    - scalebar.sep
    - scalebar.frameon
    - scalebar.color
    - scalebar.box_color
    - scalebar.box_alpha
    - scalebar.scale_loc
    - scalebar.label_loc

See the class documentation (:class:`.Scalebar`) for a description of the
parameters.
"""

__all__ = [
    "ScaleBar",
    "SI_LENGTH",
    "SI_LENGTH_RECIPROCAL",
    "IMPERIAL_LENGTH",
    "PIXEL_LENGTH",
]

# Standard library modules.
import bisect
import warnings

# Third party modules.
import matplotlib
from matplotlib.artist import Artist
from matplotlib.font_manager import FontProperties
from matplotlib.rcsetup import (
    defaultParams,
    validate_float,
    validate_bool,
    validate_color,
    ValidateInStrings,
)
from matplotlib.offsetbox import (
    AuxTransformBox,
    AnchoredOffsetbox,
)
from matplotlib.patches import Rectangle

# Local modules.
from matplotlib_scalebar.dimension import (
    _Dimension,
    SILengthDimension,
    SILengthReciprocalDimension,
    ImperialLengthDimension,
    PixelLengthDimension,
    AngleDimension,
    TimeDimension
)


# Globals and constants variables.
def _validate_locs_pair(locs):
    for loc in locs:
        if not (loc in _VALID_TEXT_LOCATIONS):
            raise ValueError(
                f"location {loc} should be one of: "
                f"{', '.join(_VALID_TEXT_LOCATIONS)}"
            )
    return locs


def _validate_floats_pair(floats):
    for f in floats:
        try:
            float(f)
        except ValueError:
            raise ValueError(f"{f} should be of type float")
    return floats


# Setup of extra parameters in the matplotlic rc
_VALID_TEXT_LOCATIONS = ["upper left", "upper centre", "upper center", "upper right",
                         "lower left", "lower centre", "lower center", "lower right",
                         "none"]

_VALID_ROTATIONS = ["horizontal", "vertical"]
_validate_rotation = ValidateInStrings(
    "rotation", _VALID_ROTATIONS, ignorecase=True)

_VALID_ARRANGEMENTS = ["lower left", "lower right", "upper right", "upper left"]
_validate_arrangement = ValidateInStrings(
    "arrangement", _VALID_ARRANGEMENTS, ignorecase=True)


def _validate_legend_loc(loc):
    rc = matplotlib.RcParams()
    rc["legend.loc"] = loc
    return loc


defaultParams.update(
    {
        "scalebar.length_fraction": [(0.2, 0.2), _validate_floats_pair],
        "scalebar.width_fraction": [0.01, validate_float],
        "scalebar.location": ["upper right", _validate_legend_loc],
        "scalebar.pad": [0.2, validate_float],
        "scalebar.border_pad": [0.1, validate_float],
        "scalebar.sep": [0.001, validate_float],
        "scalebar.frameon": [True, validate_bool],
        "scalebar.color": ["k", validate_color],
        "scalebar.box_color": ["w", validate_color],
        "scalebar.box_alpha": [1.0, validate_float],
        "scalebar.scale_loc": [("lower centre", "upper centre"), _validate_locs_pair],
        "scalebar.label_loc": [("upper centre", "lower centre"), _validate_locs_pair],
        "scalebar.rotation": ["horizontal", _validate_rotation],
        "scalebar.arrangement": ["lower left", _validate_arrangement],
    }
)


_all_deprecated = getattr(matplotlib, "_all_deprecated", {})


# Recreate the validate function
matplotlib.rcParams.validate = dict(
    (key, converter)
    for key, (default, converter) in defaultParams.items()
    if key not in _all_deprecated
)

# Dimension lookup
SI_LENGTH = "si-length"
SI_LENGTH_RECIPROCAL = "si-length-reciprocal"
IMPERIAL_LENGTH = "imperial-length"
PIXEL_LENGTH = "pixel-length"
ANGLE = "angle"
TIME = "time"

_DIMENSION_LOOKUP = {
    SI_LENGTH: SILengthDimension,
    SI_LENGTH_RECIPROCAL: SILengthReciprocalDimension,
    IMPERIAL_LENGTH: ImperialLengthDimension,
    PIXEL_LENGTH: PixelLengthDimension,
    ANGLE: AngleDimension,
    TIME: TimeDimension
}


class DualScaleBar(Artist):

    zorder = 6

    _PREFERRED_VALUES = [1, 2, 5, 10, 15, 20,
                         25, 50, 75, 100, 125, 150, 200, 500, 750]

    _LOCATIONS = {
        "upper right": 1,
        "upper left": 2,
        "lower left": 3,
        "lower right": 4,
        "right": 5,
        "center left": 6,
        "center right": 7,
        "lower center": 8,
        "upper center": 9,
        "center": 10,
    }

    def __init__(
        self,
        dx,
        dy,
        units=("m", "m"),
        dimensions=("si-length", "si-length"),
        labels=(None, None),
        length_fraction=(None, None),
        height_fraction=None,
        width_fraction=None,
        location=None,
        loc=None,
        arrangement=None,
        pad=None,
        border_pad=None,
        sep=None,
        frameon=None,
        color=None,
        box_color=None,
        box_alpha=None,
        scale_loc=(None, None),
        label_loc=(None, None),
        font_properties=None,
        label_formatter=None,
        scale_formatter=None,
        fixed_value=None,
        fixed_units=None,
        animated=False,
    ):
        """
        Creates a new scale bar.

        There are two modes of operation:

          1. Length, value and units of the scale bar are automatically
             determined based on the specified pixel size *dx* / *dy* and
             *length_fraction*. The value will only take the following numbers:
             1, 2, 5, 10, 15, 20, 25, 50, 75, 100, 125, 150, 200, 500 or 750.
          2. The desired value and units are specified by the user
             (*fixed_value* and *fixed_units*) and the length is calculated
             based on the specified pixel size *dx* / *dy*.

        :arg dx: size of one pixel along the horizontal axis in *units*
            Set ``dx`` to 1.0 if the axes image has already been calibrated by
            setting its ``extent``, or if you are plotting non-image data.
        :type dx: :class:`float`

        :arg dy: size of one pixel along the horizontal axis in *units*
            Set ``dy`` to 1.0 if the axes image has already been calibrated by
            setting its ``extent``, or if you are plotting non-image data.
        :type dy: :class:`float`

        :arg units: units of *dx* and *dy* (default: `(``m``, ``m``)`)
        :type units: :class:`2-tuple` of `str`

        :arg dimension: dimensions of *dx* and *dy* for a given *units*.
            It can either be equal
                * ``:const:`si-length```: scale bar showing km, m, cm, etc.
                * ``:const:`imperial-length```: scale bar showing in, ft, yd, mi, etc.
                * ``:const:`si-length-reciprocal```: scale bar showing 1/m, 1/cm, etc.
                * ``:const:`pixel-length```: scale bar showing px, kpx, Mpx, etc.
                * ``:const:`angle```: scale bar showing \u00b0, \u2032 or \u2032\u2032.
                * a :class:`matplotlib_scalebar.dimension._Dimension` object
        :type dimension: :class:`2-tuple` of `str` or
            :class:`2-tuple` of `matplotlib_scalebar.dimension._Dimension`

        :arg label: optional labels associated with the scale bars
            (default: `(`None`, `None`)`, no label is shown)
        :type label: :class:`2-tuple` of `str`

        :arg length_fraction: lengths of the scale bars as a fraction of the
            axes' widths (default: rcParams['scalebar.length_fraction'] or ``(0.2, 0.2)``).
            This argument is ignored if a *fixed_value* is specified.
        :type length_fraction: :class:`2-tuple` of `float`

        :arg width_fraction: width of the scale bar as a fraction of the
            axes's height (default: rcParams['scalebar.width_fraction'] or ``0.01``)
        :type width_fraction: :class:`float`

        :arg location: the location for the scale bar to be plotted, expressed either
            as a location code (same as legend), or as an (x, y) location for the
            corner of the scale box to be placed (in figure coordinates). The corner
            placed at (x, y) depends on the value of *arrangement*.
            (default: rcParams['scalebar.location'] or ``upper right``)
        :type location: :class:`str` or `2-tuple` of `float`

        :arg loc: alias for location
        :type loc: :class:`str` or `2-tuple` of `float`

        :arg arrangement: the relative location for the corner of the dual scale bars:
            either the ``upper left``, ``upper right``, ``lower left``, or ``lower right``
            corner. The corner chosen in arrangement is the one placed at (x, y) if
            coordinates are passed to *location*.
            (default: rcParams['scalebar.arrangement'] or ``lower left``)
        :type arrangement: :class `str`

        :arg pad: axis coordinates
            (default: rcParams['scalebar.pad'] or ``0.2``)
        :type pad: :class:`float`

        :arg border_pad : axis coordinates
            (default: rcParams['scalebar.border_pad'] or ``0.1``)
        :type border_pad: :class:`float`

        :arg sep : separation between scale bars and labels in axis coordinates
            (default: rcParams['scalebar.sep'] or ``0.001``)
        :type sep: :class:`float`

        :arg frameon : if True, will draw a box around the scale bar
            and label (default: rcParams['scalebar.frameon'] or ``True``)
        :type frameon: :class:`bool`

        :arg color : color for the scale bar and label
            (default: rcParams['scalebar.color'] or ``k``)
        :type color: :class:`str`

        :arg box_color: color of the box (if *frameon*)
            (default: rcParams['scalebar.box_color'] or ``w``)
        :type box_color: :class:`str`

        :arg box_alpha: transparency of box
            (default: rcParams['scalebar.box_alpha'] or ``1.0``)
        :type box_alpha: :class:`float`

        :arg scale_loc : either ``upper left``, ``upper centre``, ``upper center``,
            ``upper right``, ``lower left``, ``lower centre``, ``lower center``,
            ``lower right`` or ``none``
            (default: rcParams['scalebar.scale_loc'] or `(``lower centre``, ``upper centre``)`).
            If ``none`` the scale is not shown.
        :type scale_loc: :class:`str`

        :arg scale_loc : either ``upper left``, ``upper centre``, ``upper center``,
            ``upper right``, ``lower left``, ``lower centre``, ``lower center``,
            ``lower right`` or ``none``
            (default: rcParams['scalebar.scale_loc'] or `(``upper centre``, ``lower centre``)`).
            If ``none`` the label is not shown.
        :type scale_loc: :class:`str`

        :arg font_properties: font properties of the label text, specified
            either as dict or `fontconfig <http://www.fontconfig.org/>`_
            pattern (XML).
        :type font_properties: :class:`matplotlib.font_manager.FontProperties`,
            :class:`str` or :class:`dict`

        :arg scale_formatter: function used to format the label. Needs to take
            the value (float) and the unit (str) as input and return the label
            string.
        :type scale_formatter: :class:`func`

        :arg fixed_value: values for the scale bars. If ``None``, the value is
            automatically determined based on *length_fraction*.
        :type fixed_value: :class:`2-tuple` of `float`

        :arg fixed_units: units of the *fixed_value*s. If ``None`` and
            *fixed_value* is not ``None``, the units of *dx* / *dy* are used.
        :type fixed_units: :class:`2-tuple` of `str`

        :arg animated: animation state (default: ``False``)
        :type animated: :class`bool`
        """
        Artist.__init__(self)

        # Deprecation
        if height_fraction is not None:
            warnings.warn(
                "The height_fraction argument was deprecated. Use width_fraction instead.",
                DeprecationWarning,
            )
            width_fraction = width_fraction or height_fraction

        if label_formatter is not None:
            warnings.warn(
                "The label_formatter argument was deprecated. Use scale_formatter instead.",
                DeprecationWarning,
            )
            scale_formatter = scale_formatter or label_formatter

        if loc is not None and self._convert_location(loc) != self._convert_location(
            location
        ):
            raise ValueError("loc and location are specified and not equal")

        # Convert location to bbox_to_anchor parameter, if required
        if isinstance(location, tuple):
            self.bbox_to_anchor = location
            self.location = arrangement
        else:
            self.bbox_to_anchor = None
            self.location = location or loc

        self.dx = dx
        self.dy = dy
        self.dimensions = dimensions  # Should be initialized before units
        self.units = units
        self.labels = labels
        self.length_fraction = length_fraction
        self.width_fraction = width_fraction
        self.arrangement = arrangement
        self.pad = pad
        self.border_pad = border_pad
        self.sep = sep
        self.frameon = frameon
        self.color = color
        self.box_color = box_color
        self.box_alpha = box_alpha
        self.scale_loc = scale_loc
        self.label_loc = label_loc
        self.scale_formatter = scale_formatter
        self.font_properties = font_properties
        self.fixed_value = fixed_value
        self.fixed_units = fixed_units
        self.set_animated(animated)

    def _calculate_best_length(self, length_pxs):
        newvalues, newunits = [None, None], [None, None]
        for i in range(2):
            d = self.dx if i == 0 else self.dy
            length_px = length_pxs[i]
            unit = self.units[i]
            value = length_px * d

            newvalue, newunit = self.dimensions[i].calculate_preferred(value, unit)
            newvalues[i], newunits[i] = newvalue, newunit

            factor = value / newvalue

            index = bisect.bisect_left(self._PREFERRED_VALUES, newvalue)
            if index > 0:
                # When we get the lowest index of the list, removing -1 will
                # return the last index.
                index -= 1
            newvalues[i] = self._PREFERRED_VALUES[index]

            length_pxs[i] = newvalue * factor / d

        return length_pxs, newvalues, newunits

    def _calculate_exact_length(self, d, dimension, current_units, value, units):
        newvalue = dimension.convert(value, units, current_units)
        return newvalue / d

    def draw(self, renderer, *args, **kwargs):
        if not self.get_visible():
            return
        if self.dx == 0 or self.dy == 0:
            return

        # Late import
        from matplotlib import rcParams

        # Deprecation
        if rcParams.get("scalebar.height_fraction") is not None:
            warnings.warn(
                "The scalebar.height_fraction parameter in matplotlibrc is deprecated. "
                "Use scalebar.width_fraction instead.",
                DeprecationWarning,
            )
            rcParams.setdefault(
                "scalebar.width_fraction", rcParams["scalebar.height_fraction"]
            )

        # Get parameters
        def _get_value(attr, default):
            value = getattr(self, attr)
            if value is None or value == (None, None):
                value = rcParams.get("scalebar." + attr, default)
            return value

        length_fraction = _get_value("length_fraction", (0.2, 0.2))
        width_fraction = _get_value("width_fraction", 0.01)
        location = _get_value("location", "upper right")
        pad = _get_value("pad", 0.2)
        border_pad = _get_value("border_pad", 0.1)
        sep = _get_value("sep", 0.001)
        frameon = _get_value("frameon", True)
        color = _get_value("color", "k")
        box_color = _get_value("box_color", "w")
        box_alpha = _get_value("box_alpha", 1.0)
        scale_loc = _get_value("scale_loc", ("lower centre", "upper centre"))
        label_loc = _get_value("label_loc", ("upper centre", "lower centre"))
        font_properties = self.font_properties
        fixed_value = self.fixed_value
        fixed_units = self.fixed_units or self.units
        labels = self.labels
        arrangement = _get_value("arrangement", "lower left")
        bbox_to_anchor = self.bbox_to_anchor

        # Create text properties
        textprops = {"color": color}
        if font_properties is not None:
            textprops["fontproperties"] = font_properties

        # Calculate value, units and length
        fig, ax = self.get_figure(), self.axes
        xlim = ax.get_xlim()
        ylim = ax.get_ylim()
        dx = abs(xlim[1] - xlim[0])
        dy = abs(ylim[1] - ylim[0])
        lims = [xlim, ylim]

        # Mode 1: Auto
        if self.fixed_value is None:
            length_pxs = [dx * length_fraction[0], dy * length_fraction[1]]
            length_pxs, values, units = self._calculate_best_length(length_pxs)

        # Mode 2: Fixed
        else:
            length_pxs = [None, None]
            for i in range(2):
                length_pxs[i] = self._calculate_exact_length(
                    self.dx if i == 0 else self.dy,
                    self.dimensions[i],
                    self.units[i],
                    fixed_value[i],
                    fixed_units[i]
                )

            values = fixed_value
            units = fixed_units

        self._fixed_value = values
        self._units = units

        # Compute bar widths for both x and y axes, accounting for difference in
        #     absolute value along the axes, and for non-square figures
        ax_ratio_corr = ax.bbox.width / ax.bbox.height
        bar_width_px_x = abs(xlim[1] - xlim[0]) * width_fraction
        bar_width_px_y = abs(ylim[1] - ylim[0]) * width_fraction * ax_ratio_corr

        # Create scale bars
        x_scale_rect = Rectangle(
            (0, 0) if "lower" in arrangement else (0, length_pxs[1] - bar_width_px_y),
            length_pxs[0],
            bar_width_px_y,
            fill=True,
            facecolor=color,
            edgecolor="none",
        )
        y_scale_rect = Rectangle(
            (0, 0) if "left" in arrangement else (length_pxs[0] - bar_width_px_x, 0),
            bar_width_px_x,
            length_pxs[1],
            fill=True,
            facecolor=color,
            edgecolor="none",
        )

        scale_bar_box = AuxTransformBox(ax.transData)
        scale_bar_box.add_artist(x_scale_rect)
        scale_bar_box.add_artist(y_scale_rect)

        # Create scale labels based on the plotted dimension
        scale_text = [
            dim.create_label(value, dim.to_latex(unit))
            for dim, unit, value in zip(self.dimensions, self.units, self._fixed_value)
        ]

        # Get dimensions and positions for textboxes
        all_texts = [*scale_text, *labels]
        all_text_locs = [*scale_loc, *label_loc]

        for i in range(4):
            text = all_texts[i]
            text_loc = all_text_locs[i]

            # Start from (0, 0) in axis coordinates
            bbox = ax.transAxes.inverted().transform(ax.transData.transform((0, 0)))

            # Calculate text coordinates based on text_locs and text dimensions
            if i in [0, 2]:  # label is being placed on the x-axis

                textprops["rotation"] = "horizontal"

                # Calculate text dimensions in axis coordinates
                # All divisions by dx or dy below are to convert to axis coordinates
                # Axis coordinates mean we don't have to calculate width_fraction or
                #     sep differently for each direction
                t = ax.text(0, 0, text, fontdict=textprops)
                text_dims = t.get_window_extent(renderer).transformed(ax.transAxes.inverted())

                # Calculate distances to move along the bars
                if "center" in text_loc or 'centre' in text_loc:
                    bbox[0] += ((length_pxs[0] / dx) - text_dims.width) / 2
                if "right" in text_loc:
                    bbox[0] += (length_pxs[0] / dx) - text_dims.width

                # Calculate distances to move towards / away from the bars
                if "upper" in text_loc:
                    bbox[1] += (width_fraction * ax_ratio_corr + 0.01) + sep
                if "lower" in text_loc:
                    bbox[1] -= text_dims.height + sep

                # Move labels to the top if the bar is placed to the top
                if "upper" in arrangement:
                    bbox[1] += (length_pxs[1] / dy) - width_fraction

                # Ensure labels don't intersect with bars for certain arrangements
                if "left" in text_loc and "left" in arrangement:
                    bbox[0] += (width_fraction + 0.01)
                if "right" in text_loc and "right" in arrangement:
                    bbox[0] -= (width_fraction + 0.01)

            if i in [1, 3]:  # label is being placed on the y-axis

                textprops["rotation"] = "vertical"

                # Calculate text dimensions in axis coordinates
                # All divisions by dx or dy below are to convert to axis coordinates
                t = ax.text(0.5, 0.5, text, fontdict=textprops)
                text_dims = t.get_window_extent(renderer).transformed(ax.transAxes.inverted())

                # Calculate distances to move along the bars
                if "center" in text_loc or 'centre' in text_loc:
                    bbox[1] += ((length_pxs[1] / dy) - text_dims.height) / 2
                if "right" in text_loc:
                    bbox[1] += (length_pxs[1] / dy) - text_dims.height

                # Calculate distances to move towards / away from the bars
                if "upper" in text_loc:
                    bbox[0] -= text_dims.width + sep
                if "lower" in text_loc:
                    bbox[0] += (width_fraction + 0.01) + sep

                # Move labels to the right if the bar is placed to the right
                if "right" in arrangement:
                    bbox[0] += (length_pxs[0] / dx) - width_fraction

                # Ensure labels don't intersect with bars for certain arrangements
                if "left" in text_loc and "lower" in arrangement:
                    bbox[1] += (width_fraction + 0.01)
                if "right" in text_loc and "upper" in arrangement:
                    bbox[1] -= (width_fraction + 0.01)

                # Ensure labels don't intersect with each other for certain arrangements
                if (arrangement == "lower left" and text_loc == 'lower left'
                   and ('upper left' in all_text_locs[0] or 'upper left' in all_text_locs[2])):
                    bbox[1] += (text_dims.width + 0.01)
                if (arrangement == "lower right" and text_loc == 'upper left'
                   and ('upper right' in all_text_locs[0] or 'upper right' in all_text_locs[2])):
                    bbox[1] += (text_dims.width + 0.01)
                if (arrangement == "upper left" and text_loc == 'lower right'
                   and ('lower left' in all_text_locs[0] or 'lower left' in all_text_locs[2])):
                    bbox[1] -= (text_dims.width + 0.01)
                if (arrangement == "upper right" and text_loc == 'upper right'
                   and ('lower right' in all_text_locs[0] or 'lower right' in all_text_locs[2])):
                    bbox[1] -= (text_dims.width + 0.01)

            # Convert text location from axis coordinates to data coordinates, then
            #     recreate text at correct location to place alongside scale bars
            bbox = ax.transData.inverted().transform(ax.transAxes.transform(bbox))
            t = ax.text(*bbox, text, fontdict=textprops)
            scale_bar_box.add_artist(t)

        # Anchor bars and labels to specific location and draw
        box = AnchoredOffsetbox(
            loc=location, pad=pad, borderpad=border_pad,
            child=scale_bar_box,
            frameon=frameon, bbox_to_anchor=bbox_to_anchor,
            bbox_transform=ax.transAxes
        )
        box.axes = ax
        box.set_figure(self.get_figure())
        box.patch.set_color(box_color)
        box.patch.set_alpha(box_alpha)
        box.draw(renderer)

    # Create getters and setters
    def get_dx(self):
        return self._dx

    def set_dx(self, dx):
        self._dx = float(dx)

    dx = property(get_dx, set_dx)

    def get_dy(self):
        return self._dy

    def set_dy(self, dy):
        self._dy = float(dy)

    dy = property(get_dy, set_dy)

    def get_dimensions(self):
        return self._dimensions

    def set_dimensions(self, dimensions):
        new_dimensions = [None, None]
        for i, dimension in enumerate(dimensions):
            if dimension in _DIMENSION_LOOKUP:
                dimension = _DIMENSION_LOOKUP[dimension]()

            if not isinstance(dimension, _Dimension):
                raise ValueError(
                    f"Unknown dimension: {dimension}. "
                    f"Known dimensions: {', '.join(_DIMENSION_LOOKUP)}"
                )

            new_dimensions[i] = dimension

        self._dimensions = tuple(new_dimensions)

    dimensions = property(get_dimensions, set_dimensions)

    def get_units(self):
        return self._units

    def set_units(self, units):
        for i in range(2):
            if not self._dimensions[i].is_valid_units(units[i]):
                raise ValueError(f"Invalid unit ({units[i]}) with dimension "
                                 f"({self._dimensions[i].__class__.__name__})")
        self._units = units

    units = property(get_units, set_units)

    def get_label(self):
        return self._label

    def set_label(self, label):
        self._label = label

    label = property(get_label, set_label)

    def get_length_fraction(self):
        return self._length_fraction

    def set_length_fraction(self, fractions):
        for fraction in fractions:
            if fraction is not None:
                fraction = float(fraction)
                if fraction <= 0.0 or fraction > 1.0:
                    raise ValueError("Length fraction must be between [0.0, 1.0]")
        self._length_fraction = fractions

    length_fraction = property(get_length_fraction, set_length_fraction)

    def get_width_fraction(self):
        return self._width_fraction

    def set_width_fraction(self, fraction):
        if fraction is not None:
            fraction = float(fraction)
            if fraction <= 0.0 or fraction > 1.0:
                raise ValueError("Width fraction must be between [0.0, 1.0]")
        self._width_fraction = fraction

    width_fraction = property(get_width_fraction, set_width_fraction)

    def get_height_fraction(self):
        warnings.warn(
            "The get_height_fraction method is deprecated. Use get_width_fraction instead.",
            DeprecationWarning,
        )
        return self.width_fraction

    def set_height_fraction(self, fraction):
        warnings.warn(
            "The set_height_fraction method is deprecated. Use set_width_fraction instead.",
            DeprecationWarning,
        )
        self.width_fraction = fraction

    height_fraction = property(get_height_fraction, set_height_fraction)

    @classmethod
    def _convert_location(cls, loc):
        if isinstance(loc, str):
            if loc not in cls._LOCATIONS:
                raise ValueError(
                    f"Unknown location: {loc}. "
                    f"Valid locations: {', '.join(cls._LOCATIONS)}"
                )
            loc = cls._LOCATIONS[loc]
        return loc

    def get_location(self):
        return self._location

    def set_location(self, loc):
        if isinstance(loc, tuple):
            self._bbox_to_anchor = loc
            self._location = 3
        else:
            self._bbox_to_anchor = None
            self._location = self._convert_location(loc)

    location = property(get_location, set_location)

    get_loc = get_location
    set_loc = set_location
    loc = location

    def get_arrangement(self):
        return self._arrangement

    def set_arrangement(self, arrangement):
        self._arrangement = arrangement

    arrangement = property(get_arrangement, set_arrangement)

    def get_pad(self):
        return self._pad

    def set_pad(self, pad):
        self._pad = pad

    pad = property(get_pad, set_pad)

    def get_border_pad(self):
        return self._border_pad

    def set_border_pad(self, pad):
        self._border_pad = pad

    border_pad = property(get_border_pad, set_border_pad)

    def get_sep(self):
        return self._sep

    def set_sep(self, sep):
        self._sep = sep

    sep = property(get_sep, set_sep)

    def get_frameon(self):
        return self._frameon

    def set_frameon(self, on):
        self._frameon = on

    frameon = property(get_frameon, set_frameon)

    def get_color(self):
        return self._color

    def set_color(self, color):
        self._color = color

    color = property(get_color, set_color)

    def get_box_color(self):
        return self._box_color

    def set_box_color(self, color):
        self._box_color = color

    box_color = property(get_box_color, set_box_color)

    def get_box_alpha(self):
        return self._box_alpha

    def set_box_alpha(self, alpha):
        if alpha is not None:
            alpha = float(alpha)
            if alpha < 0.0 or alpha > 1.0:
                raise ValueError("Alpha must be between [0.0, 1.0]")
        self._box_alpha = alpha

    box_alpha = property(get_box_alpha, set_box_alpha)

    def get_scale_loc(self):
        return self._scale_loc

    def set_scale_loc(self, locs):
        for loc in locs:
            if loc is not None and loc not in _VALID_TEXT_LOCATIONS:
                raise ValueError(
                    f"Unknown location: {loc}. "
                    f"Valid locations: {', '.join(_VALID_TEXT_LOCATIONS)}"
                )
        self._scale_loc = locs

    scale_loc = property(get_scale_loc, set_scale_loc)

    def get_label_loc(self):
        return self._label_loc

    def set_label_loc(self, locs):
        for loc in locs:
            if loc is not None and loc not in _VALID_TEXT_LOCATIONS:
                raise ValueError(
                    f"Unknown location: {loc}. "
                    f"Valid locations: {', '.join(_VALID_TEXT_LOCATIONS)}"
                )

        self._label_loc = locs

    label_loc = property(get_label_loc, set_label_loc)

    def get_font_properties(self):
        return self._font_properties

    def set_font_properties(self, props):
        if props is None:
            props = FontProperties()
        elif isinstance(props, dict):
            props = FontProperties(**props)
        elif isinstance(props, str):
            props = FontProperties(props)
        else:
            raise ValueError(
                "Unsupported `font_properties`. "
                "Pass either a dict or a font config pattern as string."
            )
        self._font_properties = props

    font_properties = property(get_font_properties, set_font_properties)

    def get_scale_formatter(self):
        if self._scale_formatter is None:
            return [self.dimensions[0].create_label, self.dimensions[1].create_label]
        return self._scale_formatter

    def set_scale_formatter(self, scale_formatter):
        self._scale_formatter = scale_formatter

    scale_formatter = property(get_scale_formatter, set_scale_formatter)

    def get_label_formatter(self):
        warnings.warn(
            "The get_label_formatter method is deprecated. Use get_scale_formatter instead.",
            DeprecationWarning,
        )
        return self.scale_formatter

    def set_label_formatter(self, scale_formatter):
        warnings.warn(
            "The set_label_formatter method is deprecated. Use set_scale_formatter instead.",
            DeprecationWarning,
        )
        self.scale_formatter = scale_formatter

    label_formatter = property(get_label_formatter, set_label_formatter)

    def get_fixed_value(self):
        return self._fixed_value

    def set_fixed_value(self, value):
        self._fixed_value = value

    fixed_value = property(get_fixed_value, set_fixed_value)

    def get_fixed_units(self):
        return self._fixed_units

    def set_fixed_units(self, units):
        self._fixed_units = units

    fixed_units = property(get_fixed_units, set_fixed_units)
