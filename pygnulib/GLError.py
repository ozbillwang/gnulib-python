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
import tempfile
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
class GLErrorHandler(Exception):
  '''Exception handler for pygnulib classes.'''

  def __init__(self, errno, errinfo=None):
    '''Each error has following parameters:
    errno: code of error; used to catch error type
      1: file does not exist in GLFileSystem: <file>
      2: cannot patch file inside GLFileSystem: <file>
      3: configure file does not exist: <configure.ac>
      4: minimum supported autoconf version is 2.59, not <version>
      5: <gnulib-comp.m4> is expected to contain gl_M4_BASE([<m4base>])
      6: missing sourcebase argument
      7: missing docbase argument
      8: missing testsbase argument
      9: missing libname argument
     10: conddeps are not supported with testflag['tests']
     11: incompatible licenses on modules: <modules>
    errinfo: additional information;
    style: 0 or 1, wheter old-style'''
    self.errno = errno; self.errinfo = errinfo
    self.args = (self.errno, self.errinfo)

  def __repr__(self):
    errinfo = self.errinfo
    errors = \
    [ # Begin list of errors
      "file does not exist in GLFileSystem: %s" % repr(errinfo),
      "cannot patch file inside GLFileSystem: %s" % repr(errinfo),
      "configure file does not exist: %s" % repr(errinfo),
      "minimum supported autoconf version is 2.59, not %s" % repr(errinfo),
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
      "conddeps are not supported with testflag['tests']",
      "incompatible licenses on modules: %s" % repr(errinfo),
    ] # Complete list of errors
    if not PYTHON3:
      self.message = (b'[Errno %d] %s' % \
        (self.errno, errors[self.errno -1].encode(ENCS['default'])))
    else: # if PYTHON3
      self.message = ('[Errno %d] %s' % \
        (self.errno, errors[self.errno -1]))
    return(self.message)


class GLError(object):
  '''GLError class is used to notify user about errors and warnings.'''
  
  def __init__(self, errno, errinfo, fatal=True, style=0):
    '''Create new GLError instance.
    errno: number of error to raise; see GLErrorHandler documentation.
    errinfo: additional information; see GLErrorHandler documentation.
    fatal: True or False; if True, then a fatal error will be raised.
    style: 0 or 1, 0 for old gnulib-tool style and 1 for Pythonic style.'''
    if type(errno) is not int:
      raise(TypeError(
        'errno must be an integer, not %s' % type(errno).__name__))
    if type(fatal) is not bool:
      raise(TypeError(
        'fatal must be a bool, not %s' % type(fatal).__name__))
    if type(style) is int:
      if style != 0 and style != 1:
        raise(ValueError(
          'style must be 0 or 1, not %s' % style))
    else: # if type(style) is not bool
      raise(TypeError(
        'style must be an integer, not %s' % type(style).__name__))
    
    # Define gnulib errors
    if style == 0:
      message = '%s: *** ' % constants.APP['name']
      if errinfo == None:
        errinfo = string()
      if errno == 1:
        message += 'file %s not found' % errinfo
        fatal = True # Error will be always fatal
      elif errno == 2:
        message += 'patch file %s didn\'t apply cleanly' % errinfo
        fatal = True # Error will be always fatal
      elif errno == 3:
        message += 'cannot find %s - make sure ' % errinfo
        message += 'you run gnulib-tool from within your package\'s directory'
        fatal = True # Error will be always fatal
      elif errno == 4:
        message += 'minimum supported autoconf version is 2.59. Try adding'
        message += 'AC_PREREQ([%s])' % constants.DEFAULT_AUTOCONF_MINVERSION
        message += ' to your configure.ac.'
        fatal = True # Error will be always fatal
      elif errno == 5:
        "%s is expected to contain gl_M4_BASE([%s])" % \
          (repr(os.path.join(errinfo, 'gnulib-comp.m4')), repr(errinfo))
        fatal = True # Error will be always fatal
      elif errno == 6:
        message += 'missing --source-base option'
        fatal = True # Error will be always fatal
      elif errno == 7:
        message += 'missing --doc-base option. --doc-base has been introduced '
        message += 'on 2006-07-11; if your last invocation of \'gnulib-tool '
        message += '--import\' is before that date, you need to run'
        message += '\'gnulib-tool --import\' once, with a --doc-base option.'
        fatal = True # Error will be always fatal
      elif errno == 8:
        message += 'missing --tests-base option'
        fatal = True # Error will be always fatal
      elif errno == 9:
        message += 'missing --lib option'
        fatal = True # Error will be always fatal
      elif errno == 10:
        message += 'gnulib-tool: option --conditional-dependencies is not '
        message += 'supported with --with-tests'
        fatal = True # Error will be always fatal
      elif errno == 11:
        incompatibilities = string()
        message += 'incompatible license on modules:%s' % constants.NL
        for pair in errinfo:
          incompatibilities += pair[0]
          incompatibilities += ' %s' % pair[0]
          incompatibilities += constants.NL
        tempname = tempfile.mktemp()
        with codecs.open(tempname, 'wb', 'UTF-8') as file:
          file.write(incompatibilities)
        sed_table = 's,^\\([^ ]*\\) ,\\1' +' ' *51 +',\n'
        sed_table += 's,^\\(' +'.'*49 +'[^ ]*\) *,' +' '*17 +'\\1 ,'
        args = ['sed', '-e', sed_table, tempname]
        incompatibilities = sp.check_output(args).decode(ENCS['default'])
        message += incompatibilities
        os.remove(tempname)
      message += '%s: *** Exit.' % constants.APP['name']
      sys.stderr.write(message)
      sys.exit(1)

