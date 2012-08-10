#!/usr/bin/python
# encoding: UTF-8

#===============================================================================
# Define global imports
#===============================================================================
import os
import re
import sys
import codecs
import shutil
import filecmp
import tempfile
import subprocess as sp
from . import constants
from .GLError import GLError
from .GLConfig import GLConfig


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
# Define GLFileSystem class
#===============================================================================
class GLFileSystem(object):
  '''GLFileSystem class is used to create virtual filesystem, which is based on
  the gnulib directory and directory specified by localdir argument. Its main
  method lookup(file) is used to find file in these directories or combine it
  using Linux 'patch' utility.'''
  
  def __init__(self, config):
    '''Create new GLFileSystem instance. The only argument is localdir,
    which can be an empty string too.'''
    if type(config) is not GLConfig:
      raise(TypeError('config must be a GLConfig, not %s' % \
        type(config).__name__))
    for arg in ['destdir', 'localdir']:
      if not config.check(arg):
        raise(ValueError('%s inside GLConfig must be set' % arg))
    self.config = config
    self.tempdir = tempfile.mkdtemp()
    if type(self.tempdir) is bytes:
      self.tempdir = self.tempdir.decode(ENCS['system'])
    
  def __repr__(self):
    '''x.__repr__ <==> repr(x)'''
    return('<pygnulib.GLFileSystem>')
    
  def lookup(self, name):
    '''GLFileSystem.lookup(name) -> tuple
    
    Lookup a file in gnulib and localdir directories or combine it using Linux
    'patch' utility. If file was found, method returns string, else it raises
    GLError telling that file was not found. Function also returns flag which
    indicates whether file is a temporary file.
    GLConfig: localdir.'''
    if type(name) is bytes or type(name) is string:
      if type(name) is bytes:
        name = name.decode(ENCS['default'])
    else: # if name has not bytes or string type
      raise(TypeError(
        'name must be a string, not %s' % type(module).__name__))
    # If name exists in localdir, then we use it
    path_gnulib = joinpath(DIRS['root'], name)
    path_local = joinpath(self.config['localdir'], name)
    path_diff = joinpath(self.config['localdir'], '%s.diff' % name)
    path_temp = joinpath(self.tempdir, name)
    try: # Try to create directories
      os.makedirs(os.path.dirname(path_temp))
    except OSError as error:
      pass # Skip errors if directory exists
    if isfile(path_temp):
      os.remove(path_temp)
    if self.config['localdir'] and isfile(path_local):
      result = (path_local, False)
    else: # if path_local does not exist
      if isfile(path_gnulib):
        if self.config['localdir'] and isfile(path_diff):
          shutil.copy(path_gnulib, path_temp)
          command = 'patch -s "%s" < "%s"' % (path_temp, path_diff)
          try: # Try to apply patch
            sp.check_call(command, shell=True)
          except sp.CalledProcessError as error:
            raise(GLError(2, name))
          result = (path_temp, True)
        else: # if path_diff does not exist
          result = (path_gnulib, False)
      else: # if path_gnulib does not exist
        raise(GLError(1, name))
    return(result)


