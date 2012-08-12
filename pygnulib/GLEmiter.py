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
import subprocess as sp
from . import constants
from .GLInfo import GLInfo
from .GLError import GLError
from .GLConfig import GLConfig
from .GLModuleSystem import GLModuleTable
from .GLMakefileTable import GLMakefileTable


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
# Define GLEmiter class
#===============================================================================
class GLEmiter(object):
  '''This class is used to emit the contents of necessary files.'''
  
  def __init__(self, config):
    '''GLEmiter.__init__(config) -> GLEmiter
    
    Create GLEmiter instance.'''
    self.info = GLInfo()
    if type(config) is not GLConfig:
      raise(TypeError('config must have GLConfig type, not %s' % \
        type(config).__name__))
    self.config = config
    
  def __repr__(self):
    '''x.__repr__() <==> repr(x)'''
    result = '<pygnulib.GLEmiter %s>' % hex(id(self))
    return(result)
    
  def copyright_notice(self):
    '''GLEmiter.copyright_notice() -> string
    
    Emit a header for a generated file.'''
    emit = string()
    emit += "# %s" % self.info.copyright()
    emit += """
#
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
# Generated by gnulib-tool.\n"""
    if type(emit) is bytes:
      emit = emit.decode(ENCS['default'])
    return(constants.nlconvert(emit))
    
  def gnulib_cache(self, moduletable, actioncmd):
    '''GLEmiter.gnulib_cache(actioncmd) -> string
    
    Emit the contents of generated $m4base/gnulib-cache.m4 file.
    GLConfig: destdir, localdir, tests, sourcebase, m4base, pobase, docbase,
    testsbase, conddeps, libtool, macro_prefix, podomain, vc_files.'''
    if type(moduletable) is not GLModuleTable:
      raise(TypeError('moduletable must have GLModuleTable type, not %s' % \
        type(moduletable).__name__))
    if type(actioncmd) is bytes or type(actioncmd) is string:
      if type(actioncmd) is bytes:
        actioncmd = actioncmd.decode(ENCS['default'])
    else: # if actioncmd has not bytes or string type
      raise(TypeError('actioncmd must have string type, not %s' % \
        type(actioncmd).__name__))
    emit = string()
    destdir = self.config['destdir']
    localdir = self.config['localdir']
    testflags = list(self.config['testflags'])
    sourcebase = self.config['sourcebase']
    m4base = self.config['m4base']
    pobase = self.config['pobase']
    docbase = self.config['docbase']
    testsbase = self.config['testsbase']
    lgpl = self.config['lgpl']
    libname = self.config['libname']
    makefile = self.config['makefile']
    conddeps = self.config['conddeps']
    libtool = self.config['libtool']
    macro_prefix = self.config['macro_prefix']
    podomain = self.config['podomain']
    witness_c_macro = self.config['witness_c_macro']
    vc_files = self.config['vc_files']
    emit += self.copyright_notice()
    emit += '''#
# This file represents the specification of how gnulib-tool is used.
# It acts as a cache: It is written and read by gnulib-tool.
# In projects that use version control, this file is meant to be put under
# version control, like the configure.ac and various Makefile.am files.


# Specification in the form of a command-line invocation:
#   %s

# Specification in the form of a few \
gnulib-tool.m4 macro invocations:\n''' % actioncmd
    if not localdir or localdir.startswith('/'):
      relative_localdir = localdir
    else: # if localdir or not localdir.startswith('/')
      relative_localdir = constants.relativize(destdir, localdir)
    emit += 'gl_LOCAL_DIR([%s])\n' % relative_localdir
    emit += 'gl_MODULES([\n'
    emit += '  %s\n' % '\n  '.join(modules)
    emit += '])\n'
    if self.config.checkTestFlag(TESTS['obsolete']):
      emit += 'gl_WITH_OBSOLETE\n'
    if self.config.checkTestFlag(TESTS['cxx-tests']):
      emit += 'gl_WITH_CXX_TESTS\n'
    if self.config.checkTestFlag(TESTS['privileged-tests']):
      emit += 'gl_WITH_PRIVILEGED_TESTS\n'
    if self.config.checkTestFlag(TESTS['unportable-tests']):
      emit += 'gl_WITH_UNPORTABLE_TESTS\n'
    if self.config.checkTestFlag(TESTS['all-tests']):
      emit += 'gl_WITH_ALL_TESTS\n'
    emit += 'gl_AVOID([%s])\n' % ' '.join(avoids)
    emit += 'gl_SOURCE_BASE([%s])\n' % sourcebase
    emit += 'gl_M4_BASE([%s])\n' % m4base
    emit += 'gl_PO_BASE([%s])\n' % pobase
    emit += 'gl_DOC_BASE([%s])\n' % docbase
    emit += 'gl_TESTS_BASE([%s])\n' % testsbase
    if self.config.checkTestFlag(TESTS['tests']):
      emit += 'gl_WITH_TESTS\n'
    emit += 'gl_LIB([%s])\n' % libname
    if lgpl != False:
      if lgpl == True:
        emit += 'gl_LGPL\n'
      else: # if lgpl != True
        emit += 'gl_LGPL([%d])\n' % lgpl
    emit += 'gl_MAKEFILE_NAME([%s])\n' % makefile
    if conddeps:
      emit += 'gl_CONDITIONAL_DEPENDENCIES\n'
    if libtool:
      emit += 'gl_LIBTOOL\n'
    emit += 'gl_MACRO_PREFIX([%s])\n' % macro_prefix
    emit += 'gl_PO_DOMAIN([%s])\n' % podomain
    emit += 'gl_WITNESS_C_DOMAIN([%s])\n' % witness_c_macro
    if vc_files:
      emit += 'gl_VC_FILES([%s])\n' % vc_files
    if type(emit) is bytes:
      emit = emit.decode(ENCS['default'])
    return(constants.nlconvert(emit))
    
  def gnulib_comp(self, moduletable):
    '''GLEmiter.gnulib_comp() -> string
    
    Emit the contents of generated $m4base/gnulib-comp.m4 file.
    GLConfig: destdir, localdir, tests, sourcebase, m4base, pobase, docbase,
    testsbase, conddeps, libtool, macro_prefix, podomain, vc_files.'''
    if type(moduletable) is not GLModuleTable:
      raise(TypeError('moduletable must have GLModuleTable type, not %s' % \
        type(moduletable).__name__))
    
  def po_Makevars(self):
    '''GLEmiter.po_Makevars() -> string
    
    Emit the contents of po/ makefile parameterization.
    GLConfig: pobase, podomain.'''
    emit = string()
    pobase = self.config['pobase']
    podomain = self.config['podomain']
    top_subdir = string()
    source = '%s/' % os.path.normpath(pobase)
    if os.path.sep in source:
      for directory in source.split(os.path.sep):
        if directory != '':
          top_subdir += '../'
    top_subdir = os.path.normpath(top_subdir)
    emit += "## DO NOT EDIT! GENERATED AUTOMATICALLY!\n"
    emit += "%s\n" % self.copyright_notice()
    emit += "# Usually the message domain is the same as the package name.\n"
    emit += "# But here it has a '-gnulib' suffix.\n"
    emit += "DOMAIN = %s-gnulib\n\n" % podomain
    emit += "# These two variables depend on the location of this directory.\n"
    emit += "subdir = %s\n" % pobase
    emit += "top_subdir = %s\n" % top_subdir
    emit += """
# These options get passed to xgettext.
XGETTEXT_OPTIONS = \\
  --keyword=_ --flag=_:1:pass-c-format \\
  --keyword=N_ --flag=N_:1:pass-c-format \\
  --keyword='proper_name:1,"This is a proper name. See the gettext manual, \
section Names."' \\
  --keyword='proper_name_utf8:1,"This is a proper name. See the gettext \
manual, section Names."' \\
  --flag=error:3:c-format --flag=error_at_line:5:c-format

# This is the copyright holder that gets inserted into the header of the
# $(DOMAIN).pot file.  gnulib is copyrighted by the FSF.
COPYRIGHT_HOLDER = Free Software Foundation, Inc.

# This is the email address or URL to which the translators shall report
# bugs in the untranslated strings:
# - Strings which are not entire sentences, see the maintainer guidelines
#   in the GNU gettext documentation, section 'Preparing Strings'.
# - Strings which use unclear terms or require additional context to be
#   understood.
# - Strings which make invalid assumptions about notation of date, time or
#   money.
# - Pluralisation problems.
# - Incorrect English spelling.
# - Incorrect formatting.
# It can be your email address, or a mailing list address where translators
# can write to without being subscribed, or the URL of a web page through
# which the translators can contact you.
MSGID_BUGS_ADDRESS = bug-gnulib@gnu.org

# This is the list of locale categories, beyond LC_MESSAGES, for which the
# message catalogs shall be used.  It is usually empty.
EXTRA_LOCALE_CATEGORIES =

# This tells whether the $(DOMAIN).pot file contains messages with an 'msgctxt'
# context.  Possible values are "yes" and "no".  Set this to yes if the
# package uses functions taking also a message context, like pgettext(), or
# if in $(XGETTEXT_OPTIONS) you define keywords with a context argument.
USE_MSGCTXT = no\n"""
    if type(emit) is bytes:
      emit = emit.decode(ENCS['default'])
    return(constants.nlconvert(emit))
    
  def po_POTFILES_in(self, files):
    '''GLEmiter.po_POTFILES_in(files) -> string
    
    Emit the file list to be passed to xgettext.
    GLConfig: sourcebase.'''
    emit = string()
    sourcebase = self.config['sourcebase']
    sourcebase = '%s%s' % (self.sourcebase, os.path.sep)
    if type(sourcebase) is bytes:
      sourcebase = sourcebase.decode(ENCS['default'])
    files = [substart('lib/', sourcebase, file) for file in files]
    files = [file for file in files if file.startswith(sourcebase)]
    emit += "## DO NOT EDIT! GENERATED AUTOMATICALLY!\n"
    emit += "%s\n" % self.copyright_notice()
    emit += "# List of files which contain translatable strings.\n"
    emit += '\n'.join(files)
    emit += '\n'
    if type(emit) is bytes:
      emit = emit.decode(ENCS['default'])
    return(constants.nlconvert(emit))
    
  def initmacro_start(self):
    '''GLEmiter.initmacro_done() -> string
    
    Emit the first few statements of the gl_INIT macro.
    GLConfig: macro_prefix.'''
    emit = string()
    macro_prefix = self.config['macro_prefix']
    # Overriding AC_LIBOBJ and AC_REPLACE_FUNCS has the effect of storing
    # platform-dependent object files in ${macro_prefix_arg}_LIBOBJS instead
    # of LIBOBJS. The purpose is to allow several gnulib instantiations under
    # a single configure.ac file. (AC_CONFIG_LIBOBJ_DIR does not allow this
    # flexibility).
    # Furthermore it avoids an automake error like this when a Makefile.am
    # that uses pieces of gnulib also uses $(LIBOBJ):
    #   automatically discovered file `error.c' should not be explicitly
    #   mentioned.
    emit += "  m4_pushdef([AC_LIBOBJ],"
    emit += " m4_defn([%V1%_LIBOBJ]))\n"
    emit += "  m4_pushdef([AC_REPLACE_FUNCS],"
    emit += " m4_defn([%V1%_REPLACE_FUNCS]))\n"
    # Overriding AC_LIBSOURCES has the same purpose of avoiding the automake
    # error when a Makefile.am that uses pieces of gnulib also uses $(LIBOBJ):
    #   automatically discovered file `error.c' should not be explicitly
    #   mentioned
    # We let automake know about the files to be distributed through the
    # EXTRA_lib_SOURCES variable.
    emit += "  m4_pushdef([AC_LIBSOURCES],"
    emit += " m4_defn([%V1%_LIBSOURCES]))\n"
    # Create data variables for checking the presence of files that are
    # mentioned as AC_LIBSOURCES arguments. These are m4 variables, not shell
    # variables, because we want the check to happen when the configure file is
    # created, not when it is run. ${macro_prefix_arg}_LIBSOURCES_LIST is the
    # list of files to check for. ${macro_prefix_arg}_LIBSOURCES_DIR is the
    # subdirectory in which to expect them.
    emit += "  m4_pushdef([%V1%_LIBSOURCES_LIST], [])\n"
    emit += "  m4_pushdef([%V1%_LIBSOURCES_DIR], [])\n"
    emit += "  gl_COMMON\n"
    emit = emit.replace('%V1%', macro_prefix)
    if type(emit) is bytes:
      emit = emit.decode(ENCS['default'])
    return(constants.nlconvert(emit))
    
  def initmacro_end(self):
    '''GLEmiter.initmacro_done() -> string
    
    Emit the last few statements of the gl_INIT macro.
    GLConfig: macro_prefix.'''
    emit = string()
    macro_prefix = self.config['macro_prefix']
    # Check the presence of files that are mentioned as AC_LIBSOURCES
    # arguments. The check is performed only when autoconf is run from the
    # directory where the configure.ac resides; if it is run from a different
    # directory, the check is skipped.
    emit += """\
  m4_ifval(%V1%_LIBSOURCES_LIST, [
    m4_syscmd([test ! -d ]m4_defn([%V1%_LIBSOURCES_DIR])[ ||
      for gl_file in ]%V1%_LIBSOURCES_LIST[ ; do
        if test ! -r ]m4_defn([%V1%_LIBSOURCES_DIR])[/$gl_file ; then
          echo "missing file ]m4_defn([%V1%_LIBSOURCES_DIR])[/$gl_file" >&2
          exit 1
        fi
      done])dnl
      m4_if(m4_sysval, [0], [],
        [AC_FATAL([expected source file, required through AC_LIBSOURCES, not \
found])])
  ])
  m4_popdef([%V1%_LIBSOURCES_DIR])
  m4_popdef([%V1%_LIBSOURCES_LIST])
  m4_popdef([AC_LIBSOURCES])
  m4_popdef([AC_REPLACE_FUNCS])
  m4_popdef([AC_LIBOBJ])
  AC_CONFIG_COMMANDS_PRE([
    %V1%_libobjs=
    %V1%_ltlibobjs=
    if test -n "$%V1%_LIBOBJS"; then
      # Remove the extension.
      sed_drop_objext='s/\.o$//;s/\.obj$//'
      for i in `for i in $%V1%_LIBOBJS; do echo "$i"; done | sed -e \
"$sed_drop_objext" | sort | uniq`; do
        %V1%_libobjs="$%V1%_libobjs $i.$ac_objext"
        %V1%_ltlibobjs="$%V1%_ltlibobjs $i.lo"
      done
    fi
    AC_SUBST([%V1%_LIBOBJS], [$%V1%_libobjs])
    AC_SUBST([%V1%_LTLIBOBJS], [$%V1%_ltlibobjs])
  ])\n"""
    emit = emit.replace('%V1%', macro_prefix)
    if type(emit) is bytes:
      emit = emit.decode(ENCS['default'])
    return(constants.nlconvert(emit))
    
  def initmacro_done(self):
    '''GLEmiter.initmacro_done() -> string
    
    Emit a few statements after the gl_INIT macro.
    GLConfig: sourcebase, macro_prefix.'''
    emit = string()
    sourcebase = self.config['sourcebase']
    macro_prefix = self.config['macro_prefix']
    emit += """\

# Like AC_LIBOBJ, except that the module name goes
# into %V1%_LIBOBJS instead of into LIBOBJS.
AC_DEFUN([%V1%_LIBOBJ], [
  AS_LITERAL_IF([$1], [%V1%_LIBSOURCES([$1.c])])dnl
  %V1%_LIBOBJS="$%V1%_LIBOBJS $1.$ac_objext"
])

# Like AC_REPLACE_FUNCS, except that the module name goes
# into %V1%_LIBOBJS instead of into LIBOBJS.
AC_DEFUN([%V1%_REPLACE_FUNCS], [
  m4_foreach_w([gl_NAME], [$1], [AC_LIBSOURCES(gl_NAME[.c])])dnl
  AC_CHECK_FUNCS([$1], , [%V1%_LIBOBJ($ac_func)])
])

# Like AC_LIBSOURCES, except the directory where the source file is
# expected is derived from the gnulib-tool parameterization,
# and alloca is special cased (for the alloca-opt module).
# We could also entirely rely on EXTRA_lib..._SOURCES.
AC_DEFUN([%V1%_LIBSOURCES], [
  m4_foreach([_gl_NAME], [$1], [
    m4_if(_gl_NAME, [alloca.c], [], [
      m4_define([%V1%_LIBSOURCES_DIR], [%V2%])
      m4_append([%V1%_LIBSOURCES_LIST], _gl_NAME, [ ])
    ])
  ])
])\n"""
    emit = emit.replace('%V1%', macro_prefix)
    emit = emit.replace('%V2%', sourcebase)
    if type(emit) is bytes:
      emit = emit.decode(ENCS['default'])
    return(constants.nlconvert(emit))
    
  def lib_Makefile_am(self, destfile,
    moduletable, makefiletable, actioncmd, for_test):
    '''GLEmiter.lib_Makefile_am(destfile, moduletable, makefiletable,
         actioncmd, for_test) -> string
    
    Emits the contents of library makefile.
    GLConfig: localdir, libname, pobase, auxdir, makefile, libtool,
    macro_prefix, podomain, conddeps, witness_c_macro.'''
    if type(destfile) is bytes or type(destfile) is string:
      if type(destfile) is bytes:
        destfile = destfile.decode(ENCS['default'])
    else: # if destfile has not bytes or string type
      raise(TypeError('destfile must be a string, not %s' % \
        type(destfile).__name__))
    if type(moduletable) is not GLModuleTable:
      raise(TypeError('moduletable must be a GLModuleTable, not %s' % \
        type(moduletable).__name__))
    if type(makefiletable) is not GLMakefileTable:
      raise(TypeError('makefiletable must be a GLMakefileTable, not %s' % \
        type(makefiletable).__name__))
    if type(actioncmd) is bytes or type(actioncmd) is string:
      if type(actioncmd) is bytes:
        actioncmd = actioncmd.decode(ENCS['default'])
    else: # if actioncmd has not bytes or string type
      raise(TypeError('actioncmd must be a string, not %s' % \
        type(actioncmd).__name__))
    if type(for_test) is not bool:
      raise(TypeError('for_test must be a bool, not %s' % \
        type(for_test).__name__))
    emit = string()
    localdir = self.config['localdir']
    modcache = self.config['modcache']
    libname = self.config['libname']
    pobase = self.config['pobase']
    auxdir = self.config['auxdir']
    makefile = self.config['makefile']
    libtool = self.config['libtool']
    macro_prefix = self.config['macro_prefix']
    podomain = self.config['podomain']
    conddeps = self.config['conddeps']
    witness_c_macro = self.config['witness_c_macro']
    include_guard_prefix = self.config['include_guard_prefix']
    ac_version = self.config['ac_version']
    destfile = os.path.normpath(destfile)
    # When creating an includable Makefile.am snippet, augment variables with
    # += instead of assigning them.
    if makefile:
      assign = '+='
    else: # if not makefile
      assign = '='
    if libtool:
      libext = 'la'
      perhapsLT = 'LT'
      repl_LD_flags = False
    else: # if not libtool
      libext = 'a'
      perhapsLT = ''
      repl_LD_flags = True
    if for_test:
      # When creating a package for testing: Attempt to provoke failures,
      # especially link errors, already during "make" rather than during
      # "make check", because "make check" is not possible in a cross-compiling
      # situation. Turn check_PROGRAMS into noinst_PROGRAMS.
      repl_check_PROGRAMS = True
    else: # if not for_test
      repl_check_PROGRAMS = False
    emit += "## DO NOT EDIT! GENERATED AUTOMATICALLY!\n"
    emit += "## Process this file with automake to produce Makefile.in.\n"
    emit += self.copyright_notice()
    if actioncmd:
      if len(actioncmd) <= 3000:
        emit += "# Reproduce by: %s\n" % actioncmd
    emit += '\n'
    uses_subdirs = False
    
    # Modify allsnippets variable.
    allsnippets = string()
    for module in moduletable['main']:
      # Get conditional snippet, edit it and save to amsnippet1.
      amsnippet1 = module.getAutomakeSnippet_Conditional()
      amsnippet1 = amsnippet1.replace('lib_LIBRARIES', 'lib%_LIBRARIES')
      amsnippet1 = amsnippet1.replace('lib_LTLIBRARIES', 'lib%_LTLIBRARIES')
      if repl_LD_flags:
        pattern = compiler('lib_LDFLAGS[\t ]*\\+=(.*?)$', re.S | re.M)
        amsnippet1 = pattern.sub('', amsnippet1)
      pattern = compiler('lib_([A-Z][A-Z](?:.*?))', re.S | re.M)
      amsnippet1 = pattern.sub('%s_%s_\\1' % (libname, libext), amsnippet1)
      amsnippet1 = amsnippet1.replace('lib%_LIBRARIES', 'lib_LIBRARIES')
      amsnippet1 = amsnippet1.replace('lib%_LTLIBRARIES', 'lib_LTLIBRARIES')
      amsnippet1 = amsnippet1.replace('${gl_include_guard_prefix}',
        include_guard_prefix)
      if str(module) == 'alloca':
        amsnippet1 += '%s_%s_LIBADD += @%sALLOCA@\n' % \
          (libname, libext, perhapsLT)
        amsnippet1 += '%s_%s_DEPENDENCIES += @%sALLOCA@\n' % \
          (libname, libext, perhapsLT)
      
      # Get unconditional snippet, edit it and save to amsnippet1.
      amsnippet2 = module.getAutomakeSnippet_Unconditional()
      pattern = compiler('lib_([A-Z][A-Z](?:.*?))', re.S | re.M)
      amsnippet2 = pattern.sub('%s_%s_\\1' % (libname, libext), amsnippet2)
      if type(amsnippet1) is bytes:
        amsnippet1 = amsnippet1.decode(ENCS['default'])
      if type(amsnippet2) is bytes:
        amsnippet2 = amsnippet1.decode(ENCS['default'])
      if not (amsnippet1 +amsnippet2).isspace():
        allsnippets += '## begin gnulib module %s\n' % str(module)
        if conddeps:
          if moduletable.isConditional(module):
            name = module.getConditionalName()
            allsnippets += 'if %s\n' % name
        allsnippets += amsnippet1
        if conddeps:
          allsnippets += 'endif\n'
        allsnippets += amsnippet2
        allsnippets += '## end   gnulib module %s\n\n' % str(module)
        
        # Test whether there are some source files in subdirectories.
        for file in module.getFiles():
          if file.startswith('lib/') and file.endswith('.c') and \
          file.count('/') > 1:
            uses_subdirs = True
            break
    if not makefile:
      subdir_options = string()
      # If there are source files in subdirectories, prevent collision of the
      # object files (example: hash.c and libxml/hash.c).
      if uses_subdirs:
        subdir_options = string(' subdir-objects')
      emit += 'AUTOMAKE_OPTIONS = 1.5 gnits%s\n' % subdir_options
    emit += '\n'
    if not makefile:
      emit += 'SUBDIRS =\n'
      emit += 'noinst_HEADERS =\n'
      emit += 'noinst_LIBRARIES =\n'
      emit += 'noinst_LTLIBRARIES =\n'
      # Automake versions < 1.11.4 create an empty pkgdatadir at
      # installation time if you specify pkgdata_DATA to empty.
      # See automake bugs #10997 and #11030:
      #  * http://debbugs.gnu.org/10997
      #  * http://debbugs.gnu.org/11030
      # So we need this workaround.
      pattern = compiler('^pkgdata_DATA *\\+=', re.S | re.M)
      if pattern.findall(allsnippets):
        emit += 'pkgdata_DATA =\n'
      emit += 'EXTRA_DIST =\n'
      emit += 'BUILT_SOURCES =\n'
      emit += 'SUFFIXES =\n'
    emit += 'MOSTLYCLEANFILES %s core *.stackdump\n' % assign
    if not makefile:
      emit += 'MOSTLYCLEANDIRS =\n'
      emit += 'CLEANFILES =\n'
      emit += 'DISTCLEANFILES =\n'
      emit += 'MAINTAINERCLEANFILES =\n'
    
    # Execute edits that apply to the Makefile.am being generated.
    current_edit = int()
    makefile_am_edits = makefiletable.count()
    while current_edit != makefile_am_edits:
      dictionary = makefiletable[current_edit]
      if dictionary['var']:
        paths = list()
        paths += [joinpath(dictionary['dir'], 'Makefile.am')]
        paths += [os.path.normpath('./%s/Makefile.am' % dictionary['dir'])]
        paths = sorted(set(paths))
        if destfile in paths:
          emit += '%s += %s\n' % (dictionary['var'], dictionary['val'])
      current_edit += 1
    
    # Define two parts of cppflags variable.
    emit += '\n'
    cppflags_part1 = string()
    cppflags_part2 = string()
    if witness_c_macro:
      cppflags_part1 = ' -D%s=1' % witness_c_macro
    if for_test:
      cppflags_part2 = ' -DGNULIB_STRICT_CHECKING=1'
    cppflags = '%s%s' % (cppflags_part1, cppflags_part2)
    if not makefile:
      emit += 'AM_CPPFLAGS =%s\n' % cppflags
      emit += 'AM_CFLAGS =\n'
    else: # if makefile
      if cppflags:
        emit += 'AM_CPPFLAGS +=%s\n' % cppflags
    emit += '\n'
    
    # TODO: MAKE THIS HORRIBLE CHECK
    # grep "^[a-zA-Z0-9_]*_${perhapsLT}LIBRARIES...
    
    emit += '\n'
    emit += '%s_%s_SOURCES =\n' % (libname, libext)
    # Here we use $(LIBOBJS), not @LIBOBJS@. The value is the same. However,
    # automake during its analysis looks for $(LIBOBJS), not for @LIBOBJS@.
    emit += '%s_%s_LIBADD = $(%s_%sLIBOBJS)\n' % \
      (libname, libext, macro_prefix, perhapsLT)
    emit += '%s_%s_DEPENDENCIES = $(%s_%sLIBOBJS)' % \
      (libname, libext, macro_prefix, perhapsLT)
    emit += 'EXTRA_%s_%s_SOURCES =\n' % (libname, libext)
    if libtool:
      emit += '%s_%s_LDFLAGS = $(AM_LDFLAGS)\n' % (libname, libext)
      emit += '%s_%s_LDFLAGS += -no-undefined\n' % (libname, libext)
      # Synthesize an ${libname}_${libext}_LDFLAGS augmentation by combining
      # the link dependencies of all modules.
      links = [m.getLink() for m in moduletable['main'] if not m.isTests()]
      
      for module in moduletable['main']:
        if not module.isTests():
          
    if type(emit) is bytes:
      emit = emit.decode(ENCS['default'])
    path = '/home/ghostmansd/makefile.py.am'
    with codecs.open(path, 'wb', 'UTF-8') as file:
      file.write(emit)