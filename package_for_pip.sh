#!/usr/bin/env bash

rm -Rf dist
mkdir dist

echo "====================================="
echo "Packing: tvb_gdist"
echo "====================================="

python setup.py sdist
python setup.py bdist_wheel

rm -R build