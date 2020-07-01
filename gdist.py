import ctypes
import glob
import os
import sys

import numpy as np
import scipy.sparse


if sys.platform == 'win32':
    libfile = glob.glob('build/*/gdist_c_api.dll')[0]
    libfile = os.path.abspath(libfile)
    lib = ctypes.windll.LoadLibrary(libfile)
elif sys.platform == 'darwin':
    try:
        libfile = glob.glob('build/*/gdist*.so')[0]
    except IndexError:
        libfile = glob.glob('build/*/gdist*.dylib')[0]
    lib = ctypes.cdll.LoadLibrary(libfile)
else:
    libfile = glob.glob('build/*/gdist*.so')[0]
    lib = ctypes.cdll.LoadLibrary(libfile)

lib.compute_gdist.argtypes = [
    ctypes.c_uint,
    ctypes.c_uint,
    np.ctypeslib.ndpointer(dtype=np.float64),
    np.ctypeslib.ndpointer(dtype=np.int32),
    ctypes.c_uint,
    ctypes.c_uint,
    np.ctypeslib.ndpointer(dtype=np.int32),
    np.ctypeslib.ndpointer(dtype=np.int32),
    np.ctypeslib.ndpointer(dtype=np.float64),
    ctypes.c_double,
]
lib.compute_gdist.restype = None

lib.local_gdist_matrix.argtypes = [
    ctypes.c_uint,
    ctypes.c_uint,
    np.ctypeslib.ndpointer(dtype=np.float64),
    np.ctypeslib.ndpointer(dtype=np.int32),
    ctypes.POINTER(ctypes.c_uint),
    ctypes.c_double,
]
lib.local_gdist_matrix.restype = ctypes.POINTER(ctypes.c_double)

lib.free_memory.argtypes = [
    ctypes.POINTER(ctypes.c_double),
]
lib.free_memory.restype = None


class Gdist(object):
    def compute_gdist(
        self,
        number_of_vertices,
        number_of_triangles,
        vertices,
        triangles,
        number_of_source_indices,
        number_of_target_indices,
        source_indices_array,
        target_indices_array,
        distance_limit,
    ):
        target_indices_size = target_indices_array.size
        distance = np.empty(target_indices_size, dtype=np.float64)
        lib.compute_gdist(
            number_of_vertices,
            number_of_triangles,
            vertices,
            triangles,
            number_of_source_indices,
            number_of_target_indices,
            source_indices_array,
            target_indices_array,
            distance,
            distance_limit,
        )
        return distance

    def local_gdist_matrix(
        self,
        number_of_vertices,
        number_of_triangles,
        vertices,
        triangles,
        max_distance,
    ):
        sparse_matrix_size = ctypes.c_uint(0)
        data = lib.local_gdist_matrix(
            number_of_vertices,
            number_of_triangles,
            vertices,
            triangles,
            ctypes.byref(sparse_matrix_size),
            max_distance,
        )

        np_data = np.fromiter(
            data,
            dtype=np.float64,
            count=3 * sparse_matrix_size.value,
        )
        lib.free_memory(data)
        return np_data


def compute_gdist(
    vertices,
    triangles,
    source_indices=None,
    target_indices=None,
    max_distance=1e100,
):
    vertices = vertices.ravel()
    triangles = triangles.ravel()
    source_indices = source_indices.ravel()
    target_indices = target_indices.ravel()

    g = Gdist()
    distance = g.compute_gdist(
        number_of_vertices=vertices.size,
        number_of_triangles=triangles.size,
        vertices=vertices,
        triangles=triangles,
        number_of_source_indices=source_indices.size,
        number_of_target_indices=target_indices.size,
        source_indices_array=source_indices,
        target_indices_array=target_indices,
        distance_limit=max_distance,
    )
    return np.fromiter(distance, dtype=np.float64, count=target_indices.size)


def local_gdist_matrix(
    vertices,
    triangles,
    max_distance=1e100,
):
    vertices = vertices.ravel()
    triangles = triangles.ravel()

    g = Gdist()
    data = g.local_gdist_matrix(
        vertices.size,
        triangles.size,
        vertices,
        triangles,
        max_distance,
    )
    assert data.size % 3 == 0
    sizes = data.size // 3
    rows = data[:sizes]
    columns = data[sizes: 2 * sizes]
    data = data[2 * sizes:]

    return scipy.sparse.csc_matrix(
        (data, (rows, columns)), shape=(vertices.size // 3, vertices.size // 3)
    )
