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
  
  def __init__(self, destdir, localdir, auxdir,
    sourcebase='lib', m4base='m4', testsbase='tests', pobase='po'):
    '''Create GLEmiter instance.'''
    self.info = GLInfo()
    
    # Set destdir variable.
    if type(destdir) is bytes or type(destdir) is string:
      if type(destdir) is bytes:
        destdir = destdir.decode(ENCS['default'])
      self.destdir = destdir
    else: # if destdir has not bytes or string type
      raise(TypeError(
        'destdir must be a string, not %s' % type(destdir).__name__))
    if destdir == '':
      raise(TypeError('destdir must be set to non-zero string'))
    
    # Set localdir variable.
    if type(localdir) is bytes or type(localdir) is string:
      if type(localdir) is bytes:
        localdir = localdir.decode(ENCS['default'])
      self.localdir = localdir
    else: # if localdir has not bytes or string type
      raise(TypeError(
        'localdir must be a string, not %s' % type(localdir).__name__))
    if localdir == '':
      raise(TypeError('localdir must be set to non-zero string'))
    
    # Set destdir variable.
    if type(destdir) is bytes or type(destdir) is string:
      if type(destdir) is bytes:
        destdir = destdir.decode(ENCS['default'])
      self.destdir = destdir
    else: # if destdir has not bytes or string type
      raise(TypeError(
        'destdir must be a string, not %s' % type(destdir).__name__))
    if destdir == '':
      raise(TypeError('destdir must be set to non-zero string'))
    
    # Set sourcebase variable.
    if type(sourcebase) is bytes or type(sourcebase) is string:
      if type(sourcebase) is bytes:
        sourcebase = sourcebase.decode(ENCS['default'])
      self.sourcebase = sourcebase
    else: # if sourcebase has not bytes or string type
      raise(TypeError(
        'sourcebase must be a string, not %s' % type(sourcebase).__name__))
    if sourcebase == '':
      raise(TypeError('sourcebase must be set to non-zero string'))
    
    # Set m4base variable.
    if type(m4base) is bytes or type(m4base) is string:
      if type(m4base) is bytes:
        m4base = m4base.decode(ENCS['default'])
      self.m4base = m4base
    else: # if m4base has not bytes or string type
      raise(TypeError(
        'm4base must be a string, not %s' % type(m4base).__name__))
    if m4base == '':
      raise(TypeError('m4base must be set to non-zero string'))
    
    # Set testsbase variable.
    if type(testsbase) is bytes or type(testsbase) is string:
      if type(testsbase) is bytes:
        testsbase = testsbase.decode(ENCS['default'])
      self.testsbase = testsbase
    else: # if testsbase has not bytes or string type
      raise(TypeError(
        'testsbase must be a string, not %s' % type(testsbase).__name__))
    if testsbase == '':
      raise(TypeError('testsbase must be set to non-zero string'))
    
    # Set pobase variable.
    if type(pobase) is bytes or type(pobase) is string:
      if type(pobase) is bytes:
        pobase = pobase.decode(ENCS['default'])
      self.pobase = pobase
    else: # if pobase has not bytes or string type
      raise(TypeError(
        'pobase must be a string, not %s' % type(pobase).__name__))
    if pobase == '':
      raise(TypeError('pobase must be set to non-zero string'))
    
    # Normalize variables.
    self.destdir = os.path.normpath(destdir)
    self.localdir = os.path.normpath(localdir)
    self.auxdir = os.path.normpath(auxdir)
    self.sourcebase = os.path.normpath(sourcebase)
    self.m4base = os.path.normpath(m4base)
    self.testsbase = os.path.normpath(testsbase)
    self.pobase = os.path.normpath(pobase)
    
  def copyright_notice(self):
    '''Emit a header for a generated file.'''
    emit = string()
    emit += "# %s" % self.info.copyright()
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
    
  def po_Makevars(self, podomain):
    '''Emit the contents of po/ makefile parameterization.'''
    emit = string()
    pobase = '%s%s' % (os.path.normpath(self.pobase), os.path.sep)
    if type(pobase) is bytes:
      pobase = pobase.decode(ENCS['default'])
    if type(podomain) is bytes or type(podomain) is string:
      if type(podomain) is bytes:
        podomain = podomain.decode(ENCS['default'])
    else: # if podomain has not bytes or string type
      raise(TypeError(
        'podomain must be a string, not %s' % type(podomain).__name__))
    if podomain == '':
      raise(TypeError('podomain must be set to non-zero string'))
    top_subdir = string()
    if os.path.sep in pobase:
      dirs = len(pobase.split(os.path.sep))
      for directory in range(dirs +1):
        top_subdir += '../'
    top_subdir = os.path.normpath(top_subdir)
    emit += "## DO NOT EDIT! GENERATED AUTOMATICALLY!\n"
    emit += "%s\n" % self.copyright_notice()
    emit += "# Usually the message domain is the same as the package name.\n"
    emit += "# But here it has a '-gnulib' suffix.\n"
    emit += "DOMAIN = %s-gnulib\n\n" % podomain
    emit += "# These two variables depend on the location of this directory.\n"
    emit += "subdir = %s\n" % pobase
    emit += "top_subdir = %s\n" % top_subdir
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
    
  def po_POTFILES_in(self, files):
    '''Emit the file list to be passed to xgettext.'''
    emit = string()
    sourcebase = '%s%s' % (self.sourcebase, os.path.sep)
    if type(sourcebase) is bytes:
      sourcebase = sourcebase.decode(ENCS['default'])
    files = [substart('lib/', sourcebase, file) for file in files]
    files = [file for file in files if file.startswith(sourcebase)]
    emit += "## DO NOT EDIT! GENERATED AUTOMATICALLY!\n"
    emit += "%s\n" % self.copyright_notice()
    emit += "# List of files which contain translatable strings.\n"
    emit += '\n'.join(files)
    emit += '\n'
    if type(emit) is bytes:
      emit = emit.decode(ENCS['default'])
    return(emit)
    
  def initmacro_start(self, macro_prefix='gl'):
    '''Emit the first few statements of the gl_INIT macro.'''
    emit = string()
    if type(macro_prefix) is bytes or type(macro_prefix) is string:
      if type(macro_prefix) is bytes:
        macro_prefix = macro_prefix.decode(ENCS['default'])
    else: # if macro_prefix has not bytes or string type
      raise(TypeError(
        'macro_prefix must be a string, not %s' % type(macro_prefix).__name__))
    if macro_prefix == '':
      raise(TypeError('macro_prefix must be set to non-zero string'))
    # Overriding AC_LIBOBJ and AC_REPLACE_FUNCS has the effect of storing
    # platform-dependent object files in ${macro_prefix_arg}_LIBOBJS instead
    # of LIBOBJS. The purpose is to allow several gnulib instantiations under
    # a single configure.ac file. (AC_CONFIG_LIBOBJ_DIR does not allow this
    # flexibility).
    # Furthermore it avoids an automake error like this when a Makefile.am
    # that uses pieces of gnulib also uses $(LIBOBJ):
    #   automatically discovered file `error.c' should not be explicitly
    #   mentioned.
    emit += "  m4_pushdef([AC_LIBOBJ],"
    emit += " m4_defn([%V1%_LIBOBJ]))\n"
    emit += "  m4_pushdef([AC_REPLACE_FUNCS],"
    emit += " m4_defn([%V1%_REPLACE_FUNCS]))\n"
    # Overriding AC_LIBSOURCES has the same purpose of avoiding the automake
    # error when a Makefile.am that uses pieces of gnulib also uses $(LIBOBJ):
    #   automatically discovered file `error.c' should not be explicitly
    #   mentioned
    # We let automake know about the files to be distributed through the
    # EXTRA_lib_SOURCES variable.
    emit += "  m4_pushdef([AC_LIBSOURCES],"
    emit += " m4_defn([%V1%_LIBSOURCES]))\n"
    # Create data variables for checking the presence of files that are
    # mentioned as AC_LIBSOURCES arguments. These are m4 variables, not shell
    # variables, because we want the check to happen when the configure file is
    # created, not when it is run. ${macro_prefix_arg}_LIBSOURCES_LIST is the
    # list of files to check for. ${macro_prefix_arg}_LIBSOURCES_DIR is the
    # subdirectory in which to expect them.
    emit += "  m4_pushdef([%V1%_LIBSOURCES_LIST], [])\n"
    emit += "  m4_pushdef([%V1%_LIBSOURCES_DIR], [])\n"
    emit += "  gl_COMMON\n"
    emit = emit.replace('%V1%', macro_prefix)
    if type(emit) is bytes:
      emit = emit.decode(ENCS['default'])
    return(emit)
    
  def initmacro_end(self, macro_prefix='gl'):
    '''Emit the last few statements of the gl_INIT macro.'''
    emit = string()
    if type(macro_prefix) is bytes or type(macro_prefix) is string:
      if type(macro_prefix) is bytes:
        macro_prefix = macro_prefix.decode(ENCS['default'])
    else: # if macro_prefix has not bytes or string type
      raise(TypeError(
        'macro_prefix must be a string, not %s' % type(macro_prefix).__name__))
    if macro_prefix == '':
      raise(TypeError('macro_prefix must be set to non-zero string'))
    # Check the presence of files that are mentioned as AC_LIBSOURCES
    # arguments. The check is performed only when autoconf is run from the
    # directory where the configure.ac resides; if it is run from a different
    # directory, the check is skipped.
    emit += """\
  m4_ifval(%V1%_LIBSOURCES_LIST, [
    m4_syscmd([test ! -d ]m4_defn([%V1%_LIBSOURCES_DIR])[ ||
      for gl_file in ]%V1%_LIBSOURCES_LIST[ ; do
        if test ! -r ]m4_defn([%V1%_LIBSOURCES_DIR])[/$gl_file ; then
          echo "missing file ]m4_defn([%V1%_LIBSOURCES_DIR])[/$gl_file" >&2
          exit 1
        fi
      done])dnl
      m4_if(m4_sysval, [0], [],
        [AC_FATAL([expected source file, required through AC_LIBSOURCES, not \
found])])
  ])
  m4_popdef([%V1%_LIBSOURCES_DIR])
  m4_popdef([%V1%_LIBSOURCES_LIST])
  m4_popdef([AC_LIBSOURCES])
  m4_popdef([AC_REPLACE_FUNCS])
  m4_popdef([AC_LIBOBJ])
  AC_CONFIG_COMMANDS_PRE([
    %V1%_libobjs=
    %V1%_ltlibobjs=
    if test -n "$%V1%_LIBOBJS"; then
      # Remove the extension.
      sed_drop_objext='s/\.o$//;s/\.obj$//'
      for i in `for i in $%V1%_LIBOBJS; do echo "$i"; done | sed -e \
"$sed_drop_objext" | sort | uniq`; do
        %V1%_libobjs="$%V1%_libobjs $i.$ac_objext"
        %V1%_ltlibobjs="$%V1%_ltlibobjs $i.lo"
      done
    fi
    AC_SUBST([%V1%_LIBOBJS], [$%V1%_libobjs])
    AC_SUBST([%V1%_LTLIBOBJS], [$%V1%_ltlibobjs])
  ])\n"""
    emit = emit.replace('%V1%', macro_prefix)
    if type(emit) is bytes:
      emit = emit.decode(ENCS['default'])
    return(emit)
    
  def initmacro_done(self, macro_prefix):
    '''Emit a few statements after the gl_INIT macro.'''
    emit = string()
    emit += """\

# Like AC_LIBOBJ, except that the module name goes
# into %V1%_LIBOBJS instead of into LIBOBJS.
AC_DEFUN([%V1%_LIBOBJ], [
  AS_LITERAL_IF([$1], [%V1%_LIBSOURCES([$1.c])])dnl
  %V1%_LIBOBJS="$%V1%_LIBOBJS $1.$ac_objext"
])

# Like AC_REPLACE_FUNCS, except that the module name goes
# into %V1%_LIBOBJS instead of into LIBOBJS.
AC_DEFUN([%V1%_REPLACE_FUNCS], [
  m4_foreach_w([gl_NAME], [$1], [AC_LIBSOURCES(gl_NAME[.c])])dnl
  AC_CHECK_FUNCS([$1], , [%V1%_LIBOBJ($ac_func)])
])

# Like AC_LIBSOURCES, except the directory where the source file is
# expected is derived from the gnulib-tool parameterization,
# and alloca is special cased (for the alloca-opt module).
# We could also entirely rely on EXTRA_lib..._SOURCES.
AC_DEFUN([%V1%_LIBSOURCES], [
  m4_foreach([_gl_NAME], [$1], [
    m4_if(_gl_NAME, [alloca.c], [], [
      m4_define([%V1%_LIBSOURCES_DIR], [%V2%])
      m4_append([%V1%_LIBSOURCES_LIST], _gl_NAME, [ ])
    ])
  ])
])\n"""
    emit = emit.replace('%V1%', macro_prefix)
    emit = emit.replace('%V2%', self.sourcebase)
    if type(emit) is bytes:
      emit = emit.decode(ENCS['default'])
    return(emit)