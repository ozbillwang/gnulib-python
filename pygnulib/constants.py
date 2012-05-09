#!/usr/bin/python
'''This script is a part of PyGNULib module for gnulib.'''

from __future__ import unicode_literals
################################################################################
# Define global imports
################################################################################
import os
import sys


################################################################################
# Define module information
################################################################################
__author__ = \
[
  'Bruno Haible',
  'Paul Eggert',
  'Simon Josefsson',
  'Dmitriy Selyutin',
]
__license__ = 'GNU GPLv3+'
__copyright__ = '2012 Free Software Foundation, Inc.'
__version__ = 0.1


################################################################################
# Backward compatibility
################################################################################
# Create string compatibility
if sys.version_info.major == 2: # Using Python 2
  string = unicode
else: # Using Python 3 (PY3K)
  string = str


################################################################################
# Define global constants
################################################################################
# Declare neccessary variables
APP = dict() # Application
DIRS = dict() # Directories
UTILS = dict() # Utilities
ENCS = dict() # Encodings
FILES = dict() # Files
MODES = dict() # Modes

# Set ENCS dictionary
ENCS['system'] = sys.getfilesystemencoding()
ENCS['default'] = sys.getdefaultencoding()
ENCS['shell'] = sys.stdout.encoding
if ENCS['shell'] == None:
  ENCS['shell'] = 'UTF-8'

# Set APP dictionary
APP['name'] = os.path.basename(sys.argv[0])
APP['path'] = os.path.realpath(sys.argv[0])
if type(APP['name']) is bytes:
  APP['name'] = string(APP['name'], ENCS['system'])
if type(APP['path']) is bytes:
  APP['path'] = string(APP['path'], ENCS['system'])

# Set DIRS dictionary
DIRS['root'] = os.path.dirname(APP['path'])
DIRS['cwd'] = os.getcwd()
if type(DIRS['cwd']) is bytes:
  DIRS['cwd'] = string(DIRS['cwd'], ENCS['system'])
DIRS['build-aux'] = os.path.join(DIRS['root'], 'build-aux')
DIRS['config'] = os.path.join(DIRS['root'], 'config')
DIRS['doc'] = os.path.join(DIRS['root'], 'doc')
DIRS['lib'] = os.path.join(DIRS['root'], 'lib')
DIRS['m4'] = os.path.join(DIRS['root'], 'm4')
DIRS['modules'] = os.path.join(DIRS['root'], 'modules')
DIRS['tests'] = os.path.join(DIRS['root'], 'tests')
DIRS['git'] = os.path.join(DIRS['root'], '.git')
DIRS['cvs'] = os.path.join(DIRS['root'], 'CVS')

# Set FILES dictionary
FILES['changelog'] = os.path.join(DIRS['root'], 'ChangeLog')

# Set MODES dictionary
MODES['verbose-min'] = -2
MODES['verbose-max'] = 2
MODES['tests'] = \
{
  'default': 1,
  'obsolete': 2,
  'cxx': 4, 'c++': 4,
  'longrunning': 8,
  'privileged': 16,
  'unportable': 32,
}

# You can set AUTOCONFPATH to empty if autoconf 2.57 is already in your PATH
AUTOCONFPATH = ''
# You can set AUTOMAKEPATH to empty if automake 1.9.x is already in your PATH
AUTOMAKEPATH = ''
# You can set GETTEXTPATH to empty if autopoint 0.15 is already in your PATH
GETTEXTPATH = ''
# You can set LIBTOOLPATH to empty if libtoolize 2.x is already in your PATH
LIBTOOLPATH = ''

# You can also set the variable AUTOCONF individually
if AUTOCONFPATH:
  UTILS['autoconf'] = AUTOCONFPATH + 'autoconf'
else:
  if os.getenv('AUTOCONF'):
    UTILS['autoconf'] = os.getenv('AUTOCONF')
  else:
    UTILS['autoconf'] = 'autoconf'

# You can also set the variable AUTORECONF individually
if AUTOCONFPATH:
  UTILS['autoreconf'] = AUTOCONFPATH + 'autoreconf'
else:
  if os.getenv('AUTORECONF'):
    UTILS['autoreconf'] = os.getenv('AUTORECONF')
  else:
    UTILS['autoreconf'] = 'autoreconf'

# You can also set the variable AUTOHEADER individually
if AUTOCONFPATH:
  UTILS['autoheader'] = AUTOCONFPATH + 'autoheader'
else:
  if os.getenv('AUTOHEADER'):
    UTILS['autoheader'] = os.getenv('AUTOHEADER')
  else:
    UTILS['autoheader'] = 'autoheader'

# You can also set the variable AUTOMAKE individually
if AUTOMAKEPATH:
  UTILS['automake'] = AUTOMAKEPATH + 'automake'
else:
  if os.getenv('AUTOMAKE'):
    UTILS['automake'] = os.getenv('AUTOMAKE')
  else:
    UTILS['automake'] = 'automake'

# You can also set the variable ACLOCAL individually
if AUTOMAKEPATH:
  UTILS['aclocal'] = AUTOMAKEPATH + 'aclocal'
else:
  if os.getenv('ACLOCAL'):
    UTILS['aclocal'] = os.getenv('ACLOCAL')
  else:
    UTILS['aclocal'] = 'aclocal'

# You can also set the variable AUTOPOINT individually
if GETTEXTPATH:
  UTILS['autopoint'] = GETTEXTPATH + 'autopoint'
else:
  if os.getenv('AUTOPOINT'):
    UTILS['autopoint'] = os.getenv('AUTOPOINT')
  else:
    UTILS['autopoint'] = 'autopoint'

# You can also set the variable LIBTOOLIZE individually
if LIBTOOLPATH:
  UTILS['libtoolize'] = LIBTOOLPATH + 'libtoolize'
else:
  if os.getenv('LIBTOOLIZE'):
    UTILS['libtoolize'] = os.getenv('LIBTOOLIZE')
  else:
    UTILS['libtoolize'] = 'libtoolize'

# You can also set the variable MAKE
if os.getenv('MAKE'):
  UTILS['make'] = os.getenv('MAKE')
else:
  UTILS['make'] = 'make'

