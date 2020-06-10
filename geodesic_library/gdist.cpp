/* read mesh from file and 
 - if one vertex is specified, for all vertices of the mesh print their distances to this vertex
 - if two vertices are specified, print the shortest path between these vertices 

    Danil Kirsanov, 01/2008
    Minor cleanup, 2011, SAK.
*/
#include <iostream>
#include <fstream>

#include "geodesic_algorithm_exact.h"

extern "C" {
    double computeGdist(int numberOfVertices, int numberOfTriangles, double *vertices, double *triangles) {
        return computeGdistCpp(numberOfVertices, numberOfTriangles, vertices, triangles);
    }
}

double computeGdistCpp(int numberOfVertices, int numberOfTriangles, double *vertices, double *triangles) {
    return 1.0;
}
