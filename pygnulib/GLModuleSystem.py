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
from pprint import pprint


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
    class to look up a file in localdir or gnulib directories, or combine it
    through 'patch' utility.'''
    self.args = dict()
    if type(localdir) is bytes or type(localdir) is string:
      if type(localdir) is bytes:
        localdir = localdir.decode(ENCS['default'])
      self.localdir = localdir
    else: # if localdir has not bytes or string type
      raise(TypeError(
        'localdir must be a string, not' +type(module).__name__))
    
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
      self.localdir,
      isdir(joinpath(self.localdir, 'modules')),
      isfile(joinpath(self.localdir, 'modules', module))
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
      filesystem = GLFileSystem(self.localdir)
      path, istemp = filesystem.lookup(joinpath('modules', module))
      result = GLModule(path, istemp)
      return(result)
    else: # if self.exists(module)
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
    localdir = self.localdir
    if localdir and isdir(joinpath(localdir, 'modules')):
      os.chdir(self.localdir)
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
  '''GLModule is used to create a module object from the file with the given
  path. GLModule can get all information about module, get its dependencies,
  files, etc.'''
  
  def __init__(self, module, patched=False):
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
    self.module = module
    self.patched = patched
    with codecs.open(module, 'rb', 'UTF-8') as file:
      self.content = file.read()
    self.regex ='(?:Description:|Comment:|Status:|Notice:|Applicability:|\
Files:|Depends-on:|configure\\.ac-early:|configure\\.ac:|Makefile\\.am:|\
Include:|Link:|License:|Maintainer:)'
    
  def __eq__(self, module):
    '''x.__eq__(y) <==> x==y'''
    result = bool()
    if type(module) is GLModule:
      if self.module == module.module:
        result = True
    return(result)
    
  def __ne__(self, module):
    '''x.__ne__(y) <==> x!=y'''
    result = bool()
    if type(module) is GLModule:
      if self.module != module.module:
        result = True
    return(result)
    
  def __ge__(self, module):
    '''x.__ge__(y) <==> x>=y'''
    result = bool()
    if type(module) is GLModule:
      if self.module >= module.module:
        result = True
    return(result)
    
  def __gt__(self, module):
    '''x.__gt__(y) <==> x>y'''
    result = bool()
    if type(module) is GLModule:
      if self.module > module.module:
        result = True
    return(result)
    
  def __hash__(self):
    '''x.__hash__() <==> hash(x)'''
    module = hash(self.module)
    patched = hash(self.patched)
    result = module^patched
    return(result)
    
  def __le__(self, module):
    '''x.__le__(y) <==> x<=y'''
    result = bool()
    if type(module) is GLModule:
      if self.module <= module.module:
        result = True
    return(result)
    
  def __lt__(self, module):
    '''x.__lt__(y) <==> x<y'''
    result = bool()
    if type(module) is GLModule:
      if self.module < module.module:
        result = True
    return(result)
    
  def __str__(self):
    '''x.__str__() <==> str(x)'''
    result = self.getName()
    return(result)
    
  def __repr__(self):
    '''x.__repr__ <==> repr(x)'''
    return('<pygnulib.GLModule %s>' % repr(self.getName()))
    
  def getName(self):
    '''GLModule.getName() -> string
    
    Return the name of the module.'''
    pattern = compiler(joinpath('modules', '(.*?)$'))
    result = pattern.findall(self.module)[0]
    return(result)
    
  def isPatched(self):
    '''GLModule.isPatched() -> bool
    
    Check whether module was created after applying patch.'''
    return(self.patched)
    
  def isTests(self):
    '''GLModule.isTests() -> bool
    
    Check whether module is a -tests version of module.'''
    result = self.getName().endswith('-tests')
    return(result)
    
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
          if result != list():
            result = result[-1].strip().split('\n')
      self.cache['status'] = result
    return(list(self.cache['status']))
    
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
      if result == '':
        if self.getName().endswith('-tests'):
          result = 'tests'
        else: # if not self.getName().endswith('-tests')
          result = 'main'
      if type(result) is bytes:
        result = result.decode(ENCS['default'])
      self.cache['applicability'] = result
    return(self.cache['applicability'])
    
  def getFiles(self, autoconf_version):
    '''GLModule.getFiles(autoconf_version) -> list
    
    Return list of files.'''
    section = 'Files:'
    if type(autoconf_version) is not float:
      raise(TypeError('autoconf_version must be a float, not %s' % \
        type(autoconf_version).__name__))
    if 'files' not in self.cache:
      if section not in self.content:
        result = list()
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
    
  def getDependencies(self, localdir):
    '''GLModule.getDependencies(localdir) -> list
    
    Return list of dependencies.'''
    result = list()
    section = 'Depends-on:'
    modulesystem = GLModuleSystem(localdir)
    if 'dependencies' not in self.cache:
      if section not in self.content:
        depmodules = list()
      else: # if section in self.content
        pattern = '^%s[\t ]*(.*?)%s' % (section, self.regex)
        pattern = compiler(pattern, re.DOTALL | re.MULTILINE)
        depmodules = pattern.findall(self.content)
        if type(depmodules) is list:
          if depmodules != list():
            depmodules = depmodules[-1].strip().split('\n')
      if depmodules == ['']:
        depmodules = list()
      depmodules = [dep for dep in depmodules if not dep.startswith('#')]
      if self.isTests():
        nontests = self.getName()[:self.getName().find('-tests')]
        if modulesystem.exists(nontests):
          depmodules += [nontests]
      duplicated = list()
      for depmodule in depmodules:
        if '[' in depmodule:
          depmodule, condition = depmodule.split('[')
          depmodule = depmodule.strip()
          condition = '[%s' % condition
          if type(condition) is bytes:
            condition = condition.decode(ENCS['default'])
          condition = condition.strip()
        else: # if '[' not in depmodule
          depmodule = depmodule.strip()
          condition = None
        depmodule = modulesystem.find(depmodule)
        result.append(tuple([depmodule, condition]))
      self.cache['dependencies'] = sorted(result)
    return(list(self.cache['dependencies']))
    
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
    
  def getAutomakeSnippet(self, conditional, autoconf_version):
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


#===============================================================================
# Define GLModuleTable class
#===============================================================================
class GLModuleTable(object):
  '''GLModuleTable is used to work with the list of the modules.'''
  
  def __init__(self, localdir, avoids=list(), testflags=list(),conddeps=True):
    '''GLModuleTable.__init__(*args, **kwargs) -> GLModuleTable
    
    Create new GLModuleTable instance. If modules are specified, then add
    every module from iterable as unconditional module. If avoids is specified,
    then in transitive_closure every dependency which is in avoids won't be
    included in the final modules list. If testflags iterable is enabled, then
    don't add module which status is in the testflags. If conddeps are enabled,
    then store condition for each dependency if it has a condition.
    The only necessary argument is localdir, which is needed just to create
    modulesystem instance to look for dependencies.'''
    self.avoids = list() # Avoids
    self.dependers = dict() # Dependencies
    self.conditionals = dict() # Conditional modules
    self.unconditionals = dict() # Unconditional modules
    if type(localdir) is bytes or type(localdir) is string:
      if type(localdir) is bytes:
        localdir = localdir.decode(ENCS['default'])
      self.localdir = localdir
    else: # if localdir has not bytes or string type
      raise(TypeError(
        'localdir must be a string, not %s' % type(module).__name__))
    for avoid in avoids:
      if type(avoid) is not GLModule:
        raise(TypeError('each avoid must be a GLModule instance'))
      self.avoids += [avoids]
    for testflag in sorted(set(testflags)):
      if testflag not in TESTS.values():
        raise(TypeError('unknown testflag %s' % type(testflag).__name__))
    self.testflags = sorted(set(testflags))
    if type(conddeps) is not bool:
      raise(TypeError(
        'conddeps must be bool, not %s' % type(conddeps).__name__))
    self.conddeps = conddeps
    self.modulesystem = GLModuleSystem(localdir)
    
  def addConditional(self, parent, module, condition):
    '''GLModuleTable.addConditional(module, condition)
    
    Add new conditional dependency from parent to module with condition.'''
    if type(parent) is not GLModule:
      raise(TypeError(
        'parent must be a GLModule, not %s' % type(parent).__name__))
    if type(module) is not GLModule:
      raise(TypeError(
        'module must be a GLModule, not %s' % type(module).__name__))
    if type(condition) is bytes or type(condition) is string \
    or condition == True:
      if type(condition) is bytes:
        condition = condition.decode(ENCS['default'])
    else: # if condition has not bytes or string type or is not True
      raise(TypeError('condition must be a string or True, not %s' % \
        type(condition).__name__))
    if not str(module) in self.unconditionals:
      if str(module) not in self.dependers:
        self.dependers[module] = list()
      self.dependers[module] += [module]
      key = '%s---%s' % (str(parent), str(module))
      self.conditionals[key] = condition
    
  def addUnconditional(self, module):
    '''GLModuleTable.addUnconditional(module)
    
    Add module as unconditional dependency.'''
    if type(module) is not GLModule:
      raise(TypeError(
        'module must be a GLModule, not %s' % type(module).__name__))
    if str(module) in self.dependers:
      self.dependers.pop(str(module))
    self.unconditionals[str(module)] = True
    
  def isConditional(self, module):
    '''GLModuleTable.isConditional(module) -> bool
    
    Check whether module is unconditional.'''
    if type(module) is not GLModule:
      raise(TypeError(
        'module must be a GLModule, not %s' % type(module).__name__))
    result = str(module) in self.dependers
    return(result)
    
  def getCondition(self, parent, module):
    '''GLModuleTable.getCondition(module) -> string or True
    
    Return condition from parent to module. Condition can be string or True.
    If module is not in the list of conddeps, method returns None.'''
    if type(parent) is not GLModule:
      raise(TypeError(
        'parent must be a GLModule, not %s' % type(parent).__name__))
    if type(module) is not GLModule:
      raise(TypeError(
        'module must be a GLModule, not %s' % type(module).__name__))
    key = '%s---%s' % (str(parent), str(module))
    result = None
    if key in self.conditionals:
      result = self.conditionals[key]
    return(result)
    
  def transitive_closure(self, modules):
    '''GLModuleTable.transitive_closure(modules) -> list
    
    Use transitive closure to add module and its dependencies. Add every
    module and its dependencies from modules list, but do not add dependencies
    which contain in avoids list. If any testflag is enabled, then do not add
    dependencies which have the status as this flag. If conddeps are enabled,
    then store condition for each dependency if it has a condition. This method
    is used to update final list of modules.
    Method returns list of modules together '''
    for module in modules:
      if type(module) is not GLModule:
        raise(TypeError('each module must be a GLModule instance'))
    handledmodules = list()
    inmodules = modules
    outmodules = list()
    if self.conddeps:
      for module in modules:
        self.addUnconditional(module)
    while inmodules:
      inmodules_this_round = inmodules
      inmodules = list()
      for module in inmodules_this_round:
        outmodules += [module]
        if self.conddeps:
          automake_snippet = \
            module.getAutomakeSnippet(True, self.autoconf_version)
          pattern = compiler('^if')
          if not pattern.findall(automake_snippet):
            self.addUnconditional(module)
          conditional = self.isConditional(module)
        dependencies = module.getDependencies(self.localdir)
        depmodules = [pair[0] for pair in dependencies]
        conditions = [pair[1] for pair in dependencies]
        if TESTS['tests'] in self.testflags:
          testsname = module.getTestsName()
          if self.modulesystem.exists(testsname):
            testsmodule = self.modulesystem.find(testsname)
            depmodules += [testsmodule]
        for depmodule in depmodules:
          include = True
          includes = list()
          status = depmodule.getStatus()
          for word in status:
            if word == 'obsolete':
              if TESTS['obsolete'] in self.testflags or \
              TESTS['all-test'] in self.testflags:
                includes += [False]
            elif word == 'c++-test':
              if TESTS['c++-test'] in self.testflags or \
              TESTS['all-test'] in self.testflags:
                includes += [False]
            elif word == 'longrunning-test':
              if TESTS['longrunning-test'] in self.testflags or \
              TESTS['all-test'] in self.testflags:
                includes += [False]
            elif word == 'privileged-test':
              if TESTS['privileged-test'] in self.testflags or \
              TESTS['all-test'] in self.testflags:
                includes += [False]
            elif word == 'all-test':
              if TESTS['all-test'] in self.testflags or \
              TESTS['all-test'] in self.testflags:
                includes += [False]
            else: # if any other word
              if word.endswith('-tests'):
                if TESTS['all-test'] in self.testflags:
                  includes += [False]
            include = any(includes)
          if include and depmodule not in self.avoids:
            inmodules += [depmodule]
            if self.conddeps:
              index = depmodules.index(depmodule)
              condition = conditions[index]
              if condition:
                self.addConditional(self, module, depmodule, condition)
              else: # if condition
                if conditional:
                  self.addConditional(self, module, depmodule, True)
                else: # if not conditional
                  self.addUnconditional(self, module)
      listing = list() # Create empty list
      inmodules = sorted(set(inmodules))
      handledmodules = sorted(set(handledmodules +inmodules_this_round))
      for module in inmodules:
        if module not in handledmodules:
          listing += [module]
      inmodules = sorted(set(listing))
    modules = sorted(set(outmodules))
    return(modules)
    
  def transitive_closure_separately(self, basemodules, modules, lgpl=False):
    '''GLModuleTable.transitive_closure_separately(*args, **kwargs) -> tuple
    
    Determine main module list and tests-related module list separately.
    The main module list is the transitive closure of the specified modules,
    ignoring tests modules. Its lib/* sources go into $sourcebase/. If lgpl is
    specified, it will consist only of LGPLed source.
    The tests-related module list is the transitive closure of the specified
    modules, including tests modules, minus the main module list excluding
    modules of applicability 'all'. Its lib/* sources (brought in through
    dependencies of *-tests modules) go into $testsbase/. It may contain GPLed
    source, even if lgpl is specified.
    Method returns tuple which contains two lists: the list of main modules and
    the list of tests-related modules. Both lists contain dependencies.'''
    main_modules = list()
    tests_modules = list()
    for module in modules:
      if type(module) is not GLModule:
        raise(TypeError('each module must be a GLModule instance'))
    main_modules = self.transitive_closure_separately(basemodules)

