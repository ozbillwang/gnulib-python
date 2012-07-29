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
import shutil
import tempfile
import subprocess as sp
from pprint import pprint
from . import constants
from .GLError import GLError
from .GLMode import GLMode
from .GLModuleSystem import GLModule
from .GLModuleSystem import GLModuleTable
from .GLModuleSystem import GLModuleSystem
from .GLFileSystem import GLFileAssistant


#===============================================================================
# Define module information
#===============================================================================
__author__ = constants.__author__
__license__ = constants.__license__
__copyright__ = constants.__copyright__
__version__ = constants.__version__
__all__ = ['GLImport']


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
  '''GLImport class is used to provide methods for --import, --add-import,
  --remove-import and --update actions. This is a high-level class, so
  developers may  have to use lower-level classes to create their own
  scripts. However, if user needs just to use power of gnulib-tool, this class
  is a very good choice.'''
  
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
    conddeps=None,
    macro_prefix=None,
    podomain=None,
    witness_c_macro=None,
    vc_files=None,
    symbolic=False,
    lsymbolic=False,
  ):
    '''Create GLImport instance. There are some variables which can be used
    in __init__ section. However, you can set them later using methods inside
    GLImport class. See info for each variable in the corresponding set*
    class. The main variable, mode, must be one of the values of the MODES dict
    object, which is accessible from this module.'''
    
    # Initialization of the object.
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
    
    # Initialize some values.
    if modules == None:
      modules = list()
    if avoids == None:
      avoids = list()
    keys = \
    [
      'auxdir', 'modules', 'avoids', 'sourcebase', 'm4base', 'pobase',
      'docbase', 'testsbase', 'tests', 'libname', 'makefile', 'libtool',
      'conddeps', 'macro_prefix', 'podomain', 'vc_files', 'lgpl',
      'witness_c_macro',
    ]
    for item in keys:
      self.args[item] = ''
      self.cache[item] = ''
    self.cache['libname'] = 'libgnu'
    self.cache['conddeps'] = False
    self.cache['modules'] = list()
    self.cache['avoids'] = list()
    self.cache['flags'] = list()
    self.cache['tests'] = list()
    self.cache['lgpl'] = False
    self.cache['files'] = list()
    self.cache['vc_files'] = None
    
    # Set m4base as always needed argument.
    self.setM4Base(m4base)
    
    # mode => self.mode
    if type(mode) is int and \
      MODES['import'] <= mode <= MODES['update']:
        self.mode = mode
    else: # if mode is not int or is not 0-3
      raise(TypeError(
        "mode must be 0 <= mode <= 3, not %s" % repr(mode)))
    
    # Get cached auxdir and libtool from configure.ac/in.
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
    if auxdir == None:
      self.setAuxDir(self.cache['auxdir'])
    else: # if auxdir != None
      self.setAuxDir(auxdir)
    
    # Guess autoconf version.
    pattern = compiler('.*AC_PREREQ\((.*?)\)', re.S | re.M)
    versions = cleaner(pattern.findall(data))
    if not versions:
      version = 2.59
    else: # if versions
      version = sorted(set([float(version) for version in versions]))[-1]
    if version < 2.59:
      raise(GLError(4, version))
    self.ac_version = version
    
    # Get other cached variables.
    path = joinpath(self.args['m4base'], 'gnulib-cache.m4')
    if isfile(joinpath(self.args['m4base'], 'gnulib-cache.m4')):
      with codecs.open(path, 'rb', 'UTF-8') as file:
        data = file.read()
      
      # Create regex object and keys.
      pattern = compiler('^(gl_.*?)\\((.*?)\\)$', re.S | re.M)
      keys = \
      [
        'gl_LOCAL_DIR', 'gl_MODULES', 'gl_AVOID', 'gl_SOURCE_BASE',
        'gl_M4_BASE', 'gl_PO_BASE', 'gl_DOC_BASE', 'gl_TESTS_BASE',
        'gl_MAKEFILE_NAME', 'gl_MACRO_PREFIX', 'gl_PO_DOMAIN',
        'gl_WITNESS_C_MACRO', 'gl_VC_FILES', 'gl_LIB',
      ]
      
      # Find bool values.
      self.cache['flags'] = list()
      if 'gl_LGPL(' in data:
        keys.append('gl_LGPL')
      elif 'gl_LGPL' in data:
        self.cache['lgpl'] = True
        data = data.replace('gl_LGPL', '')
      if 'gl_LIBTOOL' in data:
        self.cache['libtool'] = True
        data = data.replace('gl_LIBTOOL', '')
      if 'gl_CONDITIONAL_DEPENDENCIES' in data:
        self.cache['conddeps'] = True
        data = data.replace('gl_CONDITIONAL_DEPENDENCIES', '')
      if 'gl_VC_FILES' in data:
        self.cache['vc_files'] = True
        data = data.replace('gl_VC_FILES', '')
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
      
      # Get cached filelist from gnulib-comp.m4.
      path = joinpath(self.getDestDir(), self.getM4Base(), 'gnulib-comp.m4')
      if isfile(path):
        with codecs.open(path, 'rb', 'UTF-8') as file:
          data = file.read()
        regex = 'AC_DEFUN\\(\\[%s_FILE_LIST\\], \\[(.*?)\\]\\)' % \
          self.cache['macro_prefix']
        pattern = compiler(regex, re.S | re.M)
        self.cache['files'] = pattern.findall(data)[-1].strip().split()
    
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
      # Override cache settings
      self.setModules(modules)
      self.setAvoids(avoids)
      self.setSourceBase(sourcebase)
      self.setM4Base(m4base)
      self.setDocBase(docbase)
      self.setTestsBase(testsbase)
      self.setMacroPrefix(macro_prefix)
      if not conddeps:
        self.disableCondDeps()
      else: # if not conddeps
        self.enableCondDeps(conddeps)
      if tests == None:
        self.setTestFlags(list())
      else: # if tests != None
        self.setTestFlags(tests)
      if libname == None:
        self.setLibName('libgnu')
      
    else: # if self.mode != MODES['import']
      if self.cache['m4base'] and \
      (self.args['m4base'] != self.cache['m4base']):
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
      self.args['tests'] = sorted(set(self.args['tests']))
      
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
      
      # conddeps => self.args['conddeps']
      if conddeps == None:
        if not self.cache['conddeps']:
          self.disableCondDeps()
        else: # if self.cache['conddeps']
          self.enableCondDeps()
      else: # if conddeps != None
        if conddeps == True:
          self.enableCondDeps()
        elif conddeps == False:
          self.disableCondDeps()
        else: # if not True or False
          raise(TypeError(
            'conddeps must be a bool, not %s' % type(conddeps).__name__))
      
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
        if not self.cache['vc_files']:
          self.resetVCFiles()
        else: # if self.cache['vc_files']
          self.enableVCFiles()
      elif type(vc_files) is bool:
        if vc_files:
          self.enableVCFiles()
        else: # if not vc_files
          self.disableVCFiles
      
      # If user tries to apply conddeps and testflag['tests'] together
      if self.args['tests'] and self.args['conddeps']:
        raise(GLError(10, None))
    
    self.copyrights = True
    if symbolic:
      self.copyrights = False
    self.symbolic = symbolic
    self.lsymbolic = lsymbolic
    
  def __repr__(self):
    '''x.__repr__ <==> repr(x)'''
    return('<pygnulib.GLImport>')
    
  def rewrite_old_files(self, files):
    '''Replace auxdir, docbase, sourcebase, m4base and testsbase from default
    to their version from cache.'''
    if type(files) is not list:
      raise(TypeError(
        'files argument must has list type, not %s' % type(files).__name__))
    files = \
    [ # Begin to convert bytes to string
      file.decode(ENCS['default']) \
      if type(file) is bytes else file \
      for file in files
    ] # Finish to convert bytes to string
    for file in files:
      if type(file) is not string:
        raise(TypeError('each file must be a string instance'))
    files = sorted(set(files))
    auxdir = self.cache['auxdir']
    docbase = self.cache['docbase']
    sourcebase = self.cache['sourcebase']
    m4base = self.cache['m4base']
    testsbase = self.cache['testsbase']
    result = list()
    for file in files:
      if file.startswith('build-aux/'):
        result += [constants.substart('build-aux/', '%s/' % auxdir, file)]
      elif file.startswith('doc/'):
        result += [constants.substart('doc/', '%s/' % docbase, file)]
      elif file.startswith('lib/'):
        result += [constants.substart('lib/', '%s/' % sourcebase, file)]
      elif file.startswith('m4/'):
        result += [constants.substart('m4/', '%s/' % m4base, file)]
      elif file.startswith('tests=lib/'):
        result += [constants.substart('tests=lib/', '%s/' % testsbase, file)]
      elif file.startswith('tests/'):
        result += [constants.substart('tests/', '%s/' % testsbase, file)]
      elif file.startswith('top/'):
        result += [constants.substart('top/', '', file)]
      else: # file is not a special file
        result += [file]
    result = sorted(set(result))
    return(list(result))
    
  def rewrite_new_files(self, files):
    '''Replace auxdir, docbase, sourcebase, m4base and testsbase from default
    to their version from arguments.'''
    if type(files) is not list:
      raise(TypeError(
        'files argument must has list type, not %s' % type(files).__name__))
    files = \
    [ # Begin to convert bytes to string
      file.decode(ENCS['default']) \
      if type(file) is bytes else file \
      for file in files
    ] # Finish to convert bytes to string
    for file in files:
      if type(file) is not string:
        raise(TypeError('each file must be a string instance'))
    files = sorted(set(files))
    auxdir = self.args['auxdir']
    docbase = self.args['docbase']
    sourcebase = self.args['sourcebase']
    m4base = self.args['m4base']
    testsbase = self.args['testsbase']
    result = list()
    for file in files:
      if file.startswith('build-aux/'):
        result += [constants.substart('build-aux/', '%s/' % auxdir, file)]
      elif file.startswith('doc/'):
        result += [constants.substart('doc/', '%s/' % docbase, file)]
      elif file.startswith('lib/'):
        result += [constants.substart('lib/', '%s/' % sourcebase, file)]
      elif file.startswith('m4/'):
        result += [constants.substart('m4/', '%s/' % m4base, file)]
      elif file.startswith('tests=lib/'):
        result += [constants.substart('tests=lib/', '%s/' % testsbase, file)]
      elif file.startswith('tests/'):
        result += [constants.substart('tests/', '%s/' % testsbase, file)]
      elif file.startswith('top/'):
        result += [constants.substart('top/', '', file)]
      else: # file is not a special file
        result += [file]
    result = sorted(set(result))
    return(list(result))
    
  def actioncmd(self):
    '''Return command-line invocation comment.'''
    modules = self.getModules()
    avoids = self.getAvoids()
    destdir = self.getDestDir()
    localdir = self.getLocalDir()
    auxdir = self.getAuxDir()
    sourcebase = self.getSourceBase()
    m4base = self.getM4Base()
    docbase = self.getDocBase()
    pobase = self.getPoBase()
    testsbase = self.getTestsBase()
    testflags = self.getTestFlags()
    conddeps = self.checkCondDeps()
    libname = self.getLibName()
    lgpl = self.getLGPL()
    makefile = self.getMakefile()
    libtool = self.checkLibtool()
    macro_prefix = self.getMacroPrefix()
    witness_c_macro = self.getWitnessCMacro()
    podomain = self.getPoDomain()
    vc_files = self.checkVCFiles()
    verbose = self.getVerbosity()
    
    # Create command-line invocation comment.
    actioncmd = 'gnulib-tool --import'
    actioncmd += ' --dir=%s' % destdir
    if localdir:
      actioncmd += ' --localdir=%s' % localdir
    actioncmd += ' --lib=%s' % libname
    actioncmd += ' --source-base=%s' % sourcebase
    actioncmd += ' --m4-base=%s' % m4base
    if pobase:
      actioncmd += ' --po-base=%s' % pobase
    actioncmd += ' --doc-base=%s' % docbase
    actioncmd += ' --tests-base=%s' % testsbase
    actioncmd += ' --aux-dir=%s' % auxdir
    if self.checkTestFlag(TESTS['tests']):
      actioncmd += ' --with-tests'
    if self.checkTestFlag(TESTS['obsolete']):
      actioncmd += ' --with-obsolete'
    if self.checkTestFlag(TESTS['c++-test']):
      actioncmd += ' --with-c++-tests'
    if self.checkTestFlag(TESTS['longrunning-test']):
      actioncmd += ' --with-longrunning-tests'
    if self.checkTestFlag(TESTS['privileged-test']):
      actioncmd += ' --with-privileged-test'
    if self.checkTestFlag(TESTS['unportable-test']):
      actioncmd += ' --with-unportable-tests'
    if self.checkTestFlag(TESTS['all-test']):
      actioncmd += ' --with-all-tests'
    for module in avoids:
      actioncmd += ' --avoid=%s' % module
    if lgpl:
      if lgpl == True:
        actioncmd += ' --lgpl'
      else: # if lgpl != True
        actioncmd += ' --lgpl=%s' % lgpl
    if makefile:
      actioncmd += ' --makefile-name=%s' % makefile
    if conddeps:
      actioncmd += ' --conditional-dependencies'
    else: # if not conddeps
      actioncmd += ' --no-conditional-dependencies'
    if libtool:
      actioncmd += ' --libtool'
    else: # if not libtool
      actioncmd += ' --no-libtool'
    actioncmd += ' --macro-prefix=%s' % macro_prefix
    if podomain:
      actioncmd = ' --podomain=%s' % podomain
    if witness_c_macro:
      actioncmd += ' --witness_c_macro=%s' % witness_c_macro
    if vc_files == True:
      actioncmd += ' --vc-files'
    elif vc_files == False:
      actioncmd += ' --no-vc-files'
    actioncmd += ' ' # Add a space
    actioncmd += ' '.join(modules)
    return(actioncmd)
    
  def prepare(self):
    '''Make all preparations before the execution of the code. Returns tuple,
    which consists of two tables. The first table represents old files and the
    second represents new files.'''
    localdir = self.getLocalDir()
    destdir = self.getDestDir()
    auxdir = self.getAuxDir()
    sourcebase = self.getSourceBase()
    m4base = self.getM4Base()
    docbase = self.getDocBase()
    pobase = self.getPoBase()
    testsbase = self.getTestsBase()
    testflags = self.getTestFlags()
    conddeps = self.checkCondDeps()
    lgpl = self.getLGPL()
    verbose = self.getVerbosity()
    modulesystem = self.modulesystem
    ac_version = self.ac_version
    copyrights = self.copyrights
    basemodules = [modulesystem.find(module) for module in self.getModules()]
    avoids = [modulesystem.find(avoid) for avoid in self.getAvoids()]
    basemodules = sorted(set(basemodules))
    avoids = sorted(set(avoids))
    
    # Perform transitive closure.
    table = GLModuleTable(localdir, avoids, testflags, conddeps)
    finalmodules = table.transitive_closure(basemodules)
    
    # Show module list.
    if verbose >= 0:
      bold_on = ''
      bold_off = ''
      term = os.getenv('TERM')
      if term == 'xterm':
        bold_on = '\x1b[1m'
        bold_off = '\x1b[0m'
        bold_on = '' # Uncomment these lines to let diff work
        bold_off = '' # Uncomment these lines to let diff work
      print('Module list with included dependencies (indented):')
      for module in finalmodules:
        if str(module) in self.getModules():
          print('  %s%s%s' % (bold_on, module, bold_off))
        else: # if str(module) not in self.getModules()
          print('    %s' % module)
    
    # Separate modules into main_modules and tests_modules.
    modules = table.transitive_closure_separately(basemodules, finalmodules)
    main_modules, tests_modules = modules
    
    # Print main_modules and tests_modules.
    if verbose >= 1:
      print('Main module list:')
      for module in main_modules:
        print('  %s' % str(module))
      print('Tests-related module list:')
      for module in tests_modules:
        print('  %s' % str(module))
    
    # Determine whether a $testsbase/libtests.a is needed.
    libtests = False
    for module in tests_modules:
      files = module.getFiles(self.ac_version)
      for file in files:
        if file.startswith('lib/'):
          libtests = True
          break
    
    # Add dummy package if it is needed.
    main_modules = table.add_dummy(main_modules, auxdir, ac_version)
    if libtests: # if we need to use libtests.a
      tests_modules = table.add_dummy(tests_modules, auxdir, ac_version)
    
    # Check license incompatibilities.
    listing = list()
    compatibilities = dict()
    incompatibilities = string()
    compatibilities['all'] = ['GPLed build tool', 'public domain', 'unlimited',
      'unmodifiable license text']
    compatibilities[3] = ['LGPL', 'LGPLv2+', 'LGPLv3+']
    compatibilities[2] = ['LGPLv2+']
    if lgpl:
      for module in main_modules:
        license = module.getLicense()
        if license not in compatibilities['all']:
          if lgpl == 3 or lgpl == True:
            if license not in compatibilities[3]:
              listing.append(tuple([str(module), license]))
          elif lgpl == 2:
            if license not in compatibilities[2]:
              listing.append(tuple([str(module), license]))
      if listing:
        raise(GLError(11, listing))
    
    # Print notices from modules.
    for module in main_modules:
      notice = module.getNotice()
      if notice:
        print('Notice from module %s:' % str(module))
        pattern = compiler('^(.*?)$', re.S | re.M)
        notice = pattern.sub('  \\1', notice)
        print(notice)

    # Determine script to apply to imported library files.
    lgpl2gpl = '''
      s/GNU Lesser General/GNU General/g
      s/Lesser General Public License/General Public License/g
      s/GNU Library General/GNU General/g
      s/Library General Public License/General Public License/g
      s/version 2\\(.1\\)\\{0,1\\}\\([ ,]\\)/version 3\\2/g'''
    sed_transform_lib_file = string()
    if 'config-h' in [str(module) for module in main_modules]:
      sed_transform_lib_file += '''
        s/^#ifdef[\t ]*HAVE_CONFIG_H[\t ]*$/#if 1/
      '''
    sed_transform_main_lib_file = sed_transform_lib_file
    if copyrights:
      if lgpl: # if lgpl is enabled
        if lgpl == 3:
          sed_transform_main_lib_file += '''
            s/GNU General/GNU Lesser General/g
            s/General Public License/Lesser General Public License/g
            s/Lesser Lesser General Public License/Lesser General Public''' \
              +' License/g'
        elif lgpl == 2:
          sed_transform_main_lib_file += '''
            s/GNU General/GNU Lesser General/g
            s/General Public License/Lesser General Public License/g
            s/Lesser Lesser General Public License/Lesser General Public''' \
              +'''License/g
            s/version [23]\\([ ,]\\)/version 2.1\\1/g'''
      else: # if lgpl is disabled
        sed_transform_main_lib_file += lgpl2gpl

    # Determine script to apply to auxiliary files that go into $auxdir/.
    sed_transform_build_aux_file = string()
    if copyrights:
      sed_transform_build_aux_file += lgpl2gpl

    # Determine script to apply to library files that go into $testsbase/.
    sed_transform_testsrelated_lib_file = sed_transform_lib_file
    if copyrights:
      sed_transform_testsrelated_lib_file += lgpl2gpl
    
    # Determine the final file lists.
    main_filelist, tests_filelist = \
      table.filelist_separately(main_modules, tests_modules, ac_version)
    filelist = sorted(set(main_filelist +tests_filelist))
    print(len(filelist))
    exit()
    if not filelist:
      raise(GLError(12, None))
    
    # Print list of files.
    if verbose >= 0:
      print('File list:')
      for file in filelist:
        if file.startswith('tests=lib/'):
          rest = file[10:]
          print('  lib/%s -> tests/%s' % (rest, rest))
        else:
          print('  %s' % file)
    
    # Prepare basic filelist and basic old_files/new_files variables.
    filelist = sorted(set(filelist))
    new_files = filelist +['m4/gnulib-tool.m4']
    old_files = list(self.cache['files'])
    path = joinpath(self.getDestDir(), self.getM4Base(), 'gnulib-tool.m4')
    if isfile(path):
      old_files += [joinpath('m4', 'gnulib-tool.m4')]
    
    # Construct tables and transformers.
    transformers = dict()
    transformers['lib'] = string(sed_transform_lib_file)
    transformers['aux'] = string(sed_transform_build_aux_file)
    transformers['main'] = string(sed_transform_main_lib_file)
    transformers['tests'] = string(sed_transform_testsrelated_lib_file)
    old_table = list()
    new_table = list()
    for src in old_files:
      dest = self.rewrite_old_files([src])[-1]
      old_table += [tuple([src, dest])]
    for src in new_files:
      dest = self.rewrite_new_files([src])[-1]
      new_table += [tuple([src, dest])]
    old_table = sorted(set(old_table))
    new_table = sorted(set(new_table))
    
    # Return the result.
    result = tuple([filelist, old_table, new_table, transformers])
    return(result)
    
  def execute(self, filelist, old_files, new_files,
    transformers, dryrun=False):
    '''Perform operations on the lists of files, which are given in a special
    format except filelist argument. Such lists of files can be created using
    GLImport.prepare() function.'''
    modules = self.getModules()
    avoids = self.getAvoids()
    destdir = self.getDestDir()
    localdir = self.getLocalDir()
    auxdir = self.getAuxDir()
    sourcebase = self.getSourceBase()
    m4base = self.getM4Base()
    docbase = self.getDocBase()
    pobase = self.getPoBase()
    testsbase = self.getTestsBase()
    testflags = self.getTestFlags()
    conddeps = self.checkCondDeps()
    libname = self.getLibName()
    lgpl = self.getLGPL()
    makefile = self.getMakefile()
    libtool = self.checkLibtool()
    macro_prefix = self.getMacroPrefix()
    witness_c_macro = self.getWitnessCMacro()
    podomain = self.getPoDomain()
    vc_files = self.checkVCFiles()
    verbose = self.getVerbosity()
    
    # Store all files to files table.
    filetable = dict()
    filetable['all'] = sorted(set(filelist))
    filetable['old'] = sorted(set(old_files))
    filetable['new'] = sorted(set(new_files))
    filetable['added'] = list()
    filetable['removed'] = list()
    
    # Create all necessary directories.
    dirs = list()
    if pobase:
      dirs += [pobase]
    if [file for file in filetable['all'] if file.startswith('doc/')]:
      dirs += [docbase]
    dirs += [sourcebase, m4base, auxdir]
    dirs += [os.path.dirname(pair[1]) for pair in filetable['new']]
    dirs = sorted(set([joinpath(destdir, d) for d in dirs]))
    for directory in dirs:
      if not isdir(directory):
        if not dryrun:
            print('Creating directory %s' % directory)
            try: # Try to create directory
              os.makedirs(directory)
            except Exception as error:
              raise(GLError(13, directory))
        else: # if dryrun
          print('Create directory %s' % directory)
    
    # Create GLFileAssistant instance to process files.
    assistant = GLFileAssistant(destdir, localdir, transformers,
      self.symbolic, self.lsymbolic, dryrun)
    
    # Files which are in old_files and not in new_files.
    # They will be removed and added to filetable['removed'] list.
    old_files = [pair[1] for pair in filetable['old']]
    new_files = [pair[1] for pair in filetable['new']]
    files = [file for file in old_files if file not in new_files]
    for file in files:
      path = joinpath(destdir, file)
      if isfile(path) or os.path.islink(path):
        if not dryrun:
          print('Removing file %s (backup in %s~)' % (path, path))
          try: # Try to move file
            shutil.move(path, '%s~' % path)
          except Exception as error:
            raise(GLError(14, file))
        else: # if dryrun
          print('Remove file %s (backup in %s~)' % (path, path))
        filetable['removed'] += [file]
    
    # Files which are in new_files and not in old_files.
    # They will be added/updated and added to filetable['removed'] list.
    already_present = False
    pairs = [pair for pair in filetable['new'] if pair[1] not in old_files]
    path = '/home/ghostmansd/Проекты/added_files_py'
    file = codecs.open(path, 'wb', 'UTF-8')
    for pair in pairs:
      original = pair[0]
      rewritten = pair[1]
      file.write('%s\t%s\n' % (original, rewritten))
      assistant.setOriginal(original)
      assistant.setRewritten(rewritten)
      assistant.add_or_update(already_present)
    filetable['added'] += assistant.getFiles()
    
    # Files which are in new_files and old_files.
    # They will be added/updated and added to filetable['removed'] list.
    already_present = True
    pairs = [pair for pair in filetable['new'] if pair[1] in old_files]
    for pair in pairs:
      original = pair[0]
      rewritten = pair[1]
      assistant.setOriginal(original)
      assistant.setRewritten(rewritten)
      assistant.add_or_update(already_present)
    filetable['added'] += assistant.getFiles()
    
    # Create command-line invocation comment.
    actioncmd = self.actioncmd()
    
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
    
  def checkCondDeps(self):
    '''Check if user enabled cond. dependencies.'''
    return(self.args['conddeps'])
    
  def enableCondDeps(self):
    '''Enable cond. dependencies (may save configure time and object code).'''
    self.args['conddeps'] = True
    
  def disableCondDeps(self):
    '''Disable cond. dependencies (may save configure time and object code).'''
    self.args['conddeps'] = False
    
  def resetCondDeps(self):
    '''Reset cond. dependencies (may save configure time and object code).'''
    self.args['conddeps'] = self.cache['conddeps']
    
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
        'libname must be a string, not %s' % type(module).__name__))
    
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
      if auxdir:
        self.args['auxdir'] = joinpath(self.args['destdir'], auxdir)
      else: # if not auxdir
        self.args['auxdir'] = auxdir
    else: # if type of auxdir is not bytes or string
      raise(TypeError(
        'auxdir must be a string, not %s' % type(auxdir).__name__))
    
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
      if sourcebase:
        self.args['sourcebase'] = joinpath(self.args['destdir'], sourcebase)
      else: # if not sourcebase
        self.args['sourcebase'] = sourcebase
    else: # if type of sourcebase is not bytes or string
      raise(TypeError(
        'sourcebase must be a string, not %s' % type(sourcebase).__name__))
    
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
      if m4base:
        self.args['m4base'] = joinpath(self.args['destdir'], m4base)
      else: # if not m4base
        self.args['m4base'] = m4base
    else: # if type of m4base is not bytes or string
      raise(TypeError(
        'm4base must be a string, not %s' % type(m4base).__name__))
    
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
      if pobase:
        self.args['pobase'] = joinpath(self.args['destdir'], pobase)
      else: # if not pobase
        self.args['pobase'] = pobase
    else: # if type of pobase is not bytes or string
      raise(TypeError(
        'pobase must be a string, not %s' % type(pobase).__name__))
    
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
      if docbase:
        self.args['docbase'] = joinpath(self.args['destdir'], docbase)
      else: # if not docbase
        self.args['docbase'] = docbase
    else: # if type of docbase is not bytes or string
      raise(TypeError(
        'docbase must be a string, not %s' % type(docbase).__name__))
    
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
      if testsbase:
        self.args['testsbase'] = joinpath(self.args['destdir'], testsbase)
      else: # if not testsbase
        self.args['testsbase'] = testsbase
    else: # if type of testsbase is not bytes or string
      raise(TypeError(
        'testsbase must be a string, not %s' % type(testsbase).__name__))
    
  def resetTestsBase(self):
    '''Reset directory relative to destdir where unit tests are placed.
    Default value for this variable is 'tests').'''
    self.setTestsBase(self.cache['testsbase'])
    
  def getLGPL(self):
    '''Check for abort if modules aren't available under the LGPL.'''
    return(self.args['lgpl'])
    
  def setLGPL(self, lgpl):
    '''Abort if modules aren't available under the LGPL.'''
    if (type(lgpl) is int and 2 <= lgpl <= 3) or type(lgpl) is bool:
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
      if makefile:
        self.args['makefile'] = makefile
      else: # if not makefile
        self.args['makefile'] = 'Makefile.am'
    else: # if type of makefile is not bytes or string
      raise(TypeError(
        'makefile must be a string, not %s' % type(makefile).__name__))
    
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
        'podomain must be a string, not %s' % type(podomain).__name__))
    
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
    '''Reset update of the version control files and set it to None.'''
    self.args['vc_files'] = None
    
  def restoreVCFiles(self):
    '''Restore update of the version control files.'''
    if not self.cache['vc_files']:
      self.resetVCFiles()
    else: # if self.cache['vc_files']
      self.enableVCFiles()

