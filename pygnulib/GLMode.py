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
from .GLError import GLError


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
PYTHON3 = constants.PYTHON3
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
# Define GLMode class
#===============================================================================
class GLMode(object):
  '''GLMode class is used to create basic mode instance. All the methods
  which can be applied to GLMode can be applied to any other mode.
  GLMode is the parent for all the other modes, so every new mode must be
  based on this class.'''
  
  def __init__\
  (
    self,
    destdir=None,
    localdir=None,
    verbose=None,
    modcache=None,
  ):
    '''Create GLImport instance. There are some variables which can be
    used in __init__ section. However, you can set them later using methods
    inside GLImport class. See info for each variable in the corresponding
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
    
  def __repr__(self):
    '''x.__repr__ <==> repr(x)'''
    return('<pygnulib.GLMode>')
    
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
        raise(GLError(1, directory))
      self.args['destdir'] = directory
    else:
      raise(TypeError(
        'directory must be a string, not %s' % type(directory).__name__))
    
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
        'directory must be a string, not %s' % type(directory).__name__))
    
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
    else: # if type(verbose) is not int
      raise(TypeError(
        'argument must be an int, not %s' % type(verbose).__name__))
    
  def resetVerbosity(self):
    '''Reset verbosity level.'''
    self.setVerbosity(self.cache['verbose'])

