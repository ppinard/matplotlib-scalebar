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
    - scalebar.label_top
    
See the class documentation (:class:`.Scalebar`) for a description of the 
parameters. 
"""

# Standard library modules.
import sys
import bisect
from operator import itemgetter
import imp

# Third party modules.
from matplotlib.artist import Artist
from matplotlib.cbook import is_string_like
from matplotlib.font_manager import FontProperties
from matplotlib.rcsetup import \
    (defaultParams, validate_float, validate_legend_loc, validate_bool,
     validate_color)

from mpl_toolkits.axes_grid.anchored_artists import AnchoredSizeBar

# Local modules.
_PREFIXES_VALUES = {'Y': 1e24, 'Z': 1e21, 'E': 1e18, 'P': 1e15, 'T': 1e12,
                    'G': 1e9, 'M': 1e6, 'k': 1e3, 'm': 1e-3, u'\u00b5': 1e-6,
                    'u': 1e-6, 'n': 1e-9, 'p': 1e-12, 'f': 1e-15, 'a': 1e-18,
                    'z': 1e-21, 'y': 1e-24}

# Globals and constants variables.

# Setup of extra parameters in the matplotlic rc
defaultParams.update(
    {'scalebar.length_fraction': [0.2, validate_float],
     'scalebar.height_fraction': [0.01, validate_float],
     'scalebar.location': ['upper right', validate_legend_loc],
     'scalebar.pad': [0.2, validate_float],
     'scalebar.border_pad': [0.1, validate_float],
     'scalebar.sep': [5, validate_float],
     'scalebar.frameon': [True, validate_bool],
     'scalebar.color': ['k', validate_color],
     'scalebar.box_color': ['w', validate_color],
     'scalebar.box_alpha': [1.0, validate_float],
     'scalebar.label_top': [False, validate_bool],
     })

# Reload matplotlib to reset the default parameters
imp.reload(sys.modules['matplotlib'])

class ScaleBar(Artist):

    zorder = 6

    _PREFERRED_VALUES = [1, 2, 5, 10, 15, 20, 25, 50, 75, 100, 125, 150, 200, 500, 750]

    _LOCATIONS = {'upper right':  1,
                  'upper left':   2,
                  'lower left':   3,
                  'lower right':  4,
                  'right':        5,
                  'center left':  6,
                  'center right': 7,
                  'lower center': 8,
                  'upper center': 9,
                  'center':       10,
              }

    def __init__(self, dx_m, length_fraction=None, height_fraction=None,
                 location=None, pad=None, border_pad=None, sep=None,
                 frameon=None, color=None, box_color=None, box_alpha=None,
                 label_top=None, font_properties=None):
        """
        Creates a new scale bar.
        
        :arg dx_m: dimension of one pixel in meters (m)
            Set ``dx_m`` to 1.0 if the axes image has already been calibrated by
            setting its ``extent``.
        :arg length_fraction: length of the scale bar as a fraction of the 
            axes's width (default: rcParams['scalebar.lenght_fraction'] or ``0.2``)
        :arg height_fraction: height of the scale bar as a fraction of the 
            axes's height (default: rcParams['scalebar.height_fraction'] or ``0.01``)
        :arg location: a location code (same as legend)
            (default: rcParams['scalebar.location'] or ``upper right``)
        :arg pad: fraction of the font size
            (default: rcParams['scalebar.pad'] or ``0.2``)
        :arg border_pad : fraction of the font size
            (default: rcParams['scalebar.border_pad'] or ``0.1``)
        :arg sep : separation between scale bar and label in points
            (default: rcParams['scalebar.sep'] or ``5``)
        :arg frameon : if True, will draw a box around the scale bar 
            and label (default: rcParams['scalebar.frameon'] or ``True``)
        :arg color : color for the scale bar and label
            (default: rcParams['scalebar.color'] or ``k``)
        :arg box_color: color of the box (if *frameon*)
            (default: rcParams['scalebar.box_color'] or ``w``)
        :arg box_alpha: transparency of box
            (default: rcParams['scalebar.box_alpha'] or ``1.0``)
        :arg label_top : if True, the label will be over the scale bar
            (default: rcParams['scalebar.label_top'] or ``False``)
        :arg font_properties: a matplotlib.font_manager.FontProperties instance, 
            optional sets the font properties for the label text
        """
        Artist.__init__(self)

        self.dx_m = dx_m
        self.length_fraction = length_fraction
        self.height_fraction = height_fraction
        self.location = location
        self.pad = pad
        self.border_pad = border_pad
        self.sep = sep
        self.frameon = frameon
        self.color = color
        self.box_color = box_color
        self.box_alpha = box_alpha
        self.label_top = label_top
        self.font_properties = FontProperties(font_properties)

    def _calculate_length(self, length_px):
        dx_m = self.dx_m
        length_m = length_px * dx_m

        prefixes_values = _PREFIXES_VALUES.copy()
        prefixes_values[''] = 1.0
        prefixes_values.pop('u')
        prefixes_values = sorted(prefixes_values.items(), key=itemgetter(1))
        values = [prefix_value[1] for prefix_value in prefixes_values]
        index = bisect.bisect_left(values, length_m)
        unit, factor = prefixes_values[index - 1]

        length_unit = length_m / factor
        index = bisect.bisect_left(self._PREFERRED_VALUES, length_unit)
        length_unit = self._PREFERRED_VALUES[index - 1]

        length_px = length_unit * factor / dx_m
        label = '%i %sm' % (length_unit, unit)

        return length_px, label

    def draw(self, renderer, *args, **kwargs):
        if not self.get_visible():
            return
        if self.dx_m == 0:
            return

        # Get parameters
        from matplotlib import rcParams # late import

        length_fraction = self.length_fraction or \
            rcParams.get('scalebar.length_fraction', 0.2)
        height_fraction = self.height_fraction or \
            rcParams.get('scalebar.height_fraction', 0.01)
        location = self.location or \
            self._LOCATIONS[rcParams.get('scalebar.location', 'upper right')]
        pad = self.pad or rcParams.get('scalebar.pad', 0.2)
        border_pad = self.border_pad or \
            rcParams.get('scalebar.border_pad', 0.1)
        sep = self.sep or rcParams.get('scalebar.sep', 5)
        frameon = self.frameon or rcParams.get('scalebar.frameon', True)
        color = self.color or rcParams.get('scalebar.color', 'k')
        box_color = self.box_color or rcParams.get('scalebar.box_color', 'w')
        box_alpha = self.box_alpha or rcParams.get('scalebar.box_alpha', 1.0)
        label_top = self.label_top or rcParams.get('scalebar.label_top', False)
        font_properties = self.font_properties

        ax = self.axes
        xlim, ylim = ax.get_xlim(), ax.get_ylim()

        # Calculate dimensions
        length_px = abs(xlim[1] - xlim[0]) * length_fraction
        length_px, label = self._calculate_length(length_px)

        size_vertical = abs(ylim[1] - ylim[0]) * height_fraction

        # Create sizebar
        sizebar = AnchoredSizeBar(transform=ax.transData,
                                  size=length_px,
                                  label=label,
                                  loc=location,
                                  pad=pad,
                                  borderpad=border_pad,
                                  sep=sep,
                                  frameon=frameon,
                                  size_vertical=size_vertical,
                                  color=color,
                                  label_top=label_top,
                                  fontproperties=font_properties)
        sizebar.axes = ax
        sizebar.set_figure(self.get_figure())
        sizebar.patch.set_color(box_color)
        sizebar.patch.set_alpha(box_alpha)
        sizebar.draw(renderer)

    def get_dx_m(self):
        return self._dx_m

    def set_dx_m(self, dx_m):
        self._dx_m = float(dx_m)

    dx_m = property(get_dx_m, set_dx_m)

    def get_length_fraction(self):
        return self._length_fraction

    def set_length_fraction(self, fraction):
        if fraction is not None:
            fraction = float(fraction)
            if fraction <= 0.0 or fraction > 1.0:
                raise ValueError('Length fraction must be between [0.0, 1.0]')
        self._length_fraction = fraction

    length_fraction = property(get_length_fraction, set_length_fraction)

    def get_height_fraction(self):
        return self._height_fraction

    def set_height_fraction(self, fraction):
        if fraction is not None:
            fraction = float(fraction)
            if fraction <= 0.0 or fraction > 1.0:
                raise ValueError('Height fraction must be between [0.0, 1.0]')
        self._height_fraction = fraction

    height_fraction = property(get_height_fraction, set_height_fraction)

    def get_location(self):
        return self._location

    def set_location(self, loc):
        if is_string_like(loc):
            if loc not in self._LOCATIONS:
                raise ValueError('Unknown location code: %s' % loc)
            loc = self._LOCATIONS[loc]
        self._location = loc

    location = property(get_location, set_location)

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
                raise ValueError('Alpha must be between [0.0, 1.0]')
        self._box_alpha = alpha

    box_alpha = property(get_box_alpha, set_box_alpha)

    def get_label_top(self):
        return self._label_top

    def set_label_top(self, top):
        self._label_top = top

    label_top = property(get_label_top, set_label_top)

    def get_font_properties(self):
        return self._font_properties

    def set_font_properties(self, props):
        self._font_properties = props

    font_properties = property(get_font_properties, set_font_properties)