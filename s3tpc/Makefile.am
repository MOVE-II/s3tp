# build libs3tp and the s3tp tool

# c11 plus all warnings
AM_CFLAGS = -std=c11 -Wall -Wextra -pedantic

# flex flags
AM_LFLAGS = -Ca

# s3tp library
lib_LTLIBRARIES = libs3tp.la
libs3tp_la_LDFLAGS = -no-undefined
libs3tp_la_SOURCES = \
                     s3tp.c

s3tpincludedir = $(includedir)/s3tp
s3tpinclude_HEADERS = \
                      s3tp.h

# s3tp executable
bin_PROGRAMS = s3tp
s3tp_SOURCES = s3tp_tool.c
s3tp_LDADD = libs3tp.la
