matplotlib-scalebar
===================

.. image:: https://travis-ci.org/ppinard/matplotlib-scalebar.svg
   :target: https://travis-ci.org/ppinard/matplotlib-scalebar
   
.. image:: https://badge.fury.io/py/matplotlib-scalebar.svg
   :target: http://badge.fury.io/py/matplotlib-scalebar

Provides a new artist for matplotlib to display a scale bar, aka micron bar.
It is particularly useful when displaying calibrated images plotted using 
plt.imshow(...). 

.. image:: https://raw.githubusercontent.com/ppinard/matplotlib-scalebar/master/doc/example1.png

The artist supports customization either directly from the **ScaleBar** object or
from the matplotlibrc.

Installation
------------

Easiest way to install using ``pip``::

    $ pip install matplotlib-scalebar
    
For development installation from the git repository::

    $ git clone git@github.com:ppinard/matplotlib-scalebar.git
    $ pip install -e matplotlib-scalebar

Example
-------

Here is an example how to add a scale bar::

   >>> import matplotlib.pyplot as plt
   >>> import matplotlib.cbook as cbook
   >>> from matplotlib_scalebar.scalebar import ScaleBar
   >>> plt.figure()
   >>> image = plt.imread(cbook.get_sample_data('grace_hopper.png'))
   >>> plt.imshow(image)
   >>> scalebar = ScaleBar(0.2) # 1 pixel = 0.2 meter
   >>> plt.gca().add_artist(scalebar)
   >>> plt.show()
   
matplotlibrc parameters
-----------------------

Here are parameters that can either be customized in the constructor of the
**ScaleBar** class or in the matplotlibrc file.

  * ``scalebar.length_fraction``: length of the scale bar as a fraction of the 
    axes's width (default: ``0.2``)
  * ``scalebar.height_fraction``: height of the scale bar as a fraction of the 
    axes's height (default: ``0.01``)
  * ``scalebar.location``: a location code (same as legend)
    (default: ``upper right``)
  * ``scalebar.pad``: fraction of the font size (default: ``0.2``)
  * ``scalebar.border_pad``: fraction of the font size (default: ``0.1``)
  * ``scalebar.sep``: separation between scale bar and label in points 
    (default: ``5``)
  * ``scalebar.frameon``: if True, will draw a box around the scale bar 
    and label (default: ``True``)
  * ``scalebar.color``: color for the scale bar and label (default: ``k``)
  * ``scalebar.box_color``: color of the box (if *frameon*) (default: ``w``)
  * ``scalebar.box_alpha``: transparency of box (default: ``1.0``)
  * ``scalebar.label_top``: if True, the label will be over the scale bar
    (default: ``False``)
  * ``scalebar.font_properties``: a matplotlib.font_manager.FontProperties instance, 
    optional sets the font properties for the label text

License
-------

License under the BSD License, compatible with matplotlib.

Copyright (c) 2015 Philippe Pinard
