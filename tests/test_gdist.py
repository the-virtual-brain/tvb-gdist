import numpy as np

import gdist


class TestComputeGdist():
    def test_flat_triangular_mesh(self):
        data = np.loadtxt("data/flat_triangular_mesh.txt", skiprows=1)
        vertices = data[0:121].astype(np.float64)
        triangles = data[121:].astype(np.int32)
        source = np.array([1], dtype=np.int32)
        target = np.array([2], dtype=np.int32)
        distance = gdist.compute_gdist(
            vertices,
            triangles,
            source_indices=source,
            target_indices=target
        )
        np.testing.assert_array_almost_equal(distance, [0.2])

    def test_hedgehog_mesh(self):
        data = np.loadtxt("data/hedgehog_mesh.txt", skiprows=1)
        vertices = data[0:300].astype(np.float64)
        triangles = data[300:].astype(np.int32)
        source = np.array([0], dtype=np.int32)
        target = np.array([1], dtype=np.int32)
        distance = gdist.compute_gdist(
            vertices,
            triangles,
            source_indices=source,
            target_indices=target
        )
        np.testing.assert_array_almost_equal(distance, [1.40522])


class TestLocalGdistMatrix:
    def test_flat_triangular_mesh(self):
        data = np.loadtxt("data/flat_triangular_mesh.txt", skiprows=1)
        vertices = data[0:121].astype(np.float64)
        triangles = data[121:].astype(np.int32)
        distances = gdist.local_gdist_matrix(vertices, triangles)
        epsilon = 1e-6 # the default value used in `assert_array_almost_equal`
        # test if the obtained matrix is symmetric
        assert (abs(distances - distances.T) > epsilon).nnz == 0
        np.testing.assert_array_almost_equal(distances.toarray()[1][0], 0.2)
        # set max distance as 0.3
        distances = gdist.local_gdist_matrix(vertices, triangles, 0.3)
        # test if the obtained matrix is symmetric
        assert (abs(distances - distances.T) > epsilon).nnz == 0
        assert np.max(distances) <= 0.3

    def test_hedgehog_mesh(self):
        data = np.loadtxt("data/hedgehog_mesh.txt", skiprows=1)
        vertices = data[0:300].astype(np.float64)
        triangles = data[300:].astype(np.int32)
        distances = gdist.local_gdist_matrix(vertices, triangles)
        epsilon = 1e-6 # the default value used in `assert_array_almost_equal`
        # test if the obtained matrix is symmetric
        assert (abs(distances - distances.T) > epsilon).nnz == 0
        np.testing.assert_array_almost_equal(
            distances.toarray()[1][0], 1.40522
        )
        # set max distance as 1.45
        distances = gdist.local_gdist_matrix(vertices, triangles, 1.45)
        # test if the obtained matrix is symmetric
        assert (abs(distances - distances.T) > epsilon).nnz == 0
        assert np.max(distances) <= 1.45
