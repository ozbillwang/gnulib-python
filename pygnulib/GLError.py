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
# Define GLError class
#===============================================================================
class GLError(Exception):
  '''Exception handler for GL classes.'''

  def __init__(self, errno, errinfo=None):
    '''Each error has following parameters:
    errno: code of error; used to catch error type
      1: destination directory does not exist: <destdir>
      2: configure file does not exist: <configure.ac>
      3: file does not exist in GLFileSystem: <file>
      4: cannot patch file inside GLFileSystem: <file>
      5: <cache> is expected to contain gl_M4_BASE([<m4base>])
      6: missing sourcebase argument
      7: missing docbase argument
      8: missing testsbase argument
      9: missing libname argument
    errinfo: additional information'''
    self.errno = errno; self.errinfo = errinfo
    self.args = (self.errno, self.errinfo)

  def __repr__(self):
    errinfo = self.errinfo
    errors = \
    [ # Begin list of errors
      "destination directory does not exist: %s" % repr(errinfo),
      "configure file does not exist: %s" % repr(errinfo),
      "file does not exist in GLFileSystem: %s" % repr(errinfo),
      "cannot patch file inside GLFileSystem: %s" % repr(errinfo),
      "%s is expected to contain gl_M4_BASE([%s])" % \
        (repr(os.path.join(errinfo, 'gnulib-comp.m4')), repr(errinfo)),
      "missing sourcebase argument; cache file doesn't contain it,"
        +" so you might have to set this argument",
      "missing docbase argument; you might have to create GLImport" \
        +" instance with mode 0 and docbase argument",
      "missing testsbase argument; cache file doesn't contain it,"
        +" so you might have to set this argument"
      "missing libname argument; cache file doesn't contain it,"
        +" so you might have to set this argument",
      "dependencies and testflag 'default' cannot be used together",
    ] # Complete list of errors
    if not PYTHON3:
      self.message = (b'[Errno %d] %s' % \
        (self.errno, errors[self.errno -1].encode(ENCS['default'])))
    else: # if PYTHON3
      self.message = ('[Errno %d] %s' % \
        (self.errno, errors[self.errno -1]))
    return(self.message)

