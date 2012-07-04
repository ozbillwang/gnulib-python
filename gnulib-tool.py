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
if __name__ == '__main__':
  
  mode = 1
  m4base = None
  destdir = '.'
  localdir = None
  modcache = None
  verbose = None
  auxdir = None
  modules = list(['canon-host'])
  avoids = list()
  sourcebase = None
  pobase = None
  docbase = None
  testsbase = None
  tests = [0, 1]
  libname = None
  lgpl = None
  makefile = None
  libtool = None
  dependencies = None
  macro_prefix = None
  podomain = None
  witness_c_macro = None
  vc_files = None
  dryrun = False
  
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
    GLImport = classes.GLImport\
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
      dependencies=dependencies,
      macro_prefix=macro_prefix,
      podomain=podomain,
      witness_c_macro=witness_c_macro,
      vc_files=vc_files,
    ).execute(dryrun)
  
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
        GLImport = classes.GLImport\
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
          dependencies=dependencies,
          macro_prefix=macro_prefix,
          podomain=podomain,
          witness_c_macro=witness_c_macro,
          vc_files=vc_files,
        ).execute(dryrun)
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
        GLImport = classes.GLImport\
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
          dependencies=dependencies,
          macro_prefix=macro_prefix,
          podomain=podomain,
          witness_c_macro=witness_c_macro,
          vc_files=vc_files,
        ).execute(dryrun)
      elif len(m4dirs) == 1:
        m4base = m4dirs[-1]
        GLImport = classes.GLImport\
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
          dependencies=dependencies,
          macro_prefix=macro_prefix,
          podomain=podomain,
          witness_c_macro=witness_c_macro,
          vc_files=vc_files,
        ).execute(dryrun)
      else: # if len(m4dirs) > 1
        for m4base in m4dirs:
          GLImport = classes.GLImport\
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
            dependencies=dependencies,
            macro_prefix=macro_prefix,
            podomain=podomain,
            witness_c_macro=witness_c_macro,
            vc_files=vc_files,
          ).execute(dryrun)
      