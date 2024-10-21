###############################################################################
#                                                                             #
# (c) 1995-2008. Progress Software Corporation. All rights reserved.          #
#                                                                             #
# Purpose:    Make file to build Unix ODBC example application                #
#                                                                             #
# Requirements:                                                               #
#                                                                             #
# Shared Library Path Variable:                                               #
# Environment variable should point to the lib directory                      #
# for this release. This will enable the linker to resolve the                #
# location of the various shared libraries and the run-time linker to         #
# resolve the location of run-time components.                                #
#                                                                             #
# To Build example, issue the following command:                              #
# %make -f example.mak                                                        #
#                                                                             #
###############################################################################

CC=gcc

#
# Compiler options
#
CCFLAGS=-m32 -g
DEFS= 
INCLUDE=-I../../include

CC64FLAGS=-m64 -g
DEFS64=-DODBC64 

#
# Define Support Libraries used.
#
LIBPATH=-Wl,-rpath-link -W ../../lib -L../../lib
LIBC=-lc
LIBS=$(LIBPATH) -lodbc -lodbcinst

LIBPATH64=-Wl,-rpath-link -W ../../lib64 -L../../lib64
LIBS64=$(LIBPATH64) -lodbc -lodbcinst

#
# Application that shows a single C source code connecting to different
# vendor databases by simply changing the passed in DSN.
#
#
# Sample program using C Compiler
#
all : example example64

example:	example.c
	$(CC) -o example $(DEFS) $(CCFLAGS) $(INCLUDE) example.c $(LIBS) $(LIBC)
	chmod 755 example

example64:	example.c
	$(CC) -o example64 $(DEFS64) $(CC64FLAGS) $(INCLUDE) example.c $(LIBS64) $(LIBC)
	chmod 755 example64

clean:
	/bin/rm -f example
	/bin/rm -f example64
#
# End of Makefile
#

