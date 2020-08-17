#include <vector>
#include <omp.h>

#include "geodesic_algorithm_exact.h"

class SparseMatrix {
public:
    std::vector<unsigned> rows, columns;
    std::vector<double> data;
};


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

SparseMatrix local_gdist_matrix_impl(
    std::vector<double> points,
    std::vector<unsigned> faces,
    double max_distance,
    bool is_one_indexed
) {
    geodesic::Mesh mesh;
    mesh.initialize_mesh_data(points, faces, is_one_indexed=is_one_indexed);    // create internal mesh data structure including edges

    SparseMatrix distances;

    std::vector<unsigned> rows, columns;
    std::vector<double> data;
    #pragma omp parallel
    {
        geodesic::GeodesicAlgorithmExact algorithm(&mesh);
        std::vector<unsigned> rows_private, columns_private;
        std::vector<double> data_private;
        #pragma omp for nowait
        for (int i = 0; i < (int)mesh.vertices().size(); ++i) {
            std::vector<geodesic::SurfacePoint> sources {&mesh.vertices()[i]};
            algorithm.propagate(sources, geodesic::GEODESIC_INF, NULL);    // cover the whole mesh
            for(int j = 0; j < (int)mesh.vertices().size(); ++j) {
                geodesic::SurfacePoint p(&mesh.vertices()[j]);

                double distance;
                unsigned best_source = algorithm.best_source(p, distance);    // for a given surface point, find closest source and distance to this source

                if (distance != 0 && distance <= geodesic::GEODESIC_INF && distance <= max_distance) {
                    rows_private.push_back(i);
                    columns_private.push_back(j);
                    data_private.push_back(distance);
                }
            }
        }
        rows.insert(rows.end(), rows_private.begin(), rows_private.end());
        columns.insert(columns.end(), columns_private.begin(), columns_private.end());
        data.insert(data.end(), data_private.begin(), data_private.end());
    }
    distances.rows = rows;
    distances.columns = columns;
    distances.data = data;
    return distances;
}
