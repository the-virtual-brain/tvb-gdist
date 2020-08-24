#include <iostream>
#include <fstream>

#include <gtest/gtest.h>

#include "../geodesic_library/geodesic_utils.h"

std::vector<std::vector<double>> sparse_to_matrix(SparseMatrix spareseMatrix, unsigned size) {
    std::vector<std::vector<double>> matrix(size, std::vector<double>(size));
    for (unsigned i = 0; i < spareseMatrix.rows.size(); ++i) {
        matrix[spareseMatrix.rows[i]][spareseMatrix.columns[i]] = spareseMatrix.data[i];
    }
    return matrix;
}


TEST(compute_gdist_impl, flat_traingular_mesh_test) {
    std::vector<double> points;
    std::vector<unsigned> faces;
    geodesic::read_mesh_from_file("../data/flat_triangular_mesh.txt", points, faces);
    std::vector<unsigned> sources = {1};
    std::vector<unsigned> targets = {2};
    std::vector<double> gdist = compute_gdist_impl(
        points,
        faces,
        sources,
        targets,
        geodesic::GEODESIC_INF,
        false,
        false
    );
    std::vector<double> expected = {0.2};
    for(unsigned i = 0; i < gdist.size(); ++i) {
        EXPECT_NEAR(gdist[i], expected[i], 1e-6);
    }
}

TEST(local_gdist_matrix_impl, flat_triangular_mesh_test) {
    std::vector<double> points;
    std::vector<unsigned> faces;
    geodesic::read_mesh_from_file("../data/flat_triangular_mesh.txt", points, faces);
    SparseMatrix gdist_matrix = local_gdist_matrix_impl(
        points,
        faces,
        geodesic::GEODESIC_INF,
        false
    );
    std::vector<std::vector<double>> matrix = sparse_to_matrix(gdist_matrix, points.size() / 3);
    EXPECT_NEAR(matrix[1][0], 0.2, 1e-6);
}

int main(int argc, char **argv) {
    testing::InitGoogleTest(&argc, argv);
    return RUN_ALL_TESTS();
}
