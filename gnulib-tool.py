#!/usr/bin/python3

################################################################################
# Define global imports
################################################################################
import os
import re
import sys
import subprocess

################################################################################
# Define module information
################################################################################
__appname__ = 'gnulib-tool'
__apppath__ = os.path.realpath(sys.argv[0])
__appdir__ = os.path.dirname(__apppath__)
__author__ = \
[
  'Bruno Haible',
  'Simon Josefsson',
  'Dmitriy Selyutin',
]
__license__ = 'GNU GPLv3+'
__version__ = 0.1

################################################################################
# Define global constants
################################################################################
# You can set AUTOCONFPATH to empty if autoconf 2.57 is already in your PATH
AUTOCONFPATH = ''
# You can set AUTOMAKEPATH to empty if automake 1.9.x is already in your PATH
AUTOMAKEPATH = ''
# You can set GETTEXTPATH to empty if autopoint 0.15 is already in your PATH
GETTEXTPATH = ''
# You can set LIBTOOLPATH to empty if libtoolize 2.x is already in your PATH
LIBTOOLPATH = ''

APPS = dict() # Create empty dictionary

# You can also set the variable AUTOCONF individually
if AUTOCONFPATH:
  APPS['autoconf'] = AUTOCONFPATH + 'autoconf'
else:
  if os.getenv('AUTOCONF'):
    APPS['autoconf'] = os.getenv('AUTOCONF')
  else:
    APPS['autoconf'] = 'autoconf'

# You can also set the variable AUTORECONF individually
if AUTOCONFPATH:
  APPS['autoreconf'] = AUTOCONFPATH + 'autoreconf'
else:
  if os.getenv('AUTORECONF'):
    APPS['autoreconf'] = os.getenv('AUTORECONF')
  else:
    APPS['autoreconf'] = 'autoreconf'

# You can also set the variable AUTOHEADER individually
if AUTOCONFPATH:
  APPS['autoheader'] = AUTOCONFPATH + 'autoheader'
else:
  if os.getenv('AUTOHEADER'):
    APPS['autoheader'] = os.getenv('AUTOHEADER')
  else:
    APPS['autoheader'] = 'autoheader'

# You can also set the variable AUTOMAKE individually
if AUTOMAKEPATH:
  APPS['automake'] = AUTOMAKEPATH + 'automake'
else:
  if os.getenv('AUTOMAKE'):
    APPS['automake'] = os.getenv('AUTOMAKE')
  else:
    APPS['automake'] = 'automake'

# You can also set the variable ACLOCAL individually
if AUTOMAKEPATH:
  APPS['aclocal'] = AUTOMAKEPATH + 'aclocal'
else:
  if os.getenv('ACLOCAL'):
    APPS['aclocal'] = os.getenv('ACLOCAL')
  else:
    APPS['aclocal'] = 'aclocal'

# You can also set the variable AUTOPOINT individually
if GETTEXTPATH:
  APPS['autopoint'] = GETTEXTPATH + 'autopoint'
else:
  if os.getenv('AUTOPOINT'):
    APPS['autopoint'] = os.getenv('AUTOPOINT')
  else:
    APPS['autopoint'] = 'autopoint'

# You can also set the variable LIBTOOLIZE individually
if LIBTOOLPATH:
  APPS['libtoolize'] = LIBTOOLPATH + 'libtoolize'
else:
  if os.getenv('LIBTOOLIZE'):
    APPS['libtoolize'] = os.getenv('LIBTOOLIZE')
  else:
    APPS['libtoolize'] = 'libtoolize'

# You can also set the variable MAKE
if os.getenv('MAKE'):
  APPS['make'] = os.getenv('MAKE')
else:
  APPS['make'] = 'make'

# Delete temporary variables
del(AUTOCONFPATH)
del(AUTOMAKEPATH)
del(GETTEXTPATH)
del(LIBTOOLPATH)
