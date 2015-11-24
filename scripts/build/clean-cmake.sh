#!/bin/sh

make clean
find -iname 'cmake*' -not -name CMakeLists.txt -not -name cmake.h.in -exec rm -rf {} \+
