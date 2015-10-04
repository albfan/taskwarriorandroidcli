cmake_minimum_required (VERSION 2.8)
project (glob)

include_directories (${CMAKE_SOURCE_DIR}/src/glob)
message ("-- Making embedded glob library")

set (glob_SRCS glob.h glob.c)

add_library (glob STATIC ${glob_SRCS})
