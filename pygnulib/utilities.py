#!/usr/bin/python
'''This script is a part of PyGNULib module for gnulib.'''

################################################################################
# Define global imports
################################################################################
import os
import re
import sys
import subprocess as sp
from . import constants


################################################################################
# Define module information
################################################################################
__author__ = constants.__author__
__license__ = constants.__license__
__copyright__ = constants.__copyright__
__version__ = constants.__version__


################################################################################
# Define global constants
################################################################################
NoneType = type(None)
string = constants.string
APP = constants.APP
DIRS = constants.DIRS
ENCS = constants.ENCS
UTILS = constants.UTILS
FILES = constants.FILES


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
      # Get date as "Fri Mar 21 07:16:51 2008 -0600" from string
      pattern = re.compile('Date:[\t ]*(.*?)\n')
      result = pattern.findall(result)[0]
      # Turn "Fri Mar 21 07:16:51 2008 -0600" into "Mar 21 2008 07:16:51 -0600"
      pattern = re.compile('^[^ ]* ([^ ]*) ([0-9]*) ([0-9:]*) ([0-9]*) ')
      result = pattern.sub('\\1 \\2 \\4 \\3 ', result)
      # Use GNU date to compute the time in GMT
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
# Define GNULibMode class
################################################################################
class GNULibMode:
  '''GNULibMode class is used to determine what kind of actions each mode
  supports and what settings can be applied to it.'''
  
  def __init__(self, mode, xtype=None):
    '''Create GNULibMode instance for using it in GNULibTool class.
    Method has only one required argument, mode, which can be string or int.
    The optional argument, xtype, can be used only in combination with extract
    mode, otherwise it is ignored.
      0, 'l', 'list':
        print the available module names
      1, 'f', 'find':
        find the modules which contain the specified file
      2, 'a', 'add', 'add-import':
        augment the list of imports from gnulib into the current package,
        by adding the given modules; if no modules are specified, update the
        current package from the current gnulib
      3, 'r', 'remove', 'remove-import':
        reduce the list of imports from gnulib into the current package,
        by removing the given modules
      4, 'u', 'update':
        update the current package, restore files omitted from version control
      5, 'td', 'testdir', 'create-testdir':
        create a scratch package with the given modules
        (pass --with-tests to include the unit tests)
      6, 'TD', 'megatestdir', 'create-megatestdir':
        create a mega scratch package with the given modules
        (pass --with-tests to include the unit tests)
      7, 't', 'test':
        test the combination of the given modules
        (pass --with-tests to include the unit tests)
        (recommended to use CC="gcc -Wall" here)
      8, 'T', 'megatest':
        test the given modules one by one and all together
        (pass --with-tests to include the unit tests)
        (recommended to use CC="gcc -Wall" here)
      9, 'x', 'extract':
        extract something (description, comment, status, etc.) using gnulib
        type of extract can be set using optional xtype argument
          0, 'd', 'descr', 'description':
            extract the description
          1, 'c', 'comment':
            extract the comment
          2, 's', 'status':
            extract the status (obsolete etc.)
          3, 'n', 'notice':
            extract the notice or banner
          4, 'a', 'applicability':
            extract the applicability
          5, 'f', 'filelist':
            extract the list of files
          6, 'D', 'deps', 'dependencies':
            extract the dependencies
          7, 'acs', 'ac-snippet', 'autoconf-snippet':
            extract the snippet for configure.ac
          8, 'ams', 'am-snippet', 'automake-snippet':
            extract the snippet for library makefile
          9, 'i', 'include', 'include-directive':
            extract the #include directive
          10, 'l', 'link', 'link-directive':
            extract the linker directive
          11, 'L', 'license':
            report the license terms of the source files under lib/
          12, 'm', 'maintainer':
            report the maintainer(s) inside gnulib
          13, 't', 'tests-module':
            report the unit test module, if it exists
      10, 'c', 'copy-file':
        copy a file that is not part of any module'''
    self.mode = None
    self.avoid = list()
    self.options = dict()
    self.available = list()
    self.dir = os.getcwd()
    if type(self.dir) is bytes:
      self.dir = string(os.getcwd(), ENCS['system'])
    self.localdir = string()
    self.verbose = int()
    self.cache = True
    counter = int()
    table = \
    [ # Don't change the structure of this table!
      ['l', 'list'],
      ['f', 'find'],
      ['a', 'add', 'add-import'],
      ['r', 'remove', 'remove-import'],
      ['u', 'update'],
      ['td', 'testdir', 'create-testdir'],
      ['TD', 'megatestdir', 'create-megatestdir'],
      ['t', 'test'],
      ['T', 'megatest'],
      ['x', 'extract'],
      ['c', 'copy-file'],
    ] # Don't change the structure of this table!
    for row in table:
      if mode == counter or mode in row:
        self.mode = row[-1]
        break
      counter += 1
    if type(self.mode) is NoneType:
      raise(TypeError)
    if mode in ['import', 'add-import', 'remove-import', 'update']:
      self.available.append('dry-run')
    elif mode in \
    [
      'import', 'add-import', 'remove-import',
      'create-testdir', 'create-megatestdir',
      'test', 'megatest',
    ]:
      self.available.append('avoid')
      self.available.append('with-tests')
      self.available.append('with-obsolete')
      self.available.append('with-c++-tests')
      self.available.append('with-longrunning-tests')
      self.available.append('with-privileged-tests')
      self.available.append('with-unportable-tests')
      self.available.append('with-all-tests')
      self.available.append('conditional-dependencies')
      self.available.append('no-conditional-dependencies')
      self.available.append('libtool')
      self.available.append('no-libtool')
    
  def addAvoid(self, module):
    '''Add module to list of modules which shall be avoided.
    Useful if you have code that provides equivalent functionality.'''
    if type(module) is bytes:
      module = string(module, ENCS['shell'])
      self.avoid.append(module)
    elif type(module) is string:
      self.avoid.append(module)
    else:
      raise(TypeError, 'argument must be a string, not %s' % type(directory))
    
  def removeAvoid(self, module):
    '''Remove module from list of modules which shall be avoided.
    Useful if you have code that provides equivalent functionality.'''
    if type(module) is bytes:
      module = string(module, ENCS['shell'])
      if module in self.avoid:
        self.avoid.remove(module)
    elif type(module) is string:
      if module in self.avoid:
        self.avoid.remove(module)
    else:
      raise(TypeError, 'argument must be a string, not %s' % type(directory))
    
  def getAvoidList(self):
    '''Return list of modules which shall be avoided.
    Useful if you have code that provides equivalent functionality.'''
    return(self.avoid)
    
  def setAvoidList(self, modules):
    '''Return list of modules which shall be avoided.
    Useful if you have code that provides equivalent functionality.'''
    self.avoid = modules
    
  def getDir(self):
    '''Ruturn the target directory. For --import, this specifies where your
    configure.ac can be found. Defaults to current directory.'''
    return(self.dir)
    
  def getLocalDir(self):
    '''Return a local override directory where to look up files before looking
    in gnulib's directory.'''
    return(self.localdir)
    
  def getOptions(self):
    '''Return all the options as the dictionary.'''
    return(self.options)
    
  def addOption(self, option, value):
    '''Set option for running gnulib. Option argument is a string which
    contains name of the option and value is the value which will be set for
    this option.'''
    options = self.options.keys()
    values = self.options.items()
    if option in options:
      self.options[option] = value
    
  def setDir(self, directory):
    '''Specify the target directory. For --import, this specifies where your
    configure.ac can be found. Defaults to current directory.'''
    if type(directory) is bytes:
      self.dir = string(directory, ENCS['shell'])
    elif type(directory) is string:
      self.dir = directory
    else:
      raise(TypeError, 'argument must be a string, not %s' % type(directory))
    
  def setLocalDir(self, directory):
    '''Specify a local override directory where to look up files before looking
    in gnulib's directory.'''
    if type(directory) is bytes:
      self.localdir = string(directory, ENCS['shell'])
    elif type(directory) is string:
      self.localdir = directory
    else:
      raise(TypeError, 'argument must be a string, not %s' % type(directory))


################################################################################
# Define GNULibTool class
################################################################################
class GNULibTool:
  
  def __init__(self, mode):
    '''Create GNULibTool instance with selected mode of work. Mode must be one
    of the following strings or numbers:'''
    self.modes = \
    [
      'list', # print the available module names
      'find', # find the modules which contain the specified file
      'add-import', # augment the list of imports from gnulib
      'remove-import', #
    ]
