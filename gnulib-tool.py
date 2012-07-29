#!/usr/bin/python
#
# Copyright (C) 2002-2012 Free Software Foundation, Inc.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

# This program is meant for authors or maintainers which want to import
# modules from gnulib into their packages.


from __future__ import unicode_literals
#===============================================================================
# Define global imports
#===============================================================================
import os
import re
import sys
import codecs
import argparse
from pygnulib import constants
from pygnulib import classes
from pprint import pprint


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
# Define main part
#===============================================================================
def main():
  # Define default error handling
  #errmode = 1 # pygnulib-style errors
  
  # Define default arguments
  mode = 1
  m4base = None
  destdir = '.'
  localdir = None
  modcache = None
  verbose = None
  auxdir = None
  modules = list(['string'])
  avoids = list()
  sourcebase = None
  pobase = None
  docbase = None
  testsbase = None
  tests = None
  libname = None
  lgpl = None
  makefile = None
  libtool = None
  conddeps = None
  macro_prefix = None
  podomain = None
  witness_c_macro = None
  vc_files = None
  dryrun = True
  
  if mode == MODES['import']:
    if not sourcebase:
      sourcebase = 'lib'
    if not m4base:
      m4base = 'm4'
    if not docbase:
      docbase = 'doc'
    if not testsbase:
      testsbase = 'tests'
    if not macro_prefix:
      macro_prefix = 'gl'
    action = classes.GLImport\
    (
      mode, m4base,
      destdir=destdir,
      localdir=localdir,
      modcache=modcache,
      verbose=verbose,
      auxdir=auxdir,
      modules=modules,
      avoids=avoids,
      sourcebase=sourcebase,
      pobase=pobase,
      docbase=docbase,
      testsbase=testsbase,
      tests=tests,
      libname=libname,
      lgpl=lgpl,
      makefile=makefile,
      libtool=libtool,
      conddeps=conddeps,
      macro_prefix=macro_prefix,
      podomain=podomain,
      witness_c_macro=witness_c_macro,
      vc_files=vc_files,
    )
  
  else: # if mode != MODE['--import']
    if m4base:
      if not isfile(joinpath(destdir, m4base, 'gnulib-cache.m4')):
        if not sourcebase:
          sourcebase = 'lib'
        if not docbase:
          docbase = 'doc'
        if not testsbase:
          testsbase = 'tests'
        if not macro_prefix:
          macro_prefix = 'gl'
        action = classes.GLImport\
        (
          mode, m4base,
          destdir=destdir,
          localdir=localdir,
          modcache=modcache,
          verbose=verbose,
          auxdir=auxdir,
          modules=modules,
          avoids=avoids,
          sourcebase=sourcebase,
          pobase=pobase,
          docbase=docbase,
          testsbase=testsbase,
          tests=tests,
          libname=libname,
          lgpl=lgpl,
          makefile=makefile,
          libtool=libtool,
          conddeps=conddeps,
          macro_prefix=macro_prefix,
          podomain=podomain,
          witness_c_macro=witness_c_macro,
          vc_files=vc_files,
        )
    else: # if not m4base
      m4dirs = list()
      dirisnext = bool()
      filepath = joinpath(destdir, 'Makefile.am')
      if isfile(filepath):
        with codecs.open(filepath, 'rb', 'UTF-8') as file:
          data = file.read()
          data = data.split('ACLOCAL_AMFLAGS')[1]
          data = data[data.find('=')+1:data.find('\n')]
        aclocal_amflags = data.split()
        for aclocal_amflag in aclocal_amflags:
          if dirisnext:
            if not isabs(aclocal_amflag):
              m4dirs += [aclocal_amflag]
          else: # if not dirisnext
            if aclocal_amflag == '-I':
              dirisnext = True
            else: # if aclocal_amflag != '-I'
              dirisnext = False
      else: # if not isfile(filepath)
        filepath = joinpath(destdir, 'aclocal.m4')
        if isfile(filepath):
          pattern = constants.compiler(r'm4_include\(\[(.*?)\]\)')
          with codecs.open(filepath, 'rb', 'UTF-8') as file:
            m4dirs = pattern.findall(file.read())
          m4dirs = [os.path.dirname(m4dir) for m4dir in m4dirs]
          m4dirs = \
          [ # Begin filtering
            m4dir for m4dir in m4dirs \
            if isfile(joinpath(destdir, m4dir, 'gnulib-cache.m4'))
          ] # Finish filtering
          m4dirs = sorted(set(m4dirs))
      
      if len(m4dirs) == 0:
        # First use of gnulib in a package.
        # Any number of additional modules can be given.
        if not sourcebase:
          sourcebase = 'lib'
        m4base = 'm4'
        if not docbase:
          docbase = 'doc'
        if not testsbase:
          testsbase = 'tests'
        if not macro_prefix:
          macro_prefix = 'gl'
        action = classes.GLImport\
        (
          mode, m4base,
          destdir=destdir,
          localdir=localdir,
          modcache=modcache,
          verbose=verbose,
          auxdir=auxdir,
          modules=modules,
          avoids=avoids,
          sourcebase=sourcebase,
          pobase=pobase,
          docbase=docbase,
          testsbase=testsbase,
          tests=tests,
          libname=libname,
          lgpl=lgpl,
          makefile=makefile,
          libtool=libtool,
          conddeps=conddeps,
          macro_prefix=macro_prefix,
          podomain=podomain,
          witness_c_macro=witness_c_macro,
          vc_files=vc_files,
        )
      elif len(m4dirs) == 1:
        m4base = m4dirs[-1]
        action = classes.GLImport\
        (
          mode, m4base,
          destdir=destdir,
          localdir=localdir,
          modcache=modcache,
          verbose=verbose,
          auxdir=auxdir,
          modules=modules,
          avoids=avoids,
          sourcebase=sourcebase,
          pobase=pobase,
          docbase=docbase,
          testsbase=testsbase,
          tests=tests,
          libname=libname,
          lgpl=lgpl,
          makefile=makefile,
          libtool=libtool,
          conddeps=conddeps,
          macro_prefix=macro_prefix,
          podomain=podomain,
          witness_c_macro=witness_c_macro,
          vc_files=vc_files,
        )
      else: # if len(m4dirs) > 1
        for m4base in m4dirs:
          action = classes.GLImport\
          (
            mode, m4base,
            destdir=destdir,
            localdir=localdir,
            modcache=modcache,
            verbose=verbose,
            auxdir=auxdir,
            modules=modules,
            avoids=avoids,
            sourcebase=sourcebase,
            pobase=pobase,
            docbase=docbase,
            testsbase=testsbase,
            tests=tests,
            libname=libname,
            lgpl=lgpl,
            makefile=makefile,
            libtool=libtool,
            conddeps=conddeps,
            macro_prefix=macro_prefix,
            podomain=podomain,
            witness_c_macro=witness_c_macro,
            vc_files=vc_files,
          )
  
  # Execute operations depending on type of action
  if type(action) is classes.GLImport:
    files, old_files, new_files, transformers = action.prepare()
    action.execute(files, old_files, new_files, transformers, dryrun)

