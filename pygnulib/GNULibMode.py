#!/usr/bin/python
# encoding: UTF-8

#===============================================================================
# Define global imports
#===============================================================================
import os
import re
import sys
import codecs
import subprocess as sp
from . import constants
from .GNULibError import GNULibError


#===============================================================================
# Define module information
#===============================================================================
__author__ = constants.__author__
__license__ = constants.__license__
__copyright__ = constants.__copyright__
__version__ = constants.__version__


#===============================================================================
# Define global constants
#===============================================================================
NoneType = type(None)
APP = constants.APP
DIRS = constants.DIRS
ENCS = constants.ENCS
UTILS = constants.UTILS
FILES = constants.FILES
MODES = constants.MODES
TESTS = constants.TESTS
compiler = constants.compiler
joinpath = constants.joinpath
cleaner = constants.cleaner
string = constants.string
isabs = os.path.isabs
isdir = os.path.isdir
isfile = os.path.isfile
normpath = os.path.normpath
relpath = os.path.relpath


#===============================================================================
# Define GNULibMode class
#===============================================================================
class GNULibMode(object):
  '''GNULibMode class is used to create basic mode instance. All the methods
  which can be applied to GNULibMode can be applied to any other mode.
  GNULibMode is the parent for all the other modes, so every new mode must be
  based on this class.'''
  
  def __init__\
  (
    self,
    destdir=None,
    localdir=None,
    verbose=None,
    modcache=None,
  ):
    '''Create GNULibImport instance. There are some variables which can be
    used in __init__ section. However, you can set them later using methods
    inside GNULibImport class. See info for each variable in the corresponding
    set* class. The main variable, mode, must be one of the values of the
    MODES dict object, which is accessible from this module.'''
    
    # Create cache dictionary
    self.args = dict()
    self.cache = dict()
    self.cache['destdir'] = '.'
    self.cache['localdir'] = ''
    self.cache['modcache'] = True
    self.cache['verbose'] = 0
    
    # destdir => self.args['destdir']
    if destdir == None:
      self.resetDestDir()
    else: # if destdir != None
      self.setDestDir(destdir)
    
    # localdir => self.args['localdir']
    if localdir == None:
      self.resetLocalDir()
    else: # if localdir != None
      self.setLocalDir(localdir)
    
    # modcache => self.args['modcache']
    if type(modcache) is NoneType:
      self.resetModuleCaching()
    elif type(modcache) is bool:
      if modcache:
        self.enableModuleCaching()
      else: # if not modcache
        self.disableModuleCaching()
    
    # verbose => self.args['localdir']
    if type(verbose) is NoneType:
      self.resetVerbosity()
    elif type(verbose) is int:
      self.setVerbosity(verbose)
    
  def getAllModules(self):
    '''Return the available module names as tuple. We could use a combination
    of os.walk() function and re module. However, it takes too much time to
    complete, so this version uses subprocess to run shell commands.'''
    args1 = ['find', 'modules', '-type', 'f', '-print']
    args2 = \
    [
      'sed',
      '-e', r's,^modules/,,',
      '-e', r'/^CVS\//d',
      '-e', r'/\/CVS\//d',
      '-e', r'/^ChangeLog$/d',
      '-e', r'/\/ChangeLog$/d',
      '-e', r'/^COPYING$/d',
      '-e', r'/\/COPYING$/d',
      '-e', r'/^README$/d',
      '-e', r'/\/README$/d',
      '-e', r'/^TEMPLATE$/d',
      '-e', r'/^TEMPLATE-EXTENDED$/d',
      '-e', r'/^TEMPLATE-TESTS$/d',
      '-e', r'/^\..*/d',
      '-e', r'/~$/d',
      '-e', r'/-tests$/d',
    ]
    localdir = self.args['localdir']
    if localdir and isdir(joinpath(localdir, 'modules')):
      os.chdir(self.args['localdir'])
      args2.append('-e')
      args2.append(r's,\.diff$,,')
    proc1 = sp.Popen(args1, stdout=sp.PIPE)
    proc2 = sp.Popen(args2, stdin=proc1.stdout, stdout=sp.PIPE)
    proc1.stdout.close() # Close the first shell pipe
    result = string(proc2.stdout.read(), ENCS['shell'])
    if result[-2:] == '\r\n':
      result = result.replace('\r\n', '\n')
    if result[-1] == '\n':
      result = result[:-1]
    listing = result.splitlines(); listing.sort()
    listing = tuple(listing)
    os.chdir(DIRS['cwd'])
    return(listing)
    
  def checkModule(self, module):
    '''Check if module exists inside gnulib dir or localdir.'''
    result = bool()
    if type(module) is bytes or type(module) is string:
      if type(module) is bytes:
        module = string(module, ENCS['system'])
    else: # if module has not bytes or string type
      raise(TypeError(
        'argument must be a string, not %s' % type(module).__name__))
    badnames = ['CVS', 'ChangeLog', 'COPYING', 'README', 'TEMPLATE',
      'TEMPLATE-EXTENDED', 'TEMPLATE-TESTS']
    if isfile(joinpath(DIRS['modules'], module)) or \
    all([ # Begin all(iterable) function
      self.args['localdir'],
      isdir(joinpath(self.args['localdir'], 'modules')),
      isfile(joinpath(self.args['localdir'], 'modules', module))
    ]): # Close all(iterable) function
      if module not in badnames:
        result = True
    return(result)
    
  def getDestDir(self):
    '''Return the target directory. For --import, this specifies where your
    configure.ac can be found. Defaults to current directory.'''
    return(self.args['destdir'])
    
  def setDestDir(self, directory):
    '''Specify the target directory. For --import, this specifies where your
    configure.ac can be found. Defaults to current directory.'''
    if type(directory) is bytes or type(directory) is string:
      if type(directory) is bytes:
        directory = string(directory, ENCS['system'])
      if not isdir(directory):
        raise(GNULibError(1, repr(directory)))
      self.args['destdir'] = directory
    else:
      raise(TypeError(
        'argument must be a string, not %s' % type(directory).__name__))
    
  def resetDestDir(self):
    '''Reset the target directory. For --import, this specifies where your
    configure.ac can be found. Defaults to current directory.'''
    self.setDestDir(self.cache['destdir'])
    
  def getLocalDir(self):
    '''Return a local override directory where to look up files before looking
    in gnulib's directory.'''
    return(self.args['localdir'])
    
  def setLocalDir(self, directory):
    '''Specify a local override directory where to look up files before looking
    in gnulib's directory.'''
    if type(directory) is bytes or type(directory) is string:
      if type(directory) is bytes:
        directory = string(directory, ENCS['system'])
      self.args['localdir'] = directory
    else:
      raise(TypeError(
        'argument must be a string, not %s' % type(directory).__name__))
    
  def resetLocalDir(self):
    '''Reset a local override directory where to look up files before looking
    in gnulib's directory.'''
    self.setLocalDir(self.cache['localdir'])
    
  def checkModuleCaching(self):
    '''Get status of module caching optimization.'''
    return(self.args['modcache'])
    
  def enableModuleCaching(self):
    '''Enable module caching optimization.'''
    self.args['modcache'] = True
    
  def disableModuleCaching(self):
    '''Disable module caching optimization.'''
    self.args['modcache'] = False
    
  def resetModuleCaching(self):
    '''Reset module caching optimization.'''
    self.args['modcache'] = self.cache['modcache']
    
  def getVerbosity(self):
    '''Get verbosity level.'''
    return(self.args['verbose'])
    
  def decreaseVerbosity(self):
    '''Decrease verbosity level.'''
    if self.args['verbose'] > MODES['verbose-min']:
      self.args['verbose'] -= 1
    
  def increaseVerbosity(self):
    '''Increase verbosity level.'''
    if self.args['verbose'] < MODES['verbose-max']:
      self.args['verbose'] += 1
    
  def setVerbosity(self, verbose):
    '''Set verbosity level to verbose, where -2 <= verbose <= 2.
    If verbosity level is less than -2, verbosity level will be set to -2.
    If verbosity level is greater than 2, verbosity level will be set to 2.'''
    if type(verbose) is int:
      if MODES['verbose-min'] <= verbose <= MODES['verbose-max']:
        self.args['verbose'] = verbose
      elif verbose < MODES['verbose-min']:
        self.args['verbose'] = MODES['verbose-min']
      elif verbose > MODES['verbose-max']:
        self.args['verbose'] = MODES['verbose-max']
    else:
      raise(TypeError(
        'argument must be a string, not %s' % type(module).__name__))
    
  def resetVerbosity(self):
    '''Reset verbosity level.'''
    self.setVerbosity(self.cache['verbose'])

