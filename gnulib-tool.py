#!/usr/bin/python3

####################################################################################################
# Define global imports
####################################################################################################
import os
import re
import sys
import subprocess

####################################################################################################
# Define module information
####################################################################################################
__all__ = ['GNULibInfo']
__license__ = 'GNU GPLv3+'
__copyright__ = '2012 Free Software Foundation, Inc.'
__author__ = \
[
  'Bruno Haible',
  'Simon Josefsson',
  'Dmitriy Selyutin',
]
__version__ = 0.1

####################################################################################################
# Define global constants
####################################################################################################
# Declare neccessary variables
APP = dict() # Application
DIRS = dict() # Directories
UTILS = dict() # Utilities

# Set APP dictionary
APP['name'] = os.path.basename(sys.argv[0])
APP['path'] = os.path.realpath(sys.argv[0])

# Set DIRS dictionary
DIRS['root'] = os.path.dirname(APP['path'])
DIRS['build-aux'] = os.path.join(DIRS['root'], 'build-aux')
DIRS['config'] = os.path.join(DIRS['root'], 'config')
DIRS['doc'] = os.path.join(DIRS['root'], 'doc')
DIRS['lib'] = os.path.join(DIRS['root'], 'lib')
DIRS['m4'] = os.path.join(DIRS['root'], 'm4')
DIRS['modules'] = os.path.join(DIRS['root'], 'modules')
DIRS['tests'] = os.path.join(DIRS['root'], 'tests')

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

# Delete temporary variables
del(AUTOCONFPATH)
del(AUTOMAKEPATH)
del(GETTEXTPATH)
del(LIBTOOLPATH)

####################################################################################################
# Define GNULibInfo class
####################################################################################################
class GNULibInfo(object):
  '''This class is used to get fromatted information about gnulib-tool.
  This information is mainly used in stdout messages, but can be used
  anywhere else. The return values are not the same as for the module,
  but still depends on them.'''
  
  def name(self):
    result = 'GNU gnulib-tool'
    return(result)
    
  def authors(self):
    '''Return formatted string which contains authors.
    The special __author__ variable is used (type is list).'''
    result = str() # Empty string
    for item in __author__:
      if item == __author__[-2]:
        result += '%s ' % item
      elif item == __author__[-1]:
        result += 'and %s' % item
      else:
        result += '%s, ' % item
    return(result)
    
  def license(self):
    result = 'License GPLv3+: GNU GPL version 3 or later <http://gnu.org/licenses/gpl.html>\n'
    result += 'This is free software: you are free to change and redistribute it.\n'
    result += 'There is NO WARRANTY, to the extent permitted by law.'
    return(result)
    
  def copyright(self):
    result = 'Copyright (C) %s' % __copyright__
    return(result)

if __name__ == '__main__':
  info = GNULibInfo()
  message = \
    '%s (here will be gnulib-tool version)\n%s\n%s\n\n%s' % \
    (info.name(), info.copyright(), info.license(), info.authors())
  print(message)