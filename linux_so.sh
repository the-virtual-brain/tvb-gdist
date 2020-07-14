mkdir build
cd build
mkdir lib.linux
cd lib.linux
g++ -std=c++11 -shared -fPIC ../../geodesic_library/gdist_c_api.cpp -o gdist_c_api.so
