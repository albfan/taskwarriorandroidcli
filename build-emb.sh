#!/bin/sh

BUILD_TYPE=Release

cmake -DCMAKE_TOOLCHAIN_FILE=android-cmake/android.toolchain.cmake \
	-DANDROID_NDK=$1 \
	-DCMAKE_BUILD_TYPE=$BUILD_TYPE \
	-DANDROID_ABI=$2 \
	-DANDROID_NATIVE_API_LEVEL="android-16" \
	-DEMBEDDED_ANDROID=1 \
	.
cmake --build .
