cmake_minimum_required (VERSION 2.8)
project (uuid)

include (CheckFunctionExists)
set (HAVE_CMAKE true)

message ("-- Making UUID library")

add_definitions(-DHAVE_USLEEP)
set (uuid_SRCS all-io.h c.h clear.c compare.c copy.c gen_uuid.c isnull.c pack.c parse.c randutils.c randutils.h  unpack.c unparse.c uuidd.h uuid.h uuidP.h uuid_time.c)

add_library (uuid STATIC ${uuid_SRCS})
