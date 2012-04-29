#!/usr/bin/python3

################################################################################
# Define global imports
################################################################################
import io
import os
import re
import sys
import time
import tempfile as tf
import subprocess as sp


################################################################################
# Define module information
################################################################################
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


################################################################################
# Define global constants
################################################################################
# Create string compatibility
if sys.version_info.major == 2: # Using Python 2
  string = unicode
else: # Using Python 3 (PY3K)
  string = str

# Declare neccessary variables
APP = dict() # Application
DIRS = dict() # Directories
UTILS = dict() # Utilities
ENCS = dict() # Encodings
FILES = dict() # Files

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
DIRS['git'] = os.path.join(DIRS['root'], '.git')
DIRS['cvs'] = os.path.join(DIRS['root'], 'CVS')

# Set FILES dictionary
FILES['changelog'] = os.path.join(DIRS['root'], 'ChangeLog')

# Set ENCS dictionary
ENCS['system'] = sys.getfilesystemencoding()
ENCS['default'] = sys.getdefaultencoding()
ENCS['shell'] = sys.stdout.encoding

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


################################################################################
# Define GNULibInfo class
################################################################################
class GNULibInfo:
  '''This class is used to get fromatted information about gnulib-tool.
  This information is mainly used in stdout messages, but can be used
  anywhere else. The return values are not the same as for the module,
  but still depends on them.'''
  
  def package(self):
    '''Return formatted string which contains name of the package.'''
    result = 'GNU gnulib-tool'
    return(result)
    
  def authors(self):
    '''Return formatted string which contains authors.
    The special __author__ variable is used (type is list).'''
    result = string() # Empty string
    for item in __author__:
      if item == __author__[-2]:
        result += '%s ' % item
      elif item == __author__[-1]:
        result += 'and %s' % item
      else:
        result += '%s, ' % item
    return(result)
    
  def license(self):
    '''Return formatted string which contains license and its description.'''
    result = 'License GPLv3+: GNU GPL version 3 or later'
    result += ' <http://gnu.org/licenses/gpl.html>\n'
    result += 'This is free software: you are free'
    result += ' to change and redistribute it.\n'
    result += 'There is NO WARRANTY, to the extent permitted by law.'
    return(result)
    
  def copyright(self):
    '''Return formatted string which contains copyright.
    The special __copyright__ variable is used (type is str).'''
    result = 'Copyright (C) %s' % __copyright__
    return(result)
    
  def date(self):
    '''Return formatted string which contains date and time in GMT format.'''
    if os.path.exists(DIRS['git']) and os.path.isdir(DIRS['git']):
      counter = int() # Create counter
      result = string() # Create string
      args = ['git', 'log', FILES['changelog']]
      proc1 = sp.Popen(args,stdout=sp.PIPE)
      proc2 = sp.Popen(['head'],
        stdin=proc1.stdout, stdout=sp.PIPE)
      proc1.stdout.close()
      while counter <= 2:
        result += string(proc2.stdout.readline(), ENCS['shell'])
        counter += 1
      pattern = re.compile('Date:[\t ]*(.*?)\n')
      result = pattern.findall(result)[0]
      pattern = re.compile('^[^ ]* ([^ ]*) ([0-9]*) ([0-9:]*) ([0-9]*) ')
      result = pattern.sub('\\1 \\2 \\4 \\3 ', result)
      args = ['date', '-d', result, '-u', '+%Y-%m-%d %H:%M:%S']
      proc = sp.check_output(args)
      result = string(proc, ENCS['shell'])
      result = result.rstrip(os.linesep)
      return(result)
    
  def version(self):
    '''Return formatted string which contains git or CVS version.'''
    if os.path.exists(DIRS['git']) and os.path.isdir(DIRS['git']):
      version_gen = os.path.join(DIRS['build-aux'], 'git-version-gen')
      args = [version_gen, DIRS['root']]
      proc = sp.check_output(args)
      result = string(proc, ENCS['shell'])
      result = result.rstrip(os.linesep)
      return(result)


################################################################################
# Run the main part
################################################################################
if __name__ == '__main__':
  info = GNULibInfo()
  message = \
    '%s (%s %s) %s\n%s\n%s\n\nWritten by %s' % \
    (
      APP['name'], info.package(), info.date(), info.version(),
      info.copyright(), info.license(), info.authors()
    )
  print(message)