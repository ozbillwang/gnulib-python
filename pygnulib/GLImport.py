#!/usr/bin/python
# encoding: UTF-8

#===============================================================================
# Define global imports
#===============================================================================
import os
import re
import sys
import locale
import codecs
import subprocess as sp
from pprint import pprint
from . import constants
from .GLError import GLError
from .GLMode import GLMode
from .GLModuleSystem import GLModule
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
# Define GLImport class
#===============================================================================
class GLImport(GLMode):
  '''GLImport class is used to provide methods for --import, --add-import
  and --remove-import actions.'''
  
  def __init__\
  (
    self,
    mode,
    m4base,
    destdir=None,
    localdir=None,
    modcache=None,
    verbose=None,
    auxdir=None,
    modules=None,
    avoids=None,
    sourcebase=None,
    pobase=None,
    docbase=None,
    testsbase=None,
    tests=None,
    libname=None,
    lgpl=None,
    makefile=None,
    libtool=None,
    dependencies=None,
    macro_prefix=None,
    podomain=None,
    witness_c_macro=None,
    vc_files=None,
  ):
    '''Create GLImport instance. There are some variables which can be used
    in __init__ section. However, you can set them later using methods inside
    GLImport class. See info for each variable in the corresponding set*
    class. The main variable, mode, must be one of the values of the MODES dict
    object, which is accessible from this module.'''
    
    # Initialization of the object
    super(GLImport, self).__init__\
    ( # Begin __init__ method
      destdir=destdir,
      localdir=localdir,
      modcache=modcache,
      verbose=verbose,
    ) # Complete __init__ method
    if type(mode) is int and \
      MODES['import'] <= mode <= MODES['update']:
        self.mode = mode
    else: # if mode is not int or is not 0-3
      raise(TypeError(
        "mode must be 0 <= mode <= 3, not %s" % repr(mode)))
    
    # Initialize some values
    if modules == None:
      modules = list()
    if avoids == None:
      avoids = list()
    keys = \
    [
      'auxdir', 'modules', 'avoids', 'sourcebase', 'm4base', 'pobase',
      'docbase', 'testsbase', 'tests', 'libname', 'makefile', 'libtool',
      'dependencies', 'macro_prefix', 'podomain', 'vc_files', 'lgpl',
      'witness_c_macro',
    ]
    for item in keys:
      self.args[item] = ''
      self.cache[item] = ''
    self.cache['libname'] = 'libgnu'
    self.cache['modules'] = list()
    self.cache['avoids'] = list()
    self.cache['flags'] = list()
    self.cache['tests'] = list()
    self.cache['lgpl'] = False
    
    # Set m4base as always needed argument
    self.setM4Base(m4base)
    
    # mode => self.mode
    if type(mode) is int and \
      MODES['import'] <= mode <= MODES['update']:
        self.mode = mode
    else: # if mode is not int or is not 0-3
      raise(TypeError(
        "mode must be 0 <= mode <= 3, not %s" % repr(mode)))
    
    # Get cached auxdir and libtool from configure.ac/in
    self.cache['auxdir'] = '.'
    path = joinpath(self.args['destdir'], 'configure.ac')
    if not isfile(path):
      path = joinpath(self.args['destdir'], 'configure.in')
      if not isfile(path):
        raise(GLError(3, path))
    with codecs.open(path, 'rb', 'UTF-8') as file:
      data = file.read()
    pattern = compiler(r'^AC_CONFIG_AUX_DIR\((.*?)\)$', re.S | re.M)
    result = cleaner(pattern.findall(data))[0]
    self.cache['auxdir'] = joinpath(result, self.args['destdir'])
    pattern = compiler(r'A[CM]_PROG_LIBTOOL', re.S | re.M)
    guessed_libtool = bool(pattern.findall(data))
    
    # Guess autoconf version
    pattern = compiler('.*AC_PREREQ\((.*?)\)$', re.S | re.M)
    versions = cleaner(pattern.findall(data))
    if not versions:
      version = 2.59
    else: # if versions
      version = sorted(set([float(version) for version in versions]))[-1]
    if version < 2.59:
      raise(GLError(4, version))
    self.autoconf_version = version
    
    # Get other cached variables
    path = joinpath(self.args['m4base'], 'gnulib-cache.m4')
    if isfile(joinpath(self.args['m4base'], 'gnulib-cache.m4')):
      with codecs.open(path, 'rb', 'UTF-8') as file:
        data = file.read()
      # Create regex object and keys
      pattern = compiler(r'^(gl_.*?)\((.*?)\)$', re.S | re.M)
      keys = \
      [
        'gl_LOCAL_DIR', 'gl_MODULES', 'gl_AVOID', 'gl_SOURCE_BASE',
        'gl_M4_BASE', 'gl_PO_BASE', 'gl_DOC_BASE', 'gl_TESTS_BASE',
        'gl_MAKEFILE_NAME', 'gl_MACRO_PREFIX', 'gl_PO_DOMAIN',
        'gl_WITNESS_C_MACRO', 'gl_VC_FILES', 'gl_LIB',
      ]
      # Find bool values
      self.cache['flags'] = list()
      if 'gl_LGPL(' in data:
        keys.append('gl_LGPL')
      elif 'gl_LGPL' in data:
        self.cache['lgpl'] = True
        data = data.replace('gl_LGPL', '')
      if 'gl_LIBTOOL' in data:
        self.cache['libtool'] = True
        data = data.replace('gl_LIBTOOL', '')
      if 'gl_WITH_TESTS' in data:
        self.cache['tests'].append(TESTS['tests'])
        data = data.replace('gl_WITH_TESTS', '')
      if 'gl_WITH_OBSOLETE' in data:
        self.cache['tests'].append(TESTS['obsolete'])
        data = data.replace('gl_WITH_OBSOLETE', '')
      if 'gl_WITH_CXX_TESTS' in data:
        self.cache['tests'].append(TESTS['c++-test'])
        data = data.replace('gl_WITH_CXX_TESTS', '')
      if 'gl_WITH_LONGRUNNING_TESTS' in data:
        self.cache['tests'].append(TESTS['longrunning-test'])
        data = data.replace('gl_WITH_LONGRUNNING_TESTS', '')
      if 'gl_WITH_PRIVILEGED_TESTS' in data:
        self.cache['tests'].append(TESTS['privileged-test'])
        data = data.replace('gl_WITH_PRIVILEGED_TESTS', '')
      if 'gl_WITH_UNPORTABLE_TESTS' in data:
        self.cache['tests'].append(TESTS['unportable-test'])
        data = data.replace('gl_WITH_UNPORTABLE_TESTS', '')
      if 'gl_WITH_ALL_TESTS' in data:
        self.cache['tests'].append(TESTS['all-test'])
        data = data.replace('gl_WITH_ALL_TESTS', '')
      # Find string values
      result = dict(pattern.findall(data))
      values = cleaner([result.get(key, '') for key in keys])
      tempdict = dict(zip(keys, values))
      if 'gl_LGPL' in tempdict:
        self.cache['lgpl'] = cleaner(tempdict['gl_LGPL'])
        if self.cache['lgpl'].isdecimal():
          self.cache['lgpl'] = int(self.cache['lgpl'])
      else: # if 'gl_LGPL' not in tempdict
        self.cache['lgpl'] = False
      if tempdict['gl_LIB']:
        self.cache['libname'] = cleaner(tempdict['gl_LIB'])
      if tempdict['gl_LOCAL_DIR']:
        self.cache['localdir'] = cleaner(tempdict['gl_LOCAL_DIR'])
      if tempdict['gl_MODULES']:
        self.cache['modules'] = cleaner(tempdict['gl_MODULES'].split())
      if tempdict['gl_AVOID']:
        self.cache['avoids'] = cleaner(tempdict['gl_AVOID'].split())
      if tempdict['gl_SOURCE_BASE']:
        self.cache['sourcebase'] = cleaner(tempdict['gl_SOURCE_BASE'])
      if tempdict['gl_M4_BASE']:
        self.cache['m4base'] = cleaner(tempdict['gl_M4_BASE'])
      if tempdict['gl_PO_BASE']:
        self.cache['pobase'] = cleaner(tempdict['gl_PO_BASE'])
      if tempdict['gl_DOC_BASE']:
        self.cache['docbase'] = cleaner(tempdict['gl_DOC_BASE'])
      if tempdict['gl_TESTS_BASE']:
        self.cache['testsbase'] = cleaner(tempdict['gl_TESTS_BASE'])
      if tempdict['gl_MAKEFILE_NAME']:
        self.cache['makefile'] = cleaner(tempdict['gl_MAKEFILE_NAME'])
      if tempdict['gl_MACRO_PREFIX']:
        self.cache['macro_prefix'] = cleaner(tempdict['gl_MACRO_PREFIX'])
      if tempdict['gl_PO_DOMAIN']:
        self.cache['podomain'] = cleaner(tempdict['gl_PO_DOMAIN'])
      if tempdict['gl_WITNESS_C_MACRO']:
        self.cache['witness_c_macro'] = cleaner(tempdict['gl_WITNESS_C_MACRO'])
    
    # The self.args['localdir'] defaults to the cached one. Recall that the 
    # cached one is relative to $destdir, whereas the one we use is relative
    # to . or absolute.
    if not self.args['localdir']:
      if self.cache['localdir']:
        if isabs(self.args['destdir']):
          self.args['localdir'] = \
            joinpath(self.args['destdir'], self.cache['localdir'])
        else: # if not isabs(self.args['destdir'])
          if isabs(self.cache['localdir']):
            self.args['localdir'] = \
              joinpath(self.args['destdir'], self.cache['localdir'])
          else: # if not isabs(self.cache['localdir'])
            self.args['localdir'] = \
              relpath(joinpath(self.args['destdir'], self.cache['localdir']))
    self.modulesystem = GLModuleSystem(self.args['localdir'])
    
    if self.mode == MODES['import']:
      self.setModules(modules)
    
    else: # if self.mode != MODES['import']
      if self.args['m4base'] != self.cache['m4base']:
        raise(GLError(5, m4base))
      
      # Perform actions with modules. In --add-import, append each given module
      # to the list of cached modules; in --remove-import, remove each given
      # module from the list of cached modules; in --update, simply set
      # self.args['modules'] to its cached version.
      self.setModules(self.cache['modules'])
      if self.mode == MODES['add-import']:
        for module in modules:
          self.addModule(module)
      elif self.mode == MODES['remove-import']:
        for module in modules:
          self.removeModule(module)
      
      # tests => self.args['tests']
      if tests == None:
        self.setTestFlags(self.cache['tests'])
      else: # if tests != None
        self.setTestFlags(tests)
        for testflag in self.cache['tests']:
          self.enableTestFlag(testflag)
      self.args['tests'] = sorted(self.args['tests'])
      
      # avoids => self.args['avoids']
      self.setAvoids(avoids +self.cache['avoids'])
      
      # sourcebase => self.args['sourcebase']
      if sourcebase == None:
        self.setSourceBase(self.cache['sourcebase'])
      else: # if sourcebase != None
        self.setSourceBase(sourcebase)
      if not self.args['sourcebase']:
        raise(GLError(6, None))
      
      # pobase => self.args['pobase']
      if pobase == None:
        self.setPoBase(self.cache['pobase'])
      else: # if pobase != None
        self.setPoBase(pobase)
      
      # docbase => self.args['docbase']
      if docbase == None:
        self.setDocBase(self.cache['docbase'])
      else: # if docbase != None
        self.setDocBase(docbase)
      if not self.args['docbase']:
        raise(GLError(7, None))
      
      # testsbase => self.args['testsbase']
      if testsbase == None:
        self.setTestsBase(self.cache['testsbase'])
      else: # if testsbase != None
        self.setTestsBase(testsbase)
      if not self.args['testsbase']:
        raise(GLError(8, None))
      
      # libname => self.args['libname']
      if libname == None:
        self.setLibName(self.cache['libname'])
      else: # if libname != None
        self.setLibName(libname)
      if not self.args['libname']:
        raise(GLError(9, None))
      
      # lgpl => self.args['lgpl']
      if lgpl == None:
        self.setLGPL(self.cache['lgpl'])
      else: # if lgpl != None
        self.setLGPL(lgpl)
      
      # makefile => self.args['makefile']
      if makefile == None:
        self.setMakefile(self.cache['makefile'])
      else: # if makefile != None
        self.setMakefile(makefile)
      
      # dependencies => self.args['dependencies']
      if type(dependencies) is bool and dependencies:
        self.enableDependencies()
      elif type(dependencies) is bool and not dependencies:
        self.disableDependencies()
      elif type(dependencies) is NoneType and self.cache['dependencies']:
        self.enableDependencies()
      elif type(dependencies) is NoneType and not self.cache['dependencies']:
        self.disableDependencies()
      
      # libtool => self.args['libtool']
      if libtool == None:
        if 'libtool' in self.cache:
          if self.cache['libtool']:
            self.enableLibtool()
          else: # if not self.cache['libtool']
            self.disableLibtool()
        else: # if 'libtool' not in self.cache
          if guessed_libtool:
            self.enableLibtool()
          else: # if not guessed_libtool
            self.disableLibtool()
      else: # if libtool != None
        if libtool:
          self.enableLibtool()
        else: # if not libtool
          self.disableLibtool()
      
      # macro_prefix => self.args['macro_prefix']
      if macro_prefix == None:
        self.setMacroPrefix(self.cache['macro_prefix'])
      else: # if macro_prefix != None
        self.setMacroPrefix(macro_prefix)
      
      # podomain => self.args['podomain']
      if podomain == None:
        self.setPoDomain(self.cache['podomain'])
      else: # if podomain != None
        self.setPoDomain(podomain)
      
      # witness_c_macro => self.args['witness_c_macro']
      if witness_c_macro == None:
        self.setWitnessCMacro(self.cache['witness_c_macro'])
      else: # if witness_c_macro != None
        self.setWitnessCMacro(witness_c_macro)
      
      # vc_files => self.args['vc_files']
      if vc_files == None:
        if self.cache['vc_files']:
          self.disableVCFiles()
        else: # if not self.cache['vc_files']
          self.enableVCFiles()
      elif type(vc_files) is bool: # if not vc_files
        if vc_files:
          self.enableVCFiles()
        else: # if not vc_files
          self.disableVCFiles
      
      if dependencies and TESTS['default'] in self.tests:
        raise(GLError(9, None))
    
    self.depmodules = list()
    self.conditions = list()
    
  def __repr__(self):
    '''x.__repr__ <==> repr(x)'''
    return('<pygnulib.GLImport>')
    
  def transitive_closure(self, module):
    '''Get dependencies of module and add them to list of modules. For each
    dependency get its dependencies, etc. Recursive function, which is used to
    set lists of dependencies and its conditions. If module is added without
    conditions, then condition is None.'''
    depmodules = module.getDependencies()
    for depmodule in depmodules:
      if '[' in depmodule:
        depmodule, condition = depmodule.split('[')
        depmodule = depmodule.strip()
        condition = '[%s' % condition
      else: # if '[' not in depmodule
        condition = None
      depmodule = self.modulesystem.find(depmodule)
      if depmodule not in self.depmodules:
          if depmodule not in self.args['avoids']:
            self.depmodules += [depmodule]
            self.conditions += [condition]
            self.transitive_closure(depmodule)
    
  def execute(self, dryrun=False):
    '''Run the GLImport and perform necessary actions. If dryrun is True, then
    only print what would have been done.'''
    system = self.modulesystem
    self.args['modules'] = \
    [ # Begin creation of GLModule list
      self.modulesystem.find(module) for module in self.getModules()
    ] # Finish creation of GLModule list
    self.args['avoids'] = \
    [ # Begin creation of GLModule list
      self.modulesystem.find(module) for module in self.getAvoids()
    ] # Finish creation of GLModule list
    
    # If testflags are disabled and conditional dependencies are disabled, we
    # just add every module to final modules list.
    for module in self.args['modules']:
      self.transitive_closure(module)
    
    # If testflags are enabled, filter dependencies whose flag is disabled.
    if self.getTestFlags():
      for depmodule in self.depmodules:
        index = self.depmodules.index(depmodule)
        status = depmodule.getStatus()
        if self.checkTestFlag(TESTS['tests']):
          testsname = depmodule.getTestsName()
          if self.modulesystem.exists(testsname):
            testsmodule = self.modulesystem.find(testsname)
            if testsmodule not in self.depmodules:
              self.depmodules += [testsmodule]
        if status == 'obsolete':
          if self.checkTestFlag(TESTS['obsolete']) or \
          self.checkTestFlag(TESTS['all-test']):
            self.depmodules.remove(depmodule)
            self.conditions.pop(index)
        elif status == 'c++-test':
          if self.checkTestFlag(TESTS['c++-test']) or \
          self.checkTestFlag(TESTS['all-test']):
            self.depmodules.remove(depmodule)
            self.conditions.pop(index)
        elif status == 'longrunning-test':
          if self.checkTestFlag(TESTS['longrunning-test']) or \
          self.checkTestFlag(TESTS['all-test']):
            self.depmodules.remove(depmodule)
            self.conditions.pop(index)
        elif status == 'privileged-test':
          if self.checkTestFlag(TESTS['privileged-test']) or \
          self.checkTestFlag(TESTS['all-test']):
            self.depmodules.remove(depmodule)
            self.conditions.pop(index)
        elif status == 'all-test':
          if self.checkTestFlag(TESTS['all-test']) or \
          self.checkTestFlag(TESTS['all-test']):
            self.depmodules.remove(depmodule)
            self.conditions.pop(index)
    
    # If conditional dependencies are enabled, filter dependencies which can be
    # added if their condition is True.
    
    exit()
    
  def addModule(self, module):
    '''Add the module to the modules list.'''
    if type(module) is bytes or type(module) is string:
      if type(module) is bytes:
        module = module.decode(ENCS['default'])
      self.args['modules'].append(module)
    else: # if module has not bytes or string type
      raise(TypeError(
        'argument must be a string, not %s' % type(module).__name__))
    
  def removeModule(self, module):
    '''Remove the module from the modules list.'''
    if type(module) is bytes or type(module) is string:
      if type(module) is bytes:
        module = module.decode(ENCS['default'])
      self.args['modules'].remove(module)
    else: # if module has not bytes or string type
      raise(TypeError(
        'argument must be a string, not %s' % type(module).__name__))
    
  def getModules(self):
    '''GLImport.getModules() -> list
    
    Return the modules list.'''
    return(list(self.args['modules']))
    
  def setModules(self, modules):
    '''Set the modules list.'''
    if type(modules) is list or type(modules) is tuple:
      old_modules = self.args['modules']
      self.args['modules'] = list()
      for module in modules:
        try: # Try to add each module
          self.addModule(module)
        except TypeError as error:
          self.args['modules'] = old_modules
          raise(TypeError('each module must be a string'))
        except GLError as error:
          self.args['modules'] = old_modules
          raise(GLError(error.errno, error.errinfo))
    else: # if type of modules is not list or tuple
      raise(TypeError(
        'modules must be a list or a tuple, not %s' % type(modules).__name__))
    
  def resetModules(self):
    '''Reset the list of the modules.'''
    self.setModules(self.cache['modules'])
    
  def addAvoid(self, module):
    '''Avoid including the given module. Useful if you have code that provides
    equivalent functionality.'''
    if type(module) is bytes or type(module) is string:
      if type(module) is bytes:
        module = module.decode(ENCS['default'])
      self.args['avoids'].append(module)
    else: # if module has not bytes or string type
      raise(TypeError(
        'argument must be a string, not %s' % type(module).__name__))
    
  def removeAvoid(self, module):
    '''Remove the given module from the list of avoided modules.'''
    if type(module) is bytes or type(module) is string:
      if type(module) is bytes:
        module = module.decode(ENCS['default'])
      self.args['avoids'].remove(module)
    else: # if module has not bytes or string type
      raise(TypeError(
        'argument must be a string, not %s' % type(module).__name__))
    
  def getAvoids(self):
    '''Return the list of the avoided modules.'''
    return(list(self.args['avoids']))
    
  def setAvoids(self, modules):
    '''Specify the modules which will be avoided.'''
    if type(modules) is list or type(modules) is tuple:
      old_avoids = self.args['avoids']
      self.args['avoids'] = list()
      for module in modules:
        try: # Try to add each module
          self.addAvoid(module)
        except TypeError as error:
          self.args['avoids'] = old_avoids
          raise(TypeError('each module must be a string'))
        except GLError as error:
          self.args['avoids'] = old_avoids
          raise(GLError(error.errno, error.errinfo))
    else: # if type of modules is not list or tuple
      raise(TypeError(
        'modules must be a list or a tuple, not %s' % type(modules).__name__))
    
  def resetAvoids(self):
    '''Reset the list of the avoided modules.'''
    self.setAvoids(self.cache['avoids'])
    
  def checkTestFlag(self, flag):
    '''Return the status of the test flag.'''
    if flag in TESTS.values():
      return(flag in self.args['tests'])
    else: # if flag is not in TESTS
      raise(TypeError('unknown flag: %s' % repr(flag)))
    
  def enableTestFlag(self, flag):
    '''Enable test flag. You can get flags from TESTS variable.'''
    if flag in TESTS.values():
      if flag not in self.args['tests']:
        self.args['tests'].append(flag)
    else: # if flag is not in TESTS
      raise(TypeError('unknown flag: %s' % repr(flag)))
    
  def disableTestFlag(self, flag):
    '''Disable test flag. You can get flags from TESTS variable.'''
    if flag in TESTS.values():
      if flag in self.args['tests']:
        self.args['tests'].remove(flag)
    else: # if flag is not in TESTS
      raise(TypeError('unknown flag: %s' % repr(flag)))
    
  def getTestFlags(self):
    '''Return test flags. You can get flags from TESTS variable.'''
    return(list(self.args['tests']))
    
  def setTestFlags(self, flags):
    '''Specify test flags. You can get flags from TESTS variable.'''
    if type(flags) is list or type(flags) is tuple:
      old_flags = self.args['tests']
      self.args['tests'] = list()
      for flag in flags:
        try: # Try to enable each flag
          self.enableTestFlag(flag)
        except TypeError as error:
          raise(TypeError('each flag must be one of TESTS integers'))
      self.args['tests'] = flags
    else: # if type of flags is not list or tuple
      raise(TypeError(
        'flags must be a list or a tuple, not %s' % type(flags).__name__))
    
  def resetTestFlags(self):
    '''Reset test flags (only default flag will be enabled).'''
    self.setTestFlags(self.cache['tests'])
    
  def checkDependencies(self):
    '''Check if user enabled cond. dependencies.'''
    return(self.args['dependencies'])
    
  def enableDependencies(self):
    '''Enable cond. dependencies (may save configure time and object code).'''
    self.args['dependencies'] = True
    
  def disableDependencies(self):
    '''Disable cond. dependencies (may save configure time and object code).'''
    self.args['dependencies'] = False
    
  def resetDependencies(self):
    '''Reset cond. dependencies (may save configure time and object code).'''
    self.args['dependencies'] = self.cache['dependencies']
    
  def checkLibtool(self):
    '''Check if user enabled libtool rules.'''
    return(self.args['libtool'])
    
  def enableLibtool(self):
    '''Enable libtool rules.'''
    self.args['libtool'] = True
    
  def disableLibtool(self):
    '''Disable libtool rules.'''
    self.args['libtool'] = False
    
  def resetLibtool(self):
    '''Reset libtool rules.'''
    self.args['libtool'] = self.cache['libtool']
    
  def getLibName(self):
    '''Return the library name. Defaults to 'libgnu'.'''
    return(self.args['libname'])
    
  def setLibName(self, libname):
    '''Specify the library name.  Defaults to 'libgnu'.'''
    if type(libname) is bytes or type(libname) is string:
      if type(libname) is bytes:
        libname = string(libname, ENCS['system'])
      self.args['libname'] = libname
    else: # if type of libname is not bytes or string
      raise(TypeError(
        'argument must be a string, not %s' % type(module).__name__))
    
  def resetLibName(self):
    '''Specify the library name.  Defaults to 'libgnu'.'''
    self.setLibName(self.cache['libname'])
    
  def getAuxDir(self):
    '''Return directory relative to --dir where auxiliary build tools are
    placed. Default comes from configure.ac or configure.in.'''
    return(self.args['auxdir'])
    
  def setAuxDir(self, auxdir):
    '''Specify directory relative to --dir where auxiliary build tools are
    placed. Default comes from configure.ac or configure.in.'''
    if type(auxdir) is bytes or type(auxdir) is string:
      if type(auxdir) is bytes:
        auxdir = string(auxdir, ENCS['system'])
      self.args['auxdir'] = joinpath(self.args['destdir'], auxdir)
    else: # if type of auxdir is not bytes or string
      raise(TypeError(
        'argument must be a string, not %s' % type(auxdir).__name__))
    
  def resetAuxDir(self):
    '''Reset directory relative to --dir where auxiliary build tools are
    placed. Default comes from configure.ac or configure.in.'''
    self.setAuxDir(self.cache['auxdir'])
    
  def getSourceBase(self):
    '''Return directory relative to destdir where source code is placed.
    Default value for this variable is 'lib').'''
    return(self.args['sourcebase'])
    
  def setSourceBase(self, sourcebase):
    '''Specify directory relative to destdir where source code is placed.
    Default value for this variable is 'lib').'''
    if type(sourcebase) is bytes or type(sourcebase) is string:
      if type(sourcebase) is bytes:
        sourcebase = string(sourcebase, ENCS['system'])
      self.args['sourcebase'] = joinpath(self.args['destdir'], sourcebase)
    else: # if type of sourcebase is not bytes or string
      raise(TypeError(
        'argument must be a string, not %s' % type(sourcebase).__name__))
    
  def resetSourceBase(self):
    '''Return directory relative to destdir where source code is placed.
    Default value for this variable is 'lib').'''
    self.setSourceBase(self.cache['sourcebase'])
    
  def getM4Base(self):
    '''Return directory relative to destdir where *.m4 macros are placed.
    Default value for this variable is 'm4').'''
    return(self.args['m4base'])
    
  def setM4Base(self, m4base):
    '''Specify directory relative to destdir where *.m4 macros are placed.
    Default value for this variable is 'm4').'''
    if type(m4base) is bytes or type(m4base) is string:
      if type(m4base) is bytes:
        m4base = string(m4base, ENCS['system'])
      self.args['m4base'] = joinpath(self.args['destdir'], m4base)
    else: # if type of m4base is not bytes or string
      raise(TypeError(
        'argument must be a string, not %s' % type(m4base).__name__))
    
  def resetM4Base(self):
    '''Reset directory relative to destdir where *.m4 macros are placed.
    Default value for this variable is 'm4').'''
    self.setM4Base(self.cache['m4base'])
    
  def getPoBase(self):
    '''Return directory relative to destdir where *.po files are placed.
    Default value for this variable is 'po').'''
    return(self.args['pobase'])
    
  def setPoBase(self, pobase):
    '''Specify directory relative to destdir where *.po files are placed.
    Default value for this variable is 'po').'''
    if type(pobase) is bytes or type(pobase) is string:
      if type(pobase) is bytes:
        pobase = string(pobase, ENCS['system'])
      self.args['pobase'] = joinpath(self.args['destdir'], pobase)
    else: # if type of pobase is not bytes or string
      raise(TypeError(
        'argument must be a string, not %s' % type(pobase).__name__))
    
  def resetPoBase(self):
    '''Reset directory relative to destdir where *.po files are placed.
    Default value for this variable is 'po').'''
    self.setPoBase(self.cache['pobase'])
    
  def getDocBase(self):
    '''Return directory relative to destdir where doc files are placed.
    Default value for this variable is 'doc').'''
    return(self.args['docbase'])
    
  def setDocBase(self, docbase):
    '''Specify directory relative to destdir where doc files are placed.
    Default value for this variable is 'doc').'''
    if type(docbase) is bytes or type(docbase) is string:
      if type(docbase) is bytes:
        docbase = string(docbase, ENCS['system'])
      self.args['docbase'] = joinpath(self.args['destdir'], docbase)
    else: # if type of docbase is not bytes or string
      raise(TypeError(
        'argument must be a string, not %s' % type(docbase).__name__))
    
  def resetDocBase(self):
    '''Reset directory relative to destdir where doc files are placed.
    Default value for this variable is 'doc').'''
    self.setDocBase(self.cache['docbase'])
    
  def getTestsBase(self):
    '''Return directory relative to destdir where unit tests are placed.
    Default value for this variable is 'tests').'''
    return(self.args['testsbase'])
    
  def setTestsBase(self, testsbase):
    '''Specify directory relative to destdir where unit tests are placed.
    Default value for this variable is 'tests').'''
    if type(testsbase) is bytes or type(testsbase) is string:
      if type(testsbase) is bytes:
        testsbase = string(testsbase, ENCS['system'])
      self.args['testsbase'] = joinpath(self.args['destdir'], testsbase)
    else: # if type of testsbase is not bytes or string
      raise(TypeError(
        'argument must be a string, not %s' % type(testsbase).__name__))
    
  def resetTestsBase(self):
    '''Reset directory relative to destdir where unit tests are placed.
    Default value for this variable is 'tests').'''
    self.setTestsBase(self.cache['testsbase'])
    
  def getLGPL(self):
    '''Check for abort if modules aren't available under the LGPL.'''
    return(self.args['lgpl'])
    
  def setLGPL(self, lgpl):
    '''Abort if modules aren't available under the LGPL.'''
    if (type(lgpl) is int and 2 <= lgpl <= 3) or lgpl == False:
        self.args['lgpl'] = lgpl
    else: # if lgpl is not False, 2 or 3
      raise(TypeError(
        "invalid LGPL version: %s" % repr(lgpl)))
    
  def resetLGPL(self):
    '''Disable abort if modules aren't available under the LGPL.'''
    self.setLGPL(self.cache['lgpl'])
    
  def getMacroPrefix(self):
    '''Return the prefix of the macros 'gl_EARLY' and 'gl_INIT'.
    Default is 'gl'.'''
    return(self.args['macro_prefix'])
    
  def setMacroPrefix(self, macro_prefix):
    '''Specify the prefix of the macros 'gl_EARLY' and 'gl_INIT'.
    Default is 'gl'.'''
    if type(macro_prefix) is bytes or type(macro_prefix) is string:
      if type(macro_prefix) is bytes:
        macro_prefix = string(macro_prefix, ENCS['system'])
      self.args['macro_prefix'] = macro_prefix
    else: # if type of macro_prefix is not bytes or string
      raise(TypeError(
        'macro_prefix must be a string, not %s' % type(macro_prefix).__name__))
    
  def resetMacroPrefix(self):
    '''Reset the prefix of the macros 'gl_EARLY' and 'gl_INIT'.
    Default is 'gl'.'''
    self.setMacroPrefix(self.cache['macro_prefix'])
    
  def getMakefile(self):
    '''Return the name of makefile in automake syntax in the source-base and
    tests-base directories. Default is 'Makefile.am'.'''
    return(self.args['makefile'])
    
  def setMakefile(self, makefile):
    '''Specify the name of makefile in automake syntax in the source-base and
    tests-base directories. Default is 'Makefile.am'.'''
    if type(makefile) is bytes or type(makefile) is string:
      if type(makefile) is bytes:
        makefile = string(makefile, ENCS['system'])
      self.args['makefile'] = makefile
    else: # if type of makefile is not bytes or string
      raise(TypeError(
        'argument must be a string, not %s' % type(makefile).__name__))
    
  def resetMakefile(self):
    '''Reset the name of makefile in automake syntax in the source-base and
    tests-base directories. Default is 'Makefile.am'.'''
    self.setMakefile(self.cache['makefile'])
    
  def getPoDomain(self):
    '''Return the prefix of the i18n domain. Usually use the package name.
    A suffix '-gnulib' is appended.'''
    return(self.args['podomain'])
    
  def setPoDomain(self, podomain):
    '''Specify the prefix of the i18n domain. Usually use the package name.
    A suffix '-gnulib' is appended.'''
    if type(podomain) is bytes or type(podomain) is string:
      if type(podomain) is bytes:
        podomain = string(podomain, ENCS['system'])
      self.args['podomain'] = podomain
    else: # if type of podomain is not bytes or string
      raise(TypeError(
        'argument must be a string, not %s' % type(podomain).__name__))
    
  def resetPoDomain(self):
    '''Reset the prefix of the i18n domain. Usually use the package name.
    A suffix '-gnulib' is appended.'''
    self.setPoDomain(self.cache['podomain'])
    
  def getWitnessCMacro(self):
    '''Return the C macro that is defined when the sources in this directory
    are compiled or used.'''
    return(self.args['witness_c_macro'])
    
  def setWitnessCMacro(self, witness_c_macro):
    '''Specify the C macro that is defined when the sources in this directory
    are compiled or used.'''
    if type(witness_c_macro) is bytes or type(witness_c_macro) is string:
      if type(witness_c_macro) is bytes:
        witness_c_macro = string(witness_c_macro, ENCS['system'])
      self.args['witness_c_macro'] = witness_c_macro
    else: # if type of witness_c_macro is not bytes or string
      raise(TypeError(
        'argument must be a string, not %s' % type(witness_c_macro).__name__))
    
  def resetWitnessCMacro(self):
    '''Return the C macro that is defined when the sources in this directory
    are compiled or used.'''
    self.setWitnessCMacro(self.cache['witness_c_macro'])
    
  def checkVCFiles(self):
    '''Check if update of the version control files is enabled or disabled.'''
    return(self.args['vc_files'])
    
  def enableVCFiles(self):
    '''Enable update of the version control files.'''
    self.args['vc_files'] = True
    
  def disableVCFiles(self):
    '''Disable update of the version control files.'''
    self.args['vc_files'] = False
    
  def resetVCFiles(self):
    '''Reset update of the version control files.'''
    if not self.cache['vc_files']:
      self.disableVCFiles()
    else: # if self.cache['vc_files']
      self.enableVCFiles()

