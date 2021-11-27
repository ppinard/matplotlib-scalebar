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
    TextArea,
    VPacker,
    HPacker,
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
)

# Globals and constants variables.

# Setup of extra parameters in the matplotlic rc
_VALID_SCALE_LOCATIONS = ["bottom", "top", "right", "left", "none"]
_validate_scale_loc = ValidateInStrings(
    "scale_loc", _VALID_SCALE_LOCATIONS, ignorecase=True
)

_VALID_LABEL_LOCATIONS = ["bottom", "top", "right", "left", "none"]
_validate_label_loc = ValidateInStrings(
    "label_loc", _VALID_LABEL_LOCATIONS, ignorecase=True
)

_VALID_ROTATIONS = ["horizontal", "vertical"]
_validate_rotation = ValidateInStrings("rotation", _VALID_ROTATIONS, ignorecase=True)


def _validate_legend_loc(loc):
    rc = matplotlib.RcParams()
    rc["legend.loc"] = loc
    return loc


defaultParams.update(
    {
        "scalebar.length_fraction": [0.2, validate_float],
        "scalebar.width_fraction": [0.01, validate_float],
        "scalebar.location": ["upper right", _validate_legend_loc],
        "scalebar.pad": [0.2, validate_float],
        "scalebar.border_pad": [0.1, validate_float],
        "scalebar.sep": [5, validate_float],
        "scalebar.frameon": [True, validate_bool],
        "scalebar.color": ["k", validate_color],
        "scalebar.box_color": ["w", validate_color],
        "scalebar.box_alpha": [1.0, validate_float],
        "scalebar.scale_loc": ["bottom", _validate_scale_loc],
        "scalebar.label_loc": ["top", _validate_label_loc],
        "scalebar.rotation": ["horizontal", _validate_rotation],
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

_DIMENSION_LOOKUP = {
    SI_LENGTH: SILengthDimension,
    SI_LENGTH_RECIPROCAL: SILengthReciprocalDimension,
    IMPERIAL_LENGTH: ImperialLengthDimension,
    PIXEL_LENGTH: PixelLengthDimension,
    ANGLE: AngleDimension,
}


class ScaleBar(Artist):

    zorder = 6

    _PREFERRED_VALUES = [1, 2, 5, 10, 15, 20, 25, 50, 75, 100, 125, 150, 200, 500, 750]

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
        units="m",
        dimension="si-length",
        label=None,
        length_fraction=None,
        height_fraction=None,
        width_fraction=None,
        location=None,
        loc=None,
        pad=None,
        border_pad=None,
        sep=None,
        frameon=None,
        color=None,
        box_color=None,
        box_alpha=None,
        scale_loc=None,
        label_loc=None,
        font_properties=None,
        label_formatter=None,
        scale_formatter=None,
        fixed_value=None,
        fixed_units=None,
        animated=False,
        rotation=None,
    ):
        """
        Creates a new scale bar.

        There are two modes of operation:

          1. Length, value and units of the scale bar are automatically
             determined based on the specified pixel size *dx* and
             *length_fraction*. The value will only take the following numbers:
             1, 2, 5, 10, 15, 20, 25, 50, 75, 100, 125, 150, 200, 500 or 750.
          2. The desired value and units are specified by the user
             (*fixed_value* and *fixed_units*) and the length is calculated
             based on the specified pixel size *dx*.

        :arg dx: size of one pixel in *units*
            Set ``dx`` to 1.0 if the axes image has already been calibrated by
            setting its ``extent``.
        :type dx: :class:`float`

        :arg units: units of *dx* (default: ``m``)
        :type units: :class:`str`

        :arg dimension: dimension of *dx* and *units*.
            It can either be equal
                * ``:const:`si-length```: scale bar showing km, m, cm, etc.
                * ``:const:`imperial-length```: scale bar showing in, ft, yd, mi, etc.
                * ``:const:`si-length-reciprocal```: scale bar showing 1/m, 1/cm, etc.
                * ``:const:`pixel-length```: scale bar showing px, kpx, Mpx, etc.
                * ``:const:`angle```: scale bar showing \u00b0, \u2032 or \u2032\u2032.
                * a :class:`matplotlib_scalebar.dimension._Dimension` object
        :type dimension: :class:`str` or
            :class:`matplotlib_scalebar.dimension._Dimension`

        :arg label: optional label associated with the scale bar
            (default: ``None``, no label is shown)
        :type label: :class:`str`

        :arg length_fraction: length of the scale bar as a fraction of the
            axes's width (default: rcParams['scalebar.lenght_fraction'] or ``0.2``).
            This argument is ignored if a *fixed_value* is specified.
        :type length_fraction: :class:`float`

        :arg width_fraction: width of the scale bar as a fraction of the
            axes's height (default: rcParams['scalebar.width_fraction'] or ``0.01``)
        :type width_fraction: :class:`float`

        :arg location: a location code (same as legend)
            (default: rcParams['scalebar.location'] or ``upper right``)
        :type location: :class:`str`

        :arg loc: alias for location
        :type loc: :class:`str`

        :arg pad: fraction of the font size
            (default: rcParams['scalebar.pad'] or ``0.2``)
        :type pad: :class:`float`

        :arg border_pad : fraction of the font size
            (default: rcParams['scalebar.border_pad'] or ``0.1``)
        :type border_pad: :class:`float`

        :arg sep : separation between scale bar and label in points
            (default: rcParams['scalebar.sep'] or ``5``)
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

        :arg scale_loc : either ``bottom``, ``top``, ``left``, ``right``, ``none``
            (default: rcParams['scalebar.scale_loc'] or ``bottom``).
            If ``none`` the scale is not shown.
        :type scale_loc: :class:`str`

        :arg label_loc: either ``bottom``, ``top``, ``left``, ``right``, ``none``
            (default: rcParams['scalebar.label_loc'] or ``top``).
            If ``none`` the label is not shown.
        :type label_loc: :class:`str`

        :arg font_properties: font properties of the label text, specified
            either as dict or `fontconfig <http://www.fontconfig.org/>`_
            pattern (XML).
        :type font_properties: :class:`matplotlib.font_manager.FontProperties`,
            :class:`str` or :class:`dict`

        :arg scale_formatter: function used to format the label. Needs to take
            the value (float) and the unit (str) as input and return the label
            string.
        :type scale_formatter: :class:`func`

        :arg fixed_value: value for the scale bar. If ``None``, the value is
            automatically determined based on *length_fraction*.
        :type fixed_value: :class:`float`

        :arg fixed_units: units of the *fixed_value*. If ``None`` and
            *fixed_value* is not ``None``, the units of *dx* are used.
        :type fixed_units: :class:`str`

        :arg animated: animation state (default: ``False``)
        :type animated: :class`bool`

        :arg rotation: either ``horizontal`` or ``vertical``
            (default: rcParams['scalebar.rotation'] or ``horizontal``)
        :type rotation: :class:`str`
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

        self.dx = dx
        self.dimension = dimension  # Should be initialize before units
        self.units = units
        self.label = label
        self.length_fraction = length_fraction
        self.width_fraction = width_fraction
        self.location = location or loc
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
        self.rotation = rotation

    def _calculate_best_length(self, length_px):
        dx = self.dx
        units = self.units
        value = length_px * dx

        newvalue, newunits = self.dimension.calculate_preferred(value, units)
        factor = value / newvalue

        index = bisect.bisect_left(self._PREFERRED_VALUES, newvalue)
        if index > 0:
            # When we get the lowest index of the list, removing -1 will
            # return the last index.
            index -= 1
        newvalue = self._PREFERRED_VALUES[index]

        length_px = newvalue * factor / dx

        return length_px, newvalue, newunits

    def _calculate_exact_length(self, value, units):
        newvalue = self.dimension.convert(value, units, self.units)
        return newvalue / self.dx

    def draw(self, renderer, *args, **kwargs):
        if not self.get_visible():
            return
        if self.dx == 0:
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
            if value is None:
                value = rcParams.get("scalebar." + attr, default)
            return value

        length_fraction = _get_value("length_fraction", 0.2)
        width_fraction = _get_value("width_fraction", 0.01)
        location = _get_value("location", "upper right")
        if isinstance(location, str):
            location = self._LOCATIONS[location.lower()]
        pad = _get_value("pad", 0.2)
        border_pad = _get_value("border_pad", 0.1)
        sep = _get_value("sep", 5)
        frameon = _get_value("frameon", True)
        color = _get_value("color", "k")
        box_color = _get_value("box_color", "w")
        box_alpha = _get_value("box_alpha", 1.0)
        scale_loc = _get_value("scale_loc", "bottom").lower()
        label_loc = _get_value("label_loc", "top").lower()
        font_properties = self.font_properties
        fixed_value = self.fixed_value
        fixed_units = self.fixed_units or self.units
        rotation = _get_value("rotation", "horizontal").lower()
        label = self.label

        # Create text properties
        textprops = {"color": color, "rotation": rotation}
        if font_properties is not None:
            textprops["fontproperties"] = font_properties

        # Calculate value, units and length
        ax = self.axes
        xlim = ax.get_xlim()
        ylim = ax.get_ylim()
        if rotation == "vertical":
            xlim, ylim = ylim, xlim

        # Mode 1: Auto
        if self.fixed_value is None:
            length_px = abs(xlim[1] - xlim[0]) * length_fraction
            length_px, value, units = self._calculate_best_length(length_px)

        # Mode 2: Fixed
        else:
            value = fixed_value
            units = fixed_units
            length_px = self._calculate_exact_length(value, units)

        scale_text = self.scale_formatter(value, self.dimension.to_latex(units))

        width_px = abs(ylim[1] - ylim[0]) * width_fraction

        # Create scale bar
        if rotation == "horizontal":
            scale_rect = Rectangle(
                (0, 0),
                length_px,
                width_px,
                fill=True,
                facecolor=color,
                edgecolor="none",
            )
        else:
            scale_rect = Rectangle(
                (0, 0),
                width_px,
                length_px,
                fill=True,
                facecolor=color,
                edgecolor="none",
            )

        scale_bar_box = AuxTransformBox(ax.transData)
        scale_bar_box.add_artist(scale_rect)

        # Create scale text
        if scale_loc != "none":
            scale_text_box = TextArea(scale_text, textprops=textprops)

            if scale_loc in ["bottom", "right"]:
                children = [scale_bar_box, scale_text_box]
            else:
                children = [scale_text_box, scale_bar_box]

            if scale_loc in ["bottom", "top"]:
                Packer = VPacker
            else:
                Packer = HPacker

            scale_box = Packer(children=children, align="center", pad=0, sep=sep)

        else:
            scale_box = scale_bar_box

        # Create label
        if label and label_loc != "none":
            label_box = TextArea(label, textprops=textprops)
        else:
            label_box = None

        # Create final offset box
        if label_box:
            if label_loc in ["bottom", "right"]:
                children = [scale_box, label_box]
            else:
                children = [label_box, scale_box]

            if label_loc in ["bottom", "top"]:
                Packer = VPacker
            else:
                Packer = HPacker

            child = Packer(children=children, align="center", pad=0, sep=sep)
        else:
            child = scale_box

        box = AnchoredOffsetbox(
            loc=location, pad=pad, borderpad=border_pad, child=child, frameon=frameon
        )

        box.axes = ax
        box.set_figure(self.get_figure())
        box.patch.set_color(box_color)
        box.patch.set_alpha(box_alpha)
        box.draw(renderer)

    def get_dx(self):
        return self._dx

    def set_dx(self, dx):
        self._dx = float(dx)

    dx = property(get_dx, set_dx)

    def get_dimension(self):
        return self._dimension

    def set_dimension(self, dimension):
        if dimension in _DIMENSION_LOOKUP:
            dimension = _DIMENSION_LOOKUP[dimension]()

        if not isinstance(dimension, _Dimension):
            raise ValueError(
                f"Unknown dimension: {dimension}. "
                f"Known dimensions: {', '.join(_DIMENSION_LOOKUP)}"
            )

        self._dimension = dimension

    dimension = property(get_dimension, set_dimension)

    def get_units(self):
        return self._units

    def set_units(self, units):
        if not self.dimension.is_valid_units(units):
            raise ValueError(f"Invalid unit ({units}) with dimension")
        self._units = units

    units = property(get_units, set_units)

    def get_label(self):
        return self._label

    def set_label(self, label):
        self._label = label

    label = property(get_label, set_label)

    def get_length_fraction(self):
        return self._length_fraction

    def set_length_fraction(self, fraction):
        if fraction is not None:
            fraction = float(fraction)
            if fraction <= 0.0 or fraction > 1.0:
                raise ValueError("Length fraction must be between [0.0, 1.0]")
        self._length_fraction = fraction

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
        self._location = self._convert_location(loc)

    location = property(get_location, set_location)

    get_loc = get_location
    set_loc = set_location
    loc = location

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

    def set_scale_loc(self, loc):
        if loc is not None and loc not in _VALID_SCALE_LOCATIONS:
            raise ValueError(
                f"Unknown location: {loc}. "
                f"Valid locations: {', '.join(_VALID_SCALE_LOCATIONS)}"
            )
        self._scale_loc = loc

    scale_loc = property(get_scale_loc, set_scale_loc)

    def get_label_loc(self):
        return self._label_loc

    def set_label_loc(self, loc):
        if loc is not None and loc not in _VALID_LABEL_LOCATIONS:
            raise ValueError(
                f"Unknown location: {loc}. "
                f"Valid locations: {', '.join(_VALID_LABEL_LOCATIONS)}"
            )

        self._label_loc = loc

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
            return self.dimension.create_label
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

    def get_rotation(self):
        return self._rotation

    def set_rotation(self, rotation):
        if rotation is not None and rotation not in _VALID_ROTATIONS:
            raise ValueError(
                f"Unknown rotation: {rotation}. "
                f"Valid locations: {', '.join(_VALID_ROTATIONS)}"
            )
        self._rotation = rotation

    rotation = property(get_rotation, set_rotation)
