import numpy as np

import gdist


def test_flat_triangular_mesh():
    temp = np.loadtxt("data/flat_triangular_mesh.txt", skiprows=1)
    vertices = temp[0:121].astype(np.float64)
    triangles = temp[121:321].astype(np.int32)
    source = np.array([1], dtype=np.int32)
    target = np.array([2], dtype=np.int32)
    distance = gdist.compute_gdist(vertices, triangles,
                                   source_indices=source, target_indices=target)
    np.testing.assert_array_almost_equal(distance, [0.2])
