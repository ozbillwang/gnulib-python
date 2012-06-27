#!/usr/bin/python
# encoding: UTF-8

#===============================================================================
# Define global imports
#===============================================================================
import os
import re
import sys
import codecs
import shutil
import tempfile
from io import BytesIO
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
# Define GLFileSystem class
#===============================================================================
class GLFileSystem(object):
  '''GLFileSystem class is used to create virtual filesystem, which is based on
  the gnulib directory and directory specified by localdir argument. Its main
  method lookup(file) is used to find file in these directories or combine it
  using Linux 'patch' utility.'''
  
  def __init__(self, localdir=''):
    '''Create new GLFileSystem instance. The only argument is localdir,
    which can be an empty string too.'''
    self.args = dict()
    if type(localdir) is bytes or type(localdir) is string:
      if type(localdir) is bytes:
        localdir = localdir.decode(ENCS['default'])
      self.args['localdir'] = localdir
    else: # if localdir has not bytes or string type
      raise(TypeError(
        'localdir must be a string, not %s' % type(localdir).__name__))
    
  def __repr__(self):
    '''x.__repr__ <==> repr(x)'''
    return('<pygnulib.GLFileSystem>')
    
  def lookup(self, name):
    '''GLFileSystem.lookup(name) -> string
    
    Lookup a file in gnulib and localdir directories or combine it using Linux
    'patch' utility. If file was found, method returns string, else it raises
    GLError telling that file was not found.'''
    if type(name) is bytes or type(name) is string:
      if type(name) is bytes:
        name = name.decode(ENCS['default'])
    else: # if name has not bytes or string type
      raise(TypeError(
        'name must be a string, not %s' % type(module).__name__))
    # If name exists in localdir, then we use it
    path_gnulib = joinpath(DIRS['root'], name)
    path_local = joinpath(self.args['localdir'], name)
    path_diff = joinpath(self.args['localdir'], '%s.diff' % name)
    path_temp = joinpath(tempfile.mkdtemp(), name)
    os.makedirs(os.path.dirname(path_temp))
    if self.args['localdir'] and isfile(path_local):
      result = (path_local, False)
    else: # if path_local does not exist
      if isfile(path_gnulib):
        if self.args['localdir'] and isfile(path_diff):
          shutil.copy(path_gnulib, path_temp)
          command = 'patch -s "%s" < "%s"' % (path_temp, path_diff)
          try: # Try to apply patch
            sp.check_call(command, shell=True)
          except sp.CalledProcessError as error:
            raise(GLError(4, name))
          result = (path_temp, True)
        else: # if path_diff does not exist
          result = (path_gnulib, False)
      else: # if path_gnulib does not exist
        raise(GLError(3, name))
    return(result)

