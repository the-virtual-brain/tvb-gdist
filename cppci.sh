# Credit: https://github.com/Caian/cppci/blob/master/.travis.yml

# Set the extra prefix for external libraries and tools
export EXTRA_DIR="$PWD/extra"
# Set the prefix used to install googletest, set the source
# directory and get the source code
export GTEST_DIR="$EXTRA_DIR/googletest"
export GTEST_SRC_DIR="$GTEST_DIR/source"
mkdir -p "$GTEST_DIR" "$GTEST_SRC_DIR"
pushd "$GTEST_SRC_DIR"
git clone --depth 1 https://github.com/google/googletest.git -b v1.8.x .
popd
# Get LLCOV
export LCOV_DIR="$EXTRA_DIR/lcov"
mkdir -p "$LCOV_DIR"
pushd "$LCOV_DIR"
wget https://github.com/linux-test-project/lcov/archive/v1.12.zip
unzip v1.12.zip
LCOV="$PWD/lcov-1.12/bin/lcov --gcov-tool gcov-6"
popd
# Build and install googletest
pushd "$GTEST_SRC_DIR"
cmake -DCMAKE_BUILD_TYPE=Release -DCMAKE_INSTALL_PREFIX="$GTEST_DIR" .
make -j
make install
popd

export PROJECT_DIR="$PWD"
export TEST_SRC_DIR="$PROJECT_DIR/tests"
export BUILD_DIR="$PROJECT_DIR/build"
# Print some information
echo "Current dir is $PWD"
echo "GTest dir is $GTEST_DIR"
# Set compiler
export CXX=/usr/bin/g++
# Set compiler flags
export CXXFLAGS="-I$PROJECT_DIR/.."
export CXXFLAGS="$CXXFLAGS -I$GTEST_DIR/include -DNDEBUG=1 --std=c++14"
# Set linker flags
export LDFLAGS="-lgtest_main -lgtest -lpthread -L$GTEST_DIR/lib"
# Set coverage flags
export COVFLAGS="--coverage"
# Create the build directory
mkdir -p "$BUILD_DIR" && pushd "$BUILD_DIR"
# Copy data folder to build directory
cp -r "$PROJECT_DIR"/data $BUILD_DIR
# Build and run each test
for test in "$TEST_SRC_DIR"/*.cpp ; do
    test_dir="$(basename $test)"
    mkdir -p "$test_dir" && pushd "$test_dir"
    $CXX $CXXFLAGS $test -o test $LDFLAGS $COVFLAGS
    ./test
    ls -l
    popd
done
popd

# Set the coverage file name for lcov
export COVERAGE_FILE="$PWD/coverage.info"
# Run lcov on the generated coverage data
$LCOV --directory "$BUILD_DIR" --base-directory "$PROJECT_DIR" --capture --output-file "$COVERAGE_FILE"
# Keep only the project headers in the coverage data by 
# removing the tests themselves and the extra libraries
$LCOV --remove "$COVERAGE_FILE" "/usr*" "$TEST_SRC_DIR/*" "$EXTRA_DIR/*" -o "$COVERAGE_FILE"
bash <(curl -s https://codecov.io/bash) -cF cpp || echo "Codecov did not collect coverage reports"
