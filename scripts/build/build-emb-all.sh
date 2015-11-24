#!/bin/sh

rm -f android-output/task*

# arm7 before 16
scripts/build/clean-cmake.sh
scripts/build/build-emb.sh $1 armeabi-v7a 10 && cp src/task android-output/task_arm7

# x86 before 16
scripts/build/clean-cmake.sh
scripts/build/build-emb.sh $1 x86 10 && cp src/task android-output/task_x86

# arm7 16
scripts/build/clean-cmake.sh
scripts/build/build-emb.sh $1 armeabi-v7a 16 && cp src/task android-output/task_arm7_16

# x86 16
scripts/build/clean-cmake.sh
scripts/build/build-emb.sh $1 x86 16 && cp src/task android-output/task_x86_16
