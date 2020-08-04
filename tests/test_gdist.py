# -*- coding: utf-8 -*-
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
    GSOC 2020
.. moduleauthor:: Ayan B
"""

import numpy as np
import scipy

import gdist


class TestComputeGdist:
    def test_flat_triangular_mesh(self):
        data = np.loadtxt("data/flat_triangular_mesh.txt", skiprows=1)
        vertices = data[0:121].astype(np.float64)
        triangles = data[121:].astype(np.int32)
        source = np.array([1], dtype=np.int32)
        target = np.array([2], dtype=np.int32)
        distance = gdist.compute_gdist(
            vertices, triangles, source_indices=source, target_indices=target
        )
        np.testing.assert_array_almost_equal(distance, [0.2])

    def test_flat_triangular_mesh_1_indexed(self):
        data = np.loadtxt(
            "data/flat_triangular_mesh_1_indexed.txt", skiprows=1,
        )
        vertices = data[0:121].astype(np.float64)
        triangles = data[121:].astype(np.int32)
        source = np.array([2], dtype=np.int32)
        target = np.array([3], dtype=np.int32)
        distance = gdist.compute_gdist(
            vertices, triangles, source, target, is_one_indexed=True,
        )
        np.testing.assert_array_almost_equal(distance, [0.2])

    def test_flat_triangular_mesh_no_target(self):
        data = np.loadtxt("data/flat_triangular_mesh.txt", skiprows=1)
        vertices = data[0:121].astype(np.float64)
        triangles = data[121:].astype(np.int32)
        source = None
        target = None
        distance = gdist.compute_gdist(vertices, triangles, source, target,)
        expected = np.loadtxt("data/flat_triangular_mesh_no_target.txt")
        np.testing.assert_array_almost_equal(distance, expected)

    def test_hedgehog_mesh(self):
        data = np.loadtxt("data/hedgehog_mesh.txt", skiprows=1)
        vertices = data[0:300].astype(np.float64)
        triangles = data[300:].astype(np.int32)
        source = np.array([0], dtype=np.int32)
        target = np.array([1], dtype=np.int32)
        distance = gdist.compute_gdist(
            vertices, triangles, source_indices=source, target_indices=target
        )
        np.testing.assert_array_almost_equal(distance, [1.40522])


class TestLocalGdistMatrix:
    def test_flat_triangular_mesh(self):
        data = np.loadtxt("data/flat_triangular_mesh.txt", skiprows=1)
        vertices = data[0:121].astype(np.float64)
        triangles = data[121:].astype(np.int32)
        distances = gdist.local_gdist_matrix(vertices, triangles)
        epsilon = 1e-6  # the default value used in `assert_array_almost_equal`
        # test if the obtained matrix is symmetric
        assert (abs(distances - distances.T) > epsilon).nnz == 0
        np.testing.assert_array_almost_equal(distances.toarray()[1][0], 0.2)
        # set max distance as 0.3
        distances = gdist.local_gdist_matrix(vertices, triangles, 0.3)
        # test if the obtained matrix is symmetric
        assert (abs(distances - distances.T) > epsilon).nnz == 0
        assert np.max(distances) <= 0.3

    def test_flat_triangular_mesh_1_indexed(self):
        data = np.loadtxt(
            "data/flat_triangular_mesh_1_indexed.txt", skiprows=1,
        )
        vertices = data[0:121].astype(np.float64)
        triangles = data[121:].astype(np.int32)
        distances = gdist.local_gdist_matrix(
            vertices, triangles, is_one_indexed=True
        )
        epsilon = 1e-6  # the default value used in `assert_array_almost_equal`
        # test if the obtained matrix is symmetric
        assert (abs(distances - distances.T) > epsilon).nnz == 0
        np.testing.assert_array_almost_equal(distances.toarray()[1][0], 0.2)
        # set max distance as 0.3
        distances = gdist.local_gdist_matrix(vertices, triangles, 0.3, True)
        # test if the obtained matrix is symmetric
        assert (abs(distances - distances.T) > epsilon).nnz == 0
        assert np.max(distances) <= 0.3

    def test_hedgehog_mesh(self):
        data = np.loadtxt("data/hedgehog_mesh.txt", skiprows=1)
        vertices = data[0:300].astype(np.float64)
        triangles = data[300:].astype(np.int32)
        distances = gdist.local_gdist_matrix(vertices, triangles)
        epsilon = 1e-6  # the default value used in `assert_array_almost_equal`
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


class TestDistanceMatrixOfSelectedPoints:
    def test_flat_triangular_mesh(self):
        data = np.loadtxt("data/flat_triangular_mesh.txt", skiprows=1)
        vertices = data[0:121].astype(np.float64)
        triangles = data[121:].astype(np.int32)
        points = np.array([2, 5, 10, 12, 14, 16], dtype=np.int32)
        distances = gdist.distance_matrix_of_selected_points(
            vertices, triangles, points,
        )
        epsilon = 1e-6
        expected = np.loadtxt("data/flat_triangular_mesh_pairwise_matrix.txt")
        np.testing.assert_array_almost_equal(distances.toarray(), expected)
        # test if the obtained matrix is symmetric
        assert (abs(distances - distances.T) > epsilon).nnz == 0
        no_of_points = points.shape[0]
        # make sure number of non-zero elements are correct
        assert distances.nnz == no_of_points * no_of_points - no_of_points
        # `distances` is of type sparse matrix
        assert type(distances) is scipy.sparse.csc_matrix
