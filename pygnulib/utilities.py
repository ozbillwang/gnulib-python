#!/usr/bin/python
'''This script is a part of PyGNULib module for gnulib.'''

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
compiler = constants.compiler
cleaner = constants.cleaner
string = constants.string
APP = constants.APP
DIRS = constants.DIRS
ENCS = constants.ENCS
UTILS = constants.UTILS
FILES = constants.FILES
MODES = constants.MODES
TESTS = constants.TESTS
isabs = os.path.isabs
isdir = os.path.isdir
isfile = os.path.isfile
joinpath = os.path.join
normpath = os.path.normpath
relpath = os.path.relpath


#===============================================================================
# Define GNULibError class
#===============================================================================
class GNULibError(Exception):
  '''Exception handler for GNULib classes.'''
  
  def __init__(self, errno, errinfo=None):
    ''' Each error has following parameters:
    errno: code of error; used to catch error type
      1: configure: path does not exist or not a file'''
    self.errno = errno; self.errinfo = errinfo
    self.args = (self.errno, self.errinfo)
  
  def __str__(self):
    errors = \
    [ # Begin list of errors
      "auxdir: configure file does not exist: %s" % self.errinfo,
      "auxdir: path does not exist or is not a dir: %s" % self.errinfo,
      "path does not exist or is not a directory: %s" % self.errinfo,
      "path does not exist or is not a file: %s" % self.errinfo,
      "file can not be found: %s" % self.errinfo,
    ] # Complete list of errors
    if not PYTHON3:
      self.message = (b'[Errno %d] %s' % \
        (self.errno, errors[self.errno -1].encode(ENCS['default'])))
    else: # if PYTHON3
      self.message = ('[Errno %d] %s' % \
        (self.errno, errors[self.errno -1]))
    return(self.message)


#===============================================================================
# Define GNULibInfo class
#===============================================================================
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
    
  def copyright_notice(self):
    '''Return a header for a generated file.'''
    result = ('# %s\n' % self.copyright())
    result += '''#
# This file is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This file is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this file.  If not, see <http://www.gnu.org/licenses/>.
#
# As a special exception to the GNU General Public License,
# this file may be distributed as part of a program that
# contains a configuration script generated by Autoconf, under
# the same distribution terms as the rest of that program.
#
# Generated by gnulib-tool.'''
    return(result)
    
  def date(self):
    '''Return formatted string which contains date and time in GMT format.'''
    if isdir(DIRS['git']):
      counter = int() # Create counter
      result = string() # Create string
      args1 = ['git', 'log', FILES['changelog']]
      args2 = ['head', '-n', '3']
      proc1 = sp.Popen(args1, stdout=sp.PIPE)
      proc2 = sp.Popen(args2, stdin=proc1.stdout, stdout=sp.PIPE)
      proc1.stdout.close() # Close the first shell pipe
      result = string(proc2.stdout.read(), ENCS['shell'])
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
    if isdir(DIRS['git']):
      version_gen = joinpath(DIRS['build-aux'], 'git-version-gen')
      args = [version_gen, DIRS['root']]
      proc = sp.check_output(args)
      result = string(proc, ENCS['shell'])
      result = result.rstrip(os.linesep)
      return(result)


#===============================================================================
# Define GNULibMode class
#===============================================================================
class GNULibMode(object):
  '''GNULibMode class is used to create basic mode instance. All the methods
  which can be applied to GNULibMode can be applied to any other mode.
  GNULibMode is the parent for all the other modes, so every new mode must be
  based on this class.'''
  
  def __init__\
  (
    self,
    verbose=0,
    destdir=None,
    localdir=None,
    modcache=False,
  ):
    '''Create GNULibMode instance. There are some variables which can be
    used in __init__ section. However you can set them later using methods
    inside GNULibImport class. Here are the types for variables:
      destdir: string; default is current directory;
      NOTE: localdir: string; default is ;
      modcache: bool; default is False;
      verbose: -2 <= int <= 2; default is 0;'''
    # destdir => self._destdir_
    if type(destdir) is NoneType:
      self._destdir_ = DIRS['cwd']
    else: # type(destdir) is not NoneType:
      if type(destdir) is bytes or type(destdir) is string:
        if type(destdir) is bytes:
          self._destdir_ = string(destdir, ENCS['system'])
        elif type(destdir) is string:
          self._destdir_ = destdir
      else:
        raise(TypeError(
          'destdir must be a string, not %s' % type(destdir).__name__))
    # localdir => self._localdir_
    if type(localdir) is NoneType:
      self._localdir_ = string()
    else: # if type(localdir) is not NoneType
      if type(localdir) is bytes or type(localdir) is string:
        if type(localdir) is bytes:
          self._localdir_ = string(localdir, ENCS['system'])
        elif type(localdir) is string:
          self._localdir_ = localdir
      else:
        raise(TypeError(
          'localdir must be a string, not %s' % type(localdir).__name__))
    # modcache => self._modcache_
    if type(modcache) is bool:
      self._modcache_ = modcache
    else:
      raise(TypeError(
        'modcache must be a bool, not %s' % type(modcache).__name__))
    # verbose => self._verbose_
    if type(verbose) is int:
      self._verbose_ = verbose
    else:
      raise(TypeError(
        'verbose must be an int, not %s' % type(verbose).__name__))
    
  def getAvailableModules(self):
    '''Return the available module names as tuple. We could use a combination
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
    if all([self._localdir_, isdir(joinpath(self._localdir_, 'modules'))]):
      os.chdir(self._localdir_)
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
    
  def getDestDir(self):
    '''Return the target directory. For --import, this specifies where your
    configure.ac can be found. Defaults to current directory.'''
    return(self._destdir_)
    
  def setDestDir(self, directory):
    '''Specify the target directory. For --import, this specifies where your
    configure.ac can be found. Defaults to current directory.'''
    if type(directory) is bytes or type(directory) is string:
      if type(directory) is bytes:
        self._destdir_ = string(directory, ENCS['system'])
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
        self._localdir_ = string(directory, ENCS['system'])
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


#===============================================================================
# Define GNULibImport class
#===============================================================================
class GNULibImport(GNULibMode):
  '''GNULibImport class is used to provide methods for --import, --add-import
  and --remove-import actions.'''
  
  def __init__\
  (
    self,
    mode,
    verbose=0,
    destdir=None,
    localdir=None,
    modcache=False,
    auxdir=None,
    modules=None,
    avoids=None,
    sourcebase=None,
    m4base=None,
    pobase=None,
    docbase=None,
    testsbase=None,
    tests=None,
    lgpl=None,
    podomain=None,
    dryrun=False,
    dependencies=None,
    libtool=None,
    libname=None,
    makefile=None,
    macro_prefix=None,  
    vc_files=None,
  ):
    '''Create GNULibImport instance. There are some variables which can be
    used in __init__ section. However you can set them later using methods
    inside GNULibImport class. Here are the types for variables:
      mode: int; from 0 to 3; required argument.
      destdir: string; default is current directory.
      localdir: string; default is cached one.
      modcache: bool; default is False.
      verbose: -2 <= int <= 2; default is 0.
      auxdir: directory relative to destdir where auxiliary build tools are
        placed; default comes from configure.ac.
      modules: list of modules which will be imported; default is cached one.
      avoids: list of modules which will be avoided; default is cached one.
      sourcebase: string; default is 'lib' or cached one; relative.
      m4base: string; default is 'm4' or cached one; relative.
      docbase: string; default is 'doc' or cached one; relative.
      testsbase: string; default is 'tests' or cached one; relative.
      tests: list which contains test codes; default is list([1]);
        you can get all the codes from MODES['tests'] dict.
      lgpl: abort if modules aren't available under the LGPL; also modify
        license template from GPL to LGPL; the version number of the LGPL can
        be specified; the default is currently LGPLv3.
      macro_prefix: string; the prefix of the macros 'gl_EARLY' and 'gl_INIT';
        default value of macro_prefix is 'gl' or cached one;
      makefile: string; default is 'Makefile.am'.'''
    # Initialization from the parent class
    super(GNULibImport, self).__init__\
    ( # Begin __init__ method
      destdir=destdir,
      localdir=localdir,
      modcache=modcache,
      verbose=verbose,
    ) # Complete __init__ method
    if type(mode) is int and MODES['import'] <= mode <= MODES['update']:
      self._mode_ = mode
    else: # if unknown mode
      raise(TypeError(
        'unknown mode: %s' % repr(mode)))
    
    # Initialize cache dictionary and set some values.
    # For mode == MODES['import'], most of these values are default.
    # For other modes, pygnulib will get them from different files.
    self._cached_ = dict()
    self._cached_['modules'] = list()
    self._cached_['avoids'] = list()
    self._cached_['sourcebase'] = normpath(joinpath(self._destdir_, 'lib'))
    self._cached_['pobase'] = normpath(joinpath(self._destdir_, 'po'))
    self._cached_['m4base'] = normpath(joinpath(self._destdir_, 'm4'))
    self._cached_['docbase'] = normpath(joinpath(self._destdir_, 'doc'))
    self._cached_['testsbase'] = normpath(joinpath(self._destdir_, 'tests'))
    self._cached_['makefile'] = 'Makefile.am'
    self._cached_['macro_prefix'] = 'gl'
    self._cached_['libname'] = 'libgnu'
    self._cached_['lgpl'] = 3
    
    # Get default auxdir and libtool from configure.ac/in
    path = relpath('configure.ac', self._destdir_)
    if not isfile(path):
      path = relpath('configure.in', self._destdir_)
      if not isfile(path):
        raise(GNULibError(1, repr(path)))
    with codecs.open(path, 'rb', 'UTF-8') as file:
      textdata = file.read()
    pattern = compiler(r'^AC_CONFIG_AUX_DIR\((.*?)\)$')
    self._cached_['auxdir'] = \
      relpath(cleaner(pattern.findall(textdata))[0], self._destdir_)
    pattern = compiler(r'A[CM]_PROG_LIBTOOL')
    self._cached_['libtool'] = bool(pattern.findall(textdata))
    
    # Set self._m4base_ for 
    
    # Set default values for other modes
    if self._mode_ != MODES['import']:
      m4dirs = list() # List of available directories
      dirisnext = bool() # If the next is a directory
      # Get ACLOCAL_AMFLAGS from Makefile.am
      path = joinpath(self._destdir_, 'Makefile.am')
      if isfile(path):
        with codecs.open(path, 'rb', 'UTF-8') as file:
          textdata = file.read()
        pattern = compiler(r'^ACLOCAL_AMFLAGS.*?=.*?(.*?)$')
        result = cleaner(pattern.findall(textdata))[0]
        # Get all relative directories
        for item in result.split():
          if not isabs(item) and dirisnext:
            m4cache = joinpath(self._destdir_, item, 'gnulib-cache.m4')
            if isfile(m4cache):
              m4dirs.append(item)
          if item == '-I':
            dirisnext = True
          else: # if item != '-I'
            dirisnext = False
      else: # Makefile.am does not exist or is not a file
        # Get m4_include from aclocal.m4
        path = joinpath(self._destdir_, 'aclocal.m4')
        if isfile(path):
          with codecs.open(path, 'rb', 'UTF-8') as file:
            textdata = file.read()
          pattern = compiler(r'^m4_include\((.*?)\)$')
          result = cleaner(pattern.findall(textdata))
          result.sort()
     
      # First use of gnulib in a package.
      if len(m4dirs) == 0:
        self.resetM4Base()
        # docbase => self._docbase_
        if type(docbase) is NoneType:
          self.resetSourceBase()
        else: # if type(docbase) is not NoneType
          self.setSourceBase(docbase)
        # testsbase => self._testsbase_
        if type(docbase) is NoneType:
          self.resetSourceBase()
        else: # if type(docbase) is not NoneType
          self.setSourceBase(docbase)
        if type(macro_prefix) is NoneType:
          self.resetMacroPrefix()
        else: # type(macro_prefix) is not NoneType:
          self.setMacroPrefix(macro_prefix)
      
      # There's only one use of gnulib here. Assume the user means it.
      elif len(m4dirs) == 1:
        self._cached_['m4base'] = m4dirs[0]
        
      # Ambiguous - guess what the user meant.
      else: # if len(m4dirs) > 1
        pass # NOTE: I'll change it later when I create self.run() method
      
    # auxdir => self._auxdir_
    if type(auxdir) is NoneType:
      self.resetAuxDir()
    else: # if type(auxdir) is not NoneType
      self.setAuxDir(auxdir)
    
    # m4base => self._m4base_
    if type(m4base) is NoneType:
      self.resetM4Base()
    else: # if type(m4base) is not NoneType
      self.setM4Base(m4base)
    
    # Get the cached settings
    path = joinpath(self._m4base_, 'gnulib-cache.m4')
    if isfile(path):
      with codecs.open(path, 'rb', 'UTF-8') as file:
        textdata = file.read()
      # Cached settings as booleans
      self._cached_['tests'] = list()
      if 'gl_LIBTOOL' in textdata:
        self._cached_['libtool'] = True
      if 'gl_WITH_OBSOLETE' in textdata:
        self._cached_['tests'].append(TESTS['obsolete'])
      if 'gl_WITH_TESTS' in textdata:
        self._cached_['tests'].append(TESTS['default'])
      if 'gl_WITH_CXX_TESTS' in textdata:
        self._cached_['tests'].append(TESTS['cxx'])
      if 'gl_WITH_LONGRUNNING_TESTS' in textdata:
        self._cached_['tests'].append(TESTS['longrunning'])
      if 'gl_WITH_PRIVILEGED_TESTS' in textdata:
        self._cached_['tests'].append(TESTS['privileged'])
      if 'gl_WITH_UNPORTABLE_TESTS' in textdata:
        self._cached_['tests'].append(TESTS['unportable'])
      if 'gl_WITH_ALL_TESTS' in textdata:
        self._cached_['tests'].append(TESTS['all'])
      textdata = textdata.replace('gl_LIBTOOL\n', '')
      textdata = textdata.replace('gl_WITH_OBSOLETE\n', '')
      textdata = textdata.replace('gl_WITH_TESTS\n', '')
      textdata = textdata.replace('gl_WITH_CXX_TESTS\n', '')
      textdata = textdata.replace('gl_WITH_LONGRUNNING_TESTS\n', '')
      textdata = textdata.replace('gl_WITH_PRIVILEGED_TESTS\n', '')
      textdata = textdata.replace('gl_WITH_UNPORTABLE_TESTS\n', '')
      textdata = textdata.replace('gl_WITH_ALL_TESTS\n', '')
      # Cached settings as strings
      pattern = compiler(r'^(gl.*?)\((.*?)\)$')
      result = dict(pattern.findall(textdata))
      keys = \
      [
        'gl_LOCAL_DIR',
        'gl_MODULES',
        'gl_AVOID',
        'gl_SOURCE_BASE',
        'gl_M4_BASE',
        'gl_PO_BASE',
        'gl_DOC_BASE',
        'gl_TESTS_BASE',
        'gl_LIB',
        'gl_LGPL',
        'gl_MAKEFILE_NAME',
        'gl_CONDITIONAL_DEPENDENCIES',
        'gl_MACRO_PREFIX',
        'gl_PO_DOMAIN',
        'gl_WITNESS_C_MACRO',
        'gl_VC_FILES',
      ]
      values = cleaner([result.get(key, '') for key in keys])
      tempdict = dict(zip(keys, values))
      if tempdict['gl_LOCAL_DIR'] != '':
        self._cached_['localdir'] = tempdict['gl_LOCAL_DIR']
      if tempdict['gl_MODULES'] != '':
        self._cached_['modules'] = cleaner(tempdict['gl_MODULES'].split())
      if tempdict['gl_AVOID'] != '':
        self._cached_['avoid'] = cleaner(tempdict['gl_AVOID'].split())
      if tempdict['gl_SOURCE_BASE'] != '':
        self._cached_['sourcebase'] = tempdict['gl_SOURCE_BASE']
      if tempdict['gl_PO_BASE'] != '':
        self._cached_['pobase'] = tempdict['gl_PO_BASE']
      if tempdict['gl_DOC_BASE'] != '':
        self._cached_['docbase'] = tempdict['gl_DOC_BASE']
      if tempdict['gl_TESTS_BASE'] != '':
        self._cached_['testsbase'] = tempdict['gl_TESTS_BASE']
      if tempdict['gl_LIB'] != '':
        self._cached_['libname'] = tempdict['gl_LIB']
      if tempdict['gl_LGPL'] != '':
        self._cached_['lgpl'] = tempdict['gl_LGPL']
      if tempdict['gl_MAKEFILE_NAME'] != '':
        self._cached_['makefile'] = tempdict['gl_MAKEFILE_NAME']
      if tempdict['gl_CONDITIONAL_DEPENDENCIES'] != '':
        self._cached_['dependencies'] = tempdict['gl_CONDITIONAL_DEPENDENCIES']
      if tempdict['gl_MACRO_PREFIX'] != '':
        self._cached_['macro_prefix'] = tempdict['gl_MACRO_PREFIX']
      if tempdict['gl_PO_DOMAIN'] != '':
        self._cached_['podomain'] = tempdict['gl_PO_DOMAIN']
      if tempdict['gl_VC_FILES'] != '':
        self._cached_['vc_files'] = tempdict['gl_VC_FILES']
    
    # modules => self._modules_
    self._modules_ = list()
    self.resetModules()
    if type(modules) is not NoneType:
      for module in modules:
        self.addModule(module)
    
    # libtool => self._libtool_
    self.resetLibtool()
    if type(libtool) is bool:
      if libtool:
        self.enableLibtool()
      else: # if not libtool
        self.disableLibtool()
    
    # tests => self._tests_
    self.resetTestFlags()
    if type(tests) is not NoneType:
      self.setTestFlags(tests)
    
    # avoids => self._avoids_
    self._avoids_ = list()
    self.resetAvoids()
    if type(avoids) is not NoneType:
      for module in avoids:
        self.addAvoid(module)
    
    # sourcebase => self._sourcebase_
    self._sourcebase_ = self._cached_['sourcebase']
    if type(sourcebase) is not NoneType:
      self.setSourceBase(sourcebase)
    
    # pobase => self._pobase_
    self._pobase_ = self._cached_['pobase']
    if type(pobase) is not NoneType:
      self.setPoBase(pobase)
    
    # docbase => self._docbase_
    self._docbase_ = self._cached_['docbase']
    if type(docbase) is not NoneType:
      self.setDocBase(docbase)
    
    # testsbase => self._testsbase_
    self._testsbase_ = self._cached_['testsbase']
    if type(testsbase) is not NoneType:
      self.setTestsBase(testsbase)
    
    # libname => self._libname_
    self._libname_ = self._cached_['libname']
    if type(libname) is not NoneType:
      self.setLibName(libname)
    
    # makefile => self._makefile_
    self._makefile_ = self._cached_['makefile']
    
    dictionary = self.__dict__
    dictionary.pop('_cached_')
    pprint(dictionary)
    
  def setDestDir(self, directory):
    '''Specify the target directory. For --import, this specifies where your
    configure.ac can be found. Defaults to current directory.'''
    super(GNULibImport, self).setDestDir(directory)
    
  def addModule(self, module):
    '''Add the module to the modules list.'''
    if type(module) is bytes or type(module) is string:
      if type(module) is bytes:
        module = string(module, ENCS['system'])
      self._modules_.append(module)
    else:
      raise(TypeError(
        'argument must be a string, not %s' % type(module).__name__))
    
  def removeModule(self, module):
    '''Remove the module from the modules list.'''
    if type(module) is bytes or type(module) is string:
      if type(module) is bytes:
        module = string(module, ENCS['system'])
      self._modules_.remove(module)
    else:
      raise(TypeError(
        'argument must be a string, not %s' % type(module).__name__))
    
  def getModules(self):
    '''Return the modules list.'''
    return(self._modules_)
    
  def setModules(self, modules):
    '''Set the modules list.'''
    if type(modules) is list or type(modules) is tuple:
      old_modules = self._modules_
      self._modules_ = list()
      for module in modules:
        if type(module) is not bytes and type(module) is not string:
          raise(TypeError(
            'every module must be a string, not %s' % type(module).__name__))
          self._modules_ = old_modules
        else: # type(module) is bytes or type(module) is string
          if type(module) is bytes:
            module = string(module, ENCS['system'])
          self._modules_.append(module)
    else:
      raise(TypeError(
        'modules must be a list or a tuple, not %s' % type(modules).__name__))
    
  def resetModules(self):
    '''Reset the list of the modules.'''
    self.setModules(self._cached_['modules'])
    
  def addAvoid(self, module):
    '''Avoid including the given module. Useful if you have code that provides
    equivalent functionality.'''
    if type(module) is bytes or type(module) is string:
      if type(module) is bytes:
        module = string(module, ENCS['system'])
      self._avoids_.append(module)
    else:
      raise(TypeError(
        'argument must be a string, not %s' % type(module).__name__))
    
  def removeAvoid(self, module):
    '''Remove the given module from the list of avoided modules.'''
    if type(module) is bytes or type(module) is string:
      if type(module) is bytes:
        module = string(module, ENCS['system'])
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
      old_avoids = self._avoids_
      self._avoids_ = list()
      for module in modules:
        if type(module) is not bytes and type(module) is not string:
          raise(TypeError(
            'every module must be a string, not %s' % type(module).__name__))
          self._avoids_ = old_avoids
        else: # type(module) is bytes or type(module) is string
          if type(module) is bytes:
            module = string(module, ENCS['system'])
          self._avoids_.append(module)
    else:
      raise(TypeError(
        'modules must be a list or a tuple, not %s' % type(modules).__name__))
    
  def resetAvoids(self):
    '''Reset the list of the avoided modules.'''
    self.setAvoids(self._cached_['avoids'])
    
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
      if flag not in self._tests_:
        self._tests_.append(flag)
    else:
      raise(TypeError('unknown flag: %s' % repr(flag)))
    
  def disableTestFlag(self, flag):
    '''Disable test flag. You can get flags from MODES['tests'] variable.'''
    if flag in MODES['tests'].keys():
      if flag in self._tests_:
        self._tests_.remove(flag)
    else:
      raise(TypeError('unknown flag: %s' % repr(flag)))
    
  def setTestFlags(self, flags):
    if type(flags) is list or type(flags) is tuple:
      for flag in flags:
        if type(flag) is not int:
          raise(TypeError(
            'every flag must be an int, not %s' % type(flag).__name__))
        elif flag not in TESTS.values():
          raise(TypeError('unknown flag: %s' % repr(flag)))
      self._tests_ = flags
    else:
      raise(TypeError(
        'flags must be a list or a tuple, not %s' % type(flags).__name__))
    
  def resetTestFlags(self):
    '''Reset test flags (only default flag will be enabled).'''
    self.setTestFlags(self._cached_['tests'])
    
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
    
  def resetLibtool(self):
    '''Reset libtool rules.'''
    self._libtool_ = self._cached_['libtool']
    
  def getLibName(self):
    '''Return the library name. Defaults to 'libgnu'.'''
    return(self._libname_)
    
  def setLibName(self, libname):
    '''Specify the library name.  Defaults to 'libgnu'.'''
    if type(libname) is bytes or type(libname) is string:
      if type(libname) is bytes:
        libname = string(libname, ENCS['system'])
      self._libname_ = libname
    else:
      raise(TypeError(
        'argument must be a string, not %s' % type(module).__name__))
    
  def resetLibName(self):
    '''Specify the library name.  Defaults to 'libgnu'.'''
    self.setLibName(self._cached_['libname'])
    
  def getAuxDir(self):
    '''Return directory relative to --dir where auxiliary build tools are
    placed. Default comes from configure.ac or configure.in.'''
    return(self._auxdir_)
    
  def setAuxDir(self, auxdir):
    '''Specify directory relative to --dir where auxiliary build tools are
    placed. Default comes from configure.ac or configure.in.'''
    if type(auxdir) is bytes or type(auxdir) is string:
      if type(auxdir) is bytes:
        self._auxdir_ = string(auxdir, ENCS['system'])
      self._auxdir_ = relpath(auxdir, self._destdir_)
    else:
      raise(TypeError(
        'argument must be a string, not %s' % type(auxdir).__name__))
    
  def resetAuxDir(self):
    '''Reset directory relative to --dir where auxiliary build tools are
    placed. Default comes from configure.ac or configure.in.'''
    path = normpath(joinpath(self._destdir_, self._cached_['auxdir']))
    self.setAuxDir(path)
    
  def getSourceBase(self):
    '''Return directory relative to destdir where source code is placed.
    Default value for this variable is 'lib').'''
    return(self._sourcebase_)
    
  def setSourceBase(self, sourcebase):
    '''Specify directory relative to destdir where source code is placed.
    Default value for this variable is 'lib').'''
    if type(sourcebase) is bytes or type(sourcebase) is string:
      if type(sourcebase) is bytes:
        sourcebase = string(sourcebase, ENCS['system'])
      self._sourcebase_ = relpath(sourcebase, self._destdir_)
    else:
      raise(TypeError(
        'argument must be a string, not %s' % type(sourcebase).__name__))
    
  def resetSourceBase(self):
    '''Return directory relative to destdir where source code is placed.
    Default value for this variable is 'lib').'''
    path = normpath(joinpath(self._destdir_, self._cached_['sourcebase']))
    self.setSourceBase(path)
    
  def getM4Base(self):
    '''Return directory relative to destdir where *.m4 macros are placed.
    Default value for this variable is 'm4').'''
    return(self._m4base_)
    
  def setM4Base(self, m4base):
    '''Specify directory relative to destdir where *.m4 macros are placed.
    Default value for this variable is 'm4').'''
    if type(m4base) is bytes or type(m4base) is string:
      if type(m4base) is bytes:
        m4base = string(m4base, ENCS['system'])
      self._m4base_ = relpath(m4base, self._destdir_)
    else:
      raise(TypeError(
        'argument must be a string, not %s' % type(m4base).__name__))
    
  def resetM4Base(self):
    '''Reset directory relative to destdir where *.m4 macros are placed.
    Default value for this variable is 'm4').'''
    path = normpath(joinpath(self._destdir_, self._cached_['m4base']))
    self.setM4Base(path)
    
  def getPoBase(self):
    '''Return directory relative to destdir where *.po files are placed.
    Default value for this variable is 'po').'''
    return(self._pobase_)
    
  def setPoBase(self, pobase):
    '''Specify directory relative to destdir where *.po files are placed.
    Default value for this variable is 'po').'''
    if type(pobase) is bytes or type(pobase) is string:
      if type(pobase) is bytes:
        pobase = string(pobase, ENCS['system'])
      self._pobase_ = relpath(pobase, self._destdir_)
    else:
      raise(TypeError(
        'argument must be a string, not %s' % type(pobase).__name__))
    
  def resetPoBase(self):
    '''Reset directory relative to destdir where *.po files are placed.
    Default value for this variable is 'po').'''
    path = normpath(joinpath(self._destdir_, self._cached_['pobase']))
    self.setPoBase(path)
    
  def getDocBase(self):
    '''Return directory relative to destdir where doc files are placed.
    Default value for this variable is 'doc').'''
    return(self._docbase_)
    
  def setDocBase(self, docbase):
    '''Specify directory relative to destdir where doc files are placed.
    Default value for this variable is 'doc').'''
    if type(docbase) is bytes or type(docbase) is string:
      if type(docbase) is bytes:
        docbase = string(docbase, ENCS['system'])
      self._docbase_ = relpath(docbase, self._destdir_)
    else:
      raise(TypeError(
        'argument must be a string, not %s' % type(docbase).__name__))
    
  def resetDocBase(self):
    '''Reset directory relative to destdir where doc files are placed.
    Default value for this variable is 'doc').'''
    path = normpath(joinpath(self._destdir_, self._cached_['docbase']))
    self.setDocBase(path)
    
  def getTestsBase(self):
    '''Return directory relative to destdir where unit tests are placed.
    Default value for this variable is 'tests').'''
    return(self._testsbase_)
    
  def setTestsBase(self, testsbase):
    '''Specify directory relative to destdir where unit tests are placed.
    Default value for this variable is 'tests').'''
    if type(testsbase) is bytes or type(testsbase) is string:
      if type(testsbase) is bytes:
        testsbase = string(testsbase, ENCS['system'])
      self._testsbase_ = relpath(testsbase, self._destdir_)
    else:
      raise(TypeError(
        'argument must be a string, not %s' % type(testsbase).__name__))
    
  def resetTestsBase(self):
    '''Reset directory relative to destdir where unit tests are placed.
    Default value for this variable is 'tests').'''
    path = normpath(joinpath(self._destdir_, self._cached_['testsbase']))
    self.setTestsBase(path)
    
  def getLGPL(self):
    '''Check for abort if modules aren't available under the LGPL.'''
    return(self._lgpl_)
    
  def setLGPL(self, lgpl):
    '''Abort if modules aren't available under the LGPL.'''
    if (type(lgpl) is int and 2 <= lgpl <= 3) or \
      (type(lgpl) is bool and lgpl == False):
        self._lgpl_ = lgpl
    else:
      raise(TypeError(
        'lgpl must be False, 2 or 3, not %s' % type(lgpl).__name__))
    
  def resetLGPL(self):
    '''Disable abort if modules aren't available under the LGPL.'''
    self.setLGPL(self._cached_['lgpl'])
    
  def getMacroPrefix(self):
    '''Return the prefix of the macros 'gl_EARLY' and 'gl_INIT'.
    Default is 'gl'.'''
    return(self._macro_prefix_)
    
  def setMacroPrefix(self, macro_prefix):
    '''Specify the prefix of the macros 'gl_EARLY' and 'gl_INIT'.
    Default is 'gl'.'''
    if type(macro_prefix) is bytes or type(macro_prefix) is string:
      if type(macro_prefix) is bytes:
        macro_prefix = string(macro_prefix, ENCS['system'])
      self._macro_prefix_ = macro_prefix
    else:
      raise(TypeError(
        'macro_prefix must be a string, not %s' % type(macro_prefix).__name__))
    
  def resetMacroPrefix(self):
    '''Reset the prefix of the macros 'gl_EARLY' and 'gl_INIT'.
    Default is 'gl'.'''
    self.setMacroPrefix(self._cached_['macro_prefix'])
    
  def getMakefile(self):
    '''Return the name of makefile in automake syntax in the source-base and
    tests-base directories. Default is 'Makefile.am'.'''
    return(self._makefile_)
    
  def setMakefile(self, makefile):
    '''Specify the name of makefile in automake syntax in the source-base and
    tests-base directories. Default is 'Makefile.am'.'''
    if type(makefile) is bytes or type(makefile) is string:
      if type(makefile) is bytes:
        makefile = string(makefile, ENCS['system'])
      self._makefile_ = makefile
    else:
      raise(TypeError(
        'argument must be a string, not %s' % type(makefile).__name__))
    
  def resetMakefile(self):
    '''Reset the name of makefile in automake syntax in the source-base and
    tests-base directories. Default is 'Makefile.am'.'''
    self.setMakefile(self._cached_['makefile'])

