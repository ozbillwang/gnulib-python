#!/usr/bin/python
'''This script is a part of PyGNULib module for gnulib.'''

from __future__ import unicode_literals
#===============================================================================
# Define global imports
#===============================================================================
import re
import os
import sys


#===============================================================================
# Define module information
#===============================================================================
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


#===============================================================================
# Backward compatibility
#===============================================================================
# Check for Python version
if sys.version_info.major == 2:
  PYTHON3 = False
else:
  PYTHON3 = True

# Create string compatibility
if not PYTHON3:
  string = unicode
else: # if PYTHON3
  string = str

# Current working directory
if not PYTHON3:
  os.getcwdb = os.getcwd
  os.getcwd = os.getcwdu


#===============================================================================
# Define global constants
#===============================================================================
# Declare neccessary variables
APP = dict() # Application
DIRS = dict() # Directories
UTILS = dict() # Utilities
ENCS = dict() # Encodings
FILES = dict() # Files
MODES = dict() # Modes
TESTS = dict() # Tests

# Set ENCS dictionary
import __main__ as interpreter
if not hasattr(interpreter, '__file__'):
  ENCS['default'] = sys.stdout.encoding
else: # if hasattr(interpreter, '__file__'):
  ENCS['default'] = 'UTF-8'
ENCS['system'] = sys.getfilesystemencoding()
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
MODES = \
{
  'import': 0,
  'add-import': 1,
  'remove-import': 2,
  'update': 3,
}
MODES['verbose-min'] = -2
MODES['verbose-default'] = 0
MODES['verbose-max'] = 2

# Set TESTS dictionary
TESTS = \
{
  'default': 1,
  'obsolete': 2,
  'cxx': 4, 'c++': 4,
  'longrunning': 8,
  'privileged': 16,
  'unportable': 32,
  'all': 64,
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


#===============================================================================
# Define global functions
#===============================================================================
def compiler(pattern):
  '''Compile regex pattern depending on version of Python.'''
  if not PYTHON3:
    pattern = re.compile(pattern, re.UNICODE | re.MULTILINE | re.DOTALL)
  else: # if PYTHON3
    pattern = re.compile(pattern, re.MULTILINE | re.DOTALL)
  return(pattern)
  
def cleaner(sequence):
  '''Clean string or list of strings after using regex.'''
  if type(sequence) is string:
    sequence = sequence.replace('[', '')
    sequence = sequence.replace(']', '')
  elif type(sequence) is list:
    sequence = [value.replace('[', '').replace(']', '') for value in sequence]
    sequence = [value.replace('(', '').replace(')', '') for value in sequence]
    sequence = [False if value == 'false' else value for value in sequence]
    sequence = [True if value == 'true' else value for value in sequence]
    sequence = [value.strip() for value in sequence]
  return(sequence)
  
def joinpath(head, *tail):
  '''joinpath(head, *tail) -> string
  
  Join two or more pathname components, inserting '/' as needed. If any
  component is an absolute path, all previous path components will be
  discarded. The second argument may be string or list of strings.'''
  result = os.path.normpath(os.path.join(head, *tail))
  return(result)
  
def str_disj(str1, str2):
  '''str_disj(str1, str2) -> string
  
  Performs logical disjunction operation. Arguments can be strings or None.
  None value for argument is as if argument equals to empty string.'''
  if str1 == None: str1 = ''
  if str2 == None: str2 = ''
  if type(str1) is not string or \
  type(str2) is not string:
    if not PYTHON3:
      raise(TypeError(b'each of objects must be a string!'))
    else: # if PYTHON3
      raise(TypeError('each of objects must be a string!'))
  if not str1:
    return(str2)
  else: # if str1
    return(str1)

