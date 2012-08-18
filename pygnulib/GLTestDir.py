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
import filecmp
import subprocess as sp
from . import constants
from .GLError import GLError
from .GLConfig import GLConfig
from .GLModuleSystem import GLModule
from .GLModuleSystem import GLModuleTable
from .GLModuleSystem import GLModuleSystem
from .GLFileSystem import GLFileSystem
from .GLFileSystem import GLFileAssistant
from .GLMakefileTable import GLMakefileTable
from .GLEmiter import GLEmiter


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
relpath = constants.relativize
string = constants.string
isabs = os.path.isabs
isdir = os.path.isdir
isfile = os.path.isfile
normpath = os.path.normpath


#===============================================================================
# Define GLTestDir class
#===============================================================================
class GLTestDir(object):
  '''GLTestDir class is used to create a scratch package with the given
  list of the modules.'''
  
  def __init__(self, config, testdir):
    '''GLTestDir.__init__(config) -> GLTestDir
    
    Create new GLTestDir instance.'''
    if type(config) is not GLConfig:
      raise(TypeError('config must be a GLConfig, not %s' % \
        type(config).__name__))
    if type(testdir) is bytes or type(testdir) is string:
      if type(testdir) is bytes:
        testdir = testdir.decode(ENCS['default'])
    self.config = config
    self.testdir = testdir
    if not os.path.exists(self.testdir):
      os.mkdir(self.testdir)
    self.emiter = GLEmiter(self.config)
    self.filesystem = GLFileSystem(self.config)
    self.modulesystem = GLModuleSystem(self.config)
    self.moduletable = GLModuleTable(self.config)
    self.assistant = GLFileAssistant(self.config)
    self.makefiletable = GLMakefileTable(self.config)
    
    # Subdirectory names.
    self.config.setSourceBase('gllib')
    self.config.setM4Base('glm4')
    self.config.setDocBase('gldoc')
    self.config.setTestsBase('gltests')
    self.config.setMacroPrefix('gl')
    self.config.resetPoBase()
    self.config.resetPoDomain()
    self.config.resetWitnessCMacro()
    self.config.resetVCFiles()
    
  def rewrite_files(self, files):
    '''GLTestDir.rewrite_files(files)
    
    Replace auxdir, docbase, sourcebase, m4base and testsbase from default
    to their version from config.'''
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
    auxdir = self.config['auxdir']
    docbase = self.config['docbase']
    sourcebase = self.config['sourcebase']
    m4base = self.config['m4base']
    testsbase = self.config['testsbase']
    result = list()
    for file in files:
      if file.startswith('build-aux/'):
        path = constants.substart('build-aux/', '%s/' % auxdir, file)
      elif file.startswith('doc/'):
        path = constants.substart('doc/', '%s/' % docbase, file)
      elif file.startswith('lib/'):
        path = constants.substart('lib/', '%s/' % sourcebase, file)
      elif file.startswith('m4/'):
        path = constants.substart('m4/', '%s/' % m4base, file)
      elif file.startswith('tests/'):
        path = constants.substart('tests/', '%s/' % testsbase, file)
      elif file.startswith('tests=lib/'):
        path = constants.substart('tests=lib/', '%s/' % testsbase, file)
      elif file.startswith('top/'):
        path = constants.substart('top/', '', file)
      else: # file is not a special file
        path = file
      result += [os.path.normpath(path)]
    result = sorted(set(result))
    return(list(result))
    
  def execute(self):
    '''GLTestDir.execute()
    
    Create a scratch package with the given modules.'''
    localdir = self.config['localdir']
    auxdir = self.config['auxdir']
    testflags = list(self.config['testflags'])
    sourcebase = self.config['sourcebase']
    m4base = self.config['m4base']
    pobase = self.config['pobase']
    docbase = self.config['docbase']
    testsbase = self.config['testsbase']
    libname = self.config['libname']
    libtool = self.config['libtool']
    witness_c_macro = self.config['witness_c_macro']
    symbolic = self.config['symbolic']
    lsymbolic = self.config['lsymbolic']
    single_configure = self.config['single_configure']
    include_guard_prefix = self.config['include_guard_prefix']
    macro_prefix = self.config['macro_prefix']
    verbose = self.config['verbosity']
    
    base_modules = [self.modulesystem.find(m) for m in self.config['modules']]
    if not base_modules:
      base_modules = self.modulesystem.list()
      base_modules = [self.modulesystem.find(m) for m in base_modules]
    # All modules together.
    # Except config-h, which breaks all modules which use HAVE_CONFIG_H.
    # Except ftruncate, mountlist, which abort the configuration on mingw.
    # Except lib-ignore, which leads to link errors when Sun C++ is used.
    base_modules = sorted(set(base_modules))
    base_modules = [module for module in base_modules if str(module) not in \
      ['config-h', 'ftruncate', 'mountlist', 'lib-ignore']]
    
    # When computing transitive closures, don't consider $module to depend on
    # $module-tests. Need this because tests are implicitly GPL and may depend
    # on GPL modules - therefore we don't want a warning in this case.
    saved_testflags = list(self.config['testflags'])
    self.config.disableTestFlag(TESTS['tests'])
    for requested_module in base_modules:
      requested_licence = requested_module.getLicense()
      # Here we use self.moduletable.transitive_closure([module]), not just
      # module.getDependencies, so that we also detect weird situations like
      # an LGPL module which depends on a GPLed build tool module which depends
      # on a GPL module.
      if requested_licence != 'GPL':
        modules = self.moduletable.transitive_closure([requested_module])
        for module in modules:
          license = module.getLicense()
          errormsg = 'module %s depends on a module ' % requested_module
          errormsg += 'with an incompatible license: %s\n' % module
          if requested_licence == 'GPLv2+':
            if license not in ['GPLv2+', 'LGPLv2+']:
              sys.stderr.write(errormsg)
          elif requested_licence in ['LGPL']:
            if license not in ['LGPL', 'LGPLv2+']:
              sys.stderr.write(errormsg)
          elif requested_licence in ['LGPLv2+']:
            if license not in ['LGPLv2+']:
              sys.stderr.write(errormsg)
    self.config.setTestFlags(saved_testflags)
    
    # Determine final module list.
    modules = self.moduletable.transitive_closure(base_modules)
    final_modules = list(modules)
    
    # Show final module list.
    if verbose >= 0:
      bold_on = ''
      bold_off = ''
      term = os.getenv('TERM')
      if term == 'xterm':
        bold_on = '\x1b[1m'
        bold_off = '\x1b[0m'
      print('Module list with included dependencies (indented):')
      for module in final_modules:
        if str(module) in self.config.getModules():
          print('  %s%s%s' % (bold_on, module, bold_off))
        else: # if str(module) not in self.config.getModules()
          print('    %s' % module)
    
    # Generate lists of the modules.
    if single_configure:
      # Determine main module list and tests-related module list separately.
      main_modules, tests_modules = \
        self.moduletable.transitive_closure_separately(
          base_modules, final_modules)
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
        files = module.getFiles()
        for file in files:
          if file.startswith('lib/'):
            libtests = True
            break
      if libtests:
        self.config.enableLibtests()
    
    if single_configure:
      # Add dummy package if it is needed.
      main_modules = self.moduletable.add_dummy(main_modules)
      if 'dummy' in [str(module) for module in main_modules]:
        main_modules = [m for m in main_modules if str(m) != 'dummy']
        dummy = self.modulesystem.find('dummy')
        main_modules = sorted(set(main_modules)) +[dummy]
      if libtests: # if we need to use libtests.a
        tests_modules = self.moduletable.add_dummy(tests_modules)
        if 'dummy' in [str(module) for module in tests_modules]:
          tests_modules = [m for m in tests_modules if str(m) != 'dummy']
          dummy = self.modulesystem.find('dummy')
          tests_modules = sorted(set(tests_modules)) +[dummy]
    else: # if not single_configure
      modules = self.moduletable.add_dummy(modules)
      if 'dummy' in [str(module) for module in modules]:
        modules = [m for m in modules if str(m) != 'dummy']
        dummy = self.modulesystem.find('dummy')
        modules = sorted(set(modules)) +[dummy]
    
    # Show banner notice of every module.
    if single_configure:
      for module in main_modules:
        notice = module.getNotice()
        if notice:
          print('Notice from module %s:' % str(module))
          pattern = compiler('^(.*?)$', re.S | re.M)
          notice = pattern.sub('  \\1', notice)
          print(notice)
    else: # if not single_configure
      for module in modules:
        notice = module.getNotice()
        if notice:
          print('Notice from module %s:' % str(module))
          pattern = compiler('^(.*?)$', re.S | re.M)
          notice = pattern.sub('  \\1', notice)
          print(notice)
    
    # Determine final file list.
    if single_configure:
      main_filelist, tests_filelist = \
        self.moduletable.filelist_separately(main_modules, tests_modules)
      filelist = sorted(set(main_filelist +tests_filelist))
    else: # if not single_configure
      filelist = self.moduletable.filelist(modules)
    
    # Print list of files.
    if verbose >= 0:
      print('File list:')
      for file in filelist:
        if file.startswith('tests=lib/'):
          rest = file[10:]
          print('  lib/%s -> tests/%s' % (rest, rest))
        else:
          print('  %s' % file)
    
    # Add files for which the copy in gnulib is newer than the one that
    # "automake --add-missing --copy" would provide.
    filelist += ['build-aux/config.guess', 'build-aux/config.sub']
    filelist = sorted(set(filelist))
    
    # Create directories.
    directories = [os.path.dirname(file) \
      for file in self.rewrite_files(filelist)]
    directories = sorted(set(directories))
    
    # Copy files or make symbolic links.
    filetable = list()
    for src in filelist:
      dest = self.rewrite_files([src])[-1]
      filetable += [tuple([dest, src])]
    for row in filetable:
      src = row[1]
      dest = row[0]
      destpath = joinpath(self.testdir, dest)
      dirname = os.path.dirname(destpath)
      if not isdir(dirname):
        os.makedirs(dirname)
      if src.startswith('tests=lib/'):
        src = constants.substart('tests=lib/', 'lib/', src)
      lookedup, flag = self.filesystem.lookup(src)
      if isfile(destpath):
        os.remove(destpath)
      if flag:
        shutil.copy(lookedup, destpath)
      else: # if not flag
        if symbolic or (lsymbolic and lookedup == joinpath(localdir, src)):
          constants.link_relative(lookedup, destpath)
        else:
          shutil.copy(lookedup, destpath)
    
    # Create $sourcebase/Makefile.am.
    for_test = True
    directory = joinpath(self.testdir, sourcebase)
    if not isdir(directory):
      os.mkdir(directory)
    destfile = joinpath(directory, 'Makefile.am')
    if single_configure:
      emit, uses_subdirs = self.emiter.lib_Makefile_am(destfile, main_modules,
        self.moduletable, self.makefiletable, '', for_test)
    else: # if not single_configure
      emit, uses_subdirs = self.emiter.lib_Makefile_am(destfile, modules,
        self.moduletable, self.makefiletable, '', for_test)
    with codecs.open(destfile, 'wb', 'UTF-8') as file:
      file.write(emit)
    any_uses_subdirs = uses_subdirs
    
    # Create $m4base/Makefile.am.
    directory = joinpath(self.testdir, m4base)
    if not isdir(directory):
      os.mkdir(directory)
    destfile = joinpath(directory, 'Makefile.am')
    emit = string()
    emit += '## Process this file with automake to produce Makefile.in.\n\n'
    emit += 'EXTRA_DIST =\n'
    for file in filelist:
      if file.startswith('m4/'):
        file = constants.substart('m4/', '', file)
        emit += 'EXTRA_DIST += %s\n' % file
    emit = constants.nlconvert(emit)
    if type(emit) is bytes:
      emit = emit.decode(ENCS['default'])
    with codecs.open(destfile, 'wb', 'UTF-8') as file:
      file.write(emit)
    
    subdirs = [sourcebase, m4base]
    subdirs_with_configure_ac = list()
    
    testsbase_appened = False
    inctests = self.config.checkTestFlag(TESTS['tests'])
    if inctests:
      directory = joinpath(self.testdir, testsbase)
      if not isdir(directory):
        os.mkdir(directory)
      if single_configure:
        # Create $testsbase/Makefile.am.
        destfile = joinpath(directory, 'Makefile.am')
        print(repr(destfile))
        witness_macro = '%stests_WITNESS' % macro_prefix
        emit, uses_subdirs = self.emiter.tests_Makefile_am(destfile,
          tests_modules, self.makefiletable, witness_macro, for_test)
        with codecs.open(destfile, 'wb', 'UTF-8') as file:
          file.write(emit)
      else: # if not single_configure
        # Create $testsbase/Makefile.am.
        destfile = joinpath(directory, 'Makefile.am')
        libtests = False
        self.config.disableLibtests()
        emit, uses_subdirs = self.emiter.tests_Makefile_am(destfile,
          modules, self.makefiletable, '', for_test)
        with codecs.open(destfile, 'wb', 'UTF-8') as file:
          file.write(emit)
        # Viewed from the $testsbase subdirectory, $auxdir is different.
        emit = string()
        saved_auxdir = self.config['auxdir']
        testsbase = '%s/' % os.path.normpath(testsbase)
        counter = int()
        auxdir = string()
        finish = (len(testsbase.split('/')) -1)
        while counter < finish:
          auxdir += '../'
          counter += 1
        auxdir = os.path.normpath(joinpath(auxdir, saved_auxdir))
        testsbase = os.path.normpath(testsbase)
        self.config.setAuxDir(auxdir)
        # Create $testsbase/configure.ac.
        emit += '# Process this file with autoconf '
        emit += 'to produce a configure script.\n'
        emit += 'AC_INIT([dummy], [0])\n'
        emit += 'AC_CONFIG_AUX_DIR([%s])\n' % auxdir
        emit += 'AM_INIT_AUTOMAKE\n\n'
        emit += 'AC_CONFIG_HEADERS([config.h])\n\n'
        emit += 'AC_PROG_CC\n'
        emit += 'AC_PROG_INSTALL\n'
        emit += 'AC_PROG_MAKE_SET\n'
        emit += 'gl_PROG_AR_RANLIB\n\n'
        if uses_subdirs:
          emit += 'AM_PROG_CC_C_O\n\n'
        snippets = list()
        for module in modules:
          if str(module) in ['gnumakefile', 'maintainer-makefile']:
            # These are meant to be used only in the top-level directory.
            pass
          else: # if str(module) not in ['gnumakefile', 'maintainer-makefile']
            snippet = module.getAutoconfSnippet_Early()
            lines = [line for line in snippet.split('\n') if line.strip()]
            snippet = '\n'.join(lines)
            pattern = compiler('AC_REQUIRE\\(\\[([^()].*?)\\]\\)', re.S | re.M)
            snippet = pattern.sub('\\1', snippet)
            snippet = snippet.strip()
            snippets += [snippet]
        snippets = [snippet for snippet in snippets if snippet.strip()]
        emit += '%s\n' % '\n'.join(snippets)
        if libtool:
          emit += 'LT_INIT([win32-dll])\n'
          emit += 'LT_LANG([C++])\n'
          emit += 'AM_CONDITIONAL([GL_COND_LIBTOOL], [true])\n'
          emit += 'gl_cond_libtool=true\n'
        else: # if not libtool
          emit += 'AM_CONDITIONAL([GL_COND_LIBTOOL], [false])\n'
          emit += 'gl_cond_libtool=false\n'
          emit += 'gl_libdeps=\n'
          emit += 'gl_ltlibdeps=\n'
        # Wrap the set of autoconf snippets into an autoconf macro that is then
        # invoked. This is needed because autoconf does not support AC_REQUIRE
        # at the top level:
        #   error: AC_REQUIRE(gt_CSHARPCOMP): cannot be used outside of an
        #     AC_DEFUN'd macro
        # but we want the AC_REQUIRE to have its normal meaning (provide one
        # expansion of the required macro before the current point, and only
        # one expansion total).
        emit += 'AC_DEFUN([gl_INIT], [\n'
        replace_auxdir = True
        emit += "gl_m4_base='../%s'\n" % m4base
        emit += self.emiter.initmacro_start(macro_prefix)
        # We don't have explicit ordering constraints between the various
        # autoconf snippets. It's cleanest to put those of the library before
        # those of the tests.
        emit += "gl_source_base='../%s'\n" % sourcebase
        emit += self.emiter.autoconfSnippets(modules,
          self.moduletable, self.assistant, 1, False, False, False,
          replace_auxdir)
        emit += "gl_source_base='.'"
        emit += self.emiter.autoconfSnippets(modules,
          self.moduletable, self.assistant, 2, False, False, False,
          replace_auxdir)
        emit += self.emiter.initmacro_end(macro_prefix)
        # _LIBDEPS and _LTLIBDEPS variables are not needed if this library is
        # created using libtool, because libtool already handles the
        # dependencies.
        if not libtool:
          libname_upper = libname.upper().replace('-', '_')
          emit += '  %s_LIBDEPS="$gl_libdeps"\n' % libname_upper
          emit += '  AC_SUBST([%s_LIBDEPS])\n' % libname_upper
          emit += '  %s_LTLIBDEPS="$gl_ltlibdeps"\n' % libname_upper
          emit += '  AC_SUBST([%s_LTLIBDEPS])\n' % libname_upper
        emit += '])\n'
        # FIXME use $sourcebase or $testsbase?
        emit += self.emiter.initmacro_done(macro_prefix, sourcebase)
        emit += '\ngl_INIT\n\n'
        # Usually $testsbase/config.h will be a superset of config.h. Verify
        # this by "merging" config.h into $testsbase/config.h; look out for gcc
        # warnings.
        emit += 'AH_TOP([#include \"../config.h\"])\n\n'
        emit += 'AC_CONFIG_FILES([Makefile])\n'
        emit += 'AC_OUTPUT\n'
        emit = constants.nlconvert(emit)
        if type(emit) is bytes:
          emit = emit.decode(ENCS['default'])
        path = joinpath(self.testdir, testsbase, 'configure.ac')
        with codecs.open(path, 'wb', 'UTF-8') as file:
          file.write(emit)
        
        # Restore changed variables.
        self.config.setAuxDir(saved_auxdir)
        auxdir = self.config['auxdir']
        subdirs_with_configure_ac += [testsbase]
      
      subdirs += [testsbase]
      testsbase_appened = True
    
    # Create Makefile.am.
    emit = string()
    emit += '## Process this file with automake to produce Makefile.in.\n\n'
    emit += 'AUTOMAKE_OPTIONS = 1.5 foreign\n\n'
    emit += 'SUBDIRS = %s\n\n' % ' '.join(subdirs)
    emit += 'ACLOCAL_AMFLAGS = -I %s\n' % m4base
    emit = constants.nlconvert(emit)
    if type(emit) is bytes:
      emit = emit.decode(ENCS['default'])
    path = joinpath(self.testdir, 'Makefile.am')
    with codecs.open(path, 'wb', 'UTF-8') as file:
      file.write(emit)
    
    # Create configure.ac
    emit = string()
    emit += '# Process this file with autoconf '
    emit += 'to produce a configure script.\n'
    emit += 'AC_INIT([dummy], [0])\n'
    if auxdir != '.':
      emit += 'AC_CONFIG_AUX_DIR([%s])\n' % auxdir
    emit += 'AM_INIT_AUTOMAKE\n\n'
    emit += 'AC_CONFIG_HEADERS([config.h])\n\n'
    emit += 'AC_PROG_CC\n'
    emit += 'AC_PROG_INSTALL\n'
    emit += 'AC_PROG_MAKE_SET\n\n'
    emit += '# For autobuild.\n'
    emit += 'AC_CANONICAL_BUILD\n'
    emit += 'AC_CANONICAL_HOST\n\n'
    emit += 'm4_pattern_forbid([^gl_[A-Z]])dnl the gnulib macro namespace\n'
    emit += 'm4_pattern_allow([^gl_ES$])dnl a valid locale name\n'
    emit += 'm4_pattern_allow([^gl_LIBOBJS$])dnl a variable\n'
    emit += 'm4_pattern_allow([^gl_LTLIBOBJS$])dnl a variable\n\n'
    emit += 'gl_PROG_AR_RANLIB\n\n'
    if any_uses_subdirs:
      emit += 'AM_PROG_CC_C_O\n'
    snippets = list()
    for module in final_modules:
      if single_configure:
        solution = True
      else: # if not single_configure
        solution = module.isNonTests()
      if solution:
        snippet = module.getAutoconfSnippet_Early()
        lines = [line for line in snippet.split('\n') if line.strip()]
        snippet = '\n'.join(lines)
        pattern = compiler('AC_REQUIRE\\(\\[([^()].*?)\\]\\)', re.S | re.M)
        snippet = pattern.sub('\\1', snippet)
        snippet = snippet.strip()
        snippets += [snippet]
    snippets = [snippet for snippet in snippets if snippet.strip()]
    emit += '%s\n' % '\n'.join(snippets)
    if libtool:
      emit += 'LT_INIT([win32-dll])\n'
      emit += 'LT_LANG([C++])\n'
      emit += 'AM_CONDITIONAL([GL_COND_LIBTOOL], [true])\n'
      emit += 'gl_cond_libtool=true\n'
    else: # if not libtool
      emit += 'AM_CONDITIONAL([GL_COND_LIBTOOL], [false])\n'
      emit += 'gl_cond_libtool=false\n'
      emit += 'gl_libdeps=\n'
      emit += 'gl_ltlibdeps=\n'
    # Wrap the set of autoconf snippets into an autoconf macro that is then
    # invoked. This is needed because autoconf does not support AC_REQUIRE
    # at the top level:
    #   error: AC_REQUIRE(gt_CSHARPCOMP): cannot be used outside of an
    #     AC_DEFUN'd macro
    # but we want the AC_REQUIRE to have its normal meaning (provide one
    # expansion of the required macro before the current point, and only one
    # expansion total).
    emit += 'AC_DEFUN([gl_INIT], [\n'
    if auxdir != 'build-aux':
      replace_auxdir = True
    else: # auxdir == 'build-aux'
      replace_auxdir = False
    emit += 'gl_m4_base=\'%s\'\n' % m4base
    emit += self.emiter.initmacro_start(macro_prefix)
    emit += 'gl_source_base=\'%s\'\n' % sourcebase
    if single_configure:
      emit += self.emiter.autoconfSnippets(main_modules, self.moduletable,
        self.assistant, 0, False, False, False, replace_auxdir)
    else: # if not single_configure
      emit += self.emiter.autoconfSnippets(modules, self.moduletable,
        self.assistant, 1, False, False, False, replace_auxdir)
    emit += self.emiter.initmacro_end(macro_prefix)
    if single_configure:
      emit += '  gltests_libdeps=\n'
      emit += '  gltests_ltlibdeps=\n'
      emit += self.emiter.initmacro_start('%stests' % macro_prefix)
      emit += '  gl_source_base=\'%s\'\n' % testsbase
      # Define a tests witness macro.
      emit += '  %stests_WITNESS=IN_GNULIB_TESTS\n' % macro_prefix
      emit += '  AC_SUBST([%stests_WITNESS])\n' % macro_prefix
      emit += '  gl_module_indicator_condition=$%stests_WITNESS\n' % \
        macro_prefix
      emit += '  m4_pushdef([gl_MODULE_INDICATOR_CONDITION], '
      emit += '[$gl_module_indicator_condition])\n'
      snippets = self.emiter.autoconfSnippets(tests_modules, self.moduletable,
        self.assistant, 1, True, False, False, replace_auxdir)
      emit += snippets.strip()
      emit += '  m4_popdef([gl_MODULE_INDICATOR_CONDITION])\n'
      emit += self.emiter.initmacro_end('%stests' % macro_prefix)
    # _LIBDEPS and _LTLIBDEPS variables are not needed if this library is
    # created using libtool, because libtool already handles the dependencies.
    if not libtool:
      libname_upper = libname.upper().replace('-', '_')
      emit += '  %s_LIBDEPS="$gl_libdeps"\n' % libname_upper
      emit += '  AC_SUBST([%s_LIBDEPS])\n' % libname_upper
      emit += '  %s_LTLIBDEPS="$gl_ltlibdeps"\n' % libname_upper
      emit += '  AC_SUBST([%s_LTLIBDEPS])\n' % libname_upper
    if single_configure and libtests:
      emit += '  LIBTESTS_LIBDEPS="$gltests_libdeps"\n'
      emit += '  AC_SUBST([LIBTESTS_LIBDEPS])\n'
    emit += '])\n'
    emit += self.emiter.initmacro_done(macro_prefix, sourcebase)
    if single_configure:
      emit += self.emiter.initmacro_done('%stests' % macro_prefix, testsbase)
    emit += '\ngl_INIT\n\n'
    if subdirs_with_configure_ac:
      if single_configure:
        emit += 'AC_CONFIG_SUBDIRS([%s])\n' % \
          ' '.join(subdirs_with_configure_ac[:-1])
      else: # if not single_configure
        emit += 'AC_CONFIG_SUBDIRS([%s])\n' % \
          ' '.join(subdirs_with_configure_ac)
    makefiles = ['Makefile']
    for directory in subdirs:
      # For subdirs that have a configure.ac by their own, it's the subdir's
      # configure.ac which creates the subdir's Makefile.am, not this one.
      makefiles += [joinpath(directory, 'Makefile')]
    if not single_configure:
      makefiles = makefiles[:-1]
    emit += 'AC_CONFIG_FILES([%s])\n' % ' '.join(makefiles)
    emit += 'AC_OUTPUT\n'
    path = joinpath(self.testdir, 'configure.ac')
    with codecs.open(path, 'wb', 'UTF-8') as file:
      file.write(emit)
    
    # Create autogenerated files.
    os.chdir(self.testdir)
    # Do not use "${AUTORECONF} --force --install", because it may invoke
    # autopoint, which brings in older versions of some of our .m4 files.
    # gettext
    if isfile(joinpath(m4base, 'gettext.m4')):
      args = [UTILS['autopoint'], '--force']
      constants.execute(args, verbose)
      for src in os.listdir(m4base):
        src = joinpath(m4base, src)
        if src.endswith('.m4~'):
          dest = src[:-1]
          if isfile(dest):
            os.remove(dest)
          shutil.move(src, dest)
    # libtoolize
    if libtool:
      args = [UTILS['libtoolize'], '--copy']
      constants.execute(args, verbose)
    # aclocal
    args = [UTILS['aclocal'], '-I', m4base]
    constants.execute(args, verbose)
    if not isdir('build-aux'):
      os.mkdir('build-aux')
    # autoconf
    args = [UTILS['autoconf']]
    constants.execute(args, verbose)
    # autoheader
    args = [UTILS['autoheader']]
    constants.execute(args, verbose)
    # automake
    args = [UTILS['automake'], '--add-missing', '--copy']
    constants.execute(args, verbose)