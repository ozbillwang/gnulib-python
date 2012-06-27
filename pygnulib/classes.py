#!/usr/bin/python
# encoding: UTF-8

from __future__ import unicode_literals
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
from .GLError import GLError
from .GLMode import GLMode
from .GLFileSystem import GLFileSystem
from .GLModuleSystem import GLModule
from .GLModuleSystem import GLModuleSystem
from .GLModule import GLModule
from .GLImport import GLImport


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


__all__ = ['GLError', 'GLMode', 'GLModule', 'GLImport']
