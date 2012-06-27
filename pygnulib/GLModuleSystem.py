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
from .GLFileSystem import GLFileSystem


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
# Define GLModuleSystem class
#===============================================================================
class GLModuleSystem(object):
  '''GLModuleSystem is used to operate with module names.'''
  
  def __init__(self, localdir, modcache):
    '''Create new GLModuleSystem instance. The necessary arguments are localdir
    and modcache, which are the same as usual. Some functions use GLFileSystem
    class to look up a file in localdir or gnulib directories, or combines it
    through 'patch' utility.'''
    self.args = dict()
    if type(localdir) is bytes or type(localdir) is string:
      if type(localdir) is bytes:
        localdir = localdir.decode(ENCS['default'])
      self.args['localdir'] = localdir
    else: # if localdir has not bytes or string type
      raise(TypeError(
        'argument must be a string, not %s' % type(module).__name__))
    if type(modcache) is bool:
      self.args['modcache'] = modcache
    else: # if type(modcache) is not bool
      raise(TypeError(
        'argument must be a bool, not %s' % type(module).__name__))
    
  def __repr__(self):
    '''x.__repr__ <==> repr(x)'''
    return('<pygnulib.GLModuleSystem>')
    
  def exists(self, module):
    '''GLModuleSystem.exists(module) -> bool
    
    Check whether the given module exists.'''
    if type(module) is bytes or string:
      if type(module) is bytes:
        module = module.decode(ENCS['default'])
    else: # if module has not bytes or string type
      raise(TypeError(
        'module must be a string, not %s' % type(module).__name__))
    result = bool()
    badnames = ['CVS', 'ChangeLog', 'COPYING', 'README', 'TEMPLATE',
      'TEMPLATE-EXTENDED', 'TEMPLATE-TESTS']
    if isfile(joinpath(DIRS['modules'], module)) or \
    all([ # Begin all(iterable) function
      self.args['localdir'],
      isdir(joinpath(self.args['localdir'], 'modules')),
      isfile(joinpath(self.args['localdir'], 'modules', module))
    ]): # Close all(iterable) function
      if module not in badnames:
        result = True
    return(result)
    
  def find(self, module):
    '''GLModuleSystem.find(module) -> GLModule
    
    Find the given module.'''
    if type(module) is bytes or string:
      if type(module) is bytes:
        module = module.decode(ENCS['default'])
    else: # if module has not bytes or string type
      raise(TypeError(
        'module must be a string, not %s' % type(module).__name__))
    if self.exists(module):
      filesystem = GLFileSystem(self.args['localdir'])
      result = filesystem.lookup(joinpath('modules', module))
      return(GLModule(result[0], result[1]))
    else: # if not self.exists(module)
      raise(GLError(3, module))
    
  def list(self):
    '''GLModuleSystem.list() -> list
   
    Return the available module names as tuple. We could use a combination
    of os.walk() function and re module. However, it takes too much time to
    complete, so this version uses subprocess to run shell commands.'''
    args1 = ['find', 'modules', '-type', 'f', '-print']
    args2 = \
    [
      'sed',
      '-e', r's,^modules/,,',
      '-e', r'/^CVS\//d',
      '-e', r'/\/CVS\//d',
      '-e', r'/^ChangeLog$/d',
      '-e', r'/\/ChangeLog$/d',
      '-e', r'/^COPYING$/d',
      '-e', r'/\/COPYING$/d',
      '-e', r'/^README$/d',
      '-e', r'/\/README$/d',
      '-e', r'/^TEMPLATE$/d',
      '-e', r'/^TEMPLATE-EXTENDED$/d',
      '-e', r'/^TEMPLATE-TESTS$/d',
      '-e', r'/^\..*/d',
      '-e', r'/~$/d',
      '-e', r'/-tests$/d',
    ]
    localdir = self.args['localdir']
    if localdir and isdir(joinpath(localdir, 'modules')):
      os.chdir(self.args['localdir'])
      args2.append('-e')
      args2.append(r's,\.diff$,,')
    proc1 = sp.Popen(args1, stdout=sp.PIPE)
    proc2 = sp.Popen(args2, stdin=proc1.stdout, stdout=sp.PIPE)
    proc1.stdout.close() # Close the first shell pipe
    result = string(proc2.stdout.read(), ENCS['shell'])
    if result[-2:] == '\r\n':
      result = result.replace('\r\n', '\n')
    if result[-1] == '\n':
      result = result[:-1]
    listing = result.splitlines(); listing.sort()
    listing = tuple(listing)
    os.chdir(DIRS['cwd'])
    return(listing)


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
        result = self.content.split('Description:')[1]
        if result.startswith('\t') or result.startswith(' '):
          result = result[1:]
        result = result.split(splitter)[0]
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
        result = self.content.split('Comment:')[1]
        if result.startswith('\t') or result.startswith(' '):
          result = result[1:]
        result = result.split(splitter)[0]
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
        result = self.content.split('Status:')[1]
        if result.startswith('\t') or result.startswith(' '):
          result = result[1:]
        result = result.split(splitter)[0]
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
        result = self.content.split('Notice:')[1]
        if result.startswith('\t') or result.startswith(' '):
          result = result[1:]
        result = result.split(splitter)[0]
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
        result = self.content.split('Applicability:')[1]
        if result.startswith('\t') or result.startswith(' '):
          result = result[1:]
        result = result.split(splitter)[0]
      self.cache['applicability'] = result
    return(self.cache['applicability'])
    
  def getFiles(self):
    '''GLModule.getFiles() -> list
    
    Return list of files.'''
    if 'files' not in self.cache:
      if 'Files:' not in self.content:
        result = list()
      else: # if 'Files:' in self.content
        splitters = \
        [ # Begin splitters list
          'Depends-on:', 'configure.ac-early:', 'configure.ac:','Makefile.am:',
          'Include:', 'Link:', 'License:', 'Maintainer:',
        ] # Finish splitters list
        splitter = self._find_splitter_(splitters)
        result = self.content.split('Files:')[1]
        if result.startswith('\t') or result.startswith(' '):
          result = result[1:]
        result = result.split(splitter)[0].strip().split()
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
        result = list()
      else: # if 'Depends-on:' in module.content
        splitters = \
        [ # Begin splitters list
          'configure.ac-early:', 'configure.ac:','Makefile.am:', 'Include:',
          'Link:', 'License:', 'Maintainer:',
        ] # Finish splitters list
        splitter = module._find_splitter_(splitters)
        result = module.content.split('Depends-on:')[1]
        if result.startswith('\t') or result.startswith(' '):
          result = result[1:]
        result = result.split(splitter)[0].strip().split()
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
        result = self.content.split('configure.ac-early:')[1]
        if result.startswith('\t') or result.startswith(' '):
          result = result[1:]
        result = result.split(splitter)[0]
      self.cache['autoconf_early'] = result
    return(self.cache['autoconf_early'])
    
  def getAutoconf(self):
    '''GLModule.getAutoconf() -> string
    
    Return autoconf snippet.'''
    if 'autoconf' not in self.cache:
      if 'configure.ac:' not in self.content:
        result = string()
      else: # if 'configure.ac:' in self.content
        splitters = \
        [ # Begin splitters list
          'Makefile.am:', 'Include:', 'Link:', 'License:', 'Maintainer:',
        ] # Finish splitters list
        splitter = self._find_splitter_(splitters)
        result = self.content.split('configure.ac:')[1]
        if result.startswith('\t') or result.startswith(' '):
          result = result[1:]
        result = result.split(splitter)[0]
      self.cache['autoconf'] = result
    return(self.cache['autoconf'])
    
  def getInclude(self):
    '''GLModule.getInclude() -> string
    
    Return include directive.'''
    if 'include' not in self.cache:
      if 'Include:' not in self.content:
        result = string()
      else: # if 'Include:' in self.content
        splitters = \
        [ # Begin splitters list
          'Link:', 'License:','Maintainer:',
        ] # Finish splitters list
        splitter = self._find_splitter_(splitters)
        result = self.content.split('Include:')[1]
        if result.startswith('\t') or result.startswith(' '):
          result = result[1:]
        result = result.split(splitter)[0]
      self.cache['include'] = result
    return(self.cache['include'])
    
  def getLink(self):
    '''GLModule.getLink() -> string
    
    Return link directive.'''
    if 'link' not in self.cache:
      if 'Link:' not in self.content:
        result = string()
      else: # if 'Link:' in self.content
        splitters = \
        [ # Begin splitters list
          'License:','Maintainer:',
        ] # Finish splitters list
        splitter = self._find_splitter_(splitters)
        result = self.content.split('Link:')[1]
        if result.startswith('\t') or result.startswith(' '):
          result = result[1:]
        result = result.split(splitter)[0]
      self.cache['link'] = result
    return(self.cache['link'])
    
  def getLicense(self):
    '''GLModule.getLicense() -> string
    
    Return module license.'''
    pass # TODO: see the latest commit
    
  def getMaintainer(self):
    '''GLModule.getMaintainer() -> string
    
    Return maintainer directive.'''
    if 'maintainer' not in self.cache:
      if 'Maintainer:' not in self.content:
        result = string()
      else: # if 'Maintainer:' in self.content
        result = self.content.split('Maintainer:')[1]
        if result.startswith('\t') or result.startswith(' '):
          result = result[1:]
        result = result.split('Maintainer:')[0]
      self.cache['maintainer'] = result
    return(self.cache['maintainer'])

