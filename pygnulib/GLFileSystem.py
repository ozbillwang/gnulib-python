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
from io import BytesIO
import subprocess as sp
from . import constants
from .GLError import GLError


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
  
  def __init__(self, localdir=''):
    '''Create new GLFileSystem instance. The only argument is localdir,
    which can be an empty string too.'''
    self.args = dict()
    if type(localdir) is bytes or type(localdir) is string:
      if type(localdir) is bytes:
        localdir = localdir.decode(ENCS['default'])
      self.localdir = localdir
    else: # if localdir has not bytes or string type
      raise(TypeError(
        'localdir must be a string, not %s' % type(localdir).__name__))
    
  def __repr__(self):
    '''x.__repr__ <==> repr(x)'''
    return('<pygnulib.GLFileSystem>')
    
  def lookup(self, name):
    '''GLFileSystem.lookup(name) -> string
    
    Lookup a file in gnulib and localdir directories or combine it using Linux
    'patch' utility. If file was found, method returns string, else it raises
    GLError telling that file was not found.'''
    if type(name) is bytes or type(name) is string:
      if type(name) is bytes:
        name = name.decode(ENCS['default'])
    else: # if name has not bytes or string type
      raise(TypeError(
        'name must be a string, not %s' % type(module).__name__))
    # If name exists in localdir, then we use it
    path_gnulib = joinpath(DIRS['root'], name)
    path_local = joinpath(self.localdir, name)
    path_diff = joinpath(self.localdir, '%s.diff' % name)
    path_temp = joinpath(tempfile.mkdtemp(), name)
    os.makedirs(os.path.dirname(path_temp))
    if self.localdir and isfile(path_local):
      result = (path_local, False)
    else: # if path_local does not exist
      if isfile(path_gnulib):
        if self.localdir and isfile(path_diff):
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
  
  def __init__(self, destdir, localdir, transformers,
    symbolic=False, lsymbolic=False, dryrun=False):
    '''Create GLFileAssistant instance.'''
    if type(destdir) is bytes or type(destdir) is string:
      if type(destdir) is bytes:
        destdir = destdir.decode(ENCS['default'])
    else: # if destdir has not bytes or string type
      raise(TypeError(
        'destdir must be a string, not %s' % (type(destdir).__name__)))
    if type(localdir) is bytes or type(localdir) is string:
      if type(localdir) is bytes:
        localdir = localdir.decode(ENCS['default'])
    else: # if localdir has not bytes or string type
      raise(TypeError(
        'localdir must be a string, not %s' % (type(localdir).__name__)))
    for transformer in transformers:
      if type(transformers[transformer]) is not string:
        raise(TypeError('each transformer must be a string instance'))
    if type(symbolic) is not bool:
      raise(TypeError(
        'symbolic must be a bool, not %s' % type(symbolic).__name__))
    if type(lsymbolic) is not bool:
      raise(TypeError(
        'lsymbolic must be a bool, not %s' % type(lsymbolic).__name__))
    if type(dryrun) is not bool:
      raise(TypeError(
        'dryrun must be a bool, not %s' % type(dryrun).__name__))
    self.tempdir = tempfile.mkdtemp()
    self.destdir = destdir
    self.localdir = localdir
    self.symbolic = symbolic
    self.lsymbolic = lsymbolic
    self.dryrun = dryrun
    self.transformers = transformers
    self.filesystem = GLFileSystem(localdir)
    self.original = None
    self.rewritten = None
    
  def setOriginal(self, file):
    '''Set the name of the original file which will be used.'''
    if type(original) is bytes or type(original) is string:
      if type(original) is bytes:
        original = original.decode(ENCS['default'])
    else: # if original has not bytes or string type
      raise(TypeError(
        'original must be a string, not %s' % (type(original).__name__)))
    self.original = original
    
  def setRewritten(self, file):
    '''Set the name of the rewritten file which will be used.'''
    if type(rewritten) is bytes or type(rewritten) is string:
      if type(rewritten) is bytes:
        rewritten = rewritten.decode(ENCS['default'])
    else: # if rewritten has not bytes or string type
      raise(TypeError(
        'rewritten must be a string, not %s' % type(rewritten).__name__))
    self.rewritten = rewritten
    
  def tmpfilename(self, path):
    '''Determine the name of a temporary file (file is relative to destdir).'''
    if type(path) is bytes or type(path) is string:
      if type(path) is bytes:
        path = path.decode(ENCS['default'])
    else: # if path has not bytes or string type
      raise(TypeError(
        'path must be a string, not %s' % (type(path).__name__)))
    if not self.dryrun:
      # Put the new contents of $file in a file in the same directory (needed
      # to guarantee that an 'mv' to "$destdir/$file" works).
      result = joinpath(self.destdir, '%s.tmp' % path)
    else: # if dryrun
      # Put the new contents of $file in a file in a temporary directory
      # (because the directory of "$file" might not exist).
      result = joinpath(self.tempdir, '%s.tmp' % os.path.basename(path))
    if type(result) is bytes:
      result = bytes.decode(ENCS['default'])
    return(result)
    
  def add(self, original, rewritten, lookedup, tmpflag):
    '''This method copies a file from gnulib into the destination directory.
    The destination is known to exist. If tmpflag is True, then lookedup file
    is a temporary one.'''
    original = self.original
    rewritten = self.rewritten
    if original == None:
      raise(TypeError('original must be set before applying the method'))
    elif rewritten == None:
      raise(TypeError('rewritten must be set before applying the method'))
    # TODO: finish this method
    
  def update(self, lookedup, tmpflag, tmpfile, already_present):
    '''This method copies a file from gnulib into the destination directory.
    The destination is known to exist. If tmpflag is True, then lookedup file
    is a temporary one.'''
    original = self.original
    rewritten = self.rewritten
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
    if not filecmp.cmp(joinpath(self.destdir, rewritten), tmpfile):
      if not self.dryrun:
        if already_present:
          print('Updating file %s (backup in %s~)' % (rewritten, rewritten))
        else: # if not already_present
          message = 'Replacing file '
          message += '%s (non-gnulib code backed up in ' % rewritten
          message += '%s~) !!' % rewritten
          print(message)
        try: # Try to replace the given file
          shutil.move(rewritten, '%s~' % rewritten)
        except Exception as error:
          raise(GLError(17, rewritten))
        loriginal = joinpath(self.localdir, original)
        if (symbolic or (symbolic and lookedup == loriginal) \
        and not tmpflag and filecmp(joinpath(lookedup, tmpfile)):
          # TODO: finish this method
    
  def add_or_update(self, already_present):
    '''This method handles a file that ought to be present afterwards.'''
    original = self.original
    rewritten = self.rewritten
    if original == None:
      raise(TypeError('original must be set before applying the method'))
    elif rewritten == None:
      raise(TypeError('rewritten must be set before applying the method'))
    if type(already_present) is not bool:
      raise(TypeError('already_present must be a bool, not %s' % \
          type(already_present).__name__))
    if original.startswith('tests=lib/'):
      xoriginal = substart('tests=lib/', 'lib/', original)
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
      args = ['sed', '-e', transformer, lookedup]
      try: # Try to transform file
        data = sp.check_output(args, shell=True)
      except Exception as error:
        raise(GLError(16, lookedup))
      with codecs.open(tmpfile, 'wb', 'UTF-8') as file:
        file.write(data)
    if isfile(joinpath(self.destdir, rewritten)):
      self.update(self, lookedup, tmpflag, tmpfile, already_present)
    else: # if not isfile(joinpath(self.destdir, rewritten))
      self.add()