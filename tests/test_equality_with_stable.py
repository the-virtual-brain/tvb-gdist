import numpy as np

import gdist


def test_equality_with_stable():
    surface_data = 'inner_skull_642'
    expected = np.loadtxt(f'data/{surface_data}/gdist_matrix.txt')
    vertices = np.loadtxt(
        f'data/{surface_data}/vertices.txt',
        dtype=np.float64,
    )
    triangles = np.loadtxt(
        f'data/{surface_data}/triangles.txt',
        dtype=np.uint32,
    )
    actual = gdist.local_gdist_matrix(
        vertices=vertices,
        triangles=triangles,
    )
    actual = actual.toarray()
    np.testing.assert_array_almost_equal(actual, expected)
