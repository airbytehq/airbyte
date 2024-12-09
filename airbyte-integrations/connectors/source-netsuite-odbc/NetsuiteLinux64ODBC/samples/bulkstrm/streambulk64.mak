#
# Copyright (c) 2010 Progress Software Corporation. All rights reserved
#
# Purpose:	Make file to build example bulk application 
#
# Requirements:
#
# Shared Library Path Variable:
#	Environment variable should point to the lib directory
#	for this release. This will enable the linker to resolve the
#	location of the various shared libraries and the run-time linker to
#	resolve the location of run-time components.
#
# Note that you must set the make file variable CC in order to build this
# example bulk program. Uncomment one of the platform specific lines in this
# make file.
# 
# To Build bulk, issue the following command:
#	%make -f bulk.mak
#
#
############################################################################

# For Linux
CC=g++
LIBC=-lc
CCFLAGS=-g

#
# Compiler options
#
# For 64-bit
DEFS=-DODBCVER=0x0350 -DODBC64
INCLUDE=-I../../include

#
# Definition for standard system linker
#
LD=ld

#
# Define Support Libraries used.
#
LIBPATH=-L../../lib64
LIBS=$(LIBPATH) -lodbc 

#
# Application that shows a single C source code connecting to different
# vendor databases by simply changing the passed in DSN.
#
#
# Sample program using C Compiler
#
bulkstrm:	bulk.cpp main.cpp
	$(CC) -o $@ $(DEFS) $(CCFLAGS) $(INCLUDE) bulk.cpp main.cpp $(LIBS) $(LIBC)

clean:
	/bin/rm bulkstrm
#
# End of Makefile
#
