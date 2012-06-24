#!/usr/bin/python
# encoding: UTF-8

#===============================================================================
# Define global imports
#===============================================================================
import os
import re
import sys
import locale
import codecs
import subprocess as sp
from . import constants


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
# Define GNULibError class
#===============================================================================
class GNULibError(Exception):
  '''Exception handler for GNULib classes.'''
  
  def __init__(self, errno, errinfo=None):
    '''Each error has following parameters:
    errno: code of error; used to catch error type
      1: destination directory does not exist: <destdir>
      2: configure file does not exist: <configure.ac>
      3: selected module does not exist: <module>
      4: <cache> is expected to contain gl_M4_BASE([m4base])
      5: missing sourcebase argument
      6: missing docbase argument
      7: missing testsbase argument
      8: missing libname argument'''
    self.args = (errno, errinfo)
    self.errno = errno
    self.errinfo = errinfo
    self.args = (self.errno, self.errinfo)
    
  def _get_message(self):
    errors = \
    [ # Begin list of errors
      "destination directory does not exist: %s" % self.errinfo,
      "configure file does not exist: %s" % self.errinfo,
      "selected module does not exist: %s" % self.errinfo,
      "%s is expected to contain gl_M4_BASE([%s])" % \
        (os.path.join(self.errinfo, 'gnulib-comp.m4'), self.errinfo),
      "missing sourcebase argument; cache file doesn't contain it,"
        +" so you might have to set this argument",
      "missing docbase argument; you might have to create GNULibImport" \
        +" instance with mode 0 and docbase argument",
      "missing testsbase argument; cache file doesn't contain it,"
        +" so you might have to set this argument"
      "missing libname argument; cache file doesn't contain it,"
        +" so you might have to set this argument",
      "dependencies and testflag 'default' cannot be used together",
    ] # Complete list of errors
    if not PYTHON3:
      self._message = (b'[Errno %d] %s' % \
        (self.errno, self.errors[self.errno -1].encode(ENCS['default'])))
    else: # if PYTHON3
      self._message = ('[Errno %d] %s' % \
        (self.errno, self.errors[self.errno -1]))
    return(self._message)
  def _set_message(self, message): 
    self._message = message
  message = property(_get_message, _set_message)
    
  #def __str__(self):
    

