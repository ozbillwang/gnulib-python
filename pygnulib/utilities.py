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
import warnings
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
str_disj = constants.str_disj
joinpath = constants.joinpath
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
      1: destination directory does not exist: <destdir>
      2: configure file does not exist: <configure.ac>
      3: selected module does not exist: <module>
      4: <cache> is expected to contain gl_M4_BASE([m4base])
      5: missing sourcebase argument
      6: missing docbase argument
      7: missing testsbase argument
      8: missing libname argument'''
    self.errno = errno; self.errinfo = errinfo
    self.args = (self.errno, self.errinfo)
  
  def __str__(self):
    errors = \
    [ # Begin list of errors
      "destination directory does not exist: %s" % self.errinfo,
      "configure file does not exist: %s" % self.errinfo,
      "selected module does not exist: %s" % self.errinfo,
      "%s is expected to contain gl_M4_BASE([%s])" % \
        (os.path.join(self.errinfo, 'gnulib-comp.m4'), self.errinfo),
      "missing sourcebase argument; cache file doesn't contain it,"
        +" so you might have to set this argument",
      "missing docbase argument; you might have to create GNULibImport" \
        +" instance with mode 0 and docbase argument",
      "missing testsbase argument; cache file doesn't contain it,"
        +" so you might have to set this argument"
      "missing libname argument; cache file doesn't contain it,"
        +" so you might have to set this argument",
      "dependencies and testflag 'default' cannot be used together",
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
    destdir=None,
    localdir=None,
    verbose=None,
    modcache=None,
  ):
    '''Create GNULibImport instance. There are some variables which can be
    used in __init__ section. However, you can set them later using methods
    inside GNULibImport class. See info for each variable in the corresponding
    set* class. The main variable, mode, must be one of the values of the
    MODES dict object, which is accessible from this module.'''
    
    # Create cache dictionary
    self.args = dict()
    self.cache = dict()
    self.cache['destdir'] = '.'
    self.cache['localdir'] = ''
    self.cache['modcache'] = True
    self.cache['verbose'] = 0
    
    # destdir => self.args['destdir']
    if destdir == None:
      self.resetDestDir()
    else: # if destdir != None
      self.setDestDir(destdir)
    
    # localdir => self.args['localdir']
    if localdir == None:
      self.resetLocalDir()
    else: # if localdir != None
      self.setLocalDir(localdir)
    
    # modcache => self.args['modcache']
    if type(modcache) is NoneType:
      self.resetModuleCaching()
    elif type(modcache) is bool:
      if modcache:
        self.enableModuleCaching()
      else: # if not modcache
        self.disableModuleCaching()
    
    # verbose => self.args['localdir']
    if type(verbose) is NoneType:
      self.resetVerbosity()
    elif type(verbose) is int:
      self.setVerbosity(verbose)
    
  def getAllModules(self):
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
    
  def checkModule(self, module):
    '''Check if module exists inside gnulib dir or localdir.'''
    result = bool()
    if type(module) is bytes or type(module) is string:
      if type(module) is bytes:
        module = string(module, ENCS['system'])
    else: # if module has not bytes or string type
      raise(TypeError(
        'argument must be a string, not %s' % type(module).__name__))
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
    
  def getDestDir(self):
    '''Return the target directory. For --import, this specifies where your
    configure.ac can be found. Defaults to current directory.'''
    return(self.args['destdir'])
    
  def setDestDir(self, directory):
    '''Specify the target directory. For --import, this specifies where your
    configure.ac can be found. Defaults to current directory.'''
    if type(directory) is bytes or type(directory) is string:
      if type(directory) is bytes:
        directory = string(directory, ENCS['system'])
      if not isdir(directory):
        raise(GNULibError(1, repr(directory)))
      self.args['destdir'] = directory
    else:
      raise(TypeError(
        'argument must be a string, not %s' % type(directory).__name__))
    
  def resetDestDir(self):
    '''Reset the target directory. For --import, this specifies where your
    configure.ac can be found. Defaults to current directory.'''
    self.setDestDir(self.cache['destdir'])
    
  def getLocalDir(self):
    '''Return a local override directory where to look up files before looking
    in gnulib's directory.'''
    return(self.args['localdir'])
    
  def setLocalDir(self, directory):
    '''Specify a local override directory where to look up files before looking
    in gnulib's directory.'''
    if type(directory) is bytes or type(directory) is string:
      if type(directory) is bytes:
        directory = string(directory, ENCS['system'])
      self.args['localdir'] = directory
    else:
      raise(TypeError(
        'argument must be a string, not %s' % type(directory).__name__))
    
  def resetLocalDir(self):
    '''Reset a local override directory where to look up files before looking
    in gnulib's directory.'''
    self.setLocalDir(self.cache['localdir'])
    
  def checkModuleCaching(self):
    '''Get status of module caching optimization.'''
    return(self.args['modcache'])
    
  def enableModuleCaching(self):
    '''Enable module caching optimization.'''
    self.args['modcache'] = True
    
  def disableModuleCaching(self):
    '''Disable module caching optimization.'''
    self.args['modcache'] = False
    
  def resetModuleCaching(self):
    '''Reset module caching optimization.'''
    self.args['modcache'] = self.cache['modcache']
    
  def getVerbosity(self):
    '''Get verbosity level.'''
    return(self.args['verbose'])
    
  def decreaseVerbosity(self):
    '''Decrease verbosity level.'''
    if self.args['verbose'] > MODES['verbose-min']:
      self.args['verbose'] -= 1
    
  def increaseVerbosity(self):
    '''Increase verbosity level.'''
    if self.args['verbose'] < MODES['verbose-max']:
      self.args['verbose'] += 1
    
  def setVerbosity(self, verbose):
    '''Set verbosity level to verbose, where -2 <= verbose <= 2.
    If verbosity level is less than -2, verbosity level will be set to -2.
    If verbosity level is greater than 2, verbosity level will be set to 2.'''
    if type(verbose) is int:
      if MODES['verbose-min'] <= verbose <= MODES['verbose-max']:
        self.args['verbose'] = verbose
      elif verbose < MODES['verbose-min']:
        self.args['verbose'] = MODES['verbose-min']
      elif verbose > MODES['verbose-max']:
        self.args['verbose'] = MODES['verbose-max']
    else:
      raise(TypeError(
        'argument must be a string, not %s' % type(module).__name__))
    
  def resetVerbosity(self):
    '''Reset verbosity level.'''
    self.setVerbosity(self.cache['verbose'])


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
    destdir=None,
    localdir=None,
    modcache=None,
    verbose=None,
    dryrun=None,
    auxdir=None,
    modules=None,
    avoids=None,
    sourcebase=None,
    m4base=None,
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
    '''Create GNULibImport instance. There are some variables which can be used
    in __init__ section. However, you can set them later using methods inside
    GNULibImport class. See info for each variable in the corresponding set*
    class. The main variable, mode, must be one of the values of the MODES dict
    object, which is accessible from this module.'''
    
    # Initialization of the object
    super(GNULibImport, self).__init__\
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
    
    # Initialize some dict values
    keys = \
    [
      'dryrun', 'auxdir', 'modules', 'avoids', 'sourcebase', 'm4base',
      'pobase', 'docbase', 'testsbase', 'tests', 'libname', 'makefile',
      'libtool', 'dependencies', 'macro_prefix', 'podomain', 'vc_files',
      'lgpl', 'witness_c_macro',
    ]
    for item in keys:
      self.args[item] = None
      self.cache[item] = None
    self.cache['libname'] = 'libgnu'
    self.cache['modules'] = list(['dummy'])
    self.cache['avoids'] = list()
    self.cache['flags'] = list()
    self.cache['tests'] = list()
    
    # mode => self.mode
    if type(mode) is int and \
      MODES['import'] <= mode <= MODES['update']:
        self.mode = mode
    else: # if mode is not int or is not 0-3
      raise(TypeError(
        "mode must be 0 <= mode <= 3, not %s" % repr(mode)))
    
    # m4base => self.args['m4base']
    if type(m4base) is NoneType:
      self.resetM4Base()
    else: # if type(m4base) is not NoneType
      self.setM4Base(m4base)
    
    # Get cached auxdir and libtool from configure.ac/in
    self.cache['auxdir'] = '.'
    path = joinpath(self.args['destdir'], 'configure.ac')
    if not isfile(path):
      path = joinpath(self.args['destdir'], 'configure.in')
      if not isfile(path):
        raise(GNULibError(2, repr(path)))
    with codecs.open(path, 'rb', 'UTF-8') as file:
      data = file.read()
    pattern = compiler(r'^AC_CONFIG_AUX_DIR\((.*?)\)$')
    result = cleaner(pattern.findall(data))[0]
    self.cache['auxdir'] = joinpath(result, self.args['destdir'])
    pattern = compiler(r'A[CM]_PROG_LIBTOOL')
    guessed_libtool = bool(pattern.findall(data))
    
    # Get other cached variables
    path = joinpath(self.args['m4base'], 'gnulib-cache.m4')
    if isfile(joinpath(self.args['m4base'], 'gnulib-cache.m4')):
      with codecs.open(path, 'rb', 'UTF-8') as file:
        data = file.read()
      # Create regex object and keys
      pattern = compiler(r'^(gl_.*?)\((.*?)\)$')
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
        self.cache['tests'].append(TESTS['default'])
        data = data.replace('gl_WITH_TESTS', '')
      if 'gl_WITH_OBSOLETE' in data:
        self.cache['tests'].append(TESTS['obsolete'])
        data = data.replace('gl_WITH_OBSOLETE', '')
      if 'gl_WITH_CXX_TESTS' in data:
        self.cache['tests'].append(TESTS['cxx'])
        data = data.replace('gl_WITH_CXX_TESTS', '')
      if 'gl_WITH_LONGRUNNING_TESTS' in data:
        self.cache['tests'].append(TESTS['longrunning'])
        data = data.replace('gl_WITH_LONGRUNNING_TESTS', '')
      if 'gl_WITH_PRIVILEGED_TESTS' in data:
        self.cache['tests'].append(TESTS['privileged'])
        data = data.replace('gl_WITH_PRIVILEGED_TESTS', '')
      if 'gl_WITH_UNPORTABLE_TESTS' in data:
        self.cache['tests'].append(TESTS['unportable'])
        data = data.replace('gl_WITH_UNPORTABLE_TESTS', '')
      if 'gl_WITH_ALL_TESTS' in data:
        self.cache['tests'].append(TESTS['all'])
        data = data.replace('gl_WITH_ALL_TESTS', '')
      # Find string values
      result = dict(pattern.findall(data))
      values = cleaner([result.get(key, '') for key in keys])
      tempdict = dict(zip(keys, values))
      if 'gl_LGPL' in tempdict:
        self.cache['lgpl'] = cleaner(tempdict['gl_LGPL'])
        if self.cache['lgpl'].isdecimal():
          self.cache['lgpl'] = int(self.cache['lgpl'])
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
    
    if self.mode == MODES['import']:
      self.setModules(modules)
    else: # if self.mode != MODES['import']
      if self.args['m4base'] != self.cache['m4base']:
        raise(GNULibError(4, m4base))
      
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
      
      # Perform actions with modules. In --add-import, append each given module
      # to the list of cached modules; in --remove-import, remove each given
      # module from the list of cached modules; in --update, simply set
      # self.args['modules'] to its cached version.
      if modules == None:
        modules = list()
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
      
      # avoids => self.args['avoids']
      self.setAvoids(avoids +self.cache['avoids'])
      
      # sourcebase => self.args['sourcebase']
      if sourcebase == None:
        self.setSourceBase(self.cache['sourcebase'])
      else: # if sourcebase != None
        self.setSourceBase(sourcebase)
      if not self.args['sourcebase']:
        raise(GNULibError(5, None))
      
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
        raise(GNULibError(6, None))
      
      # testsbase => self.args['testsbase']
      if testsbase == None:
        self.setDocBase(self.cache['testsbase'])
      else: # if testsbase != None
        self.setDocBase(testsbase)
      if not self.args['testsbase']:
        raise(GNULibError(7, None))
      
      # libname => self.args['libname']
      if libname == None:
        self.setLibName(self.cache['libname'])
      else: # if libname != None
        self.setLibName(libname)
      if not self.args['libname']:
        raise(GNULibError(8, None))
      
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
        raise(GNULibError(9, None))
   
  def setDestDir(self, directory):
    '''Specify the target directory. For --import, this specifies where your
    configure.ac can be found. Defaults to current directory.'''
    super(GNULibImport, self).setDestDir(directory)
    
  def addModule(self, module):
    '''Add the module to the modules list.'''
    if type(module) is bytes or type(module) is string:
      if type(module) is bytes:
        module = string(module, ENCS['system'])
      if not super(GNULibImport, self).checkModule(module):
        raise(GNULibError(3, repr(module)))
      self.args['modules'].append(module)
    else: # if module has not bytes or string type
      raise(TypeError(
        'argument must be a string, not %s' % type(module).__name__))
    
  def removeModule(self, module):
    '''Remove the module from the modules list.'''
    if type(module) is bytes or type(module) is string:
      if type(module) is bytes:
        module = string(module, ENCS['system'])
      if not super(GNULibImport, self).checkModule(module):
        raise(GNULibError(3, repr(module)))
      self.args['modules'].remove(module)
    else: # if module has not bytes or string type
      raise(TypeError(
        'argument must be a string, not %s' % type(module).__name__))
    
  def getModules(self):
    '''Return the modules list.'''
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
        except GNULibError as error:
          self.args['modules'] = old_modules
          raise(GNULibError(error.errno, error.errinfo))
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
        module = string(module, ENCS['system'])
      if not super(GNULibImport, self).checkModule(module):
        raise(GNULibError(3, repr(module)))
      self.args['avoids'].append(module)
    else: # if module has not bytes or string type
      raise(TypeError(
        'argument must be a string, not %s' % type(module).__name__))
    
  def removeAvoid(self, module):
    '''Remove the given module from the list of avoided modules.'''
    if type(module) is bytes or type(module) is string:
      if type(module) is bytes:
        module = string(module, ENCS['system'])
      if not super(GNULibImport, self).checkModule(module):
        raise(GNULibError(3, repr(module)))
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
        except GNULibError as error:
          self.args['avoids'] = old_avoids
          raise(GNULibError(error.errno, error.errinfo))
    else: # if type of modules is not list or tuple
      raise(TypeError(
        'modules must be a list or a tuple, not %s' % type(modules).__name__))
    
  def resetAvoids(self):
    '''Reset the list of the avoided modules.'''
    self.setAvoids(self.cache['avoids'])
    
  def checkDryRun(self):
    '''Check if user enabled dry run mode.'''
    return(self.args['dryrun'])
    
  def enableDryRun(self):
    '''Only print what would have been done.'''
    self.args['dryrun'] = True
    
  def disableDryRun(self):
    '''Really execute what shall be done.'''
    self.args['dryrun'] = False
    
  def resetDryRun(self):
    '''Reset default dryrun status.'''
    self.args['dryrun'] = self.cache['dryrun']
    
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
        "invalid LGPL version number: %s" % repr(lgpl)))
    
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

