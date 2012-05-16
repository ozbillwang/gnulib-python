#!/usr/bin/python
'''This script is a part of PyGNULib module for gnulib.'''

from __future__ import unicode_literals
#===============================================================================
# Define global imports
#===============================================================================
import os
import difflib
import subprocess as sp
from . import constants
from . import utilities


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
string = constants.string
APP = constants.APP
DIRS = constants.DIRS
ENCS = constants.ENCS
UTILS = constants.UTILS
FILES = constants.FILES
MODES = constants.MODES


#===============================================================================
# The main part of the module
#===============================================================================
gnulib_bash = os.path.join(DIRS['root'], 'gnulib-tool')
def testVersion():
  '''Test and compare output from gnulib-tool.sh and gnulib-tool.py with
  --version option enabled. Prints difference between outputs, else prints
  that test was completed successfully.'''
  print('#' *80)
  print('Begin testing of the --version output...')
  print('#' *80)
  result = string()
  info = utilities.GNULibInfo()
  message_py = \
    '%s (%s %s) %s\n%s\n%s\n\nWritten by %s.' % \
    (
      APP['name'], info.package(), info.date(), info.version(),
      info.copyright(), info.license(), info.authors()
    )
  message_py = message_py.replace('.py', '')
  message_sh = sp.check_output([gnulib_bash, '--version'])
  message_sh = string(message_sh, ENCS['shell'])
  # Edit endline symbols
  if message_sh[-2:] == '\r\n':
    message_sh = message_sh.replace('\r\n', '\n')
  message_sh = message_sh[:-1]
  # Separate into lines
  message_py = message_py.splitlines()
  message_sh = message_sh.splitlines()
  # Compare using difflib
  diff = difflib.unified_diff(message_sh, message_py)
  if message_sh != message_py:
    for line in list(diff):
      print(line)
  else: # message_sh == message_py:
    print('Test was completed successfully.\n')

def testHelp():
  '''Test and compare output from gnulib-tool.sh and gnulib-tool.py with
  --help option enabled. Prints difference between outputs, else prints
  that test was completed successfully.'''
  print('#' *80)
  print('Begin testing of the --help output...')
  print('#' *80)
  info = utilities.GNULibInfo()
  message_py = info.help()
  message_sh = sp.check_output([gnulib_bash, '--help'])
  message_sh = string(message_sh, ENCS['shell'])
  # Edit endline symbols
  if message_sh[-2:] == '\r\n':
    message_sh = message_sh.replace('\r\n', '\n')
  message_sh = message_sh[:-1]
  # Separate into lines
  message_py = message_py.splitlines()
  message_sh = message_sh.splitlines()
  # Compare using difflib
  diff = difflib.unified_diff(message_sh, message_py)
  if message_sh != message_py:
    for line in list(diff):
      print(line)
  else: # message_sh == message_py:
    print('Test was completed successfully.\n')

def testList():
  '''Test and compare output from gnulib-tool.sh and gnulib-tool.py with
  --list option enabled. Prints difference between outputs, else prints
  that test was completed successfully.'''
  print('#' *80)
  print('Begin testing of the --list output...')
  print('#' *80)
  data = utilities.GNULibImport()
  message_py = list(data.getAvailableModules())
  message_sh = sp.check_output([gnulib_bash, '--list'])
  message_sh = string(message_sh, ENCS['shell'])
  # Edit endline symbols
  if message_sh[-2:] == '\r\n':
    message_sh = message_sh.replace('\r\n', '\n')
  if message_sh[-1] == '\n':
    message_sh = message_sh[:-1]
  # Separate into lines
  message_sh = message_sh.splitlines()
  # Compare using difflib
  diff = difflib.unified_diff(message_py, message_sh)
  if message_sh != message_py:
    for line in list(diff):
      print(line)
  else: # message_sh == message_py:
    print('Test was completed successfully.\n')

