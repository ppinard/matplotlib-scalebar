matplotlib-scalebar
===================

Provides a new artist for matplotlib to display a scale bar, aka micron bar.
It is particularly useful when displaying calibrated images plotted using 
plt.imshow(...). 

The artist supports customization either directly from the *Scalebar* object or
from the matplotlibrc.

Installation
------------

Easiest way to install using ``pip``::

    $ pip install matplotlib-scalebar
    
For development installation from the git repository::

    $ git pull 
    $ pip install -e matplotlib-scalebar

Example
-------

Here is an example how to add a scale bar::

   >>> fig = plt.figure()
   >>> ax = fig.add_axes([0.0, 0.0, 1.0, 1.0])
   >>> ax.imshow(...)
   >>> scalebar = ScaleBar(0.2) # 1 pixel = 0.2 meter
   >>> ax.add_artist(scalebar)
   >>> plt.show()

License
-------

License under the BSD License, same as matplotlib.

Copyright (c) 2015 Philippe Pinard
