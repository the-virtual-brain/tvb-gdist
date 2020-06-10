#include <iostream>
#include <fstream>

#include "geodesic_library/geodesic_algorithm_exact.h"

extern "C" {
    double computeGdist(int numberOfVertices, int numberOfTriangles, double *vertices, double *triangles);
};

double computeGdist(int numberOfVertices, int numberOfTriangles, double *vertices, double *triangles) {
    return 1.0;
}
