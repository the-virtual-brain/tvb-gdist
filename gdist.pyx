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
This module defines a Cython wrapper for the geodesic distance C++ library.
The algorithm (implemented in C++) extends Mitchell, Mount and Papadimitriou
(1987) and was written by Danil Kirsanov
(http://code.google.com/archive/p/geodesic/).

The interface definitions and wrapper functions are written in Cython syntax
(http://cython.org/) and provide an API for some of the classes, functions and
constants useful for calculating the geodesic distance.

To compile, and build gdist.so using Cython::

    python setup.py build_ext --inplace

.. moduleauthor:: Gaurav Malhotra <Gaurav@tvb.invalid>
.. moduleauthor:: Stuart A. Knock <Stuart@tvb.invalid>

"""

# For compatible datatypes
import numpy
cimport numpy

# For csc_matrix returned by local_gdist_matrix()
import scipy.sparse

# Pre-cdef'd containers from the C++ standard library
from libcpp cimport bool
from libcpp.vector cimport vector

################################################################################
############ Defininitions to access the C++ geodesic distance library #########
################################################################################
cdef extern from "geodesic_mesh_elements.h" namespace "geodesic":
    cdef cppclass Vertex:
        Vertex()

cdef extern from "geodesic_mesh_elements.h" namespace "geodesic":
    cdef cppclass SurfacePoint:
        SurfacePoint()
        SurfacePoint(Vertex*)
        double& x()
        double& y()
        double& z()

cdef extern from "geodesic_mesh.h" namespace "geodesic":
    cdef cppclass Mesh:
        Mesh()
        void initialize_mesh_data(vector[double]&, vector[unsigned]&, bool)
        vector[Vertex]& vertices()

cdef extern from "geodesic_utils.h":
    vector[double] compute_gdist_impl(vector[double], vector[unsigned], vector[unsigned], vector[unsigned], double, bool, bool)

cdef extern from "geodesic_algorithm_exact.h" namespace "geodesic":
    cdef cppclass GeodesicAlgorithmExact:
        GeodesicAlgorithmExact(Mesh*)
        void propagate(vector[SurfacePoint]&, double, vector[SurfacePoint]*)
        unsigned best_source(SurfacePoint&, double&)

cdef extern from "geodesic_constants_and_simple_functions.h" namespace "geodesic":
    double GEODESIC_INF
################################################################################


cdef get_mesh(
    numpy.ndarray[numpy.float64_t, ndim=2] vertices,
    numpy.ndarray[numpy.int32_t, ndim=2] triangles,
    Mesh &amesh,
    bool is_one_indexed
):
    # Define C++ vectors to contain the mesh surface components.
    cdef vector[double] points
    cdef vector[unsigned] faces

    # Map numpy array of mesh "vertices" to C++ vector of mesh "points"
    cdef numpy.float64_t coord
    for coord in vertices.flatten():
        points.push_back(coord)

    # Map numpy array of mesh "triangles" to C++ vector of mesh "faces"
    cdef numpy.int32_t indx
    for indx in triangles.flatten():
        faces.push_back(indx)

    amesh.initialize_mesh_data(points, faces, is_one_indexed)


def compute_gdist(numpy.ndarray[numpy.float64_t, ndim=2] vertices,
                  numpy.ndarray[numpy.int32_t, ndim=2] triangles,
                  numpy.ndarray[numpy.int32_t, ndim=1] source_indices=None,
                  numpy.ndarray[numpy.int32_t, ndim=1] target_indices=None,
                  double max_distance=GEODESIC_INF,
                  bool is_one_indexed=False):
    """This is the wrapper function for computing geodesic distance between a
    set of sources and targets on a mesh surface.

    Args:
        vertices (numpy.ndarray[numpy.float64_t, ndim=2]): Defines x,y,z
            coordinates of the mesh's vertices.
        triangles (numpy.ndarray[numpy.float64_t, ndim=2]): Defines faces of
            the mesh as index triplets into vertices.
        source_indices (numpy.ndarray[numpy.int32_t, ndim=1]): Index of the
            source on the mesh.
        target_indices (numpy.ndarray[numpy.int32_t, ndim=1]): Index of the
            targets on the mesh.
        max_distance (double): Propagation algorithm stops after reaching the
            certain distance from the source.
        is_one_indexed (bool): defines if the index of the triangles data is
            one-indexed.

    Returns:
        numpy.ndarray((len(target_indices), ), dtype=numpy.float64): Specifying
            the shortest distance to the target vertices from the nearest source
            vertex on the mesh. If no target_indices are provided, all vertices
            of the mesh are considered as targets, however, in this case,
            specifying max_distance will limit the targets to those vertices
            within max_distance of a source. If no source_indices are provided,
            it defaults to 0.

    NOTE: This is the function to use when specifying localised stimuli and
    parameter variations. For efficiently using the whole mesh as sources, such
    as is required to represent local connectivity within the cortex, see the
    local_gdist_matrix() function.

    Basic usage then looks like::
        >>> import numpy
        >>> temp = numpy.loadtxt("data/flat_triangular_mesh.txt", skiprows=1)
        >>> vertices = temp[0:121].astype(numpy.float64)
        >>> triangles = temp[121:321].astype(numpy.int32)
        >>> src = numpy.array([1], dtype=numpy.int32)
        >>> trg = numpy.array([2], dtype=numpy.int32)
        >>> import gdist
        >>> gdist.compute_gdist(vertices, triangles, source_indices=src, target_indices=trg)
         array([0.2])
    """

    cdef bool propagate_on_max_distance = False
    cdef vector[double] points
    cdef vector[unsigned] faces

    if source_indices is None:
        source_indices = numpy.arange(1, dtype=numpy.int32)  # default to 0
    if target_indices is None:
        propagate_on_max_distance = True
        target_indices = numpy.arange(vertices.shape[0], dtype=numpy.int32)

    for k in vertices.flatten():
        points.push_back(k)
    for k in triangles.flatten():
        faces.push_back(k)

    distances = compute_gdist_impl(
        points,
        faces,
        source_indices,
        target_indices,
        max_distance,
        is_one_indexed,
        propagate_on_max_distance,
    )
    # TODO: Basically copies, can be improved as memory is contiguous.
    distances = numpy.asarray(distances)
    distances[distances == max_distance] = numpy.inf
    return distances


def local_gdist_matrix(numpy.ndarray[numpy.float64_t, ndim=2] vertices,
                       numpy.ndarray[numpy.int32_t, ndim=2] triangles,
                       double max_distance=GEODESIC_INF,
                       bool is_one_indexed=False):
    """This is the wrapper function for computing geodesic distance from every
    vertex on the surface to all those within a distance ``max_distance`` of
    them.

    Args:
        vertices (numpy.ndarray[numpy.float64_t, ndim=2]): Defines x,y,z
            coordinates of the mesh's vertices.
        triangles (numpy.ndarray[numpy.float64_t, ndim=2]): Defines faces of
            the mesh as index triplets into vertices.
        max_distance (double): Propagation algorithm stops after reaching the
            certain distance from the source.
        is_one_indexed (bool): defines if the index of the triangles data is
            one-indexed.

    Returns:
        scipy.sparse.csc_matrix((N, N), dtype=numpy.float64): where N
        is the number of vertices, specifying the shortest distance from all
        vertices to all the vertices within max_distance.

    Basic usage then looks like::
        >>> import numpy
        >>> temp = numpy.loadtxt("data/flat_triangular_mesh.txt", skiprows=1)
        >>> import gdist
        >>> vertices = temp[0:121].astype(numpy.float64)
        >>> triangles = temp[121:321].astype(numpy.int32)
        >>> gdist.local_gdist_matrix(vertices, triangles, max_distance=1.0)
         <121x121 sparse matrix of type '<type 'numpy.float64'>'
             with 6232 stored elements in Compressed Sparse Column format>

    Runtime and guesstimated memory usage as a function of max_distance for the
    reg_13 cortical surface mesh, ie containing 2**13 vertices per hemisphere.
    ::
        [[10, 20, 30, 40,  50,  60,  70,  80,  90, 100], # mm
         [19, 28, 49, 81, 125, 181, 248, 331, 422, 522], # s
         [ 3, 13, 30, 56,  89, 129, 177, 232, 292, 358]] # MB]

    where memory is a min-guestimate given by: mem_req = nnz * 8 / 1024 / 1024.
    """

    """
    NOTE: The best_source loop could be sped up considerably by restricting
          targets to those vertices within max_distance of the source, however,
          this will first require the efficient extraction of this information
          from the propgate step...
    """

    cdef Mesh amesh
    get_mesh(vertices, triangles, amesh, is_one_indexed)

    # Define and create object for exact algorithm on that mesh:
    cdef GeodesicAlgorithmExact *algorithm = new GeodesicAlgorithmExact(&amesh)

    cdef vector[SurfacePoint] source, targets
    cdef Py_ssize_t N = vertices.shape[0]
    cdef Py_ssize_t k
    cdef Py_ssize_t kk
    cdef numpy.float64_t distance = 0

    # Add all vertices as targets
    for k in range(N):
        targets.push_back(SurfacePoint(&amesh.vertices()[k]))

    rows = []
    columns = []
    data = []
    for k in range(N):
        source.push_back(SurfacePoint(&amesh.vertices()[k]))
        algorithm.propagate(source, max_distance, NULL)
        source.pop_back()

        for kk in range(N):  # TODO: Reduce to vertices reached during propagate.
            algorithm.best_source(targets[kk], distance)

            if (
                distance is not GEODESIC_INF
                and distance is not 0
                and distance <= max_distance
            ):
                rows.append(k)
                columns.append(kk)
                data.append(distance)

    return scipy.sparse.csc_matrix((data, (rows, columns)), shape=(N, N))


def distance_matrix_of_selected_points(
    numpy.ndarray[numpy.float64_t, ndim=2] vertices,
    numpy.ndarray[numpy.int32_t, ndim=2] triangles,
    numpy.ndarray[numpy.int32_t, ndim=1] points,
    double max_distance=GEODESIC_INF,
    bool is_one_indexed=False
):
    """Function for calculating pairwise geodesic distance for a set of points
    within a distance ``max_distance`` of them.

    Args:
        vertices (numpy.ndarray[numpy.float64_t, ndim=2]): Defines x,y,z
            coordinates of the mesh's vertices.
        triangles (numpy.ndarray[numpy.float64_t, ndim=2]): Defines faces of
            the mesh as index triplets into vertices.
        points (numpy.ndarray[numpy.int32_t, ndim=1]): Indices of the points
            among which the pairwise distances are to be calculated.
        max_distance (double): Propagation algorithm stops after reaching the
            certain distance from the source.
        is_one_indexed (bool): defines if the index of the triangles data is
            one-indexed.

    Returns:
        scipy.sparse.csc_matrix((N, N), dtype=numpy.float64): where N
            is the number of vertices, specifying the pairwise distances among
            the given points.

    Basic usage then looks like::
        >>> import numpy
        >>> temp = numpy.loadtxt("data/flat_triangular_mesh.txt", skiprows=1)
        >>> vertices = temp[0:121].astype(numpy.float64)
        >>> triangles = temp[121:321].astype(numpy.int32)
        >>> points = numpy.array([2, 5, 10], dtype=numpy.int32)
        >>> import gdist
        >>> gdist.distance_matrix_of_selected_points(
                vertices, triangles, points
            )
         <121x121 sparse matrix of type '<class 'numpy.float64'>'
            with 6 stored elements in Compressed Sparse Column format>
    """

    cdef vector[unsigned] rows
    cdef vector[unsigned] columns
    cdef vector[double] distance_matrix
    for index_point, point in enumerate(points):
        target_indices = points[index_point + 1:]

        source_index = numpy.array([point], dtype=numpy.int32)
        target_indices = numpy.array(target_indices, dtype=numpy.int32)

        distances = compute_gdist(
            vertices,
            triangles,
            source_index,
            target_indices,
            max_distance,
            is_one_indexed,
        )

        for index_distance, distance in enumerate(distances):
            rows.push_back(point)
            columns.push_back(target_indices[index_distance])
            distance_matrix.push_back(distance)
            # symmetric
            rows.push_back(target_indices[index_distance])
            columns.push_back(point)
            distance_matrix.push_back(distance)

    cdef Py_ssize_t no_of_vertices = vertices.shape[0]
    return scipy.sparse.csc_matrix(
        (distance_matrix, (rows, columns)),
        shape=(no_of_vertices, no_of_vertices)
    )