#===============================================================================
# Define GLFileAssistant class
#===============================================================================
class GLFileAssistant(object):
  '''GLFileAssistant is used to help with file processing.'''
  
  def __init__(self, config, filesystem, transformers):
    '''Create GLFileAssistant instance.'''
    if type(config) is not GLConfig:
      raise(TypeError('config must be a GLConfig, not %s' % \
        type(config).__name__))
    if type(filesystem) is not GLFileSystem:
      raise(TypeError('filesystem must be a GLFileSystem, not %s' % \
        type(config).__name__))
    for arg in ['destdir', 'localdir']:
      if not config.check(arg):
        raise(ValueError('%s inside GLConfig must be set' % arg))
    self.config = config
    self.filesystem = filesystem
    self.transformers = transformers
    self.original = None
    self.rewritten = None
    self.added = list()
    self.makefile = list()
    
  def setOriginal(self, original):
    '''GLFileAssistant.setOriginal(original)
    
    Set the name of the original file which will be used.'''
    if type(original) is bytes or type(original) is string:
      if type(original) is bytes:
        original = original.decode(ENCS['default'])
    else: # if original has not bytes or string type
      raise(TypeError(
        'original must be a string, not %s' % (type(original).__name__)))
    self.original = original
    
  def setRewritten(self, rewritten):
    '''GLFileAssistant.setRewritten(rewritten)
    
    Set the name of the rewritten file which will be used.'''
    if type(rewritten) is bytes or type(rewritten) is string:
      if type(rewritten) is bytes:
        rewritten = rewritten.decode(ENCS['default'])
    else: # if rewritten has not bytes or string type
      raise(TypeError(
        'rewritten must be a string, not %s' % type(rewritten).__name__))
    self.rewritten = rewritten
    
  def addFile(self, file):
    '''GLFileAssistant.addFile(file)
    
    Add file to the list of added files.'''
    if file not in self.added:
      self.added += [file]
    
  def removeFile(self, file):
    '''GLFileAssistant.removeFile(file)
    
    Remove file from the list of added files.'''
    if file in self.added:
      self.added.pop(file)
    
  def getFiles(self):
    '''Return list of the added files.'''
    return(list(self.added))
    
  def tmpfilename(self, path):
    '''GLFileAssistant.tmpfilename() -> string
    
    Return the name of a temporary file (file is relative to destdir).'''
    if type(path) is bytes or type(path) is string:
      if type(path) is bytes:
        path = path.decode(ENCS['default'])
    else: # if path has not bytes or string type
      raise(TypeError(
        'path must be a string, not %s' % (type(path).__name__)))
    if not self.config['dryrun']:
      # Put the new contents of $file in a file in the same directory (needed
      # to guarantee that an 'mv' to "$destdir/$file" works).
      result = joinpath(self.config['destdir'], '%s.tmp' % path)
      dirname = os.path.dirname(result)
      if dirname and not isdir(dirname):
        os.makedirs(dirname)
    else: # if self.config['dryrun']
      # Put the new contents of $file in a file in a temporary directory
      # (because the directory of "$file" might not exist).
      tempdir = self.filesystem.tempdir
      result = joinpath(tempdir, '%s.tmp' % os.path.basename(path))
      dirname = os.path.dirname(result)
      if not isdir(dirname):
        os.makedirs(dirname)
    if type(result) is bytes:
      result = bytes.decode(ENCS['default'])
    return(result)
    
  def add(self, lookedup, tmpflag, tmpfile):
    '''GLFileAssistant.add(lookedup, tmpflag, tmpfile)
    
    This method copies a file from gnulib into the destination directory.
    The destination is known to exist. If tmpflag is True, then lookedup file
    is a temporary one.'''
    original = self.original
    rewritten = self.rewritten
    for arg in ['symbolic', 'lsymbolic']:
      if not self.config.check(arg):
        raise(ValueError('%s inside GLConfig must be set' % arg))
    destdir = self.config['destdir']
    symbolic = self.config['symbolic']
    lsymbolic = self.config['lsymbolic']
    if original == None:
      raise(TypeError('original must be set before applying the method'))
    elif rewritten == None:
      raise(TypeError('rewritten must be set before applying the method'))
    if not self.config['dryrun']:
      print('Copying file %s' % rewritten)
      loriginal = joinpath(self.config['localdir'], original)
      if (symbolic or (lsymbolic and lookedup == loriginal)) \
      and not tmpflag and filecmp.cmp(lookedup, tmpfile):
        constants.link_if_changed(lookedup, joinpath(destdir, rewritten))
      else: # if any of these conditions is not met
        try: # Try to move file
          shutil.move(tmpfile, joinpath(destdir, rewritten))
        except Exception as error:
          raise(GLError(17, original))
    else: # if self.config['dryrun']
      print('Copy file %s' % rewritten)
    
  def update(self, lookedup, tmpflag, tmpfile, already_present):
    '''GLFileAssistant.update(lookedup, tmpflag, tmpfile, already_present)
    
    This method copies a file from gnulib into the destination directory.
    The destination is known to exist. If tmpflag is True, then lookedup file
    is a temporary one.'''
    original = self.original
    rewritten = self.rewritten
    for arg in ['symbolic', 'lsymbolic']:
      if not self.config.check(arg):
        raise(ValueError('%s inside GLConfig must be set' % arg))
    self.config['destdir']
    symbolic = self.config['symbolic']
    lsymbolic = self.config['lsymbolic']
    if original == None:
      raise(TypeError('original must be set before applying the method'))
    elif rewritten == None:
      raise(TypeError('rewritten must be set before applying the method'))
    if type(lookedup) is bytes or type(lookedup) is string:
      if type(lookedup) is bytes:
        lookedup = lookedup.decode(ENCS['default'])
    else: # if lookedup has not bytes or string type
      raise(TypeError(
        'lookedup must be a string, not %s' % type(lookedup).__name__))
    if type(already_present) is not bool:
      raise(TypeError('already_present must be a bool, not %s' % \
          type(already_present).__name__))
    if not filecmp.cmp(joinpath(self.config['destdir'], rewritten), tmpfile):
      backup = string('%s~' % rewritten)
      if not self.config['dryrun']:
        if already_present:
          print('Updating file %s (backup in %s)' % (rewritten, backup))
        else: # if not already_present
          message = 'Replacing file '
          message += '%s (non-gnulib code backed up in ' % rewritten
          message += '%s) !!' % backup
          print(message)
        try: # Try to replace the given file
          shutil.move(rewritten, '%s~' % rewritten)
        except Exception as error:
          raise(GLError(17, original))
        loriginal = joinpath(self.config['localdir'], original)
        if (symbolic or (lsymbolic and lookedup == loriginal)) \
        and not tmpflag and filecmp.cmp(lookedup, tmpfile):
          constants.link_if_changed(lookedup, joinpath(destdir, rewritten))
        else: # if any of these conditions is not met
          try: # Try to move file
            if exist(rewritten):
              os.remove(rewritten)
            shutil.move(tmpfile, joinpath(destdir, rewritten))
          except Exception as error:
            raise(GLError(17, original))
      else: # if self.config['dryrun']
        if already_present:
          print('Update file %s (backup in %s)' % (rewritten, backup))
        else: # if not already_present
          print('Replace file %s (backup in %s)' % (rewritten, backup))
    
  def add_or_update(self, already_present):
    '''GLFileAssistant.add_or_update(already_present)
    
    This method handles a file that ought to be present afterwards.'''
    original = self.original
    rewritten = self.rewritten
    if original == None:
      raise(TypeError('original must be set before applying the method'))
    elif rewritten == None:
      raise(TypeError('rewritten must be set before applying the method'))
    if type(already_present) is not bool:
      raise(TypeError('already_present must be a bool, not %s' % \
          type(already_present).__name__))
    xoriginal = original
    if original.startswith('tests=lib/'):
      xoriginal = constants.substart('tests=lib/', 'lib/', original)
    lookedup, tmpflag = self.filesystem.lookup(xoriginal)
    tmpfile = self.tmpfilename(rewritten)
    sed_transform_lib_file = self.transformers.get('lib', '')
    sed_transform_build_aux_file = self.transformers.get('aux', '')
    sed_transform_main_lib_file = self.transformers.get('main', '')
    sed_transform_testsrelated_lib_file = self.transformers.get('tests', '')
    try: # Try to copy lookedup file to tmpfile
      shutil.copy(lookedup, tmpfile)
    except Exception as error:
      raise(GLError(15, lookedup))
    transformer = string()
    if original.startswith('lib/'):
      if sed_transform_main_lib_file:
        transformer = sed_transform_main_lib_file
    elif original.startswith('build-aux/'):
      if sed_transform_build_aux_file:
        transformer = sed_transform_build_aux_file
    elif original.startswith('tests=lib/'):
      if sed_transform_testsrelated_lib_file:
        transformer = sed_transform_testsrelated_lib_file
    if transformer:
      args = ['sed', '-e', transformer]
      stdin = codecs.open(lookedup, 'rb', 'UTF-8')
      try: # Try to transform file
        data = sp.check_output(args, stdin=stdin, shell=False)
        data = data.decode(ENCS['shell'])
      except Exception as error:
        raise(GLError(16, lookedup))
      with codecs.open(tmpfile, 'wb', 'UTF-8') as file:
        file.write(data)
    path = joinpath(self.config['destdir'], rewritten)
    if isfile(path):
      self.update(lookedup, tmpflag, tmpfile, already_present)
      os.remove(tmpfile)
    else: # if not isfile(path)
      self.add(lookedup, tmpflag, tmpfile)
      self.addFile(rewritten)
    
  def makefileEditor(self, dir, var, val):
    '''GLFileAssistant.makefileEditor(dir, var, val)
    
    This method is used to remember that ${dir}Makefile.am needs to be edited
    to that ${var} mentions ${val}.'''
    if type(dir) is bytes or type(dir) is string:
      if type(dir) is bytes:
        dir = dir.decode(ENCS['default'])
    else: # if dir has not bytes or string type
      raise(TypeError(
        'dir must be a string, not %s' % (type(dir).__name__)))
    if type(var) is bytes or type(var) is string:
      if type(var) is bytes:
        var = var.decode(ENCS['default'])
    else: # if var has not bytes or string type
      raise(TypeError(
        'var must be a string, not %s' % (type(var).__name__)))
    if type(val) is bytes or type(val) is string:
      if type(val) is bytes:
        val = val.decode(ENCS['default'])
    else: # if val has not bytes or string type
      raise(TypeError(
        'val must be a string, not %s' % (type(val).__name__)))
    dictionary = {'dir': dir, 'var': var, 'val': val}
    self.makefile += [dictionary]
    
  def makefileTable(self):
    '''GLFileAssistant.makefileTable() -> list()
    
    Return list of Makefile.am mappings.'''
    return(list(self.makefile))
    
  def makefileParentDir(self, makefile_am):
    '''GLFileAssistant.makefileParentDir()
    
    Add a special row to Makefile.am table with the first parent directory
    which contains or will contain Makefile.am file.
    GLConfig: sourcebase, m4base, testsbase, testflags, makefile.'''
    for arg in ['sourcebase', 'm4base', 'testsbase', 'testflags']:
      if not self.config.check(arg):
        raise(ValueError('%s inside GLConfig must be set' % arg))
    m4base = self.config['makefile']
    sourcebase = self.config['sourcebase']
    testsbase = self.config['testsbase']
    inctests = TESTS['tests'] in self.config['testflags']
    dir1 = string('%s%s' % (m4base, os.path.sep))
    mfd = string('Makefile.am')
    mfx = self.config['makefile']
    dir2 = string()
    while dir1 and \
    (joinpath(self.config['destdir'], dir1, mfd) or \
    joinpath(dir1, mfd) == joinpath(sourcebase, mfx) or \
    (inctests and joinpath(dir1, mfd) == joinpath(testsbase, mfx))):
      dir2 = os.path.basename(dir2)
      dir1 = os.path.dirname(dir1)
    self.makefileEditor(dir1, 'EXTRA_DIST', joinpath(dir2, 'gnulib-cache.m4'))

