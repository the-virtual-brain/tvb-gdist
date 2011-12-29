# -*- coding: utf-8 -*-

"""
This module the building of a cython wrapper around a C++ library for 
calculating the geodesic distance between points on a mesh surface.

To build::
  python setup.py build_ext --inplace

.. moduleauthor:: Gaurav Malhotra <Gaurav@tvb.invalid>
.. moduleauthor:: Stuart A. Knock <Stuart@tvb.invalid>

"""

import numpy

from distutils.core import setup
from distutils.extension import Extension
from Cython.Distutils import build_ext

geodesic_module = [Extension(name="gdist",          # Name of extension
                             sources=["gdist.pyx"], # Filename of Cython source
                             language="c++")]       # Cython create C++ source

include_directories = [numpy.get_include(), # NumPy dtypes
                       "geodesic_library"]  # geodesic distance, C++ library.

setup(ext_modules = geodesic_module, 
      include_dirs = include_directories, 
      cmdclass = {'build_ext': build_ext})
