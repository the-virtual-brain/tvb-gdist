=================
Geodesic Library 
=================

.. image:: https://travis-ci.com/the-virtual-brain/tvb-gdist.svg?branch=trunk
    :target: https://travis-ci.com/the-virtual-brain/tvb-gdist

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

We added a Python wrapped and made small fixes to the original library, to make
it compatible with Cython.

To install this, either run ``pip install tvb-gdist`` or download
sources from GitHub and run ``python setup.py install`` in current folder.

You can also use pip to directly install from GitHub: 
``pip install git+https://github.com/the-virtual-brain/tvb-gdist``.

Basic test could be::

    python
    import gdist


Python 3, Cython, and a C++ compiler are required unless the Pypi whl files are
compatible with your system.

APIs
====

The module exposes 2 APIs.

**gdist.compute_gdist(numpy.ndarray[numpy.float64_t, ndim=2] vertices,
numpy.ndarray[numpy.int32_t, ndim=2] triangles,
numpy.ndarray[numpy.int32_t, ndim=1] source_indices = None,
numpy.ndarray[numpy.int32_t, ndim=1] target_indices = None,
double max_distance = GEODESIC_INF,
bool is_one_indexed = False)**

    This is the wrapper function for computing geodesic distance between a
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


**gdist.local_gdist_matrix(numpy.ndarray[numpy.float64_t, ndim=2] vertices,
numpy.ndarray[numpy.int32_t, ndim=2] triangles,
double max_distance = GEODESIC_INF,
bool is_one_indexed = False)**

    This is the wrapper function for computing geodesic distance from every 
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


**distance_matrix_of_selected_points(numpy.ndarray[numpy.float64_t, ndim=2] vertices,
numpy.ndarray[numpy.int32_t, ndim=2] triangles,
numpy.ndarray[numpy.int32_t, ndim=1] points,
double max_distance = GEODESIC_INF,
bool is_one_indexed = False)**

    Function for calculating pairwise geodesic distance for a set of points
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

Notes
=====

* The obtained matrix will be almost symmetrical due to floating point
  imprecision.

* In order for the algorithm to work the mesh must not be numbered incorrectly
  or disconnected or of somehow degenerate.
  
Acknowledgments
===============
This project has received funding from the European Union’s Horizon 2020 
Framework Programme for Research and Innovation under the Specific Grant 
Agreement No. 826421 - VirtualBrainCloud.
