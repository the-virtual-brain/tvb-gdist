#include <vector>

#include "geodesic_algorithm_exact.h"

std::vector<double> compute_gdist_impl(
    std::vector<double> points,
    std::vector<unsigned> faces,
    std::vector<unsigned> sources,
    std::vector<unsigned> targets,
    double max_distance,
    bool is_one_indexed,
    bool propagate_on_max_distance
) {
    geodesic::Mesh mesh;
    mesh.initialize_mesh_data(points, faces, is_one_indexed);
    geodesic::GeodesicAlgorithmExact algorithm(&mesh);

    std::vector<geodesic::SurfacePoint> all_sources, stop_points;
    for (auto k: sources) {
        all_sources.push_back(geodesic::SurfacePoint(&mesh.vertices()[k]));
    }
    for (auto k: targets) {
        stop_points.push_back(&mesh.vertices()[k]);
    }

    if (propagate_on_max_distance) {
        algorithm.propagate(all_sources, max_distance, NULL);
    } else {
        algorithm.propagate(all_sources, max_distance, &stop_points);
    }

    std::vector<double> distances(stop_points.size());
    for (unsigned k = 0; k < stop_points.size(); ++k) {
        algorithm.best_source(stop_points[k], distances[k]);
    }
    return distances;
}
