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
import filecmp
import tempfile
from io import BytesIO
import subprocess as sp
from . import constants
from .GLInfo import GLInfo
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
# Define GLEmiter class
#===============================================================================
class GLEmiter(object):
  '''This class is used to emit the contents of necessary files.'''
  
  def __init__(self, destdir, localdir):
    '''Create GLEmiter instance.'''
    if type(destdir) is bytes or type(destdir) is string:
      if type(destdir) is bytes:
        destdir = destdir.decode(ENCS['default'])
      self.destdir = destdir
    else: # if destdir has not bytes or string type
      raise(TypeError(
        'destdir must be a string, not %s' % type(destdir).__name__))
    if type(localdir) is bytes or type(localdir) is string:
      if type(localdir) is bytes:
        localdir = localdir.decode(ENCS['default'])
      self.localdir = localdir
    else: # if localdir has not bytes or string type
      raise(TypeError(
        'localdir must be a string, not %s' % type(localdir).__name__))
    self.info = GLInfo()
    
  def copyrightNotice(self):
    '''Emit a header for a generated file.'''
    emit = "# %s" % self.info.copyright()
    emit += """
#
# This file is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This file is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this file.  If not, see <http://www.gnu.org/licenses/>.
#
# As a special exception to the GNU General Public License,
# this file may be distributed as part of a program that
# contains a configuration script generated by Autoconf, under
# the same distribution terms as the rest of that program.
#
# Generated by gnulib-tool.\n"""
    if type(emit) is bytes:
      emit = emit.decode(ENCS['default'])
    return(emit)
    
  def po_Makevars(self, pobase, podomain):
    '''Emit the contents of po/ makefile parameterization.'''
    if type(pobase) is bytes or type(pobase) is string:
      if type(pobase) is bytes:
        pobase = pobase.decode(ENCS['default'])
      self.pobase = pobase
    else: # if pobase has not bytes or string type
      raise(TypeError(
        'pobase must be a string, not %s' % type(pobase).__name__))
    if type(podomain) is bytes or type(podomain) is string:
      if type(podomain) is bytes:
        podomain = podomain.decode(ENCS['default'])
      self.podomain = podomain
    else: # if podomain has not bytes or string type
      raise(TypeError(
        'podomain must be a string, not %s' % type(podomain).__name__))
    subdir = string()
    if os.path.sep in pobase:
      dirs = len(pobase.split(os.path.sep))
      for directory in range(dirs +1):
        subdir += '../'
    subdir = os.path.normpath(subdir)
    emit = "## DO NOT EDIT! GENERATED AUTOMATICALLY!\n"
    emit += "%s\n" % self.copyrightNotice()
    emit += "# Usually the message domain is the same as the package name.\n"
    emit += "# But here it has a '-gnulib' suffix.\n"
    emit += "DOMAIN = %s-gnulib\n\n" % podomain
    emit += "# These two variables depend on the location of this directory.\n"
    emit += "subdir = %s\n" % pobase
    emit += "top_subdir = %s\n" % subdir
    emit += """
# These options get passed to xgettext.
XGETTEXT_OPTIONS = \\
  --keyword=_ --flag=_:1:pass-c-format \\
  --keyword=N_ --flag=N_:1:pass-c-format \\
  --keyword='proper_name:1,"This is a proper name. See the gettext manual, \
section Names."' \\
  --keyword='proper_name_utf8:1,"This is a proper name. See the gettext \
manual, section Names."' \\
  --flag=error:3:c-format --flag=error_at_line:5:c-format

# This is the copyright holder that gets inserted into the header of the
# $(DOMAIN).pot file.  gnulib is copyrighted by the FSF.
COPYRIGHT_HOLDER = Free Software Foundation, Inc.

# This is the email address or URL to which the translators shall report
# bugs in the untranslated strings:
# - Strings which are not entire sentences, see the maintainer guidelines
#   in the GNU gettext documentation, section 'Preparing Strings'.
# - Strings which use unclear terms or require additional context to be
#   understood.
# - Strings which make invalid assumptions about notation of date, time or
#   money.
# - Pluralisation problems.
# - Incorrect English spelling.
# - Incorrect formatting.
# It can be your email address, or a mailing list address where translators
# can write to without being subscribed, or the URL of a web page through
# which the translators can contact you.
MSGID_BUGS_ADDRESS = bug-gnulib@gnu.org

# This is the list of locale categories, beyond LC_MESSAGES, for which the
# message catalogs shall be used.  It is usually empty.
EXTRA_LOCALE_CATEGORIES =

# This tells whether the $(DOMAIN).pot file contains messages with an 'msgctxt'
# context.  Possible values are "yes" and "no".  Set this to yes if the
# package uses functions taking also a message context, like pgettext(), or
# if in $(XGETTEXT_OPTIONS) you define keywords with a context argument.
USE_MSGCTXT = no\n"""
    if type(emit) is bytes:
      emit = emit.decode(ENCS['default'])
    return(emit)