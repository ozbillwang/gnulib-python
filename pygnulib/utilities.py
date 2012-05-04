#!/usr/bin/python
'''This script is a part of PyGNULib module for gnulib.'''

################################################################################
# Define global imports
################################################################################
import os
import re
import sys
import subprocess as sp
from . import constants


################################################################################
# Define module information
################################################################################
__author__ = constants.__author__
__license__ = constants.__license__
__copyright__ = constants.__copyright__
__version__ = constants.__version__


################################################################################
# Define global constants
################################################################################
NoneType = type(None)
string = constants.string
APP = constants.APP
DIRS = constants.DIRS
ENCS = constants.ENCS
UTILS = constants.UTILS
FILES = constants.FILES
MODES = constants.MODES


################################################################################
# Define GNULibInfo class
################################################################################
class GNULibInfo:
  '''This class is used to get fromatted information about gnulib-tool.
  This information is mainly used in stdout messages, but can be used
  anywhere else. The return values are not the same as for the module,
  but still depends on them.'''
  
  def package(self):
    '''Return formatted string which contains name of the package.'''
    result = 'GNU gnulib'
    return(result)
    
  def authors(self):
    '''Return formatted string which contains authors.
    The special __author__ variable is used (type is list).'''
    result = string() # Empty string
    for item in __author__:
      if item == __author__[-2]:
        result += '%s ' % item
      elif item == __author__[-1]:
        result += 'and %s' % item
      else:
        result += '%s, ' % item
    return(result)
    
  def license(self):
    '''Return formatted string which contains license and its description.'''
    result = 'License GPLv3+: GNU GPL version 3 or later'
    result += ' <http://gnu.org/licenses/gpl.html>\n'
    result += 'This is free software: you are free'
    result += ' to change and redistribute it.\n'
    result += 'There is NO WARRANTY, to the extent permitted by law.'
    return(result)
    
  def copyright(self):
    '''Return formatted string which contains copyright.
    The special __copyright__ variable is used (type is str).'''
    result = 'Copyright (C) %s' % __copyright__
    return(result)
    
  def date(self):
    '''Return formatted string which contains date and time in GMT format.'''
    if os.path.exists(DIRS['git']) and os.path.isdir(DIRS['git']):
      counter = int() # Create counter
      result = string() # Create string
      args = ['git', 'log', FILES['changelog']]
      proc1 = sp.Popen(args,stdout=sp.PIPE)
      proc2 = sp.Popen(['head'],
        stdin=proc1.stdout, stdout=sp.PIPE)
      proc1.stdout.close()
      while counter <= 2:
        result += string(proc2.stdout.readline(), ENCS['shell'])
        counter += 1
      # Get date as "Fri Mar 21 07:16:51 2008 -0600" from string
      pattern = re.compile('Date:[\t ]*(.*?)\n')
      result = pattern.findall(result)[0]
      # Turn "Fri Mar 21 07:16:51 2008 -0600" into "Mar 21 2008 07:16:51 -0600"
      pattern = re.compile('^[^ ]* ([^ ]*) ([0-9]*) ([0-9:]*) ([0-9]*) ')
      result = pattern.sub('\\1 \\2 \\4 \\3 ', result)
      # Use GNU date to compute the time in GMT
      args = ['date', '-d', result, '-u', '+%Y-%m-%d %H:%M:%S']
      proc = sp.check_output(args)
      result = string(proc, ENCS['shell'])
      result = result.rstrip(os.linesep)
      return(result)
    
  def help(self):
    '''Show help message.'''
    result = '''\
Usage: gnulib-tool --list
       gnulib-tool --find filename
       gnulib-tool --import [module1 ... moduleN]
       gnulib-tool --add-import [module1 ... moduleN]
       gnulib-tool --remove-import [module1 ... moduleN]
       gnulib-tool --update
       gnulib-tool --create-testdir --dir=directory [module1 ... moduleN]
       gnulib-tool --create-megatestdir --dir=directory [module1 ... moduleN]
       gnulib-tool --test --dir=directory module1 ... moduleN
       gnulib-tool --megatest --dir=directory [module1 ... moduleN]
       gnulib-tool --extract-description module
       gnulib-tool --extract-comment module
       gnulib-tool --extract-status module
       gnulib-tool --extract-notice module
       gnulib-tool --extract-applicability module
       gnulib-tool --extract-filelist module
       gnulib-tool --extract-dependencies module
       gnulib-tool --extract-autoconf-snippet module
       gnulib-tool --extract-automake-snippet module
       gnulib-tool --extract-include-directive module
       gnulib-tool --extract-link-directive module
       gnulib-tool --extract-license module
       gnulib-tool --extract-maintainer module
       gnulib-tool --extract-tests-module module
       gnulib-tool --copy-file file [destination]

Operation modes:

      --list                print the available module names
      --find                find the modules which contain the specified file
      --import              import the given modules into the current package
      --add-import          augment the list of imports from gnulib into the
                            current package, by adding the given modules;
                            if no modules are specified, update the current
                            package from the current gnulib
      --remove-import       reduce the list of imports from gnulib into the
                            current package, by removing the given modules
      --update              update the current package, restore files omitted
                            from version control
      --create-testdir      create a scratch package with the given modules
                            (pass --with-tests to include the unit tests)
      --create-megatestdir  create a mega scratch package with the given modules
                            one by one and all together
                            (pass --with-tests to include the unit tests)
      --test                test the combination of the given modules
                            (pass --with-tests to include the unit tests)
                            (recommended to use CC=\"gcc -Wall\" here)
      --megatest            test the given modules one by one and all together
                            (pass --with-tests to include the unit tests)
                            (recommended to use CC=\"gcc -Wall\" here)
      --extract-description        extract the description
      --extract-comment            extract the comment
      --extract-status             extract the status (obsolete etc.)
      --extract-notice             extract the notice or banner
      --extract-applicability      extract the applicability
      --extract-filelist           extract the list of files
      --extract-dependencies       extract the dependencies
      --extract-autoconf-snippet   extract the snippet for configure.ac
      --extract-automake-snippet   extract the snippet for library makefile
      --extract-include-directive  extract the #include directive
      --extract-link-directive     extract the linker directive
      --extract-license            report the license terms of the source files
                                   under lib/
      --extract-maintainer         report the maintainer(s) inside gnulib
      --extract-tests-module       report the unit test module, if it exists
      --copy-file                  copy a file that is not part of any module
      --help                Show this help text.
      --version             Show version and authorship information.

General options:

      --dir=DIRECTORY       Specify the target directory.
                            For --import, this specifies where your
                            configure.ac can be found.  Defaults to current
                            directory.
      --local-dir=DIRECTORY  Specify a local override directory where to look
                            up files before looking in gnulib's directory.
      --cache-modules       Enable module caching optimization.
      --no-cache-modules    Disable module caching optimization.
      --verbose             Increase verbosity. May be repeated.
      --quiet               Decrease verbosity. May be repeated.

Options for --import, --add/remove-import, --update:

      --dry-run             Only print what would have been done.

Options for --import, --add/remove-import,
            --create-[mega]testdir, --[mega]test:

      --with-tests          Include unit tests for the included modules.
      --with-obsolete       Include obsolete modules when they occur among the
                            dependencies. By default, dependencies to obsolete
                            modules are ignored.
      --with-c++-tests      Include even unit tests for C++ interoperability.
      --with-longrunning-tests
                            Include even unit tests that are long-runners.
      --with-privileged-tests
                            Include even unit tests that require root
                            privileges.
      --with-unportable-tests
                            Include even unit tests that fail on some platforms.
      --with-all-tests      Include all kinds of problematic unit tests.
      --avoid=MODULE        Avoid including the given MODULE. Useful if you
                            have code that provides equivalent functionality.
                            This option can be repeated.
      --conditional-dependencies
                            Support conditional dependencies (may save configure
                            time and object code).
      --no-conditional-dependencies
                            Don't use conditional dependencies.
      --libtool             Use libtool rules.
      --no-libtool          Don't use libtool rules.

Options for --import, --add/remove-import:

      --lib=LIBRARY         Specify the library name.  Defaults to 'libgnu'.
      --source-base=DIRECTORY
                            Directory relative to --dir where source code is
                            placed (default \"lib\").
      --m4-base=DIRECTORY   Directory relative to --dir where *.m4 macros are
                            placed (default \"m4\").
      --po-base=DIRECTORY   Directory relative to --dir where *.po files are
                            placed (default \"po\").
      --doc-base=DIRECTORY  Directory relative to --dir where doc files are
                            placed (default \"doc\").
      --tests-base=DIRECTORY
                            Directory relative to --dir where unit tests are
                            placed (default \"tests\").
      --aux-dir=DIRECTORY   Directory relative to --dir where auxiliary build
                            tools are placed (default comes from configure.ac).
      --lgpl[=2|=3]         Abort if modules aren't available under the LGPL.
                            Also modify license template from GPL to LGPL.
                            The version number of the LGPL can be specified;
                            the default is currently LGPLv3.
      --makefile-name=NAME  Name of makefile in automake syntax in the
                            source-base and tests-base directories
                            (default \"Makefile.am\").
      --macro-prefix=PREFIX  Specify the prefix of the macros 'gl_EARLY' and
                            'gl_INIT'. Default is 'gl'.
      --po-domain=NAME      Specify the prefix of the i18n domain. Usually use
                            the package name. A suffix '-gnulib' is appended.
      --witness-c-macro=NAME  Specify the C macro that is defined when the
                            sources in this directory are compiled or used.
      --vc-files            Update version control related files.
      --no-vc-files         Don't update version control related files
                            (.gitignore and/or .cvsignore).
      --no-changelog        Don't update or create ChangeLog files.

Options for --create-[mega]testdir, --[mega]test:

      --without-c++-tests   Exclude unit tests for C++ interoperability.
      --without-longrunning-tests
                            Exclude unit tests that are long-runners.
      --without-privileged-tests
                            Exclude unit tests that require root privileges.
      --without-unportable-tests
                            Exclude unit tests that fail on some platforms.
      --single-configure    Generate a single configure file, not a separate
                            configure file for the tests directory.

Options for --import, --add/remove-import, --update,
            --create-[mega]testdir, --[mega]test:

  -s, --symbolic, --symlink Make symbolic links instead of copying files.
      --local-symlink       Make symbolic links instead of copying files, only
                            for files from the local override directory.

Options for --import, --add/remove-import, --update:

  -S, --more-symlinks       Make symbolic links instead of copying files, and
                            don't replace copyright notices.

Report bugs to <bug-gnulib@gnu.org>.'''
    return(result)
    
  def version(self):
    '''Return formatted string which contains git or CVS version.'''
    if os.path.exists(DIRS['git']) and os.path.isdir(DIRS['git']):
      version_gen = os.path.join(DIRS['build-aux'], 'git-version-gen')
      args = [version_gen, DIRS['root']]
      proc = sp.check_output(args)
      result = string(proc, ENCS['shell'])
      result = result.rstrip(os.linesep)
      return(result)


################################################################################
# Define GNULibMode class
################################################################################
class GNULibMode:
  '''GNULibMode class is used to create basic mode instance. All the methods
  which can be applied to GNULibMode can be applied to any other mode.
  GNULibMode is the parent for all the other modes, so every new mode must be
  based on this class.'''
  
  def __init__(self):
    '''Create GNULibMode instance.'''
    self._mode_ = None
    self._destdir_ = os.getcwd()
    if type(self._destdir_) is bytes:
      self._destdir_ = string(os.getcwd(), ENCS['system'])
    self._localdir_ = string()
    self._modcache_ = True
    self._verbose_ = int()
    
  def getDestDir(self):
    '''Return the target directory. For --import, this specifies where your
    configure.ac can be found. Defaults to current directory.'''
    return(self._destdir_)
    
  def setDestDir(self, directory):
    '''Specify the target directory. For --import, this specifies where your
    configure.ac can be found. Defaults to current directory.'''
    if type(directory) is bytes or type(directory) is string:
      if type(directory) is bytes:
        self._destdir_ = string(directory, ENCS['shell'])
      elif type(directory) is string:
        self._destdir_ = directory
    else:
      raise(TypeError(
        'argument must be a string, not %s' % type(directory).__name__))
    
  def getLocalDir(self):
    '''Return a local override directory where to look up files before looking
    in gnulib's directory.'''
    return(self._localdir_)
    
  def setLocalDir(self, directory):
    '''Specify a local override directory where to look up files before looking
    in gnulib's directory.'''
    if type(directory) is bytes or type(directory) is string:
      if type(directory) is bytes:
        self._localdir_ = string(directory, ENCS['shell'])
      elif type(directory) is string:
        self._localdir_ = directory
    else:
      raise(TypeError(
        'argument must be a string, not %s' % type(directory).__name__))
    
  def checkModuleCaching(self):
    '''Get status of module caching optimization.'''
    return(self._modcache_)
    
  def enableModuleCaching(self):
    '''Enable module caching optimization.'''
    self._modcache_ = True
    
  def disableModuleCaching(self):
    '''Disable module caching optimization.'''
    self._modcache_ = False
    
  def getVerbosity(self):
    '''Get verbosity level.'''
    return(self._verbose_)
    
  def decreaseVerbosity(self):
    '''Decrease verbosity level.'''
    if self._verbose_ > MODES['verbose-min']:
      self._verbose_ -= 1
    
  def increaseVerbosity(self):
    '''Increase verbosity level.'''
    if self._verbose_ < MODES['verbose-max']:
      self._verbose_ += 1
    
  def setVerbosity(self, verbose):
    '''Set verbosity level to verbose, where -2 <= verbose <= 2.
    If verbosity level is less than -2, verbosity level will be set to -2.
    If verbosity level is greater than 2, verbosity level will be set to 2.'''
    if type(verbose) is int:
      if MODES['verbose-min'] <= verbose <= MODES['verbose-max']:
        self._verbose_ = verbose
      elif verbose < MODES['verbose-min']:
        self._verbose_ = MODES['verbose-min']
      elif verbose > MODES['verbose-max']:
        self._verbose_ = MODES['verbose-max']
    else:
      raise(TypeError(
        'argument must be a string, not %s' % type(module).__name__))


################################################################################
# Define GNULibList class
################################################################################
class GNULibList(GNULibMode):
  '''GNULibList class is used to get list of all modules.'''
  
  def run(self):
    '''Execute GNULibList.'''
    args = ['find', 'modules', '-type', 'f', '-print']
    proc = sp.check_output(args)
    result = string(proc, ENCS['shell'])


################################################################################
# Define GNULibImport class
################################################################################
class GNULibImport(GNULibMode):
  '''GNULibImport class is used to provide methods for --import, --add-import
  and --remove-import actions.'''
  
  def __init__(self):
    '''Create GNULibImport instance.'''
    self._mode_ = None
    self._destdir_ = os.getcwd()
    if type(self._destdir_) is bytes:
      self._destdir_ = string(os.getcwd(), ENCS['system'])
    self._localdir_ = string()
    self._modcache_ = True
    self._verbose_ = int()
    self._imports_ = list()
    self._dryrun_ = bool()
    self._testflags_ = list()
    self._testflags_.append(1)
    self._avoids_ = list()
    self._dependencies_ = False
    self._libtool_ = False
    self._library_ = 'libgnu'
    self._sourcebase_ = 
    
  def addImport(self, module):
    '''Import the given module into the current package.'''
    if type(module) is bytes or type(module) is string:
      if type(module) is bytes:
        module = string(module, ENCS['shell'])
      self._imports_.append(module)
    else:
      raise(TypeError(
        'argument must be a string, not %s' % type(module).__name__))
    
  def removeImport(self, module):
    '''Remove the given module from the current package.'''
    if type(module) is bytes or type(module) is string:
      if type(module) is bytes:
        module = string(module, ENCS['shell'])
      self._imports_.remove(module)
    else:
      raise(TypeError(
        'argument must be a string, not %s' % type(module).__name__))
    
  def getImports(self):
    '''Return the list of the modules from the current package.'''
    return(self._imports_)
    
  def setImports(self, modules):
    '''Specify the modules which will be imported into the current package.'''
    if type(modules) is list or type(modules) is tuple:
      for module in modules:
        if type(module) is not string:
          raise(TypeError(
            'every module must be a string, not %s' % type(module).__name__))
      self._imports_ = modules
    else:
      raise(TypeError(
        'modules must be a list or a tuple, not %s' % type(modules).__name__))
    
  def resetImports(self):
    '''Reset the list of the modules.'''
    self._imports_ = list()
    
  def checkDryRun(self):
    '''Check if user enabled dry run mode.'''
    return(self._dryrun_)
    
  def enableDryRun(self):
    '''Only print what would have been done.'''
    self._dryrun_ = True
    
  def disableDryRun(self):
    '''Really execute what shall be done.'''
    self._dryrun_ = False
    
  def enableTestFlag(self, flag):
    '''Enable test flag. You can get flags from MODES['tests'] variable.'''
    if flag in MODES['tests'].keys():
      if flag not in self._testflags_:
        self._testflags_.append(flag)
    else:
      raise(TypeError('unknown flag: %s' % repr(flag)))
    
  def disableTestFlag(self, flag):
    '''Disable test flag. You can get flags from MODES['tests'] variable.'''
    if flag in MODES['tests'].keys():
      if flag in self._testflags_:
        self._testflags_.remove(flag)
    else:
      raise(TypeError('unknown flag: %s' % repr(flag)))
    
  def setTestFlags(self, flags):
    if type(flags) is list or type(flags) is tuple:
      for flag in flags:
        if type(flag) is not string:
          raise(TypeError(
            'every flag must be an int, not %s' % type(flag).__name__))
        elif flag not in MODES['tests'].keys():
          raise(TypeError('unknown flag: %s' % repr(flag)))
      self._testflags_ = flags
    else:
      raise(TypeError(
        'flags must be a list or a tuple, not %s' % type(flags).__name__))
    
  def resetTestFlags(self):
    '''Reset test flags (only default flag will be enabled).'''
    self._testflags_ = list([1])
    
  def addAvoid(self, module):
    '''Avoid including the given module. Useful if you have code that provides
    equivalent functionality.'''
    if type(module) is bytes or type(module) is string:
      if type(module) is bytes:
        module = string(module, ENCS['shell'])
      self._avoids_.append(module)
    else:
      raise(TypeError(
        'argument must be a string, not %s' % type(module).__name__))
    
  def removeAvoid(self, module):
    '''Remove the given module from the list of avoided modules.'''
    if type(module) is bytes or type(module) is string:
      if type(module) is bytes:
        module = string(module, ENCS['shell'])
      self._avoids_.remove(module)
    else:
      raise(TypeError(
        'argument must be a string, not %s' % type(module).__name__))
    
  def getAvoids(self):
    '''Return the list of the avoided modules.'''
    return(self._avoids_)
    
  def setAvoids(self, modules):
    '''Specify the modules which will be avoided.'''
    if type(modules) is list or type(modules) is tuple:
      for module in modules:
        if type(module) is not string:
          raise(TypeError(
            'every module must be a string, not %s' % type(module).__name__))
      self._avoids_ = modules
    else:
      raise(TypeError(
        'modules must be a list or a tuple, not %s' % type(modules).__name__))
    
  def resetAvoids(self):
    '''Reset the list of the avoided modules.'''
    self._avoids_ = list()
    
  def checkDependencies(self):
    '''Check if user enabled cond. dependencies.'''
    return(self._dependencies_)
    
  def enableDependencies(self):
    '''Enable cond. dependencies (may save configure time and object code).'''
    self._dependencies_ = True
    
  def disableDependencies(self):
    '''Disable cond. dependencies (may save configure time and object code).'''
    self._dependencies_ = False
    
  def checkLibtool(self):
    '''Check if user enabled libtool rules.'''
    return(self._libtool_)
    
  def enableLibtool(self):
    '''Enable libtool rules.'''
    self._libtool_ = True
    
  def disableLibtool(self):
    '''Disable libtool rules.'''
    self._libtool_ = False
    
  def getLibName(self):
    '''Return the library name. Defaults to 'libgnu'.'''
    return(self._library_)
    
  def setLibName(self, library):
    '''Specify the library name.  Defaults to 'libgnu'.'''
    if type(library) is bytes or type(library) is string:
      if type(library) is bytes:
        library = string(library, ENCS['shell'])
      self._library_ = library
    else:
      raise(TypeError(
        'argument must be a string, not %s' % type(module).__name__))

