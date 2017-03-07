#!/bin/bash

set -e

if [ -d build ]; then
    echo "mkdir build"
    rm -rf build
    mkdir build
else
    mkdir build
fi

echo "go the the build dir"
cd build

echo "launch cmake"
cmake ..

echo "launch make"
make
sudo make -j3 install

echo "install tempusloader python package"
cd ..
cd python/tempusloader
sudo python setup.py install

echo "update lib*.so"
sudo ldconfig
