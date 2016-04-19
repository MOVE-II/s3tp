# build libs3tp and the s3tp tool

# c++14 plus all warnings
AM_CXXFLAGS = -std=c++14 -Wall -Wextra -pedantic

# flex flags
AM_LFLAGS = -Ca

# s3tp library
lib_LTLIBRARIES = libs3tp.la
libs3tp_la_LDFLAGS = -no-undefined
libs3tp_la_SOURCES = \
                     s3tp.cpp

s3tpincludedir = $(includedir)/s3tp
s3tpinclude_HEADERS = \
                      s3tp.h

# s3tp executable
bin_PROGRAMS = s3tp
s3tp_SOURCES = s3tp_tool.cpp
s3tp_LDADD = libs3tp.la
