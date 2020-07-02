Geodesic Library 
=================

The **tvb-gdist** module is a Cython interface to a C++ library
(https://code.google.com/archive/p/geodesic/) for computing
geodesic distance which is the length of shortest line between two
vertices on a triangulated mesh in three dimensions, such that the line
lies on the surface.

The algorithm is due Mitchell, Mount and Papadimitriou, 1987; the implementation
is due to Danil Kirsanov and the Cython interface to Gaurav Malhotra and
Stuart Knock (TVB Team).


Original library (published under MIT license):
https://code.google.com/archive/p/geodesic/

We added a Python wrapped and made small fixes to the original library, to make it compatible with Cython.

To install this, either run **pip install tvb-gdist** or download
sources from Github and run **python setup.py install** in current folder.

Basic test could be::

    python
    import gdist


Python 3, Cython, and a C++ compiler are required unless the Pypi whl files are compatible with your system.


Current Build Status
=====================
.. image:: https://travis-ci.com/the-virtual-brain/tvb-gdist.svg?branch=trunk
    :target: https://travis-ci.com/the-virtual-brain/tvb-gdist
