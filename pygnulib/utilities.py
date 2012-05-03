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
MODES = constants.MODES


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
  '''GNULibMode class is used to create basic mode instance. All the methods
  which can be applied to GNULibMode can be applied to any other mode.
  GNULibMode is the parent for all the other modes, so every new mode must be
  based on this class.'''
  
  def __init__(self):
    '''Create GNULibMode instance.'''
    self.mode = None
    self.destdir = os.getcwd()
    if type(self.destdir) is bytes:
      self.destdir = string(os.getcwd(), ENCS['system'])
    self.localdir = string()
    self.modcache = True
    self.verbose = int()
    
  def getDestDir(self):
    '''Return the target directory. For --import, this specifies where your
    configure.ac can be found. Defaults to current directory.'''
    return(self.destdir)
    
  def setDestDir(self, directory):
    '''Specify the target directory. For --import, this specifies where your
    configure.ac can be found. Defaults to current directory.'''
    if type(directory) is bytes or type(directory) is string:
      if type(directory) is bytes:
        self.destdir = string(directory, ENCS['shell'])
      elif type(directory) is string:
        self.destdir = directory
    else:
      raise(TypeError(
        'argument must be a string, not %s' % type(directory).__name__))
    
  def getLocalDir(self):
    '''Return a local override directory where to look up files before looking
    in gnulib's directory.'''
    return(self.localdir)
    
  def setLocalDir(self, directory):
    '''Specify a local override directory where to look up files before looking
    in gnulib's directory.'''
    if type(directory) is bytes or type(directory) is string:
      if type(directory) is bytes:
        self.localdir = string(directory, ENCS['shell'])
      elif type(directory) is string:
        self.localdir = directory
    else:
      raise(TypeError(
        'argument must be a string, not %s' % type(directory).__name__))
    
  def checkModuleCaching(self):
    '''Get status of module caching optimization.'''
    return(self.modcache)
    
  def enableModuleCaching(self):
    '''Enable module caching optimization.'''
    self.modcache = True
    
  def disableModuleCaching(self):
    '''Disable module caching optimization.'''
    self.modcache = False
    
  def getVerbosity(self):
    '''Get verbosity level.'''
    return(self.verbose)
    
  def decreaseVerbosity(self):
    '''Decrease verbosity level.'''
    if self.verbose > MODES['verbose-min']:
      self.verbose -= 1
    
  def increaseVerbosity(self):
    '''Increase verbosity level.'''
    if self.verbose < MODES['verbose-max']:
      self.verbose += 1
    
  def setVerbosity(self, verbose):
    '''Set verbosity level to verbose, where -2 <= verbose <= 2.
    If verbosity level is less than -2, verbosity level will be set to -2.
    If verbosity level is greater than 2, verbosity level will be set to 2.'''
    if type(verbose) is int:
      if MODES['verbose-min'] <= verbose <= MODES['verbose-max']:
        self.verbose = verbose
      elif verbose < MODES['verbose-min']:
        self.verbose = MODES['verbose-min']
      elif verbose > MODES['verbose-max']:
        self.verbose = MODES['verbose-max']
    else:
      raise(TypeError(
        'argument must be a string, not %s' % type(module).__name__))


################################################################################
# Define GNULibMode class
################################################################################
class GNULibImport(GNULibMode):
  '''GNULibImport class is used to provide methods for --import, --add-import,
  --remove-import and --update actions.'''
  
  def __init__(self):
    '''Create GNULibImport instance.'''
    self.mode = None
    self.destdir = os.getcwd()
    if type(self.destdir) is bytes:
      self.destdir = string(os.getcwd(), ENCS['system'])
    self.localdir = string()
    self.modcache = True
    self.verbose = int()
    self.modules = list()
    self.dryrun = bool()
    self.tests = int()
    
  def addImport(self, module):
    '''Import the given module into the current package.'''
    if type(module) is bytes or type(module) is string:
      if type(module) is bytes:
        module = string(module, ENCS['shell'])
      elif type(module) is string:
        module = module
      self.modules.append(module)
    else:
      raise(TypeError(
        'argument must be a string, not %s' % type(module).__name__))
    
  def removeImport(self, module):
    '''Remove the given module from the current package.'''
    if type(module) is bytes or type(module) is string:
      if type(module) is bytes:
        module = string(module, ENCS['shell'])
      elif type(module) is string:
        module = module
      self.modules.remove(module)
    else:
      raise(TypeError(
        'argument must be a string, not %s' % type(module).__name__))
    
  def getImports(self):
    '''Return the list of the modules from the current package.'''
    return(self.modules)
    
  def setImports(self, modules):
    '''Specify the modules which will be imported into the current package.'''
    if type(modules) is list or type(modules) is tuple:
      for module in modules:
        if type(module) is not string:
          raise(TypeError(
            'every module must be a string, not %s' % type(module).__name__))
      self.modules = modules
    else:
      raise(TypeError(
        'modules must be a list, not %s' % type(modules).__name__))
    
  def resetImports(self):
    '''Reset the list of the modules.'''
    self.modules = list()
    
  def checkDryRun(self):
    '''Check whether user enabled dry run mode.'''
    return(self.dryrun)
    
  def enableDryRun(self):
    '''Only print what would have been done.'''
    self.dryrun = True
    
  def disableDryRun(self):
    '''Really execute what shall be done.'''
    self.dryrun = False
    
  def setTestFlags(self, flags):
    '''Set test flags. You can get all flags from MODES['tests'] variable.'''
    if type(flags) is int:
      self.tests = flags

