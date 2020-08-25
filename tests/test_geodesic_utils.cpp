#include <iostream>
#include <fstream>

#include <gtest/gtest.h>

#include "../geodesic_library/geodesic_utils.h"


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

int main(int argc, char **argv) {
    testing::InitGoogleTest(&argc, argv);
    return RUN_ALL_TESTS();
}
