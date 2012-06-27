#!/usr/bin/python
# encoding: UTF-8

#===============================================================================
# Define global imports
#===============================================================================
import os
import re
import sys
import codecs
import subprocess as sp
from . import constants
from .GLError import GLError
from .GLModuleSystem import GLModuleSystem


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
# Define GLModule class
#===============================================================================
class GLModule(object):
  
  def __init__(self, module, patched):
    '''Create new GLModule instance. Arguments are module and patched, where
    module is a string representing the path to the module and patched is a
    bool indicating that module was created after applying patch.'''
    self.args = dict()
    self.cache = dict()
    self.content = string()
    if type(module) is bytes or type(module) is string:
      if type(module) is bytes:
        module = module.decode(ENCS['default'])
    else: # if module has not bytes or string type
      raise(TypeError(
        'module must be a string, not %s' % type(module).__name__))
    if type(patched) is not bool:
      raise(TypeError(
        'patched must be a bool, not %s' % type(module).__name__))
    self.args['module'] = module
    self.args['patched'] = patched
    with codecs.open(module, 'rb', 'UTF-8') as file:
      self.content = file.read()
    
  def __repr__(self):
    '''x.__repr__ <==> repr(x)'''
    return('<pygnulib.GLModule>')
    
  def _find_splitter_(self, splitters):
    '''Find splitter to split text.'''
    for splitter in splitters:
      if splitter in self.content:
        return(splitter)
        break
    
  def getName(self):
    '''GLModule.getName() -> string
    
    Return the name of the module.'''
    pattern = compiler(joinpath('modules', '(.*?)$'))
    result = pattern.findall(self.args['module'])[0]
    return(result)
    
  def isPatched(self):
    '''GLModule.isPatched() -> bool
    
    Check whether module was created after applying patch.'''
    return(self.args['patched'])
    
  def isTests(self):
    '''GLModule.isTests() -> bool
    
    Check whether module is a -tests version of module.'''
    name = self.getName()
    return(name.endswith('-tests'))
    
  def getDescription(self):
    '''GLModule.getDescription() -> string
    
    Return description of the module.'''
    if 'description' not in self.cache:
      if 'Description:' not in self.content:
        result = string()
      else: # if 'Description:' in self.content
        splitters = \
        [ # Begin splitters list
          'Comment:', 'Status:', 'Notice:', 'Applicability:', 'Files:',
          'Depends-on:', 'configure.ac-early:', 'configure.ac:',
          'Makefile.am:', 'Include:', 'Link:', 'License:', 'Maintainer:'
        ] # Finish splitters list
        splitter = self._find_splitter_(splitters)
        cutabove = self.content.split('Description:')[1]
        cutbelow = cutabove.split(splitter)[0]
        result = cutbelow.strip()
      self.cache['description'] = result
    return(self.cache['description'])
    
  def getComment(self):
    '''GLModule.getComment() -> string
    
    Return comment to module.'''
    if 'comment' not in self.cache:
      if 'Comment:' not in self.content:
        result = string()
      else: # if 'Comment:' in self.content
        splitters = \
        [ # Begin splitters list
          'Status:', 'Notice:', 'Applicability:', 'Files:', 'Depends-on:',
          'configure.ac-early:', 'configure.ac:','Makefile.am:', 'Include:',
          'Link:', 'License:', 'Maintainer:'
        ] # Finish splitters list
        splitter = self._find_splitter_(splitters)
        cutabove = self.content.split('Comment:')[1]
        cutbelow = cutabove.split(splitter)[0]
        result = cutbelow.strip()
      self.cache['comment'] = result
    return(self.cache['comment'])
    
  def getStatus(self):
    '''GLModule.getStatus() -> string
    
    Return module status.'''
    if 'status' not in self.cache:
      if 'Status:' not in self.content:
        result = string()
      else: # if 'Status:' in self.content
        splitters = \
        [ # Begin splitters list
          'Notice:', 'Applicability:', 'Files:', 'Depends-on:',
          'configure.ac-early:', 'configure.ac:','Makefile.am:', 'Include:',
          'Link:', 'License:', 'Maintainer:',
        ] # Finish splitters list
        splitter = self._find_splitter_(splitters)
        cutabove = self.content.split('Status:')[1]
        cutbelow = cutabove.split(splitter)[0]
        result = cutbelow.strip()
      self.cache['status'] = result
    return(self.cache['status'])
    
  def getNotice(self):
    '''GLModule.getNotice() -> string
    
    Return notice to module.'''
    if 'notice' not in self.cache:
      if 'Notice:' not in self.content:
        result = string()
      else: # if 'Notice:' in self.content
        splitters = \
        [ # Begin splitters list
          'Applicability:', 'Files:', 'Depends-on:', 'configure.ac-early:',
          'configure.ac:','Makefile.am:', 'Include:', 'Link:', 'License:',
          'Maintainer:',
        ] # Finish splitters list
        splitter = self._find_splitter_(splitters)
        cutabove = self.content.split('Notice:')[1]
        cutbelow = cutabove.split(splitter)[0]
        result = cutbelow.strip()
      self.cache['notice'] = result
    return(self.cache['notice'])
    
  def getApplicability(self):
    '''GLModule.getApplicability() -> string
    
    Return applicability of module.'''
    if 'applicability' not in self.cache:
      if 'Applicability:' not in self.content:
        result = string()
      else: # if 'Applicability:' in self.content
        splitters = \
        [ # Begin splitters list
          'Files:', 'Depends-on:', 'configure.ac-early:',
          'configure.ac:','Makefile.am:', 'Include:', 'Link:', 'License:',
          'Maintainer:',
        ] # Finish splitters list
        splitter = self._find_splitter_(splitters)
        cutabove = self.content.split('Applicability:')[1]
        cutbelow = cutabove.split(splitter)[0]
        result = cutbelow.strip()
      self.cache['applicability'] = result
    return(self.cache['applicability'])
    
  def getFiles(self):
    '''GLModule.getFiles() -> list
    
    Return list of files.'''
    if 'files' not in self.cache:
      if 'Files:' not in self.content:
        result = string()
      else: # if 'Files:' in self.content
        splitters = \
        [ # Begin splitters list
          'Depends-on:', 'configure.ac-early:', 'configure.ac:','Makefile.am:',
          'Include:', 'Link:', 'License:', 'Maintainer:',
        ] # Finish splitters list
        splitter = self._find_splitter_(splitters)
        cutabove = self.content.split('Files:')[1]
        cutbelow = cutabove.split(splitter)[0]
        result = cutbelow.strip().split('\n')
      self.cache['files'] = result
    return(self.cache['files'])
    
  def getDependencies(self):
    '''GLModule.getDependencies() -> list
    
    Return list of dependencies.'''
    module = self
    name = self.getName()
    if self.isTests():
      modulesystem = GLModuleSystem()
      if modulesystem.exists(name[:name.find('-tests')]):
        module = GLModuleSystem.find(name[:name.find('-tests')])
    if 'dependencies' not in module.cache:
      if 'Depends-on:' not in module.content:
        result = string()
      else: # if 'Depends-on:' in module.content
        splitters = \
        [ # Begin splitters list
          'configure.ac-early:', 'configure.ac:','Makefile.am:', 'Include:',
          'Link:', 'License:', 'Maintainer:',
        ] # Finish splitters list
        splitter = module._find_splitter_(splitters)
        cutabove = module.content.split('Depends-on:')[1]
        cutbelow = cutabove.split(splitter)[0]
        result = cutbelow.strip().split('\n')
      module.cache['dependencies'] = result
    return(module.cache['dependencies'])
    
  def getAutoconf_Early(self):
    '''GLModule.getAutoconf_Early() -> string
    
    Return autoconf-early snippet.'''
    if 'autoconf_early' not in self.cache:
      if 'configure.ac-early:' not in self.content:
        result = string()
      else: # if 'configure.ac-early:' in self.content
        splitters = \
        [ # Begin splitters list
          'configure.ac:','Makefile.am:', 'Include:', 'Link:', 'License:',
          'Maintainer:',
        ] # Finish splitters list
        splitter = self._find_splitter_(splitters)
        cutabove = self.content.split('configure.ac-early:')[1]
        cutbelow = cutabove.split(splitter)[0]
        result = cutbelow.strip()
      self.cache['autoconf_early'] = result
    return(self.cache['autoconf_early'])
    
  def getAutoconf(self):
    '''GLModule.getAutoconf() -> string
    
    Return autoconf snippet.'''
    if 'autoconf' not in self.cache:
      if 'configure.ac-early:' not in self.content:
        result = string()
      else: # if 'configure.ac-early:' in self.content
        splitters = \
        [ # Begin splitters list
          'configure.ac:','Makefile.am:', 'Include:', 'Link:', 'License:',
          'Maintainer:',
        ] # Finish splitters list
        splitter = self._find_splitter_(splitters)
        cutabove = self.content.split('configure.ac-early:')[1]
        cutbelow = cutabove.split(splitter)[0]
        result = cutbelow.strip()
      self.cache['autoconf'] = result
    return(self.cache['autoconf'])
    
  