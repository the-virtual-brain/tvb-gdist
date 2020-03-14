REM Package Geodesic Distance for Pypi

rmdir dist
mkdir dist

echo "====================================="
echo "Packing: tvb_gdist"
echo "====================================="

python setup.py sdist
python setup.py bdist_wheel

rmdir build