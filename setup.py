# -*- coding: utf-8 -*-
#
#
# TheVirtualBrain-Framework Package. This package holds all Data Management, and
# Web-UI helpful to run brain-simulations. To use it, you also need do download
# TheVirtualBrain-Scientific Package (for simulators). See content of the
# documentation-folder for more details. See also http://www.thevirtualbrain.org
#
# (c) 2012-2020, Baycrest Centre for Geriatric Care ("Baycrest") and others
#
# This program is free software: you can redistribute it and/or modify it under the
# terms of the GNU General Public License as published by the Free Software Foundation,
# either version 3 of the License, or (at your option) any later version.
# This program is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
# PARTICULAR PURPOSE.  See the GNU General Public License for more details.
# You should have received a copy of the GNU General Public License along with this
# program.  If not, see <http://www.gnu.org/licenses/>.
#
#
#   CITATION:
# When using The Virtual Brain for scientific publications, please cite it as follows:
#
#   Paula Sanz Leon, Stuart A. Knock, M. Marmaduke Woodman, Lia Domide,
#   Jochen Mersmann, Anthony R. McIntosh, Viktor Jirsa (2013)
#       The Virtual Brain: a simulator of primate brain network dynamics.
#   Frontiers in Neuroinformatics (7:10. doi: 10.3389/fninf.2013.00010)
#
#

"""
This module the building of a cython wrapper around a C++ library for
calculating the geodesic distance between points on a mesh surface.

To build::
  python setup.py build_ext --inplace

.. moduleauthor:: Gaurav Malhotra <Gaurav@tvb.invalid>
.. moduleauthor:: Stuart A. Knock <Stuart@tvb.invalid>

"""

import os
import setuptools
import numpy
from Cython.Distutils import build_ext
from Cython.Build.Dependencies import cythonize

compiler_directives = {
    "language_level": 3,
}

# Disable assertions; one is failing geodesic_mesh.h:405
define_macros = [("NDEBUG", 1)]

if "COVERAGE" in os.environ:
    compiler_directives["linetrace"] = True
    define_macros.append(("CYTHON_TRACE_NOGIL", "1"))

GEODESIC_NAME = "gdist"

GEODESIC_MODULE = [
    setuptools.Extension(
        name=GEODESIC_NAME,  # Name of extension
        sources=["gdist.pyx"],  # Filename of Cython source
        language="c++",  # Cython create C++ source
        define_macros=define_macros,
        # TODO: Monitor the c++1y option. Maybe in the future this won't be available anymore so we will have to use
        #  it's correspondent: c++14 (TVB-2797)
        extra_compile_args=["--std=c++1y"],
        extra_link_args=["--std=c++1y"],
        include_dirs=[numpy.get_include(), "geodesic_library"],
    )
]

INCLUDE_DIRS = [
    numpy.get_include(),  # NumPy dtypes
    "geodesic_library",  # geodesic distance, C++ library.
]

TEAM = "Danil Kirsanov, Gaurav Malhotra and Stuart Knock"

INSTALL_REQUIREMENTS = ["numpy", "scipy", "cython"]

with open(os.path.join(os.path.dirname(__file__), "README.rst")) as fd:
    DESCRIPTION = fd.read()


class new_build_ext(build_ext):
    def finalize_options(self):
        self.distribution.ext_modules = cythonize(
            self.distribution.ext_modules,
            compiler_directives=compiler_directives,
            annotate=False,
        )
        if not self.include_dirs:
            self.include_dirs = []
        elif isinstance(self.include_dirs, str):
            self.include_dirs = [self.include_dirs]
        self.include_dirs.append(numpy.get_include())
        super().finalize_options()


setuptools.setup(
    name="tvb-" + GEODESIC_NAME,
    version="2.2",
    ext_modules=GEODESIC_MODULE,
    include_dirs=INCLUDE_DIRS,
    cmdclass={"build_ext": new_build_ext},
    install_requires=INSTALL_REQUIREMENTS,
    description="Compute geodesic distances",
    long_description=DESCRIPTION,
    long_description_content_type='text/x-rst',
    license="GPL v3",
    author=TEAM,
    author_email="tvb.admin@thevirtualbrain.org",
    url="https://github.com/the-virtual-brain/tvb-gdist",
    keywords="gdist geodesic distance geo tvb",
)