if __name__ == '__main__':
  try: # Try to execute
    main()
  except classes.GLError as error:
    errmode = 0 # gnulib-style errors
    errno = error.errno
    errinfo = error.errinfo
    if errmode == 0:
      message = '%s: *** ' % constants.APP['name']
      if errinfo == None:
        errinfo = string()
      if errno == 1:
        message += 'file %s not found' % errinfo
      elif errno == 2:
        message += 'patch file %s didn\'t apply cleanly' % errinfo
      elif errno == 3:
        message += 'cannot find %s - make sure ' % errinfo
        message += 'you run gnulib-tool from within your package\'s directory'
      elif errno == 4:
        message += 'minimum supported autoconf version is 2.59. Try adding'
        message += 'AC_PREREQ([%s])' % constants.DEFAULT_AUTOCONF_MINVERSION
        message += ' to your configure.ac.'
      elif errno == 5:
        "%s is expected to contain gl_M4_BASE([%s])" % \
          (repr(os.path.join(errinfo, 'gnulib-comp.m4')), repr(errinfo))
      elif errno == 6:
        message += 'missing --source-base option'
      elif errno == 7:
        message += 'missing --doc-base option. --doc-base has been introduced '
        message += 'on 2006-07-11; if your last invocation of \'gnulib-tool '
        message += '--import\' is before that date, you need to run'
        message += '\'gnulib-tool --import\' once, with a --doc-base option.'
      elif errno == 8:
        message += 'missing --tests-base option'
      elif errno == 9:
        message += 'missing --lib option'
      elif errno == 10:
        message += 'gnulib-tool: option --conditional-dependencies is not '
        message += 'supported with --with-tests'
      elif errno == 11:
        incompatibilities = string()
        message += 'incompatible license on modules:%s' % constants.NL
        for pair in errinfo:
          incompatibilities += pair[0]
          incompatibilities += ' %s' % pair[1]
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
      elif errno == 12:
        message += 'refusing to do nothing'
      elif errno in [13, 14, 15, 16, 17]:
        message += 'failed'
      message += '\n%s: *** Exit.\n' % constants.APP['name']
      sys.stderr.write(message)
      sys.exit(1)

