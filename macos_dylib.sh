mkdir build
cd build
mkdir lib.macos
cd lib.macos
clang++ -std=c++11 -shared -fPIC ../../geodesic_library/gdist_c_api.cpp -o gdist_c_api.dylib
