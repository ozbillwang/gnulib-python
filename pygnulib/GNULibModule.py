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
from .GNULibMode import GNULibMode


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
# Define GNULibModule class
#===============================================================================
class GNULibModule(GNULibMode):
  '''GNULibModule is used to create module object and provides methods to get
  information about this module.'''
  
  def __init__\
  (
    self,
    module,
    destdir=None,
    localdir=None,
    verbose=None,
    modcache=None,
  ):
    '''Create new GNULibModule instance. Args are the same as for the
    GNULibMode, except for the module argument which must be a string which
    reprents the name of the module. When module is creating, GNULibModule
    checks whether module exists both in gnulib directory and directory
    specified by localdir.'''
    super(GNULibModule, self).__init__\
    ( # Begin __init__ method
      destdir=destdir,
      localdir=localdir,
      modcache=modcache,
      verbose=verbose,
    ) # Complete __init__ method
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
      if module in badnames:
        raise(GNULibError(3, repr(module)))
      else: # if module not in badnames
        self.module = module
    else: # if module was found
      raise(GNULibError(3, repr(module)))
    
    