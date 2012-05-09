#!/usr/bin/python
'''This script is a part of PyGNULib module for gnulib.'''

from __future__ import unicode_literals
################################################################################
# Define global imports
################################################################################
import os
import re
import sys
import locale
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
    modcache=False,
    verbose=0,
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
    if all( # If all conditions inside are True
    [ # If localdir was set and contains 'modules' directory
      self._localdir_,
      os.path.exists(os.path.join(self._localdir_, 'modules')),
      os.path.isdir(os.path.join(self._localdir_, 'modules')),
    ]):
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


################################################################################
# Define GNULibImport class
################################################################################
class GNULibImport(GNULibMode):
  '''GNULibImport class is used to provide methods for --import, --add-import
  and --remove-import actions.'''
  
  def __init__\
  (
    # Don't confuse with those None values; such values will be obtained basing
    # on the values of the previous variables; the another reason is to provide
    # support for Python 2 str type.
    self,
    destdir=None,
    localdir=None,
    modcache=False,
    verbose=0,
    modules=list(),
    avoids=list(),
    tests=list([1]),
    dryrun=False,
    library=None,
    sourcebase=None,
    m4base=None,
    pobase=None,
    docbase=None,
    testsbase=None,
    dependencies=bool(),
    libtool=bool(),
  ):
    '''Create GNULibImport instance. There are some variables which can be
    used in __init__ section. However you can set them later using methods
    inside GNULibImport class. Here are the types for variables:
      destdir: string; default is current directory;
      NOTE: localdir: string; default is ;
      modcache: bool; default is False;
      verbose: -2 <= int <= 2; default is 0;
      modules: list of modules which will be imported; default is empty list;
      avoids: list of modules which will be avoided; default is empty list;
      sourcebase: string; default is destdir + '/lib'; relative;
      m4base: string; default is destdir + '/m4'; relative;
      docbase: string; default is destdir + '/doc'; relative;
      testsbase: string; default is destdir + '/tests'; relative;
      tests: list which contains test codes; default is list([1]);
        you can get all the codes from MODES['tests'] dict;
      NOTE: dependencies: bool; default is received from Makefile.am;'''
    # Get attributes from the parent class
    parent = GNULibMode\
    (
      destdir=destdir,
      localdir=localdir,
      modcache=modcache,
      verbose=verbose,
    )
    self._destdir_ = parent._destdir_
    self._localdir_ = parent._localdir_
    self._modcache_ = parent._modcache_
    self._verbose_ = parent._verbose_
    # dryrun => self._dryrun_
    if type(dryrun) is bool:
      self._dryrun_ = dryrun
    else: # type(dryrun) is not bool
      raise(TypeError(
        'dryrun must be an int, not %s' % type(dryrun).__name__))
    # library => self._library_
    if type(library) is NoneType:
      self._library_ = 'libgnu'
    else: # if type(library) is not NoneType
      if type(library) is bytes or type(library) is string:
        if type(library) is bytes:
          self._library_ = string(library, ENCS['system'])
        elif type(library) is string:
          self._library_ = library
      else:
        raise(TypeError(
          'library must be a string, not %s' % type(library).__name__))
    # sourcebase => self._sourcebase_
    if type(sourcebase) is NoneType:
      self._sourcebase_ = os.path.join(self._destdir_, 'lib')
    else: # if type(sourcebase) is not NoneType
      if type(sourcebase) is bytes or type(sourcebase) is string:
        if type(sourcebase) is bytes:
          self._sourcebase_ = string(sourcebase, ENCS['system'])
        elif type(sourcebase) is string:
          self._sourcebase_ = sourcebase
      else:
        raise(TypeError(
          'sourcebase must be a string, not %s' % type(sourcebase).__name__))
    # m4base => self._m4base_
    if type(m4base) is NoneType:
      self._m4base_ = os.path.join(self._destdir_, 'm4')
    else: # if type(m4base) is not NoneType
      if type(m4base) is bytes or type(m4base) is string:
        if type(m4base) is bytes:
          self._m4base_ = string(m4base, ENCS['system'])
        elif type(m4base) is string:
          self._m4base_ = m4base
      else:
        raise(TypeError(
          'm4base must be a string, not %s' % type(m4base).__name__))
    # pobase => self._pobase_
    if type(pobase) is NoneType:
      self._pobase_ = os.path.join(self._destdir_, 'po')
    else: # if type(pobase) is not NoneType
      if type(pobase) is bytes or type(pobase) is string:
        if type(pobase) is bytes:
          self._pobase_ = string(pobase, ENCS['system'])
        elif type(pobase) is string:
          self._pobase_ = pobase
      else:
        raise(TypeError(
          'pobase must be a string, not %s' % type(pobase).__name__))
    # docbase => self._docbase_
    if type(docbase) is NoneType:
      self._docbase_ = os.path.join(self._destdir_, 'doc')
    else: # if type(docbase) is not NoneType
      if type(docbase) is bytes or type(docbase) is string:
        if type(docbase) is bytes:
          self._docbase_ = string(docbase, ENCS['system'])
        elif type(docbase) is string:
          self._docbase_ = docbase
      else:
        raise(TypeError(
          'docbase must be a string, not %s' % type(docbase).__name__))
    # testsbase => self._testsbase_
    if type(testsbase) is NoneType:
      self._testsbase_ = os.path.join(self._destdir_, 'tests')
    else: # if type(testsbase) is not NoneType
      if type(testsbase) is bytes or type(testsbase) is string:
        if type(testsbase) is bytes:
          self._testsbase_ = string(testsbase, ENCS['system'])
        elif type(testsbase) is string:
          self._testsbase_ = testsbase
      else:
        raise(TypeError(
          'testsbase must be a string, not %s' % type(testsbase).__name__))
    # dependencies => self._dependencies_
    if type(dependencies) is bool:
      self._dependencies_ = dependencies
    else: # type(dryrun) is not bool
      raise(TypeError(
        'dependencies must be a bool, not %s' % type(testsbase).__name__))
    # libtool => self._libtool_
    if type(libtool) is bool:
      self._libtool_ = libtool
    else: # type(dryrun) is not bool
      raise(TypeError(
        'libtool must be a bool, not %s' % type(testsbase).__name__))
    # modules => self._modules_
    if type(modules) is list or type(modules) is tuple:
      self._modules_ = list()
      for module in modules:
        if type(module) is not bytes and type(module) is not string:
          raise(TypeError(
            'every module must be a string, not %s' % type(module).__name__))
        else: # type(module) is bytes or type(module) is string
          if type(module) is bytes:
            module = string(module, ENCS['system'])
          self._modules_.append(module)
    else:
      raise(TypeError(
        'modules must be a list or a tuple, not %s' % type(modules).__name__))
    # avoids => self._avoids_
    if type(avoids) is list or type(avoids) is tuple:
      self._avoids_ = list()
      for module in avoids:
        if type(module) is not bytes and type(module) is not string:
          raise(TypeError(
            'every module must be a string, not %s' % type(module).__name__))
        else: # type(module) is bytes or type(module) is string
          if type(module) is bytes:
            module = string(module, ENCS['system'])
          self._avoids_.append(module)
    else:
      raise(TypeError(
        'avoids must be a list or a tuple, not %s' % type(avoids).__name__))
    
  def setDestDir(self, directory):
    '''Specify the target directory. For --import, this specifies where your
    configure.ac can be found. Defaults to current directory.'''
    super(GNULibImport, self).setDestDir(directory)
    self._sourcebase_ = os.path.join(self._destdir_, 'lib')
    self._m4base_ = os.path.join(self._destdir_, 'm4')
    self._pobase_ = os.path.join(self._destdir_, 'po')
    self._docbase_ = os.path.join(self._destdir_, 'doc')
    self._testsbase_ = os.path.join(self._destdir_, 'tests')
    
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
      for module in modules:
        old_modules = self._modules_
        self._modules_ = list()
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
    self._modules_ = list()
    
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
        library = string(library, ENCS['system'])
      self._library_ = library
    else:
      raise(TypeError(
        'argument must be a string, not %s' % type(module).__name__))
    
  def getSourceBase(self):
    '''Return directory relative to destdir where source code is placed.
    Default value for this variable is 'lib').'''
    return(self._sourcebase_)
    
  def setSourceBase(self, directory):
    '''Specify directory relative to destdir where source code is placed.
    Default value for this variable is 'lib').'''
    if type(directory) is bytes or type(directory) is string:
      if type(directory) is bytes:
        self._sourcebase_ = string(directory, ENCS['system'])
      elif type(directory) is string:
        self._sourcebase_ = directory
    else:
      raise(TypeError(
        'argument must be a string, not %s' % type(directory).__name__))
    
  def resetSourceBase(self):
    '''Return directory relative to destdir where source code is placed.
    Default value for this variable is 'lib').'''
    self._sourcebase_ = os.path.join(self._destdir_, 'lib')
    
  def getM4Base(self):
    '''Return directory relative to destdir where *.m4 macros are placed.
    Default value for this variable is 'm4').'''
    return(self._m4base_)
    
  def setM4Base(self, directory):
    '''Specify directory relative to destdir where *.m4 macros are placed.
    Default value for this variable is 'm4').'''
    if type(directory) is bytes or type(directory) is string:
      if type(directory) is bytes:
        self._m4base_ = string(directory, ENCS['system'])
      elif type(directory) is string:
        self._m4base_ = directory
    else:
      raise(TypeError(
        'argument must be a string, not %s' % type(directory).__name__))
    
  def resetM4Base(self):
    '''Reset directory relative to destdir where *.m4 macros are placed.
    Default value for this variable is 'm4').'''
    self._m4base_ = os.path.join(self._destdir_, 'm4')
    
  def getPoBase(self):
    '''Return directory relative to destdir where *.po files are placed.
    Default value for this variable is 'po').'''
    return(self._pobase_)
    
  def setPoBase(self, directory):
    '''Specify directory relative to destdir where *.po files are placed.
    Default value for this variable is 'po').'''
    if type(directory) is bytes or type(directory) is string:
      if type(directory) is bytes:
        self._pobase_ = string(directory, ENCS['system'])
      elif type(directory) is string:
        self._pobase_ = directory
    else:
      raise(TypeError(
        'argument must be a string, not %s' % type(directory).__name__))
    
  def resetPoBase(self):
    '''Reset directory relative to destdir where *.po files are placed.
    Default value for this variable is 'po').'''
    self._pobase_ = os.path.join(self._destdir_, 'po')
    
  def getDocBase(self):
    '''Return directory relative to destdir where doc files are placed.
    Default value for this variable is 'doc').'''
    return(self._docbase_)
    
  def setDocBase(self, directory):
    '''Specify directory relative to destdir where doc files are placed.
    Default value for this variable is 'doc').'''
    if type(directory) is bytes or type(directory) is string:
      if type(directory) is bytes:
        self._docbase_ = string(directory, ENCS['system'])
      elif type(directory) is string:
        self._docbase_ = directory
    else:
      raise(TypeError(
        'argument must be a string, not %s' % type(directory).__name__))
    
  def resetDocBase(self):
    '''Reset directory relative to destdir where doc files are placed.
    Default value for this variable is 'doc').'''
    self._docbase_ = os.path.join(self._destdir_, 'doc')
    
  def getTestsBase(self):
    '''Return directory relative to destdir where unit tests are placed.
    Default value for this variable is 'tests').'''
    return(self._testsbase_)
    
  def setTestsBase(self, directory):
    '''Specify directory relative to destdir where unit tests are placed.
    Default value for this variable is 'tests').'''
    if type(directory) is bytes or type(directory) is string:
      if type(directory) is bytes:
        self._testsbase_ = string(directory, ENCS['system'])
      elif type(directory) is string:
        self._testsbase_ = directory
    else:
      raise(TypeError(
        'argument must be a string, not %s' % type(directory).__name__))
    
  def resetTestsBase(self):
    '''Reset directory relative to destdir where unit tests are placed.
    Default value for this variable is 'tests').'''
    self._testsbase_ = os.path.join(self._destdir_, 'tests')

