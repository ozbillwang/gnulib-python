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
filter_filelist = constants.filter_filelist


#===============================================================================
# Define GLModuleSystem class
#===============================================================================
class GLModuleSystem(object):
  '''GLModuleSystem is used to operate with module system using dynamic
  searching and patching.'''
  
  def __init__(self, localdir):
    '''Create new GLModuleSystem instance. The necessary arguments are localdir
    and modcache, which are the same as usual. Some functions use GLFileSystem
    class to look up a file in localdir or gnulib directories, or combines it
    through 'patch' utility.'''
    self.args = dict()
    self.cache = list()
    if type(localdir) is bytes or type(localdir) is string:
      if type(localdir) is bytes:
        localdir = localdir.decode(ENCS['default'])
      self.args['localdir'] = localdir
    else: # if localdir has not bytes or string type
      raise(TypeError(
        'argument must be a string, not %s' % type(module).__name__))
    
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
    cache = [module.getName() for module in self.cache]
    if module not in cache:
      if type(module) is bytes or string:
        if type(module) is bytes:
          module = module.decode(ENCS['default'])
      else: # if module has not bytes or string type
        raise(TypeError(
          'module must be a string, not %s' % type(module).__name__))
      if self.exists(module):
        filesystem = GLFileSystem(self.args['localdir'])
        path, istemp = filesystem.lookup(joinpath('modules', module))
        result = GLModule(path, istemp)
        self.cache += [result]
        return(result)
      else: # if self.exists(module)
        raise(GLError(3, module))
    else: # if module in cache
      index = cache.index(module)
      result = self.cache[index]
      return(result)
    
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
  
  def __init__(self, module, patched=False, isdep=False):
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
    self.regex ='(?:Description:|Comment:|Status:|Notice:|Applicability:|\
Files:|Depends-on:|configure\\.ac-early:|configure\\.ac:|Makefile\\.am:|\
Include:|Link:|License:|Maintainer:)'
    
  def __eq__(self, module):
    '''x.__eq__(y) <==> x==y'''
    if type(module) is not GLModule:
      raise(TypeError(
        'cannot compare GLModule with %s' % type(module).__name__))
    result = bool()
    if self.args['module'] == module.args['module']:
      result = True
    return(result)
    
  def __ne__(self, module):
    '''x.__ne__(y) <==> x!=y'''
    if type(module) is not GLModule:
      raise(TypeError(
        'cannot compare GLModule with %s' % type(module).__name__))
    result = bool()
    if self.args['module'] != module.args['module']:
      result = True
    return(result)
    
  def __ge__(self, module):
    '''x.__ge__(y) <==> x>=y'''
    if type(module) is not GLModule:
      raise(TypeError(
        'cannot compare GLModule with %s' % type(module).__name__))
    result = bool()
    if self.args['module'] >= module.args['module']:
      result = True
    return(result)
    
  def __gt__(self, module):
    '''x.__gt__(y) <==> x>y'''
    if type(module) is not GLModule:
      raise(TypeError(
        'cannot compare GLModule with %s' % type(module).__name__))
    result = bool()
    if self.args['module'] > module.args['module']:
      result = True
    return(result)
    
  def __hash__(self):
    '''x.__hash__() <==> hash(x)'''
    moduletype = hash('<pygnulib.GLModule>')
    modulename = hash(self.getName())
    result = moduletype ^modulename
    return(result)
    
  def __le__(self, module):
    '''x.__le__(y) <==> x<=y'''
    if type(module) is not GLModule:
      raise(TypeError(
        'cannot compare GLModule with %s' % type(module).__name__))
    result = bool()
    if self.args['module'] <= module.args['module']:
      result = True
    return(result)
    
  def __lt__(self, module):
    '''x.__lt__(y) <==> x<y'''
    if type(module) is not GLModule:
      raise(TypeError(
        'cannot compare GLModule with %s' % type(module).__name__))
    result = bool()
    if self.args['module'] < module.args['module']:
      result = True
    return(result)
    
  def __repr__(self):
    '''x.__repr__ <==> repr(x)'''
    return('<pygnulib.GLModule %s>' % repr(self.getName()))
    
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
    
  def getTestsName(self):
    '''Return -tests version of the module name.'''
    result = self.getName()
    if not result.endswith('-tests'):
      result += '-tests'
    return(result)
    
  def getDescription(self):
    '''GLModule.getDescription() -> string
    
    Return description of the module.'''
    section = 'Description:'
    if 'description' not in self.cache:
      if section not in self.content:
        result = string()
      else: # if section in self.content
        pattern = '^%s[\t ]*(.*?)%s' % (section, self.regex)
        pattern = compiler(pattern, re.DOTALL | re.MULTILINE)
        result = pattern.findall(self.content)
        if type(result) is list:
          if result == list():
            result = string()
          else: # if result != list()
            result = result[-1]
      self.cache['description'] = result
    return(self.cache['description'])
    
  def getComment(self):
    '''GLModule.getComment() -> string
    
    Return comment to module.'''
    section = 'Comment:'
    if 'comment' not in self.cache:
      if section not in self.content:
        result = string()
      else: # if section in self.content
        pattern = '^%s[\t ]*(.*?)%s' % (section, self.regex)
        pattern = compiler(pattern, re.DOTALL | re.MULTILINE)
        result = pattern.findall(self.content)
        if type(result) is list:
          if result == list():
            result = string()
          else: # if result != list()
            result = result[-1]
      self.cache['comment'] = result
    return(self.cache['comment'])
    
  def getStatus(self):
    '''GLModule.getStatus() -> string
    
    Return module status.'''
    section = 'Status:'
    if 'status' not in self.cache:
      if section not in self.content:
        result = string()
      else: # if section in self.content
        pattern = '^%s[\t ]*(.*?)%s' % (section, self.regex)
        pattern = compiler(pattern, re.DOTALL | re.MULTILINE)
        result = pattern.findall(self.content)
        if type(result) is list:
          if result == list():
            result = string()
          else: # if result != list()
            result = result[-1]
      self.cache['status'] = result.strip()
    return(self.cache['status'])
    
  def getNotice(self):
    '''GLModule.getNotice() -> string
    
    Return notice to module.'''
    section = 'Notice:'
    if 'notice' not in self.cache:
      if section not in self.content:
        result = string()
      else: # if section in self.content
        pattern = '^%s[\t ]*(.*?)%s' % (section, self.regex)
        pattern = compiler(pattern, re.DOTALL | re.MULTILINE)
        result = pattern.findall(self.content)
        if type(result) is list:
          if result == list():
            result = string()
          else: # if result != list()
            result = result[-1]
      self.cache['notice'] = result
    return(self.cache['notice'])
    
  def getApplicability(self):
    '''GLModule.getApplicability() -> string
    
    Return applicability of module.'''
    section = 'Applicability:'
    if 'applicability' not in self.cache:
      if section not in self.content:
        result = string()
      else: # if section in self.content
        pattern = '^%s[\t ]*(.*?)%s' % (section, self.regex)
        pattern = compiler(pattern, re.DOTALL | re.MULTILINE)
        result = pattern.findall(self.content)
        if type(result) is list:
          if result == list():
            result = string()
          else: # if result != list()
            result = result[-1]
      self.cache['applicability'] = result
    return(self.cache['applicability'])
    
  def getFiles(self, autoconf_version=2.59):
    '''GLModule.getFiles() -> list
    
    Return list of files.'''
    section = 'Files:'
    if type(autoconf_version) is not float:
      raise(TypeError('autoconf_version must be a float, not %s' % \
        type(autoconf_version).__name__))
    if 'files' not in self.cache:
      if section not in self.content:
        result = string()
      else: # if section in self.content
        pattern = '^%s[\t ]*(.*?)%s' % (section, self.regex)
        pattern = compiler(pattern, re.DOTALL | re.MULTILINE)
        result = pattern.findall(self.content)
        if type(result) is list:
          if result != list():
            result = result[-1].strip().split('\n')
      self.cache['files'] = result
      self.cache['files'] += [joinpath('m4', '00gnulib.m4')]
      self.cache['files'] += [joinpath('m4', 'gnulib-common.m4')]
      if autoconf_version == 2.59:
        self.cache['files'] += [joinpath('m4', 'onceonly.m4')]
    return(list(self.cache['files']))
    
  def getDependencies(self):
    '''GLModule.getDependencies() -> list
    
    Return list of dependencies.'''
    module = self
    name = self.getName()
    section = 'Depends-on:'
    if self.isTests():
      modulesystem = GLModuleSystem()
      if modulesystem.exists(name[:name.find('-tests')]):
        module = GLModuleSystem.find(name[:name.find('-tests')])
    if 'dependencies' not in module.cache:
      if section not in module.content:
        result = string()
      else: # if section in module.content
        pattern = '^%s[\t ]*(.*?)%s' % (section, module.regex)
        pattern = compiler(pattern, re.DOTALL | re.MULTILINE)
        result = pattern.findall(module.content)
        if type(result) is list:
          if result != list():
            result = result[-1].strip().split('\n')
      if result == ['']: result = list()
      result = [dep for dep in result if not dep.startswith('#')]
      module.cache['dependencies'] = result
    return(list(module.cache['dependencies']))
    
  def getAutoconf_EarlySnippet(self):
    '''GLModule.getAutoconf_EarlySnippet() -> string
    
    Return autoconf-early snippet.'''
    section = 'configure.ac-early:'
    if 'autoconf-early' not in self.cache:
      if section not in self.content:
        result = string()
      else: # if section in self.content
        pattern = '^%s[\t ]*(.*?)%s' % (section, self.regex)
        pattern = compiler(pattern, re.DOTALL | re.MULTILINE)
        result = pattern.findall(self.content)
        if type(result) is list:
          if result == list():
            result = string()
          else: # if result != list()
            result = result[-1]
      self.cache['autoconf-early'] = result
    return(self.cache['autoconf-early'])
    
  def getAutoconfSnippet(self):
    '''GLModule.getAutoconfSnippet() -> string
    
    Return autoconf snippet.'''
    section = 'configure.ac:'
    if 'autoconf' not in self.cache:
      if section not in self.content:
        result = string()
      else: # if section in self.content
        pattern = '^%s[\t ]*(.*?)%s' % (section, self.regex)
        pattern = compiler(pattern, re.DOTALL | re.MULTILINE)
        result = pattern.findall(self.content)
        if type(result) is list:
          if result == list():
            result = string()
          else: # if result != list()
            result = result[-1]
      self.cache['autoconf'] = result
    return(self.cache['autoconf'])
    
  def getAutomakeSnippet(self, conditional, autoconf_version=2.59):
    '''GLModule.getAutomakeSnippet(conditional) -> string
    
    Return automake snippet.'''
    section = 'Makefile.am:'
    if type(conditional) is not bool:
      raise(TypeError(
        'conditional must be bool, not %s' % type(conditional).__name__))
    if conditional:
      if 'makefile' not in self.cache:
        if section not in self.content:
          result = string()
        else: # if section in self.content
          pattern = '^%s[\t ]*(.*?)%s' % (section, self.regex)
          pattern = compiler(pattern, re.DOTALL | re.MULTILINE)
          result = pattern.findall(self.content)
          if type(result) is list:
            if result == list():
              result = string()
            else: # if result != list()
              result = result[-1]
        self.cache['makefile'] = result
      return(self.cache['makefile'])
    else: # if not conditional
      if self.isTests():
        all_files = self.getFiles(autoconf_version)
        extra_files = filter_filelist(all_files, 'tests/', '', 'tests/', '')
        
  def getInclude(self):
    '''GLModule.getInclude() -> string
    
    Return include directive.'''
    section = 'Include:'
    if 'include' not in self.cache:
      if section not in self.content:
        result = string()
      else: # if section in self.content
        pattern = '^%s[\t ]*(.*?)%s' % (section, self.regex)
        pattern = compiler(pattern, re.DOTALL | re.MULTILINE)
        result = pattern.findall(self.content)
        if type(result) is list:
          if result == list():
            result = string()
          else: # if result != list()
            result = result[-1]
      self.cache['include'] = result
    return(self.cache['include'])
    
  def getLink(self):
    '''GLModule.getLink() -> string
    
    Return link directive.'''
    section = 'Link:'
    if 'link' not in self.cache:
      if section not in self.content:
        result = string()
      else: # if section in self.content
        pattern = '^%s[\t ]*(.*?)%s' % (section, self.regex)
        pattern = compiler(pattern, re.DOTALL | re.MULTILINE)
        result = pattern.findall(self.content)
        if type(result) is list:
          if result == list():
            result = string()
          else: # if result != list()
            result = result[-1]
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

