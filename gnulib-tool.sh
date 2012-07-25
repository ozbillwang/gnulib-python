#! /bin/sh
#
# Copyright (C) 2002-2012 Free Software Foundation, Inc.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

# This program is meant for authors or maintainers which want to import
# modules from gnulib into their packages.

progname=$0
package=gnulib
nl='
'
IFS=" ""	$nl"

# You can set AUTOCONFPATH to empty if autoconf 2.57 is already in your PATH.
AUTOCONFPATH=
#case $USER in
#  bruno )
#    AUTOCONFBINDIR=/packages/gnu-inst-autoconf/2.57/bin
#    AUTOCONFPATH="eval env PATH=${AUTOCONFBINDIR}:\$PATH "
#    ;;
#esac

# You can set AUTOMAKEPATH to empty if automake 1.9.x is already in your PATH.
AUTOMAKEPATH=

# You can set GETTEXTPATH to empty if autopoint 0.15 is already in your PATH.
GETTEXTPATH=

# You can set LIBTOOLPATH to empty if libtoolize 2.x is already in your PATH.
LIBTOOLPATH=

# If you didn't set AUTOCONFPATH and AUTOMAKEPATH, you can also set the
# variables AUTOCONF, AUTOHEADER, ACLOCAL, AUTOMAKE, AUTORECONF individually.
if test -z "${AUTOCONF}" || test -n "${AUTOCONFPATH}"; then
  AUTOCONF="${AUTOCONFPATH}autoconf"
fi
if test -z "${AUTOHEADER}" || test -n "${AUTOCONFPATH}"; then
  AUTOHEADER="${AUTOCONFPATH}autoheader"
fi
if test -z "${ACLOCAL}" || test -n "${AUTOMAKEPATH}"; then
  ACLOCAL="${AUTOMAKEPATH}aclocal"
fi
if test -z "${AUTOMAKE}" || test -n "${AUTOMAKEPATH}"; then
  AUTOMAKE="${AUTOMAKEPATH}automake"
fi
if test -z "${AUTORECONF}" || test -n "${AUTOCONFPATH}"; then
  AUTORECONF="${AUTOCONFPATH}autoreconf"
fi

# If you didn't set GETTEXTPATH, you can also set the variable AUTOPOINT.
if test -z "${AUTOPOINT}" || test -n "${GETTEXTPATH}"; then
  AUTOPOINT="${GETTEXTPATH}autopoint"
fi

# If you didn't set LIBTOOLPATH, you can also set the variable LIBTOOLIZE.
if test -z "${LIBTOOLIZE}" || test -n "${LIBTOOLPATH}"; then
  LIBTOOLIZE="${LIBTOOLPATH}libtoolize"
fi

# You can set MAKE.
if test -z "${MAKE}"; then
  MAKE=make
fi

# When using GNU sed, turn off as many GNU extensions as possible,
# to minimize the risk of accidentally using non-portable features.
# However, do this only for gnulib-tool itself, not for the code that
# gnulib-tool generates, since we don't want "sed --posix" to leak
# into makefiles. And do it only for sed versions 4.2 or newer,
# because "sed --posix" is buggy in GNU sed 4.1.5, see
# <http://lists.gnu.org/archive/html/bug-gnulib/2009-02/msg00225.html>.
if (alias) > /dev/null 2>&1 \
   && echo | sed --posix -e d >/dev/null 2>&1 \
   && case `sed --version | sed -e 's/^[^0-9]*//' -e 1q` in \
        [1-3]* | 4.[01]*) false;; \
        *) true;; \
      esac \
   ; then
  # Define sed as an alias.
  # It is not always possible to use aliases. Aliases are guaranteed to work
  # if the executing shell is bash and either it is invoked as /bin/sh or
  # is a version >= 2.0, supporting shopt. This is the common case.
  # Two other approaches (use of a variable $sed or of a function func_sed
  # instead of an alias) require massive, fragile code changes.
  # An other approach (use of function sed) requires `which sed` - but
  # 'which' is hard to emulate, due to missing "test -x" on some platforms.
  if test -n "$BASH_VERSION"; then
    shopt -s expand_aliases >/dev/null 2>&1
  fi
  alias sed='sed --posix'
fi

# sed_noop is a sed expression that does nothing.
# An empty expression does not work with the native 'sed' on AIX 6.1.
sed_noop='s,x,x,'

# sed_comments is true or false, depending whether 'sed' supports comments.
# AIX 5.3 sed barfs over indented comments.
if echo fo | sed -e 's/f/g/
# s/o/u/
 # indented comment
s/o/e/' 2>/dev/null | grep ge > /dev/null; then
  sed_comments=true
else
  sed_comments=false
fi

# func_usage
# outputs to stdout the --help usage message.
func_usage ()
{
  echo "\
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

Report bugs to <bug-gnulib@gnu.org>."
}

# func_version
# outputs to stdout the --version message.
func_version ()
{
  func_gnulib_dir
  if test -d "$gnulib_dir"/.git \
     && (git --version) >/dev/null 2>/dev/null \
     && (date --version) >/dev/null 2>/dev/null; then
    # gnulib checked out from git.
    sed_extract_first_date='/^Date/{
s/^Date:[	 ]*//p
q
}'
    date=`cd "$gnulib_dir" && git log ChangeLog | sed -n -e "$sed_extract_first_date"`
    # Turn "Fri Mar 21 07:16:51 2008 -0600" into "Mar 21 2008 07:16:51 -0600".
    sed_year_before_time='s/^[^ ]* \([^ ]*\) \([0-9]*\) \([0-9:]*\) \([0-9]*\) /\1 \2 \4 \3 /'
    date=`echo "$date" | sed -e "$sed_year_before_time"`
    # Use GNU date to compute the time in GMT.
    date=`date -d "$date" -u +"%Y-%m-%d %H:%M:%S"`
    version=' '`cd "$gnulib_dir" && ./build-aux/git-version-gen /dev/null | sed -e 's/-dirty/-modified/'`
  else
    if test -d "$gnulib_dir"/CVS \
       && (cvs --version) >/dev/null 2>/dev/null; then
      # gnulib checked out from CVS.
      sed_extract_first_date='/^date: /{
s/^date: \([0-9][0-9][0-9][0-9]\).\([0-9][0-9]\).\([0-9][0-9]\) \([0-9][0-9]:[0-9][0-9]:[0-9][0-9]\).*/\1-\2-\3 \4/p
q
}'
      date=`cd "$gnulib_dir" && cvs log -N ChangeLog 2>/dev/null | sed -n -e "$sed_extract_first_date"`
    else
      # gnulib copy without versioning information.
      date=`sed -e 's/ .*//;q' "$gnulib_dir"/ChangeLog`
    fi
    version=
  fi
  year=`"$gnulib_dir"/build-aux/mdate-sh "$self_abspathname" | sed -e 's,^.* ,,'`
  echo "\
gnulib-tool (GNU $package $date)$version
Copyright (C) $year Free Software Foundation, Inc.
License GPLv3+: GNU GPL version 3 or later <http://gnu.org/licenses/gpl.html>
This is free software: you are free to change and redistribute it.
There is NO WARRANTY, to the extent permitted by law.
"
  printf "Written by %s, %s, and %s.\n" "Bruno Haible" "Paul Eggert" "Simon Josefsson"
}

# func_emit_copyright_notice
# outputs to stdout a header for a generated file.
func_emit_copyright_notice ()
{
  sed -n -e '/Copyright/ {
               p
               q
             }' < "$self_abspathname"
  echo "#"
  echo "# This file is free software; you can redistribute it and/or modify"
  echo "# it under the terms of the GNU General Public License as published by"
  echo "# the Free Software Foundation; either version 3 of the License, or"
  echo "# (at your option) any later version."
  echo "#"
  echo "# This file is distributed in the hope that it will be useful,"
  echo "# but WITHOUT ANY WARRANTY; without even the implied warranty of"
  echo "# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the"
  echo "# GNU General Public License for more details."
  echo "#"
  echo "# You should have received a copy of the GNU General Public License"
  echo "# along with this file.  If not, see <http://www.gnu.org/licenses/>."
  echo "#"
  echo "# As a special exception to the GNU General Public License,"
  echo "# this file may be distributed as part of a program that"
  echo "# contains a configuration script generated by Autoconf, under"
  echo "# the same distribution terms as the rest of that program."
  echo "#"
  echo "# Generated by gnulib-tool."
}

# func_exit STATUS
# exits with a given status.
# This function needs to be used, rather than 'exit', when a 'trap' handler is
# in effect that refers to $?.
func_exit ()
{
  (exit $1); exit $1
}

# func_gnulib_dir
# locates the directory where the gnulib repository lives
# Input:
# - progname                 name of this program
# Sets variables
# - self_abspathname         absolute pathname of gnulib-tool
# - gnulib_dir               absolute pathname of gnulib repository
func_gnulib_dir ()
{
  case "$progname" in
    /*) self_abspathname="$progname" ;;
    */*) self_abspathname=`pwd`/"$progname" ;;
    *)
      # Look in $PATH.
      # Iterate through the elements of $PATH.
      # We use IFS=: instead of
      #   for d in `echo ":$PATH:" | sed -e 's/:::*/:.:/g' | sed -e 's/:/ /g'`
      # because the latter does not work when some PATH element contains spaces.
      # We use a canonicalized $pathx instead of $PATH, because empty PATH
      # elements are by definition equivalent to '.', however field splitting
      # according to IFS=: loses empty fields in many shells:
      #   - /bin/sh on OSF/1 and Solaris loses all empty fields (at the
      #     beginning, at the end, and in the middle),
      #   - /bin/sh on IRIX and /bin/ksh on IRIX and OSF/1 lose empty fields
      #     at the beginning and at the end,
      #   - GNU bash, /bin/sh on AIX and HP-UX, and /bin/ksh on AIX, HP-UX,
      #     Solaris lose empty fields at the end.
      # The 'case' statement is an optimization, to avoid evaluating the
      # explicit canonicalization command when $PATH contains no empty fields.
      self_abspathname=
      if test "${PATH_SEPARATOR+set}" != set; then
        # Determine PATH_SEPARATOR by trying to find /bin/sh in a PATH which
        # contains only /bin. Note that ksh looks also at the FPATH variable,
        # so we have to set that as well for the test.
        PATH_SEPARATOR=:
        (PATH='/bin;/bin'; FPATH=$PATH; sh -c :) >/dev/null 2>&1 \
          && { (PATH='/bin:/bin'; FPATH=$PATH; sh -c :) >/dev/null 2>&1 \
                 || PATH_SEPARATOR=';'
             }
      fi
      if test "$PATH_SEPARATOR" = ";"; then
        # On Windows, programs are searched in "." before $PATH.
        pathx=".;$PATH"
      else
        # On Unix, we have to convert empty PATH elements to ".".
        pathx="$PATH"
        case :$PATH: in
          *::*)
            pathx=`echo ":$PATH:" | sed -e 's/:::*/:.:/g' -e 's/^://' -e 's/:\$//'`
            ;;
        esac
      fi
      save_IFS="$IFS"
      IFS="$PATH_SEPARATOR"
      for d in $pathx; do
        IFS="$save_IFS"
        test -z "$d" && d=.
        if test -x "$d/$progname" && test ! -d "$d/$progname"; then
          self_abspathname="$d/$progname"
          break
        fi
      done
      IFS="$save_IFS"
      if test -z "$self_abspathname"; then
        func_fatal_error "could not locate the gnulib-tool program - how did you invoke it?"
      fi
      ;;
  esac
  while test -h "$self_abspathname"; do
    # Resolve symbolic link.
    linkval=`func_readlink "$self_abspathname"`
    test -n "$linkval" || break
    case "$linkval" in
      /* ) self_abspathname="$linkval" ;;
      * ) self_abspathname=`echo "$self_abspathname" | sed -e 's,/[^/]*$,,'`/"$linkval" ;;
    esac
  done
  gnulib_dir=`echo "$self_abspathname" | sed -e 's,/[^/]*$,,'`
}

# func_tmpdir
# creates a temporary directory.
# Input:
# - progname                 name of this program
# Sets variable
# - tmp             pathname of freshly created temporary directory
func_tmpdir ()
{
  # Use the environment variable TMPDIR, falling back to /tmp. This allows
  # users to specify a different temporary directory, for example, if their
  # /tmp is filled up or too small.
  : ${TMPDIR=/tmp}
  {
    # Use the mktemp program if available. If not available, hide the error
    # message.
    tmp=`(umask 077 && mktemp -d "$TMPDIR/glXXXXXX") 2>/dev/null` &&
    test -n "$tmp" && test -d "$tmp"
  } ||
  {
    # Use a simple mkdir command. It is guaranteed to fail if the directory
    # already exists.  $RANDOM is bash specific and expands to empty in shells
    # other than bash, ksh and zsh.  Its use does not increase security;
    # rather, it minimizes the probability of failure in a very cluttered /tmp
    # directory.
    tmp=$TMPDIR/gl$$-$RANDOM
    (umask 077 && mkdir "$tmp")
  } ||
  {
    echo "$progname: cannot create a temporary directory in $TMPDIR" >&2
    func_exit 1
  }
}

# func_append var value
# appends the given value to the shell variable var.
if ( foo=bar; foo+=baz && test "$foo" = barbaz ) >/dev/null 2>&1; then
  # Use bash's += operator. It reduces complexity of appending repeatedly to
  # a single variable from O(n^2) to O(n).
  func_append ()
  {
    eval "$1+=\"\$2\""
  }
  fast_func_append=true
else
  func_append ()
  {
    eval "$1=\"\$$1\$2\""
  }
  fast_func_append=false
fi

# func_remove_prefix var prefix
# removes the given prefix from the value of the shell variable var.
# var should be the name of a shell variable.
# Its value should not contain a newline and not start or end with whitespace.
# prefix should not contain the characters "$`\{}[]^|.
if ( foo=bar; eval 'test "${foo#b}" = ar' ) >/dev/null 2>&1; then
  func_remove_prefix ()
  {
    eval "$1=\${$1#\$2}"
  }
  fast_func_remove_prefix=true
else
  func_remove_prefix ()
  {
    eval "value=\"\$$1\""
    prefix="$2"
    case "$prefix" in
      *.*)
        sed_escape_dots='s/\([.]\)/\\\1/g'
        prefix=`echo "$prefix" | sed -e "$sed_escape_dots"`
        ;;
    esac
    value=`echo "$value" | sed -e "s|^${prefix}||"`
    eval "$1=\"\$value\""
  }
  fast_func_remove_prefix=false
fi

# func_remove_suffix var suffix
# removes the given suffix from the value of the shell variable var.
# var should be the name of a shell variable.
# Its value should not contain a newline and not start or end with whitespace.
# suffix should not contain the characters "$`\{}[]^|.
if ( foo=bar; eval 'test "${foo%r}" = ba' ) >/dev/null 2>&1; then
  func_remove_suffix ()
  {
    eval "$1=\${$1%\$2}"
  }
  fast_func_remove_suffix=true
else
  func_remove_suffix ()
  {
    eval "value=\"\$$1\""
    suffix="$2"
    case "$suffix" in
      *.*)
        sed_escape_dots='s/\([.]\)/\\\1/g'
        suffix=`echo "$suffix" | sed -e "$sed_escape_dots"`
        ;;
    esac
    value=`echo "$value" | sed -e "s|${suffix}\$||"`
    eval "$1=\"\$value\""
  }
  fast_func_remove_suffix=false
fi

# func_fatal_error message
# outputs to stderr a fatal error message, and terminates the program.
# Input:
# - progname                 name of this program
func_fatal_error ()
{
  echo "$progname: *** $1" 1>&2
  echo "$progname: *** Stop." 1>&2
  func_exit 1
}

# func_warning message
# Outputs to stderr a warning message,
func_warning ()
{
  echo "gnulib-tool: warning: $1" 1>&2
}

# func_readlink SYMLINK
# outputs the target of the given symlink.
if (type -p readlink) > /dev/null 2>&1; then
  func_readlink ()
  {
    # Use the readlink program from GNU coreutils.
    readlink "$1"
  }
else
  func_readlink ()
  {
    # Use two sed invocations. A single sed -n -e 's,^.* -> \(.*\)$,\1,p'
    # would do the wrong thing if the link target contains " -> ".
    LC_ALL=C ls -l "$1" | sed -e 's, -> ,#%%#,' | sed -n -e 's,^.*#%%#\(.*\)$,\1,p'
  }
fi

# func_relativize DIR1 DIR2
# computes a relative pathname RELDIR such that DIR1/RELDIR = DIR2.
# Input:
# - DIR1            relative pathname, relative to the current directory
# - DIR2            relative pathname, relative to the current directory
# Output:
# - reldir          relative pathname of DIR2, relative to DIR1
func_relativize ()
{
  dir0=`pwd`
  dir1="$1"
  dir2="$2"
  sed_first='s,^\([^/]*\)/.*$,\1,'
  sed_rest='s,^[^/]*/*,,'
  sed_last='s,^.*/\([^/]*\)$,\1,'
  sed_butlast='s,/*[^/]*$,,'
  while test -n "$dir1"; do
    first=`echo "$dir1" | sed -e "$sed_first"`
    if test "$first" != "."; then
      if test "$first" = ".."; then
        dir2=`echo "$dir0" | sed -e "$sed_last"`/"$dir2"
        dir0=`echo "$dir0" | sed -e "$sed_butlast"`
      else
        first2=`echo "$dir2" | sed -e "$sed_first"`
        if test "$first2" = "$first"; then
          dir2=`echo "$dir2" | sed -e "$sed_rest"`
        else
          dir2="../$dir2"
        fi
        dir0="$dir0"/"$first"
      fi
    fi
    dir1=`echo "$dir1" | sed -e "$sed_rest"`
  done
  reldir="$dir2"
}

# func_relconcat DIR1 DIR2
# computes a relative pathname DIR1/DIR2, with obvious simplifications.
# Input:
# - DIR1            relative pathname, relative to the current directory
# - DIR2            relative pathname, relative to DIR1
# Output:
# - relconcat       DIR1/DIR2, relative to the current directory
func_relconcat ()
{
  dir1="$1"
  dir2="$2"
  sed_first='s,^\([^/]*\)/.*$,\1,'
  sed_rest='s,^[^/]*/*,,'
  sed_last='s,^.*/\([^/]*\)$,\1,'
  sed_butlast='s,/*[^/]*$,,'
  while true; do
    first=`echo "$dir2" | sed -e "$sed_first"`
    if test "$first" = "."; then
      dir2=`echo "$dir2" | sed -e "$sed_rest"`
      if test -z "$dir2"; then
        relconcat="$dir1"
        break
      fi
    else
      last=`echo "$dir1" | sed -e "$sed_last"`
      while test "$last" = "."; do
        dir1=`echo "$dir1" | sed -e "$sed_butlast"`
        last=`echo "$dir1" | sed -e "$sed_last"`
      done
      if test -z "$dir1"; then
        relconcat="$dir2"
        break
      fi
      if test "$first" = ".."; then
        if test "$last" = ".."; then
          relconcat="$dir1/$dir2"
          break
        fi
        dir1=`echo "$dir1" | sed -e "$sed_butlast"`
        dir2=`echo "$dir2" | sed -e "$sed_rest"`
        if test -z "$dir1"; then
          relconcat="$dir2"
          break
        fi
        if test -z "$dir2"; then
          relconcat="$dir1"
          break
        fi
      else
        relconcat="$dir1/$dir2"
        break
      fi
    fi
  done
}

# func_ln SRC DEST
# Like ln -s, except that SRC is given relative to the current directory (or
# absolute), not given relative to the directory of DEST.
func_ln ()
{
  case "$1" in
    /*)
      ln -s "$1" "$2" ;;
    *) # SRC is relative.
      case "$2" in
        /*)
          ln -s "`pwd`/$1" "$2" ;;
        *) # DEST is relative too.
          ln_destdir=`echo "$2" | sed -e 's,[^/]*$,,'`
          test -n "$ln_destdir" || ln_destdir="."
          func_relativize "$ln_destdir" "$1"
          ln -s "$reldir" "$2"
          ;;
      esac
      ;;
  esac
}

# func_ln_if_changed SRC DEST
# Like func_ln, but avoids munging timestamps if the link is correct.
func_ln_if_changed ()
{
  if test $# -ne 2; then
    echo "usage: func_ln_if_changed SRC DEST" >&2
  fi
  ln_target=`func_readlink "$2"`
  if test -h "$2" && test "$1" = "$ln_target"; then
    :
  else
    rm -f "$2"
    func_ln "$1" "$2"
  fi
}

# Ensure an 'echo' command that
#   1. does not interpret backslashes and
#   2. does not print an error message "broken pipe" when writing into a pipe
#      with no writers.
#
# Test cases for problem 1:
#   echo '\n' | wc -l                 prints 1 when OK, 2 when KO
#   echo '\t' | grep t > /dev/null    has return code 0 when OK, 1 when KO
# Test cases for problem 2:
#   echo hi | true                    frequently prints
#                                     "bash: echo: write error: Broken pipe"
#                                     to standard error in bash 3.2.
#
# Problem 1 is a weird heritage from SVR4. BSD got it right (except that
# BSD echo interprets '-n' as an option, which is also not desirable).
# Nowadays the problem occurs in 4 situations:
# - in bash, when the shell option xpg_echo is set (bash >= 2.04)
#            or when it was built with --enable-usg-echo-default (bash >= 2.0)
#            or when it was built with DEFAULT_ECHO_TO_USG (bash < 2.0),
# - in zsh, when sh-emulation is not set,
# - in ksh (e.g. AIX /bin/sh and Solaris /usr/xpg4/bin/sh are ksh instances,
#           and HP-UX /bin/sh and IRIX /bin/sh behave similarly),
# - in Solaris /bin/sh and OSF/1 /bin/sh.
# We try the following workarounds:
# - for all: respawn using $CONFIG_SHELL if that is set and works.
# - for bash >= 2.04: unset the shell option xpg_echo.
# - for bash >= 2.0: define echo to a function that uses the printf built-in.
# - for bash < 2.0: define echo to a function that uses cat of a here document.
# - for zsh: turn sh-emulation on.
# - for ksh: alias echo to 'print -r'.
# - for ksh: alias echo to a function that uses cat of a here document.
# - for Solaris /bin/sh and OSF/1 /bin/sh: respawn using /bin/ksh and rely on
#   the ksh workaround.
# - otherwise: respawn using /bin/sh and rely on the workarounds.
# When respawning, we pass --no-reexec as first argument, so as to avoid
# turning this script into a fork bomb in unlucky situations.
#
# Problem 2 is specific to bash 3.2 and affects the 'echo' built-in, but not
# the 'printf' built-in. See
#   <http://lists.gnu.org/archive/html/bug-bash/2008-12/msg00050.html>
#   <http://lists.gnu.org/archive/html/bug-gnulib/2010-02/msg00154.html>
# The workaround is: define echo to a function that uses the printf built-in.
have_echo=
if echo '\t' | grep t > /dev/null; then
  have_echo=yes # Lucky!
fi
# Try the workarounds.
# Respawn using $CONFIG_SHELL if that is set and works.
if test -z "$have_echo" \
   && test "X$1" != "X--no-reexec" \
   && test -n "$CONFIG_SHELL" \
   && test -f "$CONFIG_SHELL" \
   && $CONFIG_SHELL -c "echo '\\t' | grep t > /dev/null"; then
  exec $CONFIG_SHELL "$0" --no-reexec "$@"
  exit 127
fi
# For bash >= 2.04: unset the shell option xpg_echo.
if test -z "$have_echo" \
   && test -n "$BASH_VERSION" \
   && (shopt -o xpg_echo; echo '\t' | grep t > /dev/null) 2>/dev/null; then
  shopt -o xpg_echo
  have_echo=yes
fi
# For bash >= 2.0: define echo to a function that uses the printf built-in.
# For bash < 2.0: define echo to a function that uses cat of a here document.
# (There is no win in using 'printf' over 'cat' if it is not a shell built-in.)
# Also handle problem 2, specific to bash 3.2, here.
if { test -z "$have_echo" \
     || case "$BASH_VERSION" in 3.2*) true;; *) false;; esac; \
   } \
   && test -n "$BASH_VERSION"; then \
  if type printf 2>/dev/null | grep / > /dev/null; then
    # 'printf' is not a shell built-in.
echo ()
{
cat <<EOF
$*
EOF
}
  else
    # 'printf' is a shell built-in.
echo ()
{
  printf '%s\n' "$*"
}
  fi
  if echo '\t' | grep t > /dev/null; then
    have_echo=yes
  fi
fi
# For zsh: turn sh-emulation on.
if test -z "$have_echo" \
   && test -n "$ZSH_VERSION" \
   && (emulate sh) >/dev/null 2>&1; then
  emulate sh
fi
# For ksh: alias echo to 'print -r'.
if test -z "$have_echo" \
   && (type print) >/dev/null 2>&1; then
  # A 'print' command exists.
  if type print 2>/dev/null | grep / > /dev/null; then
    :
  else
    # 'print' is a shell built-in.
    if (print -r '\told' | grep told > /dev/null) 2>/dev/null; then
      # 'print' is the ksh shell built-in.
      alias echo='print -r'
    fi
  fi
fi
if test -z "$have_echo" \
   && echo '\t' | grep t > /dev/null; then
  have_echo=yes
fi
# For ksh: alias echo to a function that uses cat of a here document.
# The ksh manual page says:
#   "Aliasing is performed when scripts are read, not while they are executed.
#    Therefore, for an alias to take effect, the alias definition command has
#    to be executed before the command which references the alias is read."
# Because of this, we have to play strange tricks with have_echo, to ensure
# that the top-level statement containing the test starts after the 'alias'
# command.
if test -z "$have_echo"; then
  bsd_echo ()
{
cat <<EOF
$*
EOF
}
  if (alias echo=bsd_echo) 2>/dev/null; then
    alias echo=bsd_echo 2>/dev/null
  fi
fi
if test -z "$have_echo" \
   && echo '\t' | grep t > /dev/null; then
  have_echo=yes
fi
if test -z "$have_echo"; then
  if (alias echo=bsd_echo) 2>/dev/null; then
    unalias echo 2>/dev/null
  fi
fi
# For Solaris /bin/sh and OSF/1 /bin/sh: respawn using /bin/ksh.
if test -z "$have_echo" \
   && test "X$1" != "X--no-reexec" \
   && test -f /bin/ksh; then
  exec /bin/ksh "$0" --no-reexec "$@"
  exit 127
fi
# Otherwise: respawn using /bin/sh.
if test -z "$have_echo" \
   && test "X$1" != "X--no-reexec" \
   && test -f /bin/sh; then
  exec /bin/sh "$0" --no-reexec "$@"
  exit 127
fi
if test -z "$have_echo"; then
  func_fatal_error "Shell does not support 'echo' correctly. Please install GNU bash and set the environment variable CONFIG_SHELL to point to it."
fi
if echo '\t' | grep t > /dev/null; then
  : # Works fine now.
else
  func_fatal_error "Shell does not support 'echo' correctly. Workaround does not work. Please report this as a bug to bug-gnulib@gnu.org."
fi
if test "X$1" = "X--no-reexec"; then
  shift
fi

# Command-line option processing.
# Removes the OPTIONS from the arguments. Sets the variables:
# - mode            list or import or add-import or remove-import or update
#                   or create-testdir or create-megatestdir
# - destdir         from --dir
# - local_gnulib_dir  from --local-dir
# - modcache        true or false, from --cache-modules/--no-cache-modules
# - verbose         integer, default 0, inc/decremented by --verbose/--quiet
# - libname, supplied_libname  from --lib
# - sourcebase      from --source-base
# - m4base          from --m4-base
# - pobase          from --po-base
# - docbase         from --doc-base
# - testsbase       from --tests-base
# - auxdir          from --aux-dir
# - inctests        true if --with-tests was given, blank otherwise
# - incobsolete     true if --with-obsolete was given, blank otherwise
# - inc_cxx_tests   true if --with-c++-tests was given, blank otherwise
# - inc_longrunning_tests  true if --with-longrunning-tests was given, blank
#                          otherwise
# - inc_privileged_tests  true if --with-privileged-tests was given, blank
#                         otherwise
# - inc_unportable_tests  true if --with-unportable-tests was given, blank
#                         otherwise
# - inc_all_tests   true if --with-all-tests was given, blank otherwise
# - excl_cxx_tests  true if --without-c++-tests was given, blank otherwise
# - excl_longrunning_tests  true if --without-longrunning-tests was given,
#                           blank otherwise
# - excl_privileged_tests  true if --without-privileged-tests was given, blank
#                          otherwise
# - excl_unportable_tests  true if --without-unportable-tests was given, blank
#                          otherwise
# - single_configure  true if --single-configure was given, false otherwise
# - avoidlist       list of modules to avoid, from --avoid
# - cond_dependencies  true if --conditional-dependencies was given, false if
#                      --no-conditional-dependencies was given, blank otherwise
# - lgpl            yes or a number if --lgpl was given, blank otherwise
# - makefile_name   from --makefile-name
# - libtool         true if --libtool was given, false if --no-libtool was
#                   given, blank otherwise
# - macro_prefix    from --macro-prefix
# - po_domain       from --po-domain
# - witness_c_macro  from --witness-c-macro
# - vc_files        true if --vc-files was given, false if --no-vc-files was
#                   given, blank otherwise
# - autoconf_minversion  minimum supported autoconf version
# - do_changelog    false if --no-changelog was given, : otherwise
# - doit            : if actions shall be executed, false if only to be printed
# - symbolic        true if --symlink or --more-symlinks was given, blank
#                   otherwise
# - lsymbolic       true if --local-symlink was given, blank otherwise
# - do_copyrights   blank if --more-symlinks was given, true otherwise
{
  mode=
  destdir=
  local_gnulib_dir=
  modcache=true
  verbose=0
  libname=libgnu
  supplied_libname=
  sourcebase=
  m4base=
  pobase=
  docbase=
  testsbase=
  auxdir=
  inctests=
  incobsolete=
  inc_cxx_tests=
  inc_longrunning_tests=
  inc_privileged_tests=
  inc_unportable_tests=
  inc_all_tests=
  excl_cxx_tests=
  excl_longrunning_tests=
  excl_privileged_tests=
  excl_unportable_tests=
  single_configure=false
  avoidlist=
  cond_dependencies=
  lgpl=
  makefile_name=
  libtool=
  macro_prefix=
  po_domain=
  witness_c_macro=
  vc_files=
  do_changelog=:
  doit=:
  symbolic=
  lsymbolic=
  do_copyrights=true

  supplied_opts="$@"

  while test $# -gt 0; do
    case "$1" in
      --list | --lis )
        mode=list
        shift ;;
      --find | --fin | --fi | --f )
        mode=find
        shift ;;
      --import | --impor | --impo | --imp | --im | --i )
        mode=import
        shift ;;
      --add-import | --add-impor | --add-impo | --add-imp | --add-im | --add-i | --add- | --add | --ad )
        mode=add-import
        shift ;;
      --remove-import | --remove-impor | --remove-impo | --remove-imp | --remove-im | --remove-i | --remove- | --remove | --remov | --remo | --rem | --re | --r )
        mode=remove-import
        shift ;;
      --update | --updat | --upda | --upd | --up | --u )
        mode=update
        shift ;;
      --create-testdir | --create-testdi | --create-testd | --create-test | --create-tes | --create-te | --create-t )
        mode=create-testdir
        shift ;;
      --create-megatestdir | --create-megatestdi | --create-megatestd | --create-megatest | --create-megates | --create-megate | --create-megat | --create-mega | --create-meg | --create-me | --create-m )
        mode=create-megatestdir
        shift ;;
      --test | --tes | --te | --t )
        mode=test
        shift ;;
      --megatest | --megates | --megate | --megat | --mega | --meg | --me | --m )
        mode=megatest
        shift ;;
      --extract-* )
        mode=`echo "X$1" | sed -e 's/^X--//'`
        shift ;;
      --copy-file | --copy-fil | --copy-fi | --copy-f | --copy- | --copy | --cop )
        mode=copy-file
        shift ;;
      --dir )
        shift
        if test $# = 0; then
          func_fatal_error "missing argument for --dir"
        fi
        destdir=$1
        shift ;;
      --dir=* )
        destdir=`echo "X$1" | sed -e 's/^X--dir=//'`
        shift ;;
      --local-dir )
        shift
        if test $# = 0; then
          func_fatal_error "missing argument for --local-dir"
        fi
        local_gnulib_dir=$1
        shift ;;
      --local-dir=* )
        local_gnulib_dir=`echo "X$1" | sed -e 's/^X--local-dir=//'`
        shift ;;
      --cache-modules | --cache-module | --cache-modul | --cache-modu | --cache-mod | --cache-mo | --cache-m | --cache- | --cache | --cach | --cac | --ca )
        modcache=true
        shift ;;
      --no-cache-modules | --no-cache-module | --no-cache-modul | --no-cache-modu | --no-cache-mod | --no-cache-mo | --no-cache-m | --no-cache- | --no-cache | --no-cach | --no-cac | --no-ca )
        modcache=false
        shift ;;
      --verbose | --verbos | --verbo | --verb )
        verbose=`expr $verbose + 1`
        shift ;;
      --quiet | --quie | --qui | --qu | --q )
        verbose=`expr $verbose - 1`
        shift ;;
      --lib )
        shift
        if test $# = 0; then
          func_fatal_error "missing argument for --lib"
        fi
        libname=$1
        supplied_libname=true
        shift ;;
      --lib=* )
        libname=`echo "X$1" | sed -e 's/^X--lib=//'`
        supplied_libname=true
        shift ;;
      --source-base )
        shift
        if test $# = 0; then
          func_fatal_error "missing argument for --source-base"
        fi
        sourcebase=$1
        shift ;;
      --source-base=* )
        sourcebase=`echo "X$1" | sed -e 's/^X--source-base=//'`
        shift ;;
      --m4-base )
        shift
        if test $# = 0; then
          func_fatal_error "missing argument for --m4-base"
        fi
        m4base=$1
        shift ;;
      --m4-base=* )
        m4base=`echo "X$1" | sed -e 's/^X--m4-base=//'`
        shift ;;
      --po-base )
        shift
        if test $# = 0; then
          func_fatal_error "missing argument for --po-base"
        fi
        pobase=$1
        shift ;;
      --po-base=* )
        pobase=`echo "X$1" | sed -e 's/^X--po-base=//'`
        shift ;;
      --doc-base )
        shift
        if test $# = 0; then
          func_fatal_error "missing argument for --doc-base"
        fi
        docbase=$1
        shift ;;
      --doc-base=* )
        docbase=`echo "X$1" | sed -e 's/^X--doc-base=//'`
        shift ;;
      --tests-base )
        shift
        if test $# = 0; then
          func_fatal_error "missing argument for --tests-base"
        fi
        testsbase=$1
        shift ;;
      --tests-base=* )
        testsbase=`echo "X$1" | sed -e 's/^X--tests-base=//'`
        shift ;;
      --aux-dir )
        shift
        if test $# = 0; then
          func_fatal_error "missing argument for --aux-dir"
        fi
        auxdir=$1
        shift ;;
      --aux-dir=* )
        auxdir=`echo "X$1" | sed -e 's/^X--aux-dir=//'`
        shift ;;
      --with-tests | --with-test | --with-tes | --with-te | --with-t)
        inctests=true
        shift ;;
      --with-obsolete | --with-obsolet | --with-obsole | --with-obsol | --with-obso | --with-obs | --with-ob | --with-o)
        incobsolete=true
        shift ;;
      --with-c++-tests | --with-c++-test | --with-c++-tes | --with-c++-te | --with-c++-t | --with-c++- | --with-c++ | --with-c+ | --with-c)
        inc_cxx_tests=true
        shift ;;
      --with-longrunning-tests | --with-longrunning-test | --with-longrunning-tes | --with-longrunning-te | --with-longrunning-t | --with-longrunning- | --with-longrunning | --with-longrunnin | --with-longrunni | --with-longrunn | --with-longrun | --with-longru | --with-longr | --with-long | --with-lon | --with-lo | --with-l)
        inc_longrunning_tests=true
        shift ;;
      --with-privileged-tests | --with-privileged-test | --with-privileged-tes | --with-privileged-te | --with-privileged-t | --with-privileged- | --with-privileged | --with-privilege | --with-privileg | --with-privile | --with-privil | --with-privi | --with-priv | --with-pri | --with-pr | --with-p)
        inc_privileged_tests=true
        shift ;;
      --with-unportable-tests | --with-unportable-test | --with-unportable-tes | --with-unportable-te | --with-unportable-t | --with-unportable- | --with-unportable | --with-unportabl | --with-unportab | --with-unporta | --with-unport | --with-unpor | --with-unpo | --with-unp | --with-un | --with-u)
        inc_unportable_tests=true
        shift ;;
      --with-all-tests | --with-all-test | --with-all-tes | --with-all-te | --with-all-t | --with-all- | --with-all | --with-al | --with-a)
        inc_all_tests=true
        shift ;;
      --without-c++-tests | --without-c++-test | --without-c++-tes | --without-c++-te | --without-c++-t | --without-c++- | --without-c++ | --without-c+ | --without-c)
        excl_cxx_tests=true
        shift ;;
      --without-longrunning-tests | --without-longrunning-test | --without-longrunning-tes | --without-longrunning-te | --without-longrunning-t | --without-longrunning- | --without-longrunning | --without-longrunnin | --without-longrunni | --without-longrunn | --without-longrun | --without-longru | --without-longr | --without-long | --without-lon | --without-lo | --without-l)
        excl_longrunning_tests=true
        shift ;;
      --without-privileged-tests | --without-privileged-test | --without-privileged-tes | --without-privileged-te | --without-privileged-t | --without-privileged- | --without-privileged | --without-privilege | --without-privileg | --without-privile | --without-privil | --without-privi | --without-priv | --without-pri | --without-pr | --without-p)
        excl_privileged_tests=true
        shift ;;
      --without-unportable-tests | --without-unportable-test | --without-unportable-tes | --without-unportable-te | --without-unportable-t | --without-unportable- | --without-unportable | --without-unportabl | --without-unportab | --without-unporta | --without-unport | --without-unpor | --without-unpo | --without-unp | --without-un | --without-u)
        excl_unportable_tests=true
        shift ;;
      --single-configure | --single-configur | --single-configu | --single-config | --single-confi | --single-conf | --single-con | --single-con | --single-co | --single-c | --single- | --single | --singl | --sing | --sin | --si)
        single_configure=true
        shift ;;
      --avoid )
        shift
        if test $# = 0; then
          func_fatal_error "missing argument for --avoid"
        fi
        func_append avoidlist " $1"
        shift ;;
      --avoid=* )
        arg=`echo "X$1" | sed -e 's/^X--avoid=//'`
        func_append avoidlist " $arg"
        shift ;;
      --conditional-dependencies | --conditional-dependencie | --conditional-dependenci | --conditional-dependenc | --conditional-dependen | --conditional-depende | --conditional-depend | --conditional-depen | --conditional-depe | --conditional-dep | --conditional-de | --conditional-d | --conditional- | --conditional | --conditiona | --condition | --conditio | --conditi | --condit | --condi | --cond | --con)
        cond_dependencies=true
        shift ;;
      --no-conditional-dependencies | --no-conditional-dependencie | --no-conditional-dependenci | --no-conditional-dependenc | --no-conditional-dependen | --no-conditional-depende | --no-conditional-depend | --no-conditional-depen | --no-conditional-depe | --no-conditional-dep | --no-conditional-de | --no-conditional-d | --no-conditional- | --no-conditional | --no-conditiona | --no-condition | --no-conditio | --no-conditi | --no-condit | --no-condi | --no-cond | --no-con | --no-co)
        cond_dependencies=false
        shift ;;
      --lgpl )
        lgpl=yes
        shift ;;
      --lgpl=* )
        arg=`echo "X$1" | sed -e 's/^X--lgpl=//'`
        case "$arg" in
          2 | 3) ;;
          *) func_fatal_error "invalid LGPL version number for --lgpl" ;;
        esac
        lgpl=$arg
        shift ;;
      --makefile-name )
        shift
        if test $# = 0; then
          func_fatal_error "missing argument for --makefile-name"
        fi
        makefile_name="$1"
        shift ;;
      --makefile-name=* )
        makefile_name=`echo "X$1" | sed -e 's/^X--makefile-name=//'`
        shift ;;
      --libtool )
        libtool=true
        shift ;;
      --no-libtool )
        libtool=false
        shift ;;
      --macro-prefix )
        shift
        if test $# = 0; then
          func_fatal_error "missing argument for --macro-prefix"
        fi
        macro_prefix="$1"
        shift ;;
      --macro-prefix=* )
        macro_prefix=`echo "X$1" | sed -e 's/^X--macro-prefix=//'`
        shift ;;
      --po-domain )
        shift
        if test $# = 0; then
          func_fatal_error "missing argument for --po-domain"
        fi
        po_domain="$1"
        shift ;;
      --po-domain=* )
        po_domain=`echo "X$1" | sed -e 's/^X--po-domain=//'`
        shift ;;
      --witness-c-macro )
        shift
        if test $# = 0; then
          func_fatal_error "missing argument for --witness-c-macro"
        fi
        witness_c_macro="$1"
        shift ;;
      --witness-c-macro=* )
        witness_c_macro=`echo "X$1" | sed -e 's/^X--witness-c-macro=//'`
        shift ;;
      --vc-files )
        vc_files=true
        shift ;;
      --no-vc-files )
        vc_files=false
        shift ;;
      --no-changelog | --no-changelo | --no-changel | --no-change | --no-chang | --no-chan | --no-cha | --no-ch )
        do_changelog=false
        shift ;;
      --dry-run )
        doit=false
        shift ;;
      -s | --symbolic | --symboli | --symbol | --symbo | --symb | --symlink | --symlin | --symli | --syml | --sym | --sy )
        symbolic=true
        shift ;;
      --local-symlink | --local-symlin | --local-symli | --local-syml | --local-sym | --local-sy | --local-s )
        lsymbolic=true
        shift ;;
      -S | --more-symlinks | --more-symlink | --more-symlin | --more-symli | --more-syml | --more-sym | --more-sy | --more-s | --more- | --more | --mor | --mo )
        symbolic=true
        do_copyrights=
        shift ;;
      --help | --hel | --he | --h )
        func_usage
        func_exit $? ;;
      --version | --versio | --versi | --vers )
        func_version
        func_exit $? ;;
      -- )
        # Stop option processing
        shift
        break ;;
      -* )
        echo "gnulib-tool: unknown option $1" 1>&2
        echo "Try 'gnulib-tool --help' for more information." 1>&2
        func_exit 1 ;;
      * )
        break ;;
    esac
  done

  if case "$mode" in import | add-import | remove-import) true;; *) false;; esac; then
    if test -n "$excl_cxx_tests" || test -n "$excl_longrunning_tests" \
       || test -n "$excl_privileged_tests" || test -n "$excl_unportable_tests" \
       || test "$single_configure" != false; then
      echo "gnulib-tool: invalid options for '$mode' mode" 1>&2
      echo "Try 'gnulib-tool --help' for more information." 1>&2
      func_exit 1
    fi
  fi
  if test "$mode" = update; then
    if test $# != 0; then
      echo "gnulib-tool: too many arguments in 'update' mode" 1>&2
      echo "Try 'gnulib-tool --help' for more information." 1>&2
      echo "If you really want to modify the gnulib configuration of your project," 1>&2
      echo "you need to use 'gnulib --import' - at your own risk!" 1>&2
      func_exit 1
    fi
    if test -n "$local_gnulib_dir" || test -n "$supplied_libname" \
       || test -n "$sourcebase" || test -n "$m4base" || test -n "$pobase" \
       || test -n "$docbase" || test -n "$testsbase" || test -n "$auxdir" \
       || test -n "$inctests" || test -n "$incobsolete" \
       || test -n "$inc_cxx_tests" || test -n "$inc_longrunning_tests" \
       || test -n "$inc_privileged_tests" || test -n "$inc_unportable_tests" \
       || test -n "$inc_all_tests" \
       || test -n "$excl_cxx_tests" || test -n "$excl_longrunning_tests" \
       || test -n "$excl_privileged_tests" || test -n "$excl_unportable_tests" \
       || test -n "$avoidlist" || test -n "$lgpl" || test -n "$makefile_name" \
       || test -n "$macro_prefix" || test -n "$po_domain" \
       || test -n "$witness_c_macro" || test -n "$vc_files"; then
      echo "gnulib-tool: invalid options for 'update' mode" 1>&2
      echo "Try 'gnulib-tool --help' for more information." 1>&2
      echo "If you really want to modify the gnulib configuration of your project," 1>&2
      echo "you need to use 'gnulib --import' - at your own risk!" 1>&2
      func_exit 1
    fi
    do_changelog=false
  fi
  if test -n "$pobase" && test -z "$po_domain"; then
    echo "gnulib-tool: together with --po-base, you need to specify --po-domain" 1>&2
    echo "Try 'gnulib-tool --help' for more information." 1>&2
    func_exit 1
  fi
  if test -z "$pobase" && test -n "$po_domain"; then
    func_warning "--po-domain has no effect without a --po-base option"
  fi
  if test "$cond_dependencies" = true && test -n "$inctests"; then
    echo "gnulib-tool: option --conditional-dependencies is not supported with --with-tests" 1>&2
    func_exit 1
  fi

  # Determine the minimum supported autoconf version from the project's
  # configure.ac.
  DEFAULT_AUTOCONF_MINVERSION="2.59"
  autoconf_minversion=
  configure_ac=
  if case "$mode" in import | add-import | remove-import | update) true;; *) false;; esac \
     && test -n "$destdir"; then
    if test -f "$destdir"/configure.ac; then
      configure_ac="$destdir/configure.ac"
    else
      if test -f "$destdir"/configure.in; then
        configure_ac="$destdir/configure.in"
      fi
    fi
  else
    if test -f configure.ac; then
      configure_ac="configure.ac"
    else
      if test -f configure.in; then
        configure_ac="configure.in"
      fi
    fi
  fi
  if test -n "$configure_ac"; then
    # Use sed, not autoconf --trace, to look for the AC_PREREQ invocation,
    # because when some m4 files are omitted from a version control repository,
    # "autoconf --trace=AC_PREREQ" fails with an error message like this:
    #   m4: aclocal.m4:851: Cannot open m4/absolute-header.m4: No such file or directory
    #   autom4te: m4 failed with exit status: 1
    prereqs=
    my_sed_traces='
      s,#.*$,,
      s,^dnl .*$,,
      s, dnl .*$,,
      /AC_PREREQ/ {
        s,^.*AC_PREREQ([[ ]*\([^])]*\).*$,\1,p
      }'
    prereqs=`sed -n -e "$my_sed_traces" < "$configure_ac"`
    if test -n "$prereqs"; then
      autoconf_minversion=`
        for version in $prereqs; do echo $version; done |
        LC_ALL=C sort -nru | sed -e 1q
      `
    fi
  fi
  if test -z "$autoconf_minversion"; then
    autoconf_minversion=$DEFAULT_AUTOCONF_MINVERSION
  fi
  case "$autoconf_minversion" in
    1.* | 2.[0-4]* | 2.5[0-8]*)
      func_fatal_error "minimum supported autoconf version is 2.59. Try adding AC_PREREQ([$DEFAULT_AUTOCONF_MINVERSION]) to your configure.ac." ;;
  esac

  # Remove trailing slashes from the directory names. This is necessary for
  # m4base (to avoid an error in func_import) and optional for the others.
  sed_trimtrailingslashes='s,\([^/]\)//*$,\1,'
  case "$local_gnulib_dir" in
    */ ) local_gnulib_dir=`echo "$local_gnulib_dir" | sed -e "$sed_trimtrailingslashes"` ;;
  esac
  case "$sourcebase" in
    */ ) sourcebase=`echo "$sourcebase" | sed -e "$sed_trimtrailingslashes"` ;;
  esac
  case "$m4base" in
    */ ) m4base=`echo "$m4base" | sed -e "$sed_trimtrailingslashes"` ;;
  esac
  case "$pobase" in
    */ ) pobase=`echo "$pobase" | sed -e "$sed_trimtrailingslashes"` ;;
  esac
  case "$docbase" in
    */ ) docbase=`echo "$docbase" | sed -e "$sed_trimtrailingslashes"` ;;
  esac
  case "$testsbase" in
    */ ) testsbase=`echo "$testsbase" | sed -e "$sed_trimtrailingslashes"` ;;
  esac
  case "$auxdir" in
    */ ) auxdir=`echo "$auxdir" | sed -e "$sed_trimtrailingslashes"` ;;
  esac
}

func_gnulib_dir
func_tmpdir
trap 'exit_status=$?
      if test "$signal" != 0; then
        echo "caught signal $signal" >&2
      fi
      rm -rf "$tmp"
      exit $exit_status' 0
for signal in 1 2 3 13 15; do
  trap '{ signal='$signal'; func_exit 1; }' $signal
done
signal=0

# Note: The 'eval' silences stderr output in dash.
if (declare -A x && { x[f/2]='foo'; x[f/3]='bar'; eval test '${x[f/2]}' = foo; }) 2>/dev/null; then
  # Zsh 4 and Bash 4 have associative arrays.
  have_associative=true
else
  # For other shells, use 'eval' with computed shell variable names.
  have_associative=false
fi

# func_lookup_file file
# looks up a file in $local_gnulib_dir or $gnulib_dir, or combines it through
# 'patch'.
# Input:
# - local_gnulib_dir  from --local-dir
# Output:
# - lookedup_file   name of the merged (combined) file
# - lookedup_tmp    true if it is located in the tmp directory, blank otherwise
func_lookup_file ()
{
  lkfile="$1"
  if test -n "$local_gnulib_dir" && test -f "$local_gnulib_dir/$lkfile"; then
    lookedup_file="$local_gnulib_dir/$lkfile"
    lookedup_tmp=
  else
    if test -f "$gnulib_dir/$lkfile"; then
      if test -n "$local_gnulib_dir" && test -f "$local_gnulib_dir/$lkfile.diff"; then
        lkbase=`echo "$lkfile" | sed -e 's,^.*/,,'`
        rm -f "$tmp/$lkbase"
        cp "$gnulib_dir/$lkfile" "$tmp/$lkbase"
        patch -s "$tmp/$lkbase" < "$local_gnulib_dir/$lkfile.diff" \
          || func_fatal_error "patch file $local_gnulib_dir/$lkfile.diff didn't apply cleanly"
        lookedup_file="$tmp/$lkbase"
        lookedup_tmp=true
      else
        lookedup_file="$gnulib_dir/$lkfile"
        lookedup_tmp=
      fi
    else
      func_fatal_error "file $gnulib_dir/$lkfile not found"
    fi
  fi
}

# func_sanitize_modulelist
# receives a list of possible module names on standard input, one per line.
# It removes those which are just file names unrelated to modules, and outputs
# the resulting list to standard output, one per line.
func_sanitize_modulelist ()
{
  sed -e '/^CVS\//d' -e '/\/CVS\//d' \
      -e '/^ChangeLog$/d' -e '/\/ChangeLog$/d' \
      -e '/^COPYING$/d' -e '/\/COPYING$/d' \
      -e '/^README$/d' -e '/\/README$/d' \
      -e '/^TEMPLATE$/d' \
      -e '/^TEMPLATE-EXTENDED$/d' \
      -e '/^TEMPLATE-TESTS$/d' \
      -e '/^\..*/d' \
      -e '/~$/d'
}

# func_all_modules
# Input:
# - local_gnulib_dir  from --local-dir
func_all_modules ()
{
  # Filter out metainformation files like README, which are not modules.
  # Filter out unit test modules; they can be retrieved through
  # --extract-tests-module if desired.
  {
    (cd "$gnulib_dir" && find modules -type f -print | sed -e 's,^modules/,,')
    if test -n "$local_gnulib_dir" && test -d "$local_gnulib_dir/modules"; then
      (cd "$local_gnulib_dir" && find modules -type f -print | sed -e 's,^modules/,,' -e 's,\.diff$,,')
    fi
  } \
      | func_sanitize_modulelist \
      | sed -e '/-tests$/d' \
      | LC_ALL=C sort -u
}

# func_exists_module module
# tests whether a module, given by name, exists
# Input:
# - local_gnulib_dir  from --local-dir
func_exists_module ()
{
  { test -f "$gnulib_dir/modules/$1" \
    || { test -n "$local_gnulib_dir" && test -d "$local_gnulib_dir/modules" \
         && test -f "$local_gnulib_dir/modules/$1"; }; } \
  && test "CVS" != "$1" \
  && test "ChangeLog" != "$1" \
  && test "COPYING" != "$1" \
  && test "README" != "$1" \
  && test "TEMPLATE" != "$1" \
  && test "TEMPLATE-EXTENDED" != "$1" \
  && test "TEMPLATE-TESTS" != "$1"
}

# func_verify_module
# verifies a module name
# Input:
# - local_gnulib_dir  from --local-dir
# - module          module name argument
func_verify_module ()
{
  if func_exists_module "$module"; then
    # OK, $module is a correct module name.
    # Verify that building the module description with 'patch' succeeds.
    func_lookup_file "modules/$module"
  else
    func_warning "module $module doesn't exist"
    module=
  fi
}

# func_verify_nontests_module
# verifies a module name, excluding tests modules
# Input:
# - local_gnulib_dir  from --local-dir
# - module          module name argument
func_verify_nontests_module ()
{
  case "$module" in
    *-tests ) module= ;;
    * ) func_verify_module ;;
  esac
}

# func_verify_tests_module
# verifies a module name, considering only tests modules
# Input:
# - local_gnulib_dir  from --local-dir
# - module          module name argument
func_verify_tests_module ()
{
  case "$module" in
    *-tests ) func_verify_module ;;
    * ) module= ;;
  esac
}

# Suffix of a sed expression that extracts a particular field from a
# module description.
# A field starts with a line that contains a keyword, such as 'Description',
# followed by a colon and optional whitespace. All following lines, up to
# the next field (or end of file if there is none) form the contents of the
# field.
# An absent field is equivalent to a field with empty contents.
# NOTE: Keep this in sync with sed_extract_cache_prog below!
sed_extract_prog=':[	 ]*$/ {
  :a
    n
    s/^Description:[	 ]*$//
    s/^Comment:[	 ]*$//
    s/^Status:[	 ]*$//
    s/^Notice:[	 ]*$//
    s/^Applicability:[	 ]*$//
    s/^Files:[	 ]*$//
    s/^Depends-on:[	 ]*$//
    s/^configure\.ac-early:[	 ]*$//
    s/^configure\.ac:[	 ]*$//
    s/^Makefile\.am:[	 ]*$//
    s/^Include:[	 ]*$//
    s/^Link:[	 ]*$//
    s/^License:[	 ]*$//
    s/^Maintainer:[	 ]*$//
    tb
    p
    ba
  :b
}'

# Piece of a sed expression that converts a field header line to a shell
# variable name,
# NOTE: Keep this in sync with sed_extract_prog above!
sed_extract_field_header='
  s/^Description:[	 ]*$/description/
  s/^Comment:[	 ]*$/comment/
  s/^Status:[	 ]*$/status/
  s/^Notice:[	 ]*$/notice/
  s/^Applicability:[	 ]*$/applicability/
  s/^Files:[	 ]*$/files/
  s/^Depends-on:[	 ]*$/dependson/
  s/^configure\.ac-early:[	 ]*$/configureac_early/
  s/^configure\.ac:[	 ]*$/configureac/
  s/^Makefile\.am:[	 ]*$/makefile/
  s/^Include:[	 ]*$/include/
  s/^Link:[	 ]*$/link/
  s/^License:[	 ]*$/license/
  s/^Maintainer:[	 ]*$/maintainer/'

if $modcache; then

  if $have_associative; then

    # Declare the associative arrays.
    declare -A modcache_cached
    sed_to_declare_statement='s|^.*/\([a-zA-Z0-9_]*\)/$|declare -A modcache_\1|p'
    declare_script=`echo "$sed_extract_field_header" | sed -n -e "$sed_to_declare_statement"`
    eval "$declare_script"

  else

    # func_cache_var module
    # computes the cache variable name corresponding to $module.
    # Note: This computation can map different module names to the same
    # cachevar (such as 'foo-bar', 'foo_bar', or 'foo/bar'); the caller has
    # to protect against this case.
    # Output:
    # - cachevar               a shell variable name
    if (f=foo; eval echo '${f//o/e}') < /dev/null 2>/dev/null | grep fee >/dev/null; then
      # Bash 2.0 and newer, ksh, and zsh support the syntax
      #   ${param//pattern/replacement}
      # as a shorthand for
      #   `echo "$param" | sed -e "s/pattern/replacement/g"`.
      # Note: The 'eval' is necessary for dash and NetBSD /bin/sh.
      eval 'func_cache_var ()
      {
        cachevar=c_${1//[!a-zA-Z0-9_]/_}
      }'
    else
      func_cache_var ()
      {
        case $1 in
          *[!a-zA-Z0-9_]*)
            cachevar=c_`echo "$1" | LC_ALL=C sed -e 's/[^a-zA-Z0-9_]/_/g'` ;;
          *)
            cachevar=c_$1 ;;
        esac
      }
    fi

  fi

  # func_init_sed_convert_to_cache_statements
  # Input:
  # - modcachevar_assignment
  # Output:
  # - sed_convert_to_cache_statements
  func_init_sed_convert_to_cache_statements ()
  {
    # 'sed' script that turns a module description into shell script
    # assignments, suitable to be eval'ed.  All active characters are escaped.
    # This script turns
    #   Description:
    #   Some module's description
    #
    #   Files:
    #   lib/file.h
    # into:
    #   modcache_description[$1]=\
    #   'Some module'"'"'s description
    #   '
    #   modcache_files[$1]=\
    #   'lib/file.h'
    # or:
    #   c_MODULE_description_set=set; c_MODULE_description=\
    #   'Some module'"'"'s description
    #   '
    #   c_MODULE_files_set=set; c_MODULE_files=\
    #   'lib/file.h'
    # The script consists of two parts:
    # 1) Ignore the lines before the first field header.
    # 2) A loop, treating non-field-header lines by escaping single quotes
    #    and adding a closing quote in the last line,
    sed_convert_to_cache_statements="
      :llla
        # Here we have not yet seen a field header.

        # See if the current line contains a field header.
        t llla1
        :llla1
        ${sed_extract_field_header}
        t lllb

        # No field header. Ignore the line.

        # Read the next line. Upon EOF, just exit.
        n
      b llla

      :lllb
        # The current line contains a field header.

        # Turn it into the beginning of an assignment.
        s/^\\(.*\\)\$/${modcachevar_assignment}\\\\/

        # Move it to the hold space. Don't print it yet,
        # because we want no assignment if the field is empty.
        h

        # Read the next line.
        # Upon EOF, the field was empty. Print no assignment. Just exit.
        n

        # See if the current line contains a field header.
        t lllb1
        :lllb1
        ${sed_extract_field_header}
        # If it is, the previous field was empty. Print no assignment.
        t lllb

        # Not a field header.

        # Print the previous line, held in the hold space.
        x
        p
        x

        # Transform single quotes.
        s/'/'\"'\"'/g

        # Prepend a single quote.
        s/^/'/

        :lllc

          # Move it to the hold space.
          h

          # Read the next line.
          # Upon EOF, branch.
          \${
            b llle
          }
          n

          # See if the current line contains a field header.
          t lllc1
          :lllc1
          ${sed_extract_field_header}
          t llld

          # Print the previous line, held in the hold space.
          x
          p
          x

          # Transform single quotes.
          s/'/'\"'\"'/g

        b lllc

        :llld
        # A field header.
        # Print the previous line, held in the hold space, with a single quote
        # to end the assignment.
        x
        s/\$/'/
        p
        x

      b lllb

      :llle
      # EOF seen.
      # Print the previous line, held in the hold space, with a single quote
      # to end the assignment.
      x
      s/\$/'/
      p
      # Exit.
      n
      "
    if ! $sed_comments; then
      # Remove comments.
      sed_convert_to_cache_statements=`echo "$sed_convert_to_cache_statements" \
                                       | sed -e 's/^ *//' -e 's/^#.*//'`
    fi
  }

  if $have_associative; then
    # sed_convert_to_cache_statements does not depend on the module.
    modcachevar_assignment='modcache_\1[$1]='
    func_init_sed_convert_to_cache_statements
  fi

  # func_cache_lookup_module module
  #
  # looks up a module, like 'func_lookup_file modules/$module', and stores all
  # of its relevant data in a cache in the memory of the processing shell.  If
  # already cached, it does not look it up again, thus saving file access time.
  # Parameters:
  # - module                             non-empty string
  # Output if $have_associative:
  # - modcache_cached[$module]           set to yes
  # - modcache_description[$module] ==
  # - modcache_status[$module]        \  set to the field's value, minus the
  # - ...                             /  final newline,
  # - modcache_maintainer[$module]  ==   or unset if the field's value is empty
  # Output if ! $have_associative:
  # - cachevar                           a shell variable name
  # - ${cachevar}_cached                 set to $module
  # - ${cachevar}_description       ==
  # - ${cachevar}_status              \  set to the field's value, minus the
  # - ...                             /  final newline,
  # - ${cachevar}_maintainer        ==   or unset if the field's value is empty
  # - ${cachevar}_description_set   ==
  # - ${cachevar}_status_set          \  set to non-empty if the field's value
  # - ...                             /  is non-empty,
  # - ${cachevar}_maintainer_set    ==   or unset if the field's value is empty
  func_cache_lookup_module ()
  {
    if $have_associative; then
      eval 'cached=${modcache_cached[$1]}'
    else
      func_cache_var "$1"
      eval "cached=\"\$${cachevar}_cached\""
    fi
    if test -z "$cached"; then
      # Not found in cache. Look it up on the file system.
      func_lookup_file "modules/$1"
      if $have_associative; then
        eval 'modcache_cached[$1]=yes'
      else
        eval "${cachevar}_cached=\"\$1\""
      fi
      if ! $have_associative; then
        # sed_convert_to_cache_statements depends on the module.
        modcachevar_assignment="${cachevar}"'_\1_set=set; '"${cachevar}"'_\1='
        func_init_sed_convert_to_cache_statements
      fi
      cache_statements=`LC_ALL=C sed -n -e "$sed_convert_to_cache_statements" < "$lookedup_file"`
      eval "$cache_statements"
    else
      if ! $have_associative; then
        if test "$1" != "$cached"; then
          func_fatal_error "cache variable collision between $1 and $cached"
        fi
      fi
    fi
  }

fi

# func_get_description module
# Input:
# - local_gnulib_dir  from --local-dir
# - modcache          true or false, from --cache-modules/--no-cache-modules
func_get_description ()
{
  if ! $modcache; then
    func_lookup_file "modules/$1"
    sed -n -e "/^Description$sed_extract_prog" < "$lookedup_file"
  else
    func_cache_lookup_module "$1"
    # Output the field's value, including the final newline (if any).
    if $have_associative; then
      if eval 'test -n "${modcache_description[$1]+set}"'; then
        eval 'echo "${modcache_description[$1]}"'
      fi
    else
      eval "field_set=\"\$${cachevar}_description_set\""
      if test -n "$field_set"; then
        eval "field_value=\"\$${cachevar}_description\""
        echo "${field_value}"
      fi
    fi
  fi
}

# func_get_comment module
# Input:
# - local_gnulib_dir  from --local-dir
# - modcache          true or false, from --cache-modules/--no-cache-modules
func_get_comment ()
{
  if ! $modcache; then
    func_lookup_file "modules/$1"
    sed -n -e "/^Comment$sed_extract_prog" < "$lookedup_file"
  else
    func_cache_lookup_module "$1"
    # Output the field's value, including the final newline (if any).
    if $have_associative; then
      if eval 'test -n "${modcache_comment[$1]+set}"'; then
        eval 'echo "${modcache_comment[$1]}"'
      fi
    else
      eval "field_set=\"\$${cachevar}_comment_set\""
      if test -n "$field_set"; then
        eval "field_value=\"\$${cachevar}_comment\""
        echo "${field_value}"
      fi
    fi
  fi
}

# func_get_status module
# Input:
# - local_gnulib_dir  from --local-dir
# - modcache          true or false, from --cache-modules/--no-cache-modules
func_get_status ()
{
  if ! $modcache; then
    func_lookup_file "modules/$1"
    sed -n -e "/^Status$sed_extract_prog" < "$lookedup_file"
  else
    func_cache_lookup_module "$1"
    # Output the field's value, including the final newline (if any).
    if $have_associative; then
      if eval 'test -n "${modcache_status[$1]+set}"'; then
        eval 'echo "${modcache_status[$1]}"'
      fi
    else
      eval "field_set=\"\$${cachevar}_status_set\""
      if test -n "$field_set"; then
        eval "field_value=\"\$${cachevar}_status\""
        echo "${field_value}"
      fi
    fi
  fi
}

# func_get_notice module
# Input:
# - local_gnulib_dir  from --local-dir
# - modcache          true or false, from --cache-modules/--no-cache-modules
func_get_notice ()
{
  if ! $modcache; then
    func_lookup_file "modules/$1"
    sed -n -e "/^Notice$sed_extract_prog" < "$lookedup_file"
  else
    func_cache_lookup_module "$1"
    # Output the field's value, including the final newline (if any).
    if $have_associative; then
      if eval 'test -n "${modcache_notice[$1]+set}"'; then
        eval 'echo "${modcache_notice[$1]}"'
      fi
    else
      eval "field_set=\"\$${cachevar}_notice_set\""
      if test -n "$field_set"; then
        eval "field_value=\"\$${cachevar}_notice\""
        echo "${field_value}"
      fi
    fi
  fi
}

# func_get_applicability module
# Input:
# - local_gnulib_dir  from --local-dir
# - modcache          true or false, from --cache-modules/--no-cache-modules
# The expected result (on stdout) is either 'main', or 'tests', or 'all'.
func_get_applicability ()
{
  if ! $modcache; then
    func_lookup_file "modules/$1"
    my_applicability=`sed -n -e "/^Applicability$sed_extract_prog" < "$lookedup_file"`
  else
    func_cache_lookup_module "$1"
    # Get the field's value, without the final newline.
    if $have_associative; then
      eval 'my_applicability="${modcache_applicability[$1]}"'
    else
      eval "my_applicability=\"\$${cachevar}_applicability\""
    fi
  fi
  if test -n "$my_applicability"; then
    echo $my_applicability
  else
    # The default is 'main' or 'tests', depending on the module's name.
    case $1 in
      *-tests) echo "tests";;
      *)       echo "main";;
    esac
  fi
}

# func_get_filelist module
# Input:
# - local_gnulib_dir  from --local-dir
# - modcache          true or false, from --cache-modules/--no-cache-modules
func_get_filelist ()
{
  if ! $modcache; then
    func_lookup_file "modules/$1"
    sed -n -e "/^Files$sed_extract_prog" < "$lookedup_file"
  else
    func_cache_lookup_module "$1"
    # Output the field's value, including the final newline (if any).
    if $have_associative; then
      if eval 'test -n "${modcache_files[$1]+set}"'; then
        eval 'echo "${modcache_files[$1]}"'
      fi
    else
      eval "field_set=\"\$${cachevar}_files_set\""
      if test -n "$field_set"; then
        eval "field_value=\"\$${cachevar}_files\""
        echo "${field_value}"
      fi
    fi
  fi
  echo m4/00gnulib.m4
  echo m4/gnulib-common.m4
  case "$autoconf_minversion" in
    2.59)
      echo m4/onceonly.m4
      ;;
  esac
}

# func_filter_filelist outputvar separator filelist prefix suffix removed_prefix removed_suffix [added_prefix [added_suffix]]
# stores in outputvar the filtered and processed filelist. Filtering: Only the
# elements starting with prefix and ending with suffix are considered.
# Processing: removed_prefix and removed_suffix are removed from each element,
# added_prefix and added_suffix are added to each element.
# prefix, suffix should not contain shell-special characters.
# removed_prefix, removed_suffix should not contain the characters "$`\{}[]^|.
# added_prefix, added_suffix should not contain the characters \|&.
func_filter_filelist ()
{
  if test "$2" != "$nl" \
     || { $fast_func_append \
          && { test -z "$6" || $fast_func_remove_prefix; } \
          && { test -z "$7" || $fast_func_remove_suffix; }; \
        }; then
    ffflist=
    for fff in $3; do
      # Do not quote possibly-empty parameters in case patterns,
      # AIX and HP-UX ksh won't match them if they are empty.
      case "$fff" in
        $4*$5)
          if test -n "$6"; then
            func_remove_prefix fff "$6"
          fi
          if test -n "$7"; then
            func_remove_suffix fff "$7"
          fi
          fff="$8${fff}$9"
          if test -z "$ffflist"; then
            ffflist="${fff}"
          else
            func_append ffflist "$2${fff}"
          fi
          ;;
      esac
    done
  else
    sed_fff_filter="s|^$6\(.*\)$7\$|$8\\1$9|"
    ffflist=`for fff in $3; do
               case "$fff" in
                 $4*$5) echo "$fff" ;;
               esac
             done | sed -e "$sed_fff_filter"`
  fi
  eval "$1=\"\$ffflist\""
}

# func_get_dependencies module
# Input:
# - local_gnulib_dir  from --local-dir
# - modcache          true or false, from --cache-modules/--no-cache-modules
func_get_dependencies ()
{
  # ${module}-tests implicitly depends on ${module}, if that module exists.
  case "$1" in
    *-tests)
      fgd1="$1"
      func_remove_suffix fgd1 '-tests'
      if func_exists_module "$fgd1"; then
        echo "$fgd1"
      fi
      ;;
  esac
  # Then the explicit dependencies listed in the module description.
  { if ! $modcache; then
      func_lookup_file "modules/$1"
      sed -n -e "/^Depends-on$sed_extract_prog" < "$lookedup_file"
    else
      func_cache_lookup_module "$1"
      # Output the field's value, including the final newline (if any).
      if $have_associative; then
        if eval 'test -n "${modcache_dependson[$1]+set}"'; then
          eval 'echo "${modcache_dependson[$1]}"'
        fi
      else
        eval "field_set=\"\$${cachevar}_dependson_set\""
        if test -n "$field_set"; then
          eval "field_value=\"\$${cachevar}_dependson\""
          echo "${field_value}"
        fi
      fi
    fi
  } \
  | sed -e '/^#/d'
}

# func_get_autoconf_early_snippet module
# Input:
# - local_gnulib_dir  from --local-dir
# - modcache          true or false, from --cache-modules/--no-cache-modules
func_get_autoconf_early_snippet ()
{
  if ! $modcache; then
    func_lookup_file "modules/$1"
    sed -n -e "/^configure\.ac-early$sed_extract_prog" < "$lookedup_file"
  else
    func_cache_lookup_module "$1"
    # Output the field's value, including the final newline (if any).
    if $have_associative; then
      if eval 'test -n "${modcache_configureac_early[$1]+set}"'; then
        eval 'echo "${modcache_configureac_early[$1]}"'
      fi
    else
      eval "field_set=\"\$${cachevar}_configureac_early_set\""
      if test -n "$field_set"; then
        eval "field_value=\"\$${cachevar}_configureac_early\""
        echo "${field_value}"
      fi
    fi
  fi
}

# func_get_autoconf_snippet module
# Input:
# - local_gnulib_dir  from --local-dir
# - modcache          true or false, from --cache-modules/--no-cache-modules
func_get_autoconf_snippet ()
{
  if ! $modcache; then
    func_lookup_file "modules/$1"
    sed -n -e "/^configure\.ac$sed_extract_prog" < "$lookedup_file"
  else
    func_cache_lookup_module "$1"
    # Output the field's value, including the final newline (if any).
    if $have_associative; then
      if eval 'test -n "${modcache_configureac[$1]+set}"'; then
        eval 'echo "${modcache_configureac[$1]}"'
      fi
    else
      eval "field_set=\"\$${cachevar}_configureac_set\""
      if test -n "$field_set"; then
        eval "field_value=\"\$${cachevar}_configureac\""
        echo "${field_value}"
      fi
    fi
  fi
}

# func_get_automake_snippet_conditional module
# returns the part of the Makefile.am snippet that can be put inside Automake
# conditionals.
# Input:
# - local_gnulib_dir  from --local-dir
# - modcache          true or false, from --cache-modules/--no-cache-modules
func_get_automake_snippet_conditional ()
{
  if ! $modcache; then
    func_lookup_file "modules/$1"
    sed -n -e "/^Makefile\.am$sed_extract_prog" < "$lookedup_file"
  else
    func_cache_lookup_module "$1"
    # Output the field's value, including the final newline (if any).
    if $have_associative; then
      if eval 'test -n "${modcache_makefile[$1]+set}"'; then
        eval 'echo "${modcache_makefile[$1]}"'
      fi
    else
      eval "field_set=\"\$${cachevar}_makefile_set\""
      if test -n "$field_set"; then
        eval "field_value=\"\$${cachevar}_makefile\""
        echo "${field_value}"
      fi
    fi
  fi
}

# func_get_automake_snippet_unconditional module
# returns the part of the Makefile.am snippet that must stay outside of
# Automake conditionals.
# Input:
# - local_gnulib_dir  from --local-dir
# - modcache          true or false, from --cache-modules/--no-cache-modules
func_get_automake_snippet_unconditional ()
{
  case "$1" in
    *-tests)
      # *-tests module live in tests/, not lib/.
      # Synthesize an EXTRA_DIST augmentation.
      all_files=`func_get_filelist $1`
      func_filter_filelist tests_files " " "$all_files" 'tests/' '' 'tests/' ''
      extra_files="$tests_files"
      path=~/extra_files
      echo "$tests_files > "$path"
      if test -n "$extra_files"; then
        echo "EXTRA_DIST +=" $extra_files
        echo
      fi
      ;;
    *)
      # Synthesize an EXTRA_DIST augmentation.
      sed_combine_lines='/\\$/{
        :a
        N
        s/\\\n/ /
        s/\\$/\\/
        ta
      }'
      sed_extract_mentioned_files='s/^lib_SOURCES[	 ]*+=[	 ]*//p'
      already_mentioned_files=` \
        { if ! $modcache; then
            func_lookup_file "modules/$1"
            sed -n -e "/^Makefile\.am$sed_extract_prog" < "$lookedup_file"
          else
            func_cache_lookup_module "$1"
            if $have_associative; then
              if eval 'test -n "${modcache_makefile[$1]+set}"'; then
                eval 'echo "${modcache_makefile[$1]}"'
              fi
            else
              eval 'field_set="$'"${cachevar}"'_makefile_set"'
              if test -n "$field_set"; then
                eval 'field_value="$'"${cachevar}"'_makefile"'
                echo "${field_value}"
              fi
            fi
          fi
        } \
        | sed -e "$sed_combine_lines" \
        | sed -n -e "$sed_extract_mentioned_files" | sed -e 's/#.*//'`
      all_files=`func_get_filelist $1`
      func_filter_filelist lib_files "$nl" "$all_files" 'lib/' '' 'lib/' ''
      # Remove $already_mentioned_files from $lib_files.
      echo "$lib_files" | LC_ALL=C sort -u > "$tmp"/lib-files
      extra_files=`for f in $already_mentioned_files; do echo $f; done \
                   | LC_ALL=C sort -u | LC_ALL=C join -v 2 - "$tmp"/lib-files`
      if test -n "$extra_files"; then
        echo "EXTRA_DIST +=" $extra_files
        echo
      fi
      # Synthesize also an EXTRA_lib_SOURCES augmentation.
      # This is necessary so that automake can generate the right list of
      # dependency rules.
      # A possible approach would be to use autom4te --trace of the redefined
      # AC_LIBOBJ and AC_REPLACE_FUNCS macros when creating the Makefile.am
      # (use autom4te --trace, not just grep, so that AC_LIBOBJ invocations
      # inside autoconf's built-in macros are not missed).
      # But it's simpler and more robust to do it here, based on the file list.
      # If some .c file exists and is not used with AC_LIBOBJ - for example,
      # a .c file is preprocessed into another .c file for BUILT_SOURCES -,
      # automake will generate a useless dependency; this is harmless.
      case "$1" in
        relocatable-prog-wrapper) ;;
        pt_chown) ;;
        *)
          func_filter_filelist extra_files "$nl" "$extra_files" '' '.c' '' ''
          if test -n "$extra_files"; then
            echo "EXTRA_lib_SOURCES +=" $extra_files
            echo
          fi
          ;;
      esac
      # Synthesize an EXTRA_DIST augmentation also for the files in build-aux/.
      func_filter_filelist buildaux_files "$nl" "$all_files" 'build-aux/' '' 'build-aux/' ''
      if test -n "$buildaux_files"; then
        sed_prepend_auxdir='s,^,$(top_srcdir)/'"$auxdir"'/,'
        echo "EXTRA_DIST += "`echo "$buildaux_files" | sed -e "$sed_prepend_auxdir"`
        echo
      fi
      # Synthesize an EXTRA_DIST augmentation also for the files from top/.
      func_filter_filelist top_files "$nl" "$all_files" 'top/' '' 'top/' ''
      if test -n "$top_files"; then
        sed_prepend_topdir='s,^,$(top_srcdir)/,'
        echo "EXTRA_DIST += "`echo "$top_files" | sed -e "$sed_prepend_topdir"`
        echo
      fi
      ;;
  esac
}

# func_get_automake_snippet module
# Input:
# - local_gnulib_dir  from --local-dir
# - modcache          true or false, from --cache-modules/--no-cache-modules
func_get_automake_snippet ()
{
  func_get_automake_snippet_conditional "$1"
  func_get_automake_snippet_unconditional "$1"
}

# func_get_include_directive module
# Input:
# - local_gnulib_dir  from --local-dir
# - modcache          true or false, from --cache-modules/--no-cache-modules
func_get_include_directive ()
{
  {
    if ! $modcache; then
      func_lookup_file "modules/$1"
      sed -n -e "/^Include$sed_extract_prog" < "$lookedup_file"
    else
      func_cache_lookup_module "$1"
      # Output the field's value, including the final newline (if any).
      if $have_associative; then
        if eval 'test -n "${modcache_include[$1]+set}"'; then
          eval 'echo "${modcache_include[$1]}"'
        fi
      else
        eval "field_set=\"\$${cachevar}_include_set\""
        if test -n "$field_set"; then
          eval "field_value=\"\$${cachevar}_include\""
          echo "${field_value}"
        fi
      fi
    fi
  } | sed -e 's/^\(["<]\)/#include \1/'
}

# func_get_link_directive module
# Input:
# - local_gnulib_dir  from --local-dir
# - modcache          true or false, from --cache-modules/--no-cache-modules
func_get_link_directive ()
{
  if ! $modcache; then
    func_lookup_file "modules/$1"
    sed -n -e "/^Link$sed_extract_prog" < "$lookedup_file"
  else
    func_cache_lookup_module "$1"
    # Output the field's value, including the final newline (if any).
    if $have_associative; then
      if eval 'test -n "${modcache_link[$1]+set}"'; then
        eval 'echo "${modcache_link[$1]}"'
      fi
    else
      eval "field_set=\"\$${cachevar}_link_set\""
      if test -n "$field_set"; then
        eval "field_value=\"\$${cachevar}_link\""
        echo "${field_value}"
      fi
    fi
  fi
}

# func_get_license_raw module
# Input:
# - local_gnulib_dir  from --local-dir
# - modcache          true or false, from --cache-modules/--no-cache-modules
func_get_license_raw ()
{
  if ! $modcache; then
    func_lookup_file "modules/$1"
    sed -n -e "/^License$sed_extract_prog" < "$lookedup_file"
  else
    func_cache_lookup_module "$1"
    # Output the field's value, including the final newline (if any).
    if $have_associative; then
      if eval 'test -n "${modcache_license[$1]+set}"'; then
        eval 'echo "${modcache_license[$1]}"'
      fi
    else
      eval "field_set=\"\$${cachevar}_license_set\""
      if test -n "$field_set"; then
        eval "field_value=\"\$${cachevar}_license\""
        echo "${field_value}"
      fi
    fi
  fi
}

# func_get_license module
# Input:
# - local_gnulib_dir  from --local-dir
# - modcache          true or false, from --cache-modules/--no-cache-modules
func_get_license ()
{
  # Warn if the License field is missing.
  case "$1" in
    *-tests ) ;;
    * )
      license=`func_get_license_raw "$1"`
      if test -z "$license"; then
        func_warning "module $1 lacks a License"
      fi
      ;;
  esac
  {
    func_get_license_raw "$1"
    # The default is GPL.
    echo "GPL"
  } | sed -e 's,^ *$,,' | sed -e 1q
}

# func_get_maintainer module
# Input:
# - local_gnulib_dir  from --local-dir
# - modcache          true or false, from --cache-modules/--no-cache-modules
func_get_maintainer ()
{
  if ! $modcache; then
    func_lookup_file "modules/$1"
    sed -n -e "/^Maintainer$sed_extract_prog" < "$lookedup_file"
  else
    func_cache_lookup_module "$1"
    # Output the field's value, including the final newline (if any).
    if $have_associative; then
      if eval 'test -n "${modcache_maintainer[$1]+set}"'; then
        eval 'echo "${modcache_maintainer[$1]}"'
      fi
    else
      eval "field_set=\"\$${cachevar}_maintainer_set\""
      if test -n "$field_set"; then
        eval "field_value=\"\$${cachevar}_maintainer\""
        echo "${field_value}"
      fi
    fi
  fi
}

# func_get_tests_module module
# Input:
# - local_gnulib_dir  from --local-dir
func_get_tests_module ()
{
  # The naming convention for tests modules is hardwired: ${module}-tests.
  if test -f "$gnulib_dir/modules/$1"-tests \
     || { test -n "$local_gnulib_dir" && test -d "$local_gnulib_dir/modules" \
          && test -f "$local_gnulib_dir/modules/$1"-tests; }; then
    echo "$1"-tests
  fi
}

# func_acceptable module
# tests whether a module is acceptable.
# Input:
# - avoidlist       list of modules to avoid
func_acceptable ()
{
  for avoid in $avoidlist; do
    if test "$avoid" = "$1"; then
      return 1
    fi
  done
  return 0
}

# sed expression to keep the first 32 characters of each line.
sed_first_32_chars='s/^\(................................\).*/\1/'

# func_module_shellfunc_name module
# computes the shell function name that will contain the m4 macros for the module.
# Input:
# - macro_prefix    prefix to use
# Output:
# - shellfunc       shell function name
func_module_shellfunc_name ()
{
  case $1 in
    *[!a-zA-Z0-9_]*)
      shellfunc=func_${macro_prefix}_gnulib_m4code_`echo "$1" | md5sum | LC_ALL=C sed -e "$sed_first_32_chars"` ;;
    *)
      shellfunc=func_${macro_prefix}_gnulib_m4code_$1 ;;
  esac
}

# func_module_shellvar_name module
# computes the shell variable name the will be set to true once the m4 macros
# for the module have been executed.
# Output:
# - shellvar        shell variable name
func_module_shellvar_name ()
{
  case $1 in
    *[!a-zA-Z0-9_]*)
      shellvar=${macro_prefix}_gnulib_enabled_`echo "$1" | md5sum | LC_ALL=C sed -e "$sed_first_32_chars"` ;;
    *)
      shellvar=${macro_prefix}_gnulib_enabled_$1 ;;
  esac
}

# func_module_conditional_name module
# computes the automake conditional name for the module.
# Output:
# - conditional     name of automake conditional
func_module_conditional_name ()
{
  case $1 in
    *[!a-zA-Z0-9_]*)
      conditional=${macro_prefix}_GNULIB_ENABLED_`echo "$1" | md5sum | LC_ALL=C sed -e "$sed_first_32_chars"` ;;
    *)
      conditional=${macro_prefix}_GNULIB_ENABLED_$1 ;;
  esac
}

# func_uncond_add_module B
# notes the presence of B as an unconditional module.
#
# func_conddep_add_module A B cond
# notes the presence of a conditional dependency from module A to module B,
# subject to the condition that A is enabled and cond is true.
#
# func_cond_module_p B
# tests whether module B is conditional.
#
# func_cond_module_condition A B
# returns the condition when B should be enabled as a dependency of A, once the
# m4 code for A has been executed.
# Output: - condition
#
if $have_associative; then
  declare -A conddep_isuncond
  declare -A conddep_dependers
  declare -A conddep_condition
  func_uncond_add_module ()
  {
    eval 'conddep_isuncond[$1]=true'
    eval 'unset conddep_dependers[$1]'
  }
  func_conddep_add_module ()
  {
    eval 'isuncond="${conddep_isuncond[$2]}"'
    if test -z "$isuncond"; then
      # No unconditional dependency to B known at this point.
      eval 'conddep_dependers[$2]="${conddep_dependers[$2]} $1"'
      eval 'conddep_condition[$1---$2]="$3"'
    fi
  }
  func_cond_module_p ()
  {
    eval 'previous_dependers="${conddep_dependers[$1]}"'
    test -n "$previous_dependers"
  }
  func_cond_module_condition ()
  {
    eval 'condition="${conddep_condition[$1---$2]}"'
  }
else
  func_uncond_add_module ()
  {
    case $1 in
      *[!a-zA-Z0-9_]*)
        suffix=`echo "$1" | md5sum | LC_ALL=C sed -e "$sed_first_32_chars"` ;;
      *)
        suffix=$1 ;;
    esac
    eval 'conddep_isuncond_'"$suffix"'=true'
    eval 'unset conddep_dependers_'"$suffix"
  }
  func_conddep_add_module ()
  {
    case $2 in
      *[!a-zA-Z0-9_]*)
        suffix=`echo "$2" | md5sum | LC_ALL=C sed -e "$sed_first_32_chars"` ;;
      *)
        suffix=$2 ;;
    esac
    eval 'isuncond="${conddep_isuncond_'"$suffix"'}"'
    if test -z "$isuncond"; then
      eval 'conddep_dependers_'"$suffix"'="${conddep_dependers_'"$suffix"'} $1"'
      suffix=`echo "$1---$2" | md5sum | LC_ALL=C sed -e "$sed_first_32_chars"`
      eval 'conddep_condition_'"$suffix"'="$3"'
    fi
  }
  func_cond_module_p ()
  {
    case $1 in
      *[!a-zA-Z0-9_]*)
        suffix=`echo "$1" | md5sum | LC_ALL=C sed -e "$sed_first_32_chars"` ;;
      *)
        suffix=$1 ;;
    esac
    eval 'previous_dependers="${conddep_dependers_'"$suffix"'}"'
    test -n "$previous_dependers"
  }
  func_cond_module_condition ()
  {
    suffix=`echo "$1---$2" | md5sum | LC_ALL=C sed -e "$sed_first_32_chars"`
    eval 'condition="${conddep_condition_'"$suffix"'}"'
  }
fi

sed_dependencies_without_conditions='s/ *\[.*//'

# func_modules_transitive_closure
# Input:
# - local_gnulib_dir  from --local-dir
# - modcache        true or false, from --cache-modules/--no-cache-modules
# - modules         list of specified modules
# - inctests        true if tests should be included, blank otherwise
# - incobsolete     true if obsolete modules among dependencies should be
#                   included, blank otherwise
# - inc_cxx_tests   true if C++ interoperability tests should be included,
#                   blank otherwise
# - inc_longrunning_tests  true if long-runnings tests should be included,
#                          blank otherwise
# - inc_privileged_tests  true if tests that require root privileges should be
#                         included, blank otherwise
# - inc_unportable_tests  true if tests that fail on some platforms should be
#                         included, blank otherwise
# - inc_all_direct_tests   true if all kinds of problematic unit tests among
#                          the unit tests of the specified modules should be
#                          included, blank otherwise
# - inc_all_indirect_tests   true if all kinds of problematic unit tests among
#                            the unit tests of the dependencies should be
#                            included, blank otherwise
# - excl_cxx_tests   true if C++ interoperability tests should be excluded,
#                    blank otherwise
# - excl_longrunning_tests  true if long-runnings tests should be excluded,
#                           blank otherwise
# - excl_privileged_tests  true if tests that require root privileges should be
#                          excluded, blank otherwise
# - excl_unportable_tests  true if tests that fail on some platforms should be
#                          excluded, blank otherwise
# - avoidlist       list of modules to avoid
# - cond_dependencies  true if conditional dependencies shall be supported,
#                      blank otherwise
# - tmp             pathname of a temporary directory
# Output:
# - modules         list of modules, including dependencies
# - conddep_dependers, conddep_condition  information about conditionally
#                                         enabled modules
func_modules_transitive_closure ()
{
  sed_escape_dependency='s|\([/.]\)|\\\1|g'
  # In order to process every module only once (for speed), process an "input
  # list" of modules, producing an "output list" of modules. During each round,
  # more modules can be queued in the input list. Once a module on the input
  # list has been processed, it is added to the "handled list", so we can avoid
  # to process it again.
  handledmodules=
  inmodules="$modules"
  outmodules=
  fmtc_inc_all_tests="$inc_all_direct_tests"
  if test "$cond_dependencies" = true; then
    for module in $inmodules; do
      func_verify_module
      if test -n "$module"; then
        if func_acceptable $module; then
          func_uncond_add_module $module
        fi
      fi
    done
  fi
  while test -n "$inmodules"; do
    inmodules_this_round="$inmodules"
    inmodules=                    # Accumulator, queue for next round
    for module in $inmodules_this_round; do
      func_verify_module
      if test -n "$module"; then
        if func_acceptable $module; then
          func_append outmodules " $module"
          if test "$cond_dependencies" = true; then
            if func_get_automake_snippet_conditional $module | grep '^if ' > /dev/null; then
              # A module whose Makefile.am snippet contains a reference to an
              # automake conditional. If we were to use it conditionally, we
              # would get an error
              #   configure: error: conditional "..." was never defined.
              # because automake 1.11.1 does not handle nested conditionals
              # correctly. As a workaround, make the module unconditional.
              func_uncond_add_module $module
            fi
            if func_cond_module_p $module; then
              conditional=true
            else
              conditional=false
            fi
          fi
          deps=`func_get_dependencies $module | sed -e "$sed_dependencies_without_conditions"`
          # Duplicate dependencies are harmless, but Jim wants a warning.
          duplicated_deps=`echo "$deps" | LC_ALL=C sort | LC_ALL=C uniq -d`
          if test -n "$duplicated_deps"; then
            func_warning "module $module has duplicated dependencies: "`echo $duplicated_deps`
          fi
          if test -n "$inctests"; then
            testsmodule=`func_get_tests_module $module`
            if test -n "$testsmodule"; then
              deps="$deps $testsmodule"
            fi
          fi
          for dep in $deps; do
            # Determine whether to include the dependency or tests module.
            inc=true
            for word in `func_get_status $dep`; do
              case "$word" in
                obsolete)
                  test -n "$incobsolete" \
                    || inc=false
                  ;;
                c++-test)
                  test -z "$excl_cxx_tests" \
                    || inc=false
                  test -n "$fmtc_inc_all_tests" || test -n "$inc_cxx_tests" \
                    || inc=false
                  ;;
                longrunning-test)
                  test -z "$excl_longrunning_tests" \
                    || inc=false
                  test -n "$fmtc_inc_all_tests" || test -n "$inc_longrunning_tests" \
                    || inc=false
                  ;;
                privileged-test)
                  test -z "$excl_privileged_tests" \
                    || inc=false
                  test -n "$fmtc_inc_all_tests" || test -n "$inc_privileged_tests" \
                    || inc=false
                  ;;
                unportable-test)
                  test -z "$excl_unportable_tests" \
                    || inc=false
                  test -n "$fmtc_inc_all_tests" || test -n "$inc_unportable_tests" \
                    || inc=false
                  ;;
                *-test)
                  test -n "$fmtc_inc_all_tests" \
                    || inc=false
                  ;;
              esac
            done
            if $inc && func_acceptable "$dep"; then
              func_append inmodules " $dep"
              if test "$cond_dependencies" = true; then
                escaped_dep=`echo "$dep" | sed -e "$sed_escape_dependency"`
                sed_extract_condition1='/^ *'"$escaped_dep"' *$/{
                  s/^.*$/true/p
                }'
                sed_extract_condition2='/^ *'"$escaped_dep"' *\[.*\] *$/{
                  s/^ *'"$escaped_dep"' *\[\(.*\)\] *$/\1/p
                }'
                condition=`func_get_dependencies $module | sed -n -e "$sed_extract_condition1" -e "$sed_extract_condition2"`
                if test "$condition" = true; then
                  condition=
                fi
                if test -n "$condition"; then
                  func_conddep_add_module "$module" "$dep" "$condition"
                else
                  if $conditional; then
                    func_conddep_add_module "$module" "$dep" true
                  else
                    func_uncond_add_module "$dep"
                  fi
                fi
              fi
            fi
          done
        fi
      fi
    done
    handledmodules=`for m in $handledmodules $inmodules_this_round; do echo $m; done | LC_ALL=C sort -u`
    # Remove $handledmodules from $inmodules.
    for m in $inmodules; do echo $m; done | LC_ALL=C sort -u > "$tmp"/queued-modules
    inmodules=`echo "$handledmodules" | LC_ALL=C join -v 2 - "$tmp"/queued-modules`
    fmtc_inc_all_tests="$inc_all_indirect_tests"
  done
  modules=`for m in $outmodules; do echo $m; done | LC_ALL=C sort -u`
  rm -f "$tmp"/queued-modules
}

# func_show_module_list
# Input:
# - specified_modules  list of specified modules (one per line, sorted)
# - modules         complete list of modules (one per line, sorted)
# - tmp             pathname of a temporary directory
func_show_module_list ()
{
  if case "$TERM" in
       xterm*) test -t 1;;
       *) false;;
     esac; then
    # Assume xterm compatible escape sequences.
    bold_on=`printf '\x1b[1m'`
    bold_off=`printf '\x1b[0m'`
  else
    bold_on=
    bold_off=
  fi
  echo "Module list with included dependencies (indented):"
  echo "$specified_modules" | sed -e '/^$/d' -e 's/$/| /' > "$tmp"/specified-modules
  echo "$modules" | sed -e '/^$/d' \
    | LC_ALL=C join -t '|' -a2 "$tmp"/specified-modules - \
    | sed -e 's/^\(.*\)|.*/|\1/' -e 's/^/    /' -e 's/^    |\(.*\)$/  '"${bold_on}"'\1'"${bold_off}"'/'
}

# func_modules_transitive_closure_separately
# Determine main module list and tests-related module list separately.
# The main module list is the transitive closure of the specified modules,
# ignoring tests modules. Its lib/* sources go into $sourcebase/. If --lgpl
# is specified, it will consist only of LGPLed source.
# The tests-related module list is the transitive closure of the specified
# modules, including tests modules, minus the main module list excluding
# modules of applicability 'all'. Its lib/* sources (brought in through
# dependencies of *-tests modules) go into $testsbase/. It may contain GPLed
# source, even if --lgpl is specified.
# Input:
# - local_gnulib_dir  from --local-dir
# - modcache        true or false, from --cache-modules/--no-cache-modules
# - specified_modules  list of specified modules
# - inctests        true if tests should be included, blank otherwise
# - incobsolete     true if obsolete modules among dependencies should be
#                   included, blank otherwise
# - inc_cxx_tests   true if C++ interoperability tests should be included,
#                   blank otherwise
# - inc_longrunning_tests  true if long-runnings tests should be included,
#                          blank otherwise
# - inc_privileged_tests  true if tests that require root privileges should be
#                         included, blank otherwise
# - inc_unportable_tests  true if tests that fail on some platforms should be
#                         included, blank otherwise
# - inc_all_direct_tests   true if all kinds of problematic unit tests among
#                          the unit tests of the specified modules should be
#                          included, blank otherwise
# - inc_all_indirect_tests   true if all kinds of problematic unit tests among
#                            the unit tests of the dependencies should be
#                            included, blank otherwise
# - excl_cxx_tests   true if C++ interoperability tests should be excluded,
#                    blank otherwise
# - excl_longrunning_tests  true if long-runnings tests should be excluded,
#                           blank otherwise
# - excl_privileged_tests  true if tests that require root privileges should be
#                          excluded, blank otherwise
# - excl_unportable_tests  true if tests that fail on some platforms should be
#                          excluded, blank otherwise
# - avoidlist       list of modules to avoid
# - cond_dependencies  true if conditional dependencies shall be supported,
#                      blank otherwise
# - tmp             pathname of a temporary directory
# Output:
# - main_modules    list of modules, including dependencies
# - testsrelated_modules  list of tests-related modules, including dependencies
# - conddep_dependers, conddep_condition  information about conditionally
#                                         enabled modules
func_modules_transitive_closure_separately ()
{
  # Determine main module list.
  saved_inctests="$inctests"
  inctests=""
  modules="$specified_modules"
  func_modules_transitive_closure
  main_modules="$modules"
  inctests="$saved_inctests"
  if test $verbose -ge 1; then
    echo "Main module list:"
    echo "$main_modules" | sed -e 's/^/  /'
  fi
  # Determine tests-related module list.
  echo "$final_modules" | LC_ALL=C sort -u > "$tmp"/final-modules
  testsrelated_modules=`for module in $main_modules; do
                          if test \`func_get_applicability $module\` = main; then
                            echo $module
                          fi
                        done \
                        | LC_ALL=C sort -u | LC_ALL=C join -v 2 - "$tmp"/final-modules`
  echo "$testsrelated_modules" > ~/testsrelated_modules
  echo "$main_modules" > ~/main_modules
  if test $verbose -ge 1; then
    echo "Tests-related module list:"
    echo "$testsrelated_modules" | sed -e 's/^/  /'
  fi
}

# func_determine_use_libtests
# Determines whether a $testsbase/libtests.a is needed.
# Input:
# - local_gnulib_dir  from --local-dir
# - modcache        true or false, from --cache-modules/--no-cache-modules
# - testsrelated_modules  list of tests-related modules, including dependencies
# Output:
# - use_libtests    true if a $testsbase/libtests.a is needed, false otherwise
func_determine_use_libtests ()
{
  use_libtests=false
  for module in $testsrelated_modules; do
    func_verify_nontests_module
    if test -n "$module"; then
      all_files=`func_get_filelist $module`
      # Test whether some file in $all_files lies in lib/.
      for f in $all_files; do
        case $f in
          lib/*)
            use_libtests=true
            break 2
            ;;
        esac
      done
    fi
  done
}

# func_modules_add_dummy
# Input:
# - local_gnulib_dir  from --local-dir
# - modcache        true or false, from --cache-modules/--no-cache-modules
# - modules         list of modules, including dependencies
# Output:
# - modules         list of modules, including 'dummy' if needed
func_modules_add_dummy ()
{
  # Determine whether any module provides a lib_SOURCES augmentation.
  have_lib_SOURCES=
  sed_remove_backslash_newline=':a
/\\$/{
s/\\$//
N
s/\n//
ba
}'
  for module in $modules; do
    func_verify_nontests_module
    if test -n "$module"; then
      # Extract the value of "lib_SOURCES += ...".
      for file in `func_get_automake_snippet "$module" | sed -e "$sed_remove_backslash_newline" | sed -n -e 's,^lib_SOURCES[	 ]*+=\([^#]*\).*$,\1,p'`; do
        # Ignore .h files since they are not compiled.
        case "$file" in
          *.h) ;;
          *)
            have_lib_SOURCES=yes
            break 2
            ;;
        esac
      done
    fi
  done
  # Add the dummy module, to make sure the library will be non-empty.
  if test -z "$have_lib_SOURCES"; then
    if func_acceptable "dummy"; then
      func_append modules " dummy"
    fi
  fi
}

# func_modules_add_dummy_separately
# Input:
# - local_gnulib_dir  from --local-dir
# - modcache        true or false, from --cache-modules/--no-cache-modules
# - main_modules    list of modules, including dependencies
# - testsrelated_modules  list of tests-related modules, including dependencies
# - use_libtests    true if a $testsbase/libtests.a is needed, false otherwise
# Output:
# - main_modules    list of modules, including 'dummy' if needed
# - testsrelated_modules  list of tests-related modules, including 'dummy' if
#                         needed
func_modules_add_dummy_separately ()
{
  # Add the dummy module to the main module list if needed.
  modules="$main_modules"
  func_modules_add_dummy
  main_modules="$modules"

  # Add the dummy module to the tests-related module list if needed.
  if $use_libtests; then
    modules="$testsrelated_modules"
    func_modules_add_dummy
    testsrelated_modules="$modules"
  fi
}

# func_modules_notice
# Input:
# - local_gnulib_dir  from --local-dir
# - modcache        true or false, from --cache-modules/--no-cache-modules
# - verbose         integer, default 0, inc/decremented by --verbose/--quiet
# - modules         list of modules, including dependencies
func_modules_notice ()
{
  if test $verbose -ge -1; then
    for module in $modules; do
      func_verify_module
      if test -n "$module"; then
        msg=`func_get_notice $module`
        if test -n "$msg"; then
          echo "Notice from module $module:"
          echo "$msg" | sed -e 's/^/  /'
        fi
      fi
    done
  fi
}

# func_modules_to_filelist
# Input:
# - local_gnulib_dir  from --local-dir
# - modcache        true or false, from --cache-modules/--no-cache-modules
# - modules         list of modules, including dependencies
# Output:
# - files           list of files
func_modules_to_filelist ()
{
  files=
  for module in $modules; do
    func_verify_module
    if test -n "$module"; then
      fs=`func_get_filelist $module`
      func_append files " $fs"
    fi
  done
  files=`for f in $files; do echo $f; done | LC_ALL=C sort -u`
}

# func_modules_to_filelist_separately
# Determine the final file lists.
# They must be computed separately, because files in lib/* go into
# $sourcebase/ if they are in the main file list but into $testsbase/
# if they are in the tests-related file list. Furthermore lib/dummy.c
# can be in both.
# Input:
# - local_gnulib_dir  from --local-dir
# - modcache        true or false, from --cache-modules/--no-cache-modules
# - main_modules    list of modules, including dependencies
# - testsrelated_modules  list of tests-related modules, including dependencies
func_modules_to_filelist_separately ()
{
  # Determine final main file list.
  modules="$main_modules"
  func_modules_to_filelist
  main_files="$files"
  # Determine final tests-related file list.
  modules="$testsrelated_modules"
  func_modules_to_filelist
  testsrelated_files=`echo "$files" | sed -e 's,^lib/,tests=lib/,'`
  # Merge both file lists.
  sed_remove_empty_lines='/^$/d'
  files=`{ echo "$main_files"; echo "$testsrelated_files"; } | sed -e "$sed_remove_empty_lines" | LC_ALL=C sort -u`
  if test $verbose -ge 0; then
    echo "File list:"
    sed_prettyprint_files='s,^tests=lib/\(.*\)$,lib/\1 -> tests/\1,'
    echo "$files" | sed -e "$sed_prettyprint_files" -e 's/^/  /'
  fi
}

# func_compute_include_guard_prefix
# Determine include_guard_prefix.
# Input:
# - macro_prefix    prefix of gl_LIBOBJS macros to use
# Output:
# - include_guard_prefix  replacement for ${gl_include_guard_prefix}
# - sed_replace_include_guard_prefix
#                   sed expression for resolving ${gl_include_guard_prefix}
func_compute_include_guard_prefix ()
{
  if test "$macro_prefix" = gl; then
    include_guard_prefix='GL'
  else
    include_guard_prefix='GL_'`echo "$macro_prefix" | LC_ALL=C tr '[a-z]' '[A-Z]'`
  fi
  sed_replace_include_guard_prefix='s/\${gl_include_guard_prefix}/'"${include_guard_prefix}"'/g'
}

# func_execute_command command [args...]
# Executes a command.
# Uses also the variables
# - verbose         integer, default 0, inc/decremented by --verbose/--quiet
func_execute_command ()
{
  if test $verbose -ge 0; then
    echo "executing $*"
    "$@"
  else
    # Commands like automake produce output to stderr even when they succeed.
    # Turn this output off if the command succeeds.
    "$@" > "$tmp"/cmdout 2>&1
    cmdret=$?
    if test $cmdret = 0; then
      rm -f "$tmp"/cmdout
    else
      echo "executing $*"
      cat "$tmp"/cmdout 1>&2
      rm -f "$tmp"/cmdout
      (exit $cmdret)
    fi
  fi
}

# func_dest_tmpfilename file
# determines the name of a temporary file (file is relative to destdir).
# Input:
# - destdir         target directory
# - doit            : if actions shall be executed, false if only to be printed
# - tmp             pathname of a temporary directory
# Sets variable:
#   - tmpfile       absolute filename of the temporary file
func_dest_tmpfilename ()
{
  if $doit; then
    # Put the new contents of $file in a file in the same directory (needed
    # to guarantee that an 'mv' to "$destdir/$file" works).
    tmpfile="$destdir/$1.tmp"
  else
    # Put the new contents of $file in a file in a temporary directory
    # (because the directory of "$file" might not exist).
    tmpfile="$tmp"/`basename "$1"`.tmp
  fi
}

# func_add_file
# copies a file from gnulib into the destination directory. The destination
# is known to not exist.
# Input:
# - destdir         target directory
# - local_gnulib_dir  from --local-dir
# - modcache        true or false, from --cache-modules/--no-cache-modules
# - f               the original file name
# - lookedup_file   name of the merged (combined) file
# - lookedup_tmp    true if it is located in the tmp directory, blank otherwise
# - g               the rewritten file name
# - tmpfile         absolute filename of the temporary file
# - doit            : if actions shall be executed, false if only to be printed
# - symbolic        true if files should be symlinked, copied otherwise
# - lsymbolic       true if files from local_gnulib_dir should be symlinked,
#                   copied otherwise
func_add_file ()
{
  if $doit; then
    echo "Copying file $g"
    if { test -n "$symbolic" \
         || { test -n "$lsymbolic" \
              && test "$lookedup_file" = "$local_gnulib_dir/$f"; }; } \
       && test -z "$lookedup_tmp" \
       && cmp -s "$lookedup_file" "$tmpfile"; then
      func_ln_if_changed "$lookedup_file" "$destdir/$g"
    else
      mv -f "$tmpfile" "$destdir/${g}" || func_fatal_error "failed"
    fi
  else
    echo "Copy file $g"
  fi
}

# func_update_file
# copies a file from gnulib into the destination directory. The destination
# is known to exist.
# Input:
# - destdir         target directory
# - local_gnulib_dir  from --local-dir
# - modcache        true or false, from --cache-modules/--no-cache-modules
# - f               the original file name
# - lookedup_file   name of the merged (combined) file
# - lookedup_tmp    true if it is located in the tmp directory, blank otherwise
# - g               the rewritten file name
# - tmpfile         absolute filename of the temporary file
# - doit            : if actions shall be executed, false if only to be printed
# - symbolic        true if files should be symlinked, copied otherwise
# - lsymbolic       true if files from local_gnulib_dir should be symlinked,
#                   copied otherwise
# - already_present  nonempty if the file should already exist, empty otherwise
func_update_file ()
{
  if cmp -s "$destdir/$g" "$tmpfile"; then
    : # The file has not changed.
  else
    # Replace the file.
    if $doit; then
      if test -n "$already_present"; then
        echo "Updating file $g (backup in ${g}~)"
      else
        echo "Replacing file $g (non-gnulib code backed up in ${g}~) !!"
      fi
      mv -f "$destdir/$g" "$destdir/${g}~" || func_fatal_error "failed"
      if { test -n "$symbolic" \
           || { test -n "$lsymbolic" \
                && test "$lookedup_file" = "$local_gnulib_dir/$f"; }; } \
         && test -z "$lookedup_tmp" \
         && cmp -s "$lookedup_file" "$tmpfile"; then
        func_ln_if_changed "$lookedup_file" "$destdir/$g"
      else
        mv -f "$tmpfile" "$destdir/${g}" || func_fatal_error "failed"
      fi
    else
      if test -n "$already_present"; then
        echo "Update file $g (backup in ${g}~)"
      else
        echo "Replace file $g (non-gnulib code backed up in ${g}~) !!"
      fi
    fi
  fi
}

# func_emit_lib_Makefile_am
# emits the contents of library makefile to standard output.
# Input:
# - local_gnulib_dir  from --local-dir
# - modcache        true or false, from --cache-modules/--no-cache-modules
# - modules         list of modules, including dependencies
# - libname         library name
# - pobase          directory relative to destdir where to place *.po files
# - auxdir          directory relative to destdir where to place build aux files
# - makefile_name   from --makefile-name
# - libtool         true if libtool will be used, false or blank otherwise
# - macro_prefix    prefix of gl_LIBOBJS macros to use
# - po_domain       prefix of i18n domain to use (without -gnulib suffix)
# - witness_c_macro  from --witness-c-macro
# - actioncmd       (optional) command that will reproduce this invocation
# - for_test        true if creating a package for testing, false otherwise
# - sed_replace_include_guard_prefix
#                   sed expression for resolving ${gl_include_guard_prefix}
# - destfile        filename relative to destdir of makefile being generated
# Input/Output:
# - makefile_am_edits and makefile_am_edit${edit}_{dir,var,val}
#                   list of edits to be done to Makefile.am variables
# Output:
# - uses_subdirs    nonempty if object files in subdirs exist
func_emit_lib_Makefile_am ()
{
  # When creating an includable Makefile.am snippet, augment variables with
  # += instead of assigning them.
  if test -n "$makefile_name"; then
    assign='+='
  else
    assign='='
  fi
  if test "$libtool" = true; then
    libext=la
    perhapsLT=LT
    sed_eliminate_LDFLAGS="$sed_noop"
  else
    libext=a
    perhapsLT=
    sed_eliminate_LDFLAGS='/^lib_LDFLAGS[	 ]*+=/d'
  fi
  if $for_test; then
    # When creating a package for testing: Attempt to provoke failures,
    # especially link errors, already during "make" rather than during
    # "make check", because "make check" is not possible in a cross-compiling
    # situation. Turn check_PROGRAMS into noinst_PROGRAMS.
    sed_transform_check_PROGRAMS='s,check_PROGRAMS,noinst_PROGRAMS,g'
  else
    sed_transform_check_PROGRAMS="$sed_noop"
  fi
  echo "## DO NOT EDIT! GENERATED AUTOMATICALLY!"
  echo "## Process this file with automake to produce Makefile.in."
  func_emit_copyright_notice
  if test -n "$actioncmd"; then
    # The maximum line length (excluding the terminating newline) of any file
    # that is to be preprocessed by config.status is 3070.  config.status uses
    # awk, and the HP-UX 11.00 awk fails if a line has length >= 3071;
    # similarly, the IRIX 6.5 awk fails if a line has length >= 3072.
    len=`echo "$actioncmd" | wc -c`
    if test -n "$len" && test "$len" -le 3000; then
      echo "# Reproduce by: $actioncmd"
    fi
  fi
  echo
  uses_subdirs=
  {
    for module in $modules; do
      func_verify_nontests_module
      if test -n "$module"; then
        {
          func_get_automake_snippet_conditional "$module" |
            LC_ALL=C \
            sed -e 's,lib_LIBRARIES,lib%_LIBRARIES,g' \
                -e 's,lib_LTLIBRARIES,lib%_LTLIBRARIES,g' \
                -e "$sed_eliminate_LDFLAGS" \
                -e 's,lib_\([A-Z][A-Z]*\),'"${libname}_${libext}"'_\1,g' \
                -e 's,lib%_LIBRARIES,lib_LIBRARIES,g' \
                -e 's,lib%_LTLIBRARIES,lib_LTLIBRARIES,g' \
                -e "$sed_transform_check_PROGRAMS" \
                -e "$sed_replace_include_guard_prefix"
          if test "$module" = 'alloca'; then
            echo "${libname}_${libext}_LIBADD += @${perhapsLT}ALLOCA@"
            echo "${libname}_${libext}_DEPENDENCIES += @${perhapsLT}ALLOCA@"
          fi
        } > "$tmp"/amsnippet1
        {
          func_get_automake_snippet_unconditional "$module" |
            LC_ALL=C sed -e 's,lib_\([A-Z][A-Z]*\),'"${libname}_${libext}"'_\1,g'
        } > "$tmp"/amsnippet2
        # Skip the contents if it's entirely empty.
        if grep '[^	 ]' "$tmp"/amsnippet1 "$tmp"/amsnippet2 > /dev/null ; then
          echo "## begin gnulib module $module"
          echo
          if test "$cond_dependencies" = true; then
            if func_cond_module_p "$module"; then
              func_module_conditional_name "$module"
              echo "if $conditional"
            fi
          fi
          cat "$tmp"/amsnippet1
          if test "$cond_dependencies" = true; then
            if func_cond_module_p "$module"; then
              echo "endif"
            fi
          fi
          cat "$tmp"/amsnippet2
          echo "## end   gnulib module $module"
          echo
        fi
        rm -f "$tmp"/amsnippet1 "$tmp"/amsnippet2
        # Test whether there are some source files in subdirectories.
        for f in `func_get_filelist "$module"`; do
          case $f in
            lib/*/*.c)
              uses_subdirs=yes
              break
              ;;
          esac
        done
      fi
    done
  } > "$tmp"/allsnippets
  if test -z "$makefile_name"; then
    # If there are source files in subdirectories, prevent collision of the
    # object files (example: hash.c and libxml/hash.c).
    subdir_options=
    if test -n "$uses_subdirs"; then
      subdir_options=' subdir-objects'
    fi
    echo "AUTOMAKE_OPTIONS = 1.5 gnits${subdir_options}"
  fi
  echo
  if test -z "$makefile_name"; then
    echo "SUBDIRS ="
    echo "noinst_HEADERS ="
    echo "noinst_LIBRARIES ="
    echo "noinst_LTLIBRARIES ="
    # Automake versions < 1.11.4 create an empty pkgdatadir at
    # installation time if you specify pkgdata_DATA to empty.
    # See automake bugs #10997 and #11030:
    #  * http://debbugs.gnu.org/10997
    #  * http://debbugs.gnu.org/11030
    # So we need this workaround.
    if grep '^pkgdata_DATA *+=' "$tmp"/allsnippets > /dev/null; then
      echo "pkgdata_DATA ="
    fi
    echo "EXTRA_DIST ="
    echo "BUILT_SOURCES ="
    echo "SUFFIXES ="
  fi
  echo "MOSTLYCLEANFILES $assign core *.stackdump"
  if test -z "$makefile_name"; then
    echo "MOSTLYCLEANDIRS ="
    echo "CLEANFILES ="
    echo "DISTCLEANFILES ="
    echo "MAINTAINERCLEANFILES ="
  fi
  # Execute edits that apply to the Makefile.am being generated.
  edit=0
  while test $edit != $makefile_am_edits; do
    edit=`expr $edit + 1`
    eval dir=\"\$makefile_am_edit${edit}_dir\"
    eval var=\"\$makefile_am_edit${edit}_var\"
    eval val=\"\$makefile_am_edit${edit}_val\"
    if test -n "$var"; then
      if test "${dir}Makefile.am" = "$destfile" || test "./${dir}Makefile.am" = "$destfile"; then
        echo "${var} += ${val}"
        eval "makefile_am_edit${edit}_var="
      fi
    fi
  done
  if test -n "$witness_c_macro"; then
    cppflags_part1=" -D$witness_c_macro=1"
  else
    cppflags_part1=
  fi
  if $for_test; then
    cppflags_part2=" -DGNULIB_STRICT_CHECKING=1"
  else
    cppflags_part2=
  fi
  if test -z "$makefile_name"; then
    echo
    echo "AM_CPPFLAGS =$cppflags_part1$cppflags_part2"
    echo "AM_CFLAGS ="
  else
    if test -n "$cppflags_part1$cppflags_part2"; then
      echo
      echo "AM_CPPFLAGS +=$cppflags_part1$cppflags_part2"
    fi
  fi
  echo
  if LC_ALL=C grep "^[a-zA-Z0-9_]*_${perhapsLT}LIBRARIES *+\{0,1\}= *$libname\\.$libext\$" "$tmp"/allsnippets > /dev/null \
     || { test -n "$makefile_name" \
          && test -f "$sourcebase/Makefile.am" \
          && LC_ALL=C grep "^[a-zA-Z0-9_]*_${perhapsLT}LIBRARIES *+\{0,1\}= *$libname\\.$libext\$" "$sourcebase/Makefile.am" > /dev/null; \
        }; then
    # One of the snippets or the user's Makefile.am already specifies an
    # installation location for the library. Don't confuse automake by saying
    # it should not be installed.
    :
  else
    # By default, the generated library should not be installed.
    echo "noinst_${perhapsLT}LIBRARIES += $libname.$libext"
  fi
  echo
  echo "${libname}_${libext}_SOURCES ="
  # Here we use $(LIBOBJS), not @LIBOBJS@. The value is the same. However,
  # automake during its analysis looks for $(LIBOBJS), not for @LIBOBJS@.
  echo "${libname}_${libext}_LIBADD = \$(${macro_prefix}_${perhapsLT}LIBOBJS)"
  echo "${libname}_${libext}_DEPENDENCIES = \$(${macro_prefix}_${perhapsLT}LIBOBJS)"
  echo "EXTRA_${libname}_${libext}_SOURCES ="
  if test "$libtool" = true; then
    echo "${libname}_${libext}_LDFLAGS = \$(AM_LDFLAGS)"
    echo "${libname}_${libext}_LDFLAGS += -no-undefined"
    # Synthesize an ${libname}_${libext}_LDFLAGS augmentation by combining
    # the link dependencies of all modules.
    for module in $modules; do
      func_verify_nontests_module
      if test -n "$module"; then
        func_get_link_directive "$module"
      fi
    done \
      | LC_ALL=C sed -e '/^$/d' -e 's/ when linking with libtool.*//' \
      | LC_ALL=C sort -u \
      | LC_ALL=C sed -e 's/^/'"${libname}_${libext}"'_LDFLAGS += /'
  fi
  echo
  if test -n "$pobase"; then
    echo "AM_CPPFLAGS += -DDEFAULT_TEXT_DOMAIN=\\\"${po_domain}-gnulib\\\""
    echo
  fi
  cat "$tmp"/allsnippets \
    | sed -e 's|\$(top_srcdir)/build-aux/|$(top_srcdir)/'"$auxdir"'/|g'
  echo
  echo "mostlyclean-local: mostlyclean-generic"
  echo "	@for dir in '' \$(MOSTLYCLEANDIRS); do \\"
  echo "	  if test -n \"\$\$dir\" && test -d \$\$dir; then \\"
  echo "	    echo \"rmdir \$\$dir\"; rmdir \$\$dir; \\"
  echo "	  fi; \\"
  echo "	done; \\"
  echo "	:"
  rm -f "$tmp"/allsnippets
}

# func_emit_po_Makevars
# emits the contents of po/ makefile parameterization to standard output.
# Input:
# - local_gnulib_dir  from --local-dir
# - modcache        true or false, from --cache-modules/--no-cache-modules
# - sourcebase      directory relative to destdir where to place source code
# - pobase          directory relative to destdir where to place *.po files
# - po_domain       prefix of i18n domain to use (without -gnulib suffix)
func_emit_po_Makevars ()
{
  echo "## DO NOT EDIT! GENERATED AUTOMATICALLY!"
  func_emit_copyright_notice
  echo
  echo "# Usually the message domain is the same as the package name."
  echo "# But here it has a '-gnulib' suffix."
  echo "DOMAIN = ${po_domain}-gnulib"
  echo
  echo "# These two variables depend on the location of this directory."
  echo "subdir = ${pobase}"
  echo "top_builddir = "`echo "$pobase" | sed -e 's,//*,/,g' -e 's,[^/][^/]*,..,g'`
  echo
  cat <<\EOF
# These options get passed to xgettext.
XGETTEXT_OPTIONS = \
  --keyword=_ --flag=_:1:pass-c-format \
  --keyword=N_ --flag=N_:1:pass-c-format \
  --keyword='proper_name:1,"This is a proper name. See the gettext manual, section Names."' \
  --keyword='proper_name_utf8:1,"This is a proper name. See the gettext manual, section Names."' \
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
USE_MSGCTXT = no
EOF
}

# func_emit_po_POTFILES_in
# emits the file list to be passed to xgettext to standard output.
# Input:
# - local_gnulib_dir  from --local-dir
# - modcache        true or false, from --cache-modules/--no-cache-modules
# - sourcebase      directory relative to destdir where to place source code
# - files           list of new files
func_emit_po_POTFILES_in ()
{
  echo "## DO NOT EDIT! GENERATED AUTOMATICALLY!"
  func_emit_copyright_notice
  echo
  echo "# List of files which contain translatable strings."
  echo "$files" | sed -n -e "s,^lib/,$sourcebase/,p"
}

# func_emit_tests_Makefile_am witness_macro
# emits the contents of tests makefile to standard output.
# Input:
# - local_gnulib_dir  from --local-dir
# - modcache        true or false, from --cache-modules/--no-cache-modules
# - modules         list of modules, including dependencies
# - libname         library name
# - auxdir          directory relative to destdir where to place build aux files
# - makefile_name   from --makefile-name
# - libtool         true if libtool will be used, false or blank otherwise
# - sourcebase      relative directory containing lib source code
# - m4base          relative directory containing autoconf macros
# - testsbase       relative directory containing unit test code
# - macro_prefix    prefix of gl_LIBOBJS macros to use
# - witness_c_macro  from --witness-c-macro
# - for_test        true if creating a package for testing, false otherwise
# - single_configure  true if a single configure file should be generated,
#                     false for a separate configure file for the tests
# - use_libtests    true if a libtests.a should be built, false otherwise
# - sed_replace_include_guard_prefix
#                   sed expression for resolving ${gl_include_guard_prefix}
# - destfile        filename relative to destdir of makefile being generated
# Input/Output:
# - makefile_am_edits and makefile_am_edit${edit}_{dir,var,val}
#                   list of edits to be done to Makefile.am variables
# Output:
# - uses_subdirs    nonempty if object files in subdirs exist
func_emit_tests_Makefile_am ()
{
  witness_macro="$1"
  if test "$libtool" = true; then
    libext=la
    sed_eliminate_LDFLAGS="$sed_noop"
  else
    libext=a
    sed_eliminate_LDFLAGS='/^lib_LDFLAGS[	 ]*+=/d'
  fi
  if $for_test; then
    # When creating a package for testing: Attempt to provoke failures,
    # especially link errors, already during "make" rather than during
    # "make check", because "make check" is not possible in a cross-compiling
    # situation. Turn check_PROGRAMS into noinst_PROGRAMS.
    sed_transform_check_PROGRAMS='s,check_PROGRAMS,noinst_PROGRAMS,g'
  else
    sed_transform_check_PROGRAMS="$sed_noop"
  fi
  testsbase_inverse=`echo "$testsbase" | sed -e 's,/$,,' | sed -e 's,[^/][^/]*,..,g'`
  echo "## DO NOT EDIT! GENERATED AUTOMATICALLY!"
  echo "## Process this file with automake to produce Makefile.in."
  func_emit_copyright_notice
  echo
  uses_subdirs=
  {
    for module in $modules; do
      if $for_test && ! $single_configure; then
        func_verify_tests_module
      else
        func_verify_module
      fi
      if test -n "$module"; then
        {
          func_get_automake_snippet "$module" |
            LC_ALL=C \
            sed -e 's,lib_LIBRARIES,lib%_LIBRARIES,g' \
                -e 's,lib_LTLIBRARIES,lib%_LTLIBRARIES,g' \
                -e "$sed_eliminate_LDFLAGS" \
                -e 's,lib_\([A-Z][A-Z]*\),libtests_a_\1,g' \
                -e 's,lib%_LIBRARIES,lib_LIBRARIES,g' \
                -e 's,lib%_LTLIBRARIES,lib_LTLIBRARIES,g' \
                -e "$sed_transform_check_PROGRAMS" \
                -e "$sed_replace_include_guard_prefix"
          if $use_libtests && test "$module" = 'alloca'; then
            echo "libtests_a_LIBADD += @${perhapsLT}ALLOCA@"
            echo "libtests_a_DEPENDENCIES += @${perhapsLT}ALLOCA@"
          fi
        } > "$tmp"/amsnippet
        # Skip the contents if it's entirely empty.
        if grep '[^	 ]' "$tmp"/amsnippet > /dev/null ; then
          # Mention long-running tests at the end.
          ofd=3
          for word in `func_get_status "$module"`; do
            if test "$word" = 'longrunning-test'; then
              ofd=4
              break
            fi
          done
          { echo "## begin gnulib module $module"
            echo
            cat "$tmp"/amsnippet
            echo "## end   gnulib module $module"
            echo
          } >&$ofd
        fi
        rm -f "$tmp"/amsnippet
        # Test whether there are some source files in subdirectories.
        for f in `func_get_filelist "$module"`; do
          case $f in
            lib/*/*.c | tests/*/*.c)
              uses_subdirs=yes
              break
              ;;
          esac
        done
      fi
    done
  } 3> "$tmp"/main_snippets 4> "$tmp"/longrunning_snippets
  # Generate dependencies here, since it eases the debugging of test failures.
  # If there are source files in subdirectories, prevent collision of the
  # object files (example: hash.c and libxml/hash.c).
  subdir_options=
  if test -n "$uses_subdirs"; then
    subdir_options=' subdir-objects'
  fi
  echo "AUTOMAKE_OPTIONS = 1.5 foreign${subdir_options}"
  echo
  if $for_test && ! $single_configure; then
    echo "ACLOCAL_AMFLAGS = -I ${testsbase_inverse}/${m4base}"
    echo
  fi
  # Nothing is being added to SUBDIRS; nevertheless the existence of this
  # variable is needed to avoid an error from automake:
  #   "AM_GNU_GETTEXT used but SUBDIRS not defined"
  echo "SUBDIRS = ."
  echo "TESTS ="
  echo "XFAIL_TESTS ="
  echo "TESTS_ENVIRONMENT ="
  echo "noinst_PROGRAMS ="
  if ! $for_test; then
    echo "check_PROGRAMS ="
  fi
  echo "noinst_HEADERS ="
  echo "noinst_LIBRARIES ="
  if $use_libtests; then
    if $for_test; then
      echo "noinst_LIBRARIES += libtests.a"
    else
      echo "check_LIBRARIES = libtests.a"
    fi
  fi
  # Automake versions < 1.11.4 create an empty pkgdatadir at
  # installation time if you specify pkgdata_DATA to empty.
  # See automake bugs #10997 and #11030:
  #  * http://debbugs.gnu.org/10997
  #  * http://debbugs.gnu.org/11030
  # So we need this workaround.
  if grep '^pkgdata_DATA *+=' "$tmp"/main_snippets "$tmp"/longrunning_snippets > /dev/null; then
    echo "pkgdata_DATA ="
  fi
  echo "EXTRA_DIST ="
  echo "BUILT_SOURCES ="
  echo "SUFFIXES ="
  echo "MOSTLYCLEANFILES = core *.stackdump"
  echo "MOSTLYCLEANDIRS ="
  echo "CLEANFILES ="
  echo "DISTCLEANFILES ="
  echo "MAINTAINERCLEANFILES ="
  # Execute edits that apply to the Makefile.am being generated.
  edit=0
  while test $edit != $makefile_am_edits; do
    edit=`expr $edit + 1`
    eval dir=\"\$makefile_am_edit${edit}_dir\"
    eval var=\"\$makefile_am_edit${edit}_var\"
    eval val=\"\$makefile_am_edit${edit}_val\"
    if test -n "$var"; then
      if test "${dir}Makefile.am" = "$destfile" || test "./${dir}Makefile.am" = "$destfile"; then
        echo "${var} += ${val}"
        eval "makefile_am_edit${edit}_var="
      fi
    fi
  done
  echo
  echo "AM_CPPFLAGS = \\"
  if $for_test; then
    echo "  -DGNULIB_STRICT_CHECKING=1 \\"
  fi
  if test -n "$witness_c_macro"; then
    echo "  -D$witness_c_macro=1 \\"
  fi
  if test -n "${witness_macro}"; then
    echo "  -D@${witness_macro}@=1 \\"
  fi
  echo "  -I. -I\$(srcdir) \\"
  echo "  -I${testsbase_inverse} -I\$(srcdir)/${testsbase_inverse} \\"
  echo "  -I${testsbase_inverse}/${sourcebase-lib} -I\$(srcdir)/${testsbase_inverse}/${sourcebase-lib}"
  echo
  local_ldadd_before=''
  local_ldadd_after=''
  if $use_libtests; then
    # All test programs need to be linked with libtests.a.
    # It needs to be passed to the linker before ${libname}.${libext}, since
    # the tests-related modules depend on the main modules.
    # It also needs to be passed to the linker after ${libname}.${libext}
    # because the latter might contain incomplete modules (such as the 'error'
    # module whose dependency to 'progname' is voluntarily omitted).
    # The LIBTESTS_LIBDEPS can be passed to the linker once or twice, it does
    # not matter.
    local_ldadd_before=' libtests.a'
    local_ldadd_after=' libtests.a $(LIBTESTS_LIBDEPS)'
  fi
  echo "LDADD =${local_ldadd_before} ${testsbase_inverse}/${sourcebase-lib}/${libname}.${libext}${local_ldadd_after}"
  echo
  if $use_libtests; then
    echo "libtests_a_SOURCES ="
    # Here we use $(LIBOBJS), not @LIBOBJS@. The value is the same. However,
    # automake during its analysis looks for $(LIBOBJS), not for @LIBOBJS@.
    echo "libtests_a_LIBADD = \$(${macro_prefix}tests_LIBOBJS)"
    echo "libtests_a_DEPENDENCIES = \$(${macro_prefix}tests_LIBOBJS)"
    echo "EXTRA_libtests_a_SOURCES ="
    # The circular dependency in LDADD requires this.
    echo "AM_LIBTOOLFLAGS = --preserve-dup-deps"
    echo
  fi
  # Many test scripts use ${EXEEXT} or ${srcdir}.
  # EXEEXT is defined by AC_PROG_CC through autoconf.
  # srcdir is defined by autoconf and automake.
  echo "TESTS_ENVIRONMENT += EXEEXT='@EXEEXT@' srcdir='\$(srcdir)'"
  echo
  cat "$tmp"/main_snippets "$tmp"/longrunning_snippets \
    | sed -e 's|\$(top_srcdir)/build-aux/|$(top_srcdir)/'"$auxdir"'/|g'
  echo "# Clean up after Solaris cc."
  echo "clean-local:"
  echo "	rm -rf SunWS_cache"
  echo
  echo "mostlyclean-local: mostlyclean-generic"
  echo "	@for dir in '' \$(MOSTLYCLEANDIRS); do \\"
  echo "	  if test -n \"\$\$dir\" && test -d \$\$dir; then \\"
  echo "	    echo \"rmdir \$\$dir\"; rmdir \$\$dir; \\"
  echo "	  fi; \\"
  echo "	done; \\"
  echo "	:"
  rm -f "$tmp"/main_snippets "$tmp"/longrunning_snippets
}

# func_emit_initmacro_start macro_prefix
# emits the first few statements of the gl_INIT macro to standard output.
# - macro_prefix    prefix of gl_EARLY, gl_INIT macros to use
func_emit_initmacro_start ()
{
  macro_prefix_arg="$1"
  # Overriding AC_LIBOBJ and AC_REPLACE_FUNCS has the effect of storing
  # platform-dependent object files in ${macro_prefix_arg}_LIBOBJS instead of
  # LIBOBJS.  The purpose is to allow several gnulib instantiations under
  # a single configure.ac file.  (AC_CONFIG_LIBOBJ_DIR does not allow this
  # flexibility.)
  # Furthermore it avoids an automake error like this when a Makefile.am
  # that uses pieces of gnulib also uses $(LIBOBJ):
  #   automatically discovered file `error.c' should not be explicitly mentioned
  echo "  m4_pushdef([AC_LIBOBJ], m4_defn([${macro_prefix_arg}_LIBOBJ]))"
  echo "  m4_pushdef([AC_REPLACE_FUNCS], m4_defn([${macro_prefix_arg}_REPLACE_FUNCS]))"
  # Overriding AC_LIBSOURCES has the same purpose of avoiding the automake
  # error when a Makefile.am that uses pieces of gnulib also uses $(LIBOBJ):
  #   automatically discovered file `error.c' should not be explicitly mentioned
  # We let automake know about the files to be distributed through the
  # EXTRA_lib_SOURCES variable.
  echo "  m4_pushdef([AC_LIBSOURCES], m4_defn([${macro_prefix_arg}_LIBSOURCES]))"
  # Create data variables for checking the presence of files that are mentioned
  # as AC_LIBSOURCES arguments. These are m4 variables, not shell variables,
  # because we want the check to happen when the configure file is created,
  # not when it is run. ${macro_prefix_arg}_LIBSOURCES_LIST is the list of
  # files to check for. ${macro_prefix_arg}_LIBSOURCES_DIR is the subdirectory
  # in which to expect them.
  echo "  m4_pushdef([${macro_prefix_arg}_LIBSOURCES_LIST], [])"
  echo "  m4_pushdef([${macro_prefix_arg}_LIBSOURCES_DIR], [])"
  echo "  gl_COMMON"
}

# func_emit_initmacro_end macro_prefix
# emits the last few statements of the gl_INIT macro to standard output.
# - macro_prefix    prefix of gl_EARLY, gl_INIT macros to use
func_emit_initmacro_end ()
{
  macro_prefix_arg="$1"
  # Check the presence of files that are mentioned as AC_LIBSOURCES arguments.
  # The check is performed only when autoconf is run from the directory where
  # the configure.ac resides; if it is run from a different directory, the
  # check is skipped.
  echo "  m4_ifval(${macro_prefix_arg}_LIBSOURCES_LIST, ["
  echo "    m4_syscmd([test ! -d ]m4_defn([${macro_prefix_arg}_LIBSOURCES_DIR])[ ||"
  echo "      for gl_file in ]${macro_prefix_arg}_LIBSOURCES_LIST[ ; do"
  echo "        if test ! -r ]m4_defn([${macro_prefix_arg}_LIBSOURCES_DIR])[/\$gl_file ; then"
  echo "          echo \"missing file ]m4_defn([${macro_prefix_arg}_LIBSOURCES_DIR])[/\$gl_file\" >&2"
  echo "          exit 1"
  echo "        fi"
  echo "      done])dnl"
  echo "      m4_if(m4_sysval, [0], [],"
  echo "        [AC_FATAL([expected source file, required through AC_LIBSOURCES, not found])])"
  echo "  ])"
  echo "  m4_popdef([${macro_prefix_arg}_LIBSOURCES_DIR])"
  echo "  m4_popdef([${macro_prefix_arg}_LIBSOURCES_LIST])"
  echo "  m4_popdef([AC_LIBSOURCES])"
  echo "  m4_popdef([AC_REPLACE_FUNCS])"
  echo "  m4_popdef([AC_LIBOBJ])"
  echo "  AC_CONFIG_COMMANDS_PRE(["
  echo "    ${macro_prefix_arg}_libobjs="
  echo "    ${macro_prefix_arg}_ltlibobjs="
  echo "    if test -n \"\$${macro_prefix_arg}_LIBOBJS\"; then"
  echo "      # Remove the extension."
  echo "      sed_drop_objext='s/\\.o\$//;s/\\.obj\$//'"
  echo "      for i in \`for i in \$${macro_prefix_arg}_LIBOBJS; do echo \"\$i\"; done | sed -e \"\$sed_drop_objext\" | sort | uniq\`; do"
  echo "        ${macro_prefix_arg}_libobjs=\"\$${macro_prefix_arg}_libobjs \$i.\$ac_objext\""
  echo "        ${macro_prefix_arg}_ltlibobjs=\"\$${macro_prefix_arg}_ltlibobjs \$i.lo\""
  echo "      done"
  echo "    fi"
  echo "    AC_SUBST([${macro_prefix_arg}_LIBOBJS], [\$${macro_prefix_arg}_libobjs])"
  echo "    AC_SUBST([${macro_prefix_arg}_LTLIBOBJS], [\$${macro_prefix_arg}_ltlibobjs])"
  echo "  ])"
}

# func_emit_initmacro_done macro_prefix sourcebase
# emits a few statements after the gl_INIT macro to standard output.
# - macro_prefix    prefix of gl_EARLY, gl_INIT macros to use
# - sourcebase      directory relative to destdir where to place source code
func_emit_initmacro_done ()
{
  macro_prefix_arg="$1"
  sourcebase_arg="$2"
  echo
  echo "# Like AC_LIBOBJ, except that the module name goes"
  echo "# into ${macro_prefix_arg}_LIBOBJS instead of into LIBOBJS."
  echo "AC_DEFUN([${macro_prefix_arg}_LIBOBJ], ["
  echo "  AS_LITERAL_IF([\$1], [${macro_prefix_arg}_LIBSOURCES([\$1.c])])dnl"
  echo "  ${macro_prefix_arg}_LIBOBJS=\"\$${macro_prefix_arg}_LIBOBJS \$1.\$ac_objext\""
  echo "])"
  echo
  echo "# Like AC_REPLACE_FUNCS, except that the module name goes"
  echo "# into ${macro_prefix_arg}_LIBOBJS instead of into LIBOBJS."
  echo "AC_DEFUN([${macro_prefix_arg}_REPLACE_FUNCS], ["
  echo "  m4_foreach_w([gl_NAME], [\$1], [AC_LIBSOURCES(gl_NAME[.c])])dnl"
  echo "  AC_CHECK_FUNCS([\$1], , [${macro_prefix_arg}_LIBOBJ(\$ac_func)])"
  echo "])"
  echo
  echo "# Like AC_LIBSOURCES, except the directory where the source file is"
  echo "# expected is derived from the gnulib-tool parameterization,"
  echo "# and alloca is special cased (for the alloca-opt module)."
  echo "# We could also entirely rely on EXTRA_lib..._SOURCES."
  echo "AC_DEFUN([${macro_prefix_arg}_LIBSOURCES], ["
  echo "  m4_foreach([_gl_NAME], [\$1], ["
  echo "    m4_if(_gl_NAME, [alloca.c], [], ["
  echo "      m4_define([${macro_prefix_arg}_LIBSOURCES_DIR], [$sourcebase_arg])"
  echo "      m4_append([${macro_prefix_arg}_LIBSOURCES_LIST], _gl_NAME, [ ])"
  echo "    ])"
  echo "  ])"
  echo "])"
}

# func_emit_autoconf_snippet indentation
# emits the autoconf snippet of a module.
# Input:
# - local_gnulib_dir  from --local-dir
# - modcache          true or false, from --cache-modules/--no-cache-modules
# - sed_replace_build_aux  sed expression that replaces reference to build-aux
# - sed_replace_include_guard_prefix
#                     sed expression for resolving ${gl_include_guard_prefix}
# - module            the module name
# - toplevel          true or false. 'false' means a subordinate use of
#                     gnulib-tool.
# - disable_libtool   true or false. It tells whether to disable libtool
#                     handling even if it has been specified through the
#                     command line options.
# - disable_gettext   true or false. It tells whether to disable AM_GNU_GETTEXT
#                     invocations.
# - indentation       spaces to prepend on each line
func_emit_autoconf_snippet ()
{
  if { case $module in
         gnumakefile | maintainer-makefile)
           # These modules are meant to be used only in the top-level directory.
           $toplevel ;;
         *)
           true ;;
       esac
     }; then
    func_get_autoconf_snippet "$module" \
      | sed -e '/^$/d;' -e "s/^/$indentation/" \
            -e "$sed_replace_build_aux" \
            -e "$sed_replace_include_guard_prefix" \
      | { if $disable_libtool; then
            sed -e 's/\$gl_cond_libtool/false/g' \
                -e 's/gl_libdeps/gltests_libdeps/g' \
                -e 's/gl_ltlibdeps/gltests_ltlibdeps/g'
          else
            cat
          fi
        } \
      | { if $disable_gettext; then
            sed -e 's/AM_GNU_GETTEXT(\[external\])/dnl you must add AM_GNU_GETTEXT([external]) or similar to configure.ac./'
          else
            cat
          fi
        }
    if test "$module" = 'alloca' && test "$libtool" = true && ! $disable_libtool; then
      echo 'changequote(,)dnl'
      echo 'LTALLOCA=`echo "$ALLOCA" | sed -e '"'"'s/\.[^.]* /.lo /g;s/\.[^.]*$/.lo/'"'"'`'
      echo 'changequote([, ])dnl'
      echo 'AC_SUBST([LTALLOCA])'
    fi
  fi
}

# func_emit_autoconf_snippets modules verifier toplevel disable_libtool disable_gettext
# collects and emit the autoconf snippets of a set of modules.
# Input:
# - local_gnulib_dir  from --local-dir
# - modcache          true or false, from --cache-modules/--no-cache-modules
# - sed_replace_build_aux  sed expression that replaces reference to build-aux
# - sed_replace_include_guard_prefix
#                     sed expression for resolving ${gl_include_guard_prefix}
# - modules           the list of modules.
# - verifier          one of func_verify_module, func_verify_nontests_module,
#                     func_verify_tests_module. It selects the subset of
#                     $modules to consider.
# - toplevel          true or false. 'false' means a subordinate use of
#                     gnulib-tool.
# - disable_libtool   true or false. It tells whether to disable libtool
#                     handling even if it has been specified through the
#                     command line options.
# - disable_gettext   true or false. It tells whether to disable AM_GNU_GETTEXT
#                     invocations.
func_emit_autoconf_snippets ()
{
  verifier="$2"
  toplevel="$3"
  disable_libtool="$4"
  disable_gettext="$5"
  if test "$cond_dependencies" = true; then
    for m in $modules; do echo $m; done | LC_ALL=C sort -u > "$tmp"/modules
    # Emit the autoconf code for the unconditional modules.
    for module in $1; do
      eval $verifier
      if test -n "$module"; then
        if func_cond_module_p "$module"; then
          :
        else
          func_emit_autoconf_snippet "  "
        fi
      fi
    done
    # Initialize the shell variables indicating that the modules are enabled.
    for module in $1; do
      eval $verifier
      if test -n "$module"; then
        if func_cond_module_p "$module"; then
          func_module_shellvar_name "$module"
          echo "  $shellvar=false"
        fi
      fi
    done
    # Emit the autoconf code for the conditional modules, each in a separate
    # function. This makes it possible to support cycles among conditional
    # modules.
    for module in $1; do
      eval $verifier
      if test -n "$module"; then
        if func_cond_module_p "$module"; then
          func_module_shellfunc_name "$module"
          func_module_shellvar_name "$module"
          echo "  $shellfunc ()"
          echo '  {'
          echo "    if ! \$$shellvar; then"
          func_emit_autoconf_snippet "      "
          echo "      $shellvar=true"
          deps=`func_get_dependencies $module | sed -e "$sed_dependencies_without_conditions"`
          # Intersect $deps with the modules list $1.
          deps=`for m in $deps; do echo $m; done | LC_ALL=C sort -u | LC_ALL=C join - "$tmp"/modules`
          for dep in $deps; do
            if func_cond_module_p "$dep"; then
              func_module_shellfunc_name "$dep"
              func_cond_module_condition "$module" "$dep"
              if test "$condition" != true; then
                echo "      if $condition; then"
                echo "        $shellfunc"
                echo '      fi'
              else
                echo "      $shellfunc"
              fi
            else
              # The autoconf code for $dep has already been emitted above and
              # therefore is already executed when this function is run.
              :
            fi
          done
          echo '    fi'
          echo '  }'
        fi
      fi
    done
    # Emit the dependencies from the unconditional to the conditional modules.
    for module in $1; do
      eval $verifier
      if test -n "$module"; then
        if func_cond_module_p "$module"; then
          :
        else
          deps=`func_get_dependencies $module | sed -e "$sed_dependencies_without_conditions"`
          # Intersect $deps with the modules list $1.
          deps=`for m in $deps; do echo $m; done | LC_ALL=C sort -u | LC_ALL=C join - "$tmp"/modules`
          for dep in $deps; do
            if func_cond_module_p "$dep"; then
              func_module_shellfunc_name "$dep"
              func_cond_module_condition "$module" "$dep"
              if test "$condition" != true; then
                echo "  if $condition; then"
                echo "    $shellfunc"
                echo '  fi'
              else
                echo "  $shellfunc"
              fi
            else
              # The autoconf code for $dep has already been emitted above and
              # therefore is already executed when this code is run.
              :
            fi
          done
        fi
      fi
    done
    # Define the Automake conditionals.
    echo "  m4_pattern_allow([^${macro_prefix}_GNULIB_ENABLED_])"
    for module in $1; do
      eval $verifier
      if test -n "$module"; then
        if func_cond_module_p "$module"; then
          func_module_conditional_name "$module"
          func_module_shellvar_name "$module"
          echo "  AM_CONDITIONAL([$conditional], [\$$shellvar])"
        fi
      fi
    done
  else
    # Ignore the conditions, and enable all modules unconditionally.
    for module in $1; do
      eval $verifier
      if test -n "$module"; then
        func_emit_autoconf_snippet "  "
      fi
    done
  fi
}

# func_import modules
# Uses also the variables
# - mode            import or add-import or remove-import or update
# - destdir         target directory
# - local_gnulib_dir  from --local-dir
# - modcache        true or false, from --cache-modules/--no-cache-modules
# - verbose         integer, default 0, inc/decremented by --verbose/--quiet
# - libname         library name
# - supplied_libname  true if --lib was given, blank otherwise
# - sourcebase      directory relative to destdir where to place source code
# - m4base          directory relative to destdir where to place *.m4 macros
# - pobase          directory relative to destdir where to place *.po files
# - docbase         directory relative to destdir where to place doc files
# - testsbase       directory relative to destdir where to place unit test code
# - auxdir          directory relative to destdir where to place build aux files
# - inctests        true if --with-tests was given, blank otherwise
# - incobsolete     true if --with-obsolete was given, blank otherwise
# - inc_cxx_tests   true if --with-c++-tests was given, blank otherwise
# - inc_longrunning_tests  true if --with-longrunning-tests was given, blank
#                          otherwise
# - inc_privileged_tests  true if --with-privileged-tests was given, blank
#                         otherwise
# - inc_unportable_tests  true if --with-unportable-tests was given, blank
#                         otherwise
# - inc_all_tests   true if --with-all-tests was given, blank otherwise
# - avoidlist       list of modules to avoid, from --avoid
# - cond_dependencies  true if --conditional-dependencies was given, false if
#                      --no-conditional-dependencies was given, blank otherwise
# - lgpl            yes or a number if library's license shall be LGPL,
#                   blank otherwise
# - makefile_name   from --makefile-name
# - libtool         true if --libtool was given, false if --no-libtool was
#                   given, blank otherwise
# - guessed_libtool true if the configure.ac file uses libtool, false otherwise
# - macro_prefix    prefix of gl_EARLY, gl_INIT macros to use
# - po_domain       prefix of i18n domain to use (without -gnulib suffix)
# - witness_c_macro  from --witness-c-macro
# - vc_files        true if --vc-files was given, false if --no-vc-files was
#                   given, blank otherwise
# - autoconf_minversion  minimum supported autoconf version
# - doit            : if actions shall be executed, false if only to be printed
# - symbolic        true if files should be symlinked, copied otherwise
# - lsymbolic       true if files from local_gnulib_dir should be symlinked,
#                   copied otherwise
# - do_copyrights   true if copyright notices in files should be replaced,
#                   blank otherwise
func_import ()
{
  # Get the cached settings.
  # In 'import' mode, we read them only for the purpose of knowing the old
  # installed file list, and don't use them as defaults.
  cached_local_gnulib_dir=
  cached_specified_modules=
  cached_incobsolete=
  cached_inc_cxx_tests=
  cached_inc_longrunning_tests=
  cached_inc_privileged_tests=
  cached_inc_unportable_tests=
  cached_inc_all_tests=
  cached_avoidlist=
  cached_sourcebase=
  cached_m4base=
  cached_pobase=
  cached_docbase=
  cached_testsbase=
  cached_inctests=
  cached_libname=
  cached_lgpl=
  cached_makefile_name=
  cached_cond_dependencies=
  cached_libtool=
  cached_macro_prefix=
  cached_po_domain=
  cached_witness_c_macro=
  cached_vc_files=
  cached_files=
  if test -f "$destdir"/$m4base/gnulib-cache.m4; then
    cached_libtool=false
    my_sed_traces='
      s,#.*$,,
      s,^dnl .*$,,
      s, dnl .*$,,
      /gl_LOCAL_DIR(/ {
        s,^.*gl_LOCAL_DIR([[ ]*\([^]"$`\\)]*\).*$,cached_local_gnulib_dir="\1",p
      }
      /gl_MODULES(/ {
        ta
        :a
          s/)/)/
          tb
          N
          ba
        :b
        s,^.*gl_MODULES([[ ]*\([^]"$`\\)]*\).*$,cached_specified_modules="\1",p
      }
      /gl_WITH_OBSOLETE/ {
        s,^.*$,cached_incobsolete=true,p
      }
      /gl_WITH_CXX_TESTS/ {
        s,^.*$,cached_inc_cxx_tests=true,p
      }
      /gl_WITH_LONGRUNNING_TESTS/ {
        s,^.*$,cached_inc_longrunning_tests=true,p
      }
      /gl_WITH_PRIVILEGED_TESTS/ {
        s,^.*$,cached_inc_privileged_tests=true,p
      }
      /gl_WITH_UNPORTABLE_TESTS/ {
        s,^.*$,cached_inc_unportable_tests=true,p
      }
      /gl_WITH_ALL_TESTS/ {
        s,^.*$,cached_inc_all_tests=true,p
      }
      /gl_AVOID(/ {
        s,^.*gl_AVOID([[ ]*\([^]"$`\\)]*\).*$,cached_avoidlist="\1",p
      }
      /gl_SOURCE_BASE(/ {
        s,^.*gl_SOURCE_BASE([[ ]*\([^]"$`\\)]*\).*$,cached_sourcebase="\1",p
      }
      /gl_M4_BASE(/ {
        s,^.*gl_M4_BASE([[ ]*\([^]"$`\\)]*\).*$,cached_m4base="\1",p
      }
      /gl_PO_BASE(/ {
        s,^.*gl_PO_BASE([[ ]*\([^]"$`\\)]*\).*$,cached_pobase="\1",p
      }
      /gl_DOC_BASE(/ {
        s,^.*gl_DOC_BASE([[ ]*\([^]"$`\\)]*\).*$,cached_docbase="\1",p
      }
      /gl_TESTS_BASE(/ {
        s,^.*gl_TESTS_BASE([[ ]*\([^]"$`\\)]*\).*$,cached_testsbase="\1",p
      }
      /gl_WITH_TESTS/ {
        s,^.*$,cached_inctests=true,p
      }
      /gl_LIB(/ {
        s,^.*gl_LIB([[ ]*\([^]"$`\\)]*\).*$,cached_libname="\1",p
      }
      /gl_LGPL(/ {
        s,^.*gl_LGPL([[ ]*\([^]"$`\\)]*\).*$,cached_lgpl="\1",p
      }
      /gl_LGPL/ {
        s,^.*$,cached_lgpl=yes,p
      }
      /gl_MAKEFILE_NAME(/ {
        s,^.*gl_MAKEFILE_NAME([[ ]*\([^]"$`\\)]*\).*$,cached_makefile_name="\1",p
      }
      /gl_CONDITIONAL_DEPENDENCIES/ {
        s,^.*$,cached_cond_dependencies=true,p
      }
      /gl_LIBTOOL/ {
        s,^.*$,cached_libtool=true,p
      }
      /gl_MACRO_PREFIX(/ {
        s,^.*gl_MACRO_PREFIX([[ ]*\([^]"$`\\)]*\).*$,cached_macro_prefix="\1",p
      }
      /gl_PO_DOMAIN(/ {
        s,^.*gl_PO_DOMAIN([[ ]*\([^]"$`\\)]*\).*$,cached_po_domain="\1",p
      }
      /gl_WITNESS_C_MACRO(/ {
        s,^.*gl_WITNESS_C_MACRO([[ ]*\([^]"$`\\)]*\).*$,cached_witness_c_macro="\1",p
      }
      /gl_VC_FILES(/ {
        s,^.*gl_VC_FILES([[ ]*\([^]"$`\\)]*\).*$,cached_vc_files="\1",p
      }'
    eval `sed -n -e "$my_sed_traces" < "$destdir"/$m4base/gnulib-cache.m4`
    if test -f "$destdir"/$m4base/gnulib-comp.m4; then
      my_sed_traces='
        s,#.*$,,
        s,^dnl .*$,,
        s, dnl .*$,,
        /AC_DEFUN(\['"${cached_macro_prefix}"'_FILE_LIST\], \[/ {
          s,^.*$,cached_files=",p
          n
          ta
          :a
          s,^\]).*$,",
          tb
          s,["$`\\],,g
          p
          n
          ba
          :b
          p
        }'
      eval `sed -n -e "$my_sed_traces" < "$destdir"/$m4base/gnulib-comp.m4`
    fi
  fi

  if test "$mode" = import; then
    # In 'import' mode, the new set of specified modules overrides the cached
    # set of modules. Ignore the cached settings.
    specified_modules="$1"
  else
    # Merge the cached settings with the specified ones.
    # The m4base must be the same as expected from the pathname.
    if test -n "$cached_m4base" && test "$cached_m4base" != "$m4base"; then
      func_fatal_error "$m4base/gnulib-cache.m4 is expected to contain gl_M4_BASE([$m4base])"
    fi
    # The local_gnulib_dir defaults to the cached one. Recall that the cached one
    # is relative to $destdir, whereas the one we use is relative to . or absolute.
    if test -z "$local_gnulib_dir"; then
      if test -n "$cached_local_gnulib_dir"; then
        case "$destdir" in
          /*)
            local_gnulib_dir="$destdir/$cached_local_gnulib_dir" ;;
          *)
            case "$cached_local_gnulib_dir" in
              /*)
                local_gnulib_dir="$destdir/$cached_local_gnulib_dir" ;;
              *)
                func_relconcat "$destdir" "$cached_local_gnulib_dir"
                local_gnulib_dir="$relconcat" ;;
            esac ;;
        esac
      fi
    fi
    case $mode in
      add-import)
        # Append the cached and the specified module names. So that
        # "gnulib-tool --add-import foo" means to add the module foo.
        specified_modules="$cached_specified_modules $1"
        ;;
      remove-import)
        # Take the cached module names, minus the specified module names.
        specified_modules=
        if $have_associative; then
          # Use an associative array, for O(N) worst-case run time.
          declare -A to_remove
          for m in $1; do
            eval 'to_remove[$m]=yes'
          done
          for module in $cached_specified_modules; do
            if eval 'test -z "${to_remove[$module]}"'; then
              func_append specified_modules "$module "
            fi
          done
        else
          # This loop has O(N²) worst-case run time.
          for module in $cached_specified_modules; do
            to_remove=
            for m in $1; do
              if test "$m" = "$module"; then
                to_remove=yes
                break
              fi
            done
            if test -z "$to_remove"; then
              func_append specified_modules "$module "
            fi
          done
        fi
        ;;
      update)
        # Take the cached module names. There are no specified module names.
        specified_modules="$cached_specified_modules"
        ;;
    esac
    # Included obsolete modules among the dependencies if specified either way.
    if test -z "$incobsolete"; then
      incobsolete="$cached_incobsolete"
    fi
    # Included special kinds of tests modules among the dependencies if specified
    # either way.
    if test -z "$inc_cxx_tests"; then
      inc_cxx_tests="$cached_inc_cxx_tests"
    fi
    if test -z "$inc_longrunning_tests"; then
      inc_longrunning_tests="$cached_inc_longrunning_tests"
    fi
    if test -z "$inc_privileged_tests"; then
      inc_privileged_tests="$cached_inc_privileged_tests"
    fi
    if test -z "$inc_unportable_tests"; then
      inc_unportable_tests="$cached_inc_unportable_tests"
    fi
    if test -z "$inc_all_tests"; then
      inc_all_tests="$cached_inc_all_tests"
    fi
    # Append the cached and the specified avoidlist. This is probably better
    # than dropping the cached one when --avoid is specified at least once.
    avoidlist=`for m in $cached_avoidlist $avoidlist; do echo $m; done | LC_ALL=C sort -u`
    avoidlist=`echo $avoidlist`

    # The sourcebase defaults to the cached one.
    if test -z "$sourcebase"; then
      sourcebase="$cached_sourcebase"
      if test -z "$sourcebase"; then
        func_fatal_error "missing --source-base option"
      fi
    fi
    # The pobase defaults to the cached one.
    if test -z "$pobase"; then
      pobase="$cached_pobase"
    fi
    # The docbase defaults to the cached one.
    if test -z "$docbase"; then
      docbase="$cached_docbase"
      if test -z "$docbase"; then
        func_fatal_error "missing --doc-base option. --doc-base has been introduced on 2006-07-11; if your last invocation of 'gnulib-tool --import' is before that date, you need to run 'gnulib-tool --import' once, with a --doc-base option."
      fi
    fi
    # The testsbase defaults to the cached one.
    if test -z "$testsbase"; then
      testsbase="$cached_testsbase"
      if test -z "$testsbase"; then
        func_fatal_error "missing --tests-base option"
      fi
    fi
    # Require the tests if specified either way.
    if test -z "$inctests"; then
      inctests="$cached_inctests"
    fi
    # The libname defaults to the cached one.
    if test -z "$supplied_libname"; then
      libname="$cached_libname"
      if test -z "$libname"; then
        func_fatal_error "missing --lib option"
      fi
    fi
    # Require LGPL if specified either way.
    if test -z "$lgpl"; then
      lgpl="$cached_lgpl"
    fi
    # The makefile_name defaults to the cached one.
    if test -z "$makefile_name"; then
      makefile_name="$cached_makefile_name"
    fi
    # Use conditional dependencies if specified either way.
    if test -z "$cond_dependencies"; then
      cond_dependencies="$cached_cond_dependencies"
    fi
    # Use libtool if specified either way, or if guessed.
    if test -z "$libtool"; then
      if test -n "$cached_m4base"; then
        libtool="$cached_libtool"
      else
        libtool="$guessed_libtool"
      fi
    fi
    # The macro_prefix defaults to the cached one.
    if test -z "$macro_prefix"; then
      macro_prefix="$cached_macro_prefix"
      if test -z "$macro_prefix"; then
        func_fatal_error "missing --macro-prefix option"
      fi
    fi
    # The po_domain defaults to the cached one.
    if test -z "$po_domain"; then
      po_domain="$cached_po_domain"
    fi
    # The witness_c_macro defaults to the cached one.
    if test -z "$witness_c_macro"; then
      witness_c_macro="$cached_witness_c_macro"
    fi
    # The vc_files defaults to the cached one.
    if test -z "$vc_files"; then
      vc_files="$cached_vc_files"
    fi
    # Ensure constraints.
    if test "$cond_dependencies" = true && test -n "$inctests"; then
      echo "gnulib-tool: option --conditional-dependencies is not supported with --with-tests" 1>&2
      func_exit 1
    fi
  fi
  # --without-*-tests options are not supported here.
  excl_cxx_tests=
  excl_longrunning_tests=
  excl_privileged_tests=
  excl_unportable_tests=

  # Canonicalize the list of specified modules.
  specified_modules=`for m in $specified_modules; do echo $m; done | LC_ALL=C sort -u`

  # Include all kinds of tests modules if --with-all-tests was specified.
  inc_all_direct_tests="$inc_all_tests"
  inc_all_indirect_tests="$inc_all_tests"

  # Determine final module list.
  modules="$specified_modules"
  func_modules_transitive_closure
  if test $verbose -ge 0; then
    func_show_module_list
  fi
  final_modules="$modules"

  # Determine main module list and tests-related module list separately.
  func_modules_transitive_closure_separately

  # Determine whether a $testsbase/libtests.a is needed.
  func_determine_use_libtests

  # Add the dummy module to the main module list or to the tests-related module
  # list if needed.
  func_modules_add_dummy_separately

  # If --lgpl, verify that the licenses of modules are compatible.
  if test -n "$lgpl"; then
    license_incompatibilities=
    for module in $main_modules; do
      license=`func_get_license $module`
      case $license in
        'GPLed build tool') ;;
        'public domain' | 'unlimited' | 'unmodifiable license text') ;;
        *)
          case "$lgpl" in
            yes | 3)
              case $license in
                LGPL | LGPLv2+ | LGPLv3+) ;;
                *) func_append license_incompatibilities "$module $license$nl" ;;
              esac
              ;;
            2)
              case $license in
                LGPLv2+) ;;
                *) func_append license_incompatibilities "$module $license$nl" ;;
              esac
              ;;
            *) func_fatal_error "invalid value lgpl=$lgpl" ;;
          esac
          ;;
      esac
    done
    if test -n "$license_incompatibilities"; then
      # Format the license incompatibilities as a table.
      sed_expand_column1_width50_indent17='s,^\([^ ]*\) ,\1                                                   ,
s,^\(.................................................[^ ]*\) *,                 \1 ,'
      license_incompatibilities=`echo "$license_incompatibilities" | sed -e "$sed_expand_column1_width50_indent17"`
      func_fatal_error "incompatible license on modules:$nl$license_incompatibilities"
    fi
  fi

  # Show banner notice of every module.
  modules="$main_modules"
  func_modules_notice

  # Determine script to apply to imported library files.
  sed_transform_lib_file=
  for module in $main_modules; do
    if test $module = config-h; then
      # Assume config.h exists, and that -DHAVE_CONFIG_H is omitted.
      sed_transform_lib_file=$sed_transform_lib_file'
        s/^#ifdef[	 ]*HAVE_CONFIG_H[	 ]*$/#if 1/
      '
      break
    fi
  done
  sed_transform_main_lib_file="$sed_transform_lib_file"
  if test -n "$do_copyrights"; then
    if test -n "$lgpl"; then
      # Update license.
      case "$lgpl" in
        yes | 3)
          sed_transform_main_lib_file=$sed_transform_main_lib_file'
            s/GNU General/GNU Lesser General/g
            s/General Public License/Lesser General Public License/g
            s/Lesser Lesser General Public License/Lesser General Public License/g
          '
          ;;
        2)
          sed_transform_main_lib_file=$sed_transform_main_lib_file'
            s/GNU General/GNU Lesser General/g
            s/General Public License/Lesser General Public License/g
            s/Lesser Lesser General Public License/Lesser General Public License/g

            s/version [23]\([ ,]\)/version 2.1\1/g
          '
          ;;
        *) func_fatal_error "invalid value lgpl=$lgpl" ;;
      esac
    else
      # Update license.
      sed_transform_main_lib_file=$sed_transform_main_lib_file'
        s/GNU Lesser General/GNU General/g
        s/Lesser General Public License/General Public License/g

        s/GNU Library General/GNU General/g
        s/Library General Public License/General Public License/g

        s/version 2\(.1\)\{0,1\}\([ ,]\)/version 3\2/g
      '
    fi
  fi

  # Determine script to apply to auxiliary files that go into $auxdir/.
  sed_transform_build_aux_file=
  if test -n "$do_copyrights"; then
    # Update license.
    sed_transform_build_aux_file=$sed_transform_build_aux_file'
      s/GNU Lesser General/GNU General/g
      s/Lesser General Public License/General Public License/g

      s/GNU Library General/GNU General/g
      s/Library General Public License/General Public License/g

      s/version 2\(.1\)\{0,1\}\([ ,]\)/version 3\2/g
    '
  fi

  # Determine script to apply to library files that go into $testsbase/.
  sed_transform_testsrelated_lib_file="$sed_transform_lib_file"
  if test -n "$do_copyrights"; then
    # Update license.
    sed_transform_testsrelated_lib_file=$sed_transform_testsrelated_lib_file'
      s/GNU Lesser General/GNU General/g
      s/Lesser General Public License/General Public License/g

      s/GNU Library General/GNU General/g
      s/Library General Public License/General Public License/g

      s/version 2\(.1\)\{0,1\}\([ ,]\)/version 3\2/g
    '
  fi

  # Determine the final file lists.
  func_modules_to_filelist_separately

  test -n "$files" \
    || func_fatal_error "refusing to do nothing"

  # Add m4/gnulib-tool.m4 to the file list. It is not part of any module.
  new_files="$files m4/gnulib-tool.m4"
  old_files="$cached_files"
  if test -f "$destdir"/$m4base/gnulib-tool.m4; then
    func_append old_files " m4/gnulib-tool.m4"
  fi

echo $docbase

  rewritten='%REWRITTEN%'
  sed_rewrite_old_files="\
    s,^build-aux/,$rewritten$auxdir/,
    s,^doc/,$rewritten$cached_docbase/,
    s,^lib/,$rewritten$cached_sourcebase/,
    s,^m4/,$rewritten$cached_m4base/,
    s,^tests/,$rewritten$cached_testsbase/,
    s,^tests=lib/,$rewritten$cached_testsbase/,
    s,^top/,$rewritten,
    s,^$rewritten,,"
  sed_rewrite_new_files="\
    s,^build-aux/,$rewritten$auxdir/,
    s,^doc/,$rewritten$docbase/,
    s,^lib/,$rewritten$sourcebase/,
    s,^m4/,$rewritten$m4base/,
    s,^tests/,$rewritten$testsbase/,
    s,^tests=lib/,$rewritten$testsbase/,
    s,^top/,$rewritten,
    s,^$rewritten,,"

  # Create directories.
  { echo "$sourcebase"
    echo "$m4base"
    if test -n "$pobase"; then
      echo "$pobase"
    fi
    docfiles=`echo "$files" | sed -n -e 's,^doc/,,p'`
    if test -n "$docfiles"; then
      echo "$docbase"
    fi
    if test -n "$inctests"; then
      echo "$testsbase"
    fi
    echo "$auxdir"
    for f in $files; do echo $f; done \
      | sed -e "$sed_rewrite_new_files" \
      | sed -n -e 's,^\(.*\)/[^/]*,\1,p' \
      | LC_ALL=C sort -u
  } > "$tmp"/dirs
  { # Rearrange file descriptors. Needed because "while ... done < ..."
    # constructs are executed in a subshell e.g. by Solaris 10 /bin/sh.
    exec 5<&0 < "$tmp"/dirs
    while read d; do
      if test ! -d "$destdir/$d"; then
        if $doit; then
          echo "Creating directory $destdir/$d"
          mkdir -p "$destdir/$d" || func_fatal_error "failed"
        else
          echo "Create directory $destdir/$d"
        fi
      fi
    done
    exec 0<&5 5<&-
  }

  # Copy files or make symbolic links. Remove obsolete files.
  added_files=''
  removed_files=''
  delimiter='	'
  # Construct a table with 2 columns: rewritten-file-name original-file-name,
  # representing the files according to the last gnulib-tool invocation.
  for f in $old_files; do echo $f; done \
    | sed -e "s,^.*\$,&$delimiter&," -e "$sed_rewrite_old_files" \
    | LC_ALL=C sort \
    > "$tmp"/old-files
  # Construct a table with 2 columns: rewritten-file-name original-file-name,
  # representing the files after this gnulib-tool invocation.
  for f in $new_files; do echo $f; done \
    | sed -e "s,^.*\$,&$delimiter&," -e "$sed_rewrite_new_files" \
    | LC_ALL=C sort \
    > "$tmp"/new-files
  # First the files that are in old-files, but not in new-files:
  sed_take_first_column='s,'"$delimiter"'.*,,'
  for g in `LC_ALL=C join -t"$delimiter" -v1 "$tmp"/old-files "$tmp"/new-files | sed -e "$sed_take_first_column"`; do
    # Remove the file. Do nothing if the user already removed it.
    if test -f "$destdir/$g" || test -h "$destdir/$g"; then
      if $doit; then
        echo "Removing file $g (backup in ${g}~)"
        mv -f "$destdir/$g" "$destdir/${g}~" || func_fatal_error "failed"
      else
        echo "Remove file $g (backup in ${g}~)"
      fi
      func_append removed_files "$g$nl"
    fi
  done
  # func_add_or_update handles a file that ought to be present afterwards.
  # Uses parameters
  # - f             the original file name
  # - g             the rewritten file name
  # - already_present  nonempty if the file should already exist, empty
  #                    otherwise
  func_add_or_update ()
  {
    of="$f"
    case "$f" in
      tests=lib/*) f=`echo "$f" | sed -e 's,^tests=lib/,lib/,'` ;;
    esac
    func_dest_tmpfilename "$g"
    func_lookup_file "$f"
    cp "$lookedup_file" "$tmpfile" || func_fatal_error "failed"
    if test -n "$sed_transform_main_lib_file"; then
      case "$of" in
        lib/*)
          sed -e "$sed_transform_main_lib_file" \
            < "$lookedup_file" > "$tmpfile" || func_fatal_error "failed"
          ;;
      esac
    fi
    if test -n "$sed_transform_build_aux_file"; then
      case "$of" in
        build-aux/*)
          sed -e "$sed_transform_build_aux_file" \
            < "$lookedup_file" > "$tmpfile" || func_fatal_error "failed"
          ;;
      esac
    fi
    if test -n "$sed_transform_testsrelated_lib_file"; then
      case "$of" in
        tests=lib/*)
          sed -e "$sed_transform_testsrelated_lib_file" \
            < "$lookedup_file" > "$tmpfile" || func_fatal_error "failed"
          ;;
      esac
    fi
    if test -f "$destdir/$g"; then
      # The file already exists.
      func_update_file
    else
      # Install the file.
      # Don't protest if the file should be there but isn't: it happens
      # frequently that developers don't put autogenerated files under version control.
      func_add_file
      func_append added_files "$g$nl"
    fi
    rm -f "$tmpfile"
  }
  # Then the files that are in new-files, but not in old-files:
  sed_take_last_column='s,^.*'"$delimiter"',,'
  already_present=
  LC_ALL=C join -t"$delimiter" -v2 "$tmp"/old-files "$tmp"/new-files \
    | sed -e "$sed_take_last_column" \
    | sed -e "s,^.*\$,&$delimiter&," -e "$sed_rewrite_new_files" > "$tmp"/added-files
  { # Rearrange file descriptors. Needed because "while ... done < ..."
    # constructs are executed in a subshell e.g. by Solaris 10 /bin/sh.
    exec 5<&0 < "$tmp"/added-files
    while read g f; do
      func_add_or_update
    done
    exec 0<&5 5<&-
  }
  # Then the files that are in new-files and in old-files:
  already_present=true
  LC_ALL=C join -t"$delimiter" "$tmp"/old-files "$tmp"/new-files \
    | sed -e "$sed_take_last_column" \
    | sed -e "s,^.*\$,&$delimiter&," -e "$sed_rewrite_new_files" > "$tmp"/kept-files
  { # Rearrange file descriptors. Needed because "while ... done < ..."
    # constructs are executed in a subshell e.g. by Solaris 10 /bin/sh.
    exec 5<&0 < "$tmp"/kept-files
    while read g f; do
      func_add_or_update
    done
    exec 0<&5 5<&-
  }

  # Command-line invocation printed in a comment in generated gnulib-cache.m4.
  actioncmd="gnulib-tool --import"
  func_append actioncmd " --dir=$destdir"
  if test -n "$local_gnulib_dir"; then
    func_append actioncmd " --local-dir=$local_gnulib_dir"
  fi
  func_append actioncmd " --lib=$libname"
  func_append actioncmd " --source-base=$sourcebase"
  func_append actioncmd " --m4-base=$m4base"
  if test -n "$pobase"; then
    func_append actioncmd " --po-base=$pobase"
  fi
  func_append actioncmd " --doc-base=$docbase"
  func_append actioncmd " --tests-base=$testsbase"
  func_append actioncmd " --aux-dir=$auxdir"
  if test -n "$inctests"; then
    func_append actioncmd " --with-tests"
  fi
  if test -n "$incobsolete"; then
    func_append actioncmd " --with-obsolete"
  fi
  if test -n "$inc_cxx_tests"; then
    func_append actioncmd " --with-c++-tests"
  fi
  if test -n "$inc_longrunning_tests"; then
    func_append actioncmd " --with-longrunning-tests"
  fi
  if test -n "$inc_privileged_tests"; then
    func_append actioncmd " --with-privileged-tests"
  fi
  if test -n "$inc_unportable_tests"; then
    func_append actioncmd " --with-unportable-tests"
  fi
  if test -n "$inc_all_tests"; then
    func_append actioncmd " --with-all-tests"
  fi
  for module in $avoidlist; do
    func_append actioncmd " --avoid=$module"
  done
  if test -n "$lgpl"; then
    if test "$lgpl" = yes; then
      func_append actioncmd " --lgpl"
    else
      func_append actioncmd " --lgpl=$lgpl"
    fi
  fi
  if test -n "$makefile_name"; then
    func_append actioncmd " --makefile-name=$makefile_name"
  fi
  if test "$cond_dependencies" = true; then
    func_append actioncmd " --conditional-dependencies"
  else
    func_append actioncmd " --no-conditional-dependencies"
  fi
  if test "$libtool" = true; then
    func_append actioncmd " --libtool"
  else
    func_append actioncmd " --no-libtool"
  fi
  func_append actioncmd " --macro-prefix=$macro_prefix"
  if test -n "$po_domain"; then
    func_append actioncmd " --po-domain=$po_domain"
  fi
  if test -n "$witness_c_macro"; then
    func_append actioncmd " --witness-c-macro=$witness_c_macro"
  fi
  if test -n "$vc_files"; then
    if test "$vc_files" = true; then
      func_append actioncmd " --vc-files"
    else
      func_append actioncmd " --no-vc-files"
    fi
  fi
  func_append actioncmd " `echo $specified_modules`"

  # Determine include_guard_prefix.
  func_compute_include_guard_prefix

  # Default the makefile name to Makefile.am.
  if test -n "$makefile_name"; then
    makefile_am=$makefile_name
  else
    makefile_am=Makefile.am
  fi

  # Create normal Makefile.ams.
  for_test=false

  # Setup list of Makefile.am edits that are to be performed afterwards.
  # Some of these edits apply to files that we will generate; others are
  # under the responsibility of the developer.
  makefile_am_edits=0
  # func_note_Makefile_am_edit dir var value
  # remembers that ${dir}Makefile.am needs to be edited to that ${var} mentions
  # ${value}.
  func_note_Makefile_am_edit ()
  {
    makefile_am_edits=`expr $makefile_am_edits + 1`
    eval makefile_am_edit${makefile_am_edits}_dir=\"\$1\"
    eval makefile_am_edit${makefile_am_edits}_var=\"\$2\"
    eval makefile_am_edit${makefile_am_edits}_val=\"\$3\"
  }
  if test "$makefile_am" = Makefile.am; then
    sourcebase_dir=`echo "$sourcebase" | sed -n -e 's,/[^/]*$,/,p'`
    sourcebase_base=`basename "$sourcebase"`
    func_note_Makefile_am_edit "$sourcebase_dir" SUBDIRS "$sourcebase_base"
  fi
  if test -n "$pobase"; then
    pobase_dir=`echo "$pobase" | sed -n -e 's,/[^/]*$,/,p'`
    pobase_base=`basename "$pobase"`
    func_note_Makefile_am_edit "$pobase_dir" SUBDIRS "$pobase_base"
  fi
  if test -n "$inctests"; then
    if test "$makefile_am" = Makefile.am; then
      testsbase_dir=`echo "$testsbase" | sed -n -e 's,/[^/]*$,/,p'`
      testsbase_base=`basename "$testsbase"`
      func_note_Makefile_am_edit "$testsbase_dir" SUBDIRS "$testsbase_base"
    fi
  fi
  func_note_Makefile_am_edit "" ACLOCAL_AMFLAGS "-I ${m4base}"
  {
    # Find the first parent directory of $m4base that contains or will contain
    # a Makefile.am.
    sed_last='s,^.*/\([^/][^/]*\)//*$,\1/,
s,//*$,/,'
    sed_butlast='s,[^/][^/]*//*$,,'
    dir1="${m4base}/"; dir2=""
    while test -n "$dir1" \
          && ! { test -f "${destdir}/${dir1}Makefile.am" \
                 || test "${dir1}Makefile.am" = "$sourcebase/$makefile_am" \
                 || test "./${dir1}Makefile.am" = "$sourcebase/$makefile_am" \
                 || { test -n "$inctests" \
                      && { test "${dir1}Makefile.am" = "$testsbase/$makefile_am" \
                           || test "./${dir1}Makefile.am" = "$testsbase/$makefile_am"; }; }; }; do
      dir2=`echo "$dir1" | sed -e "$sed_last"`"$dir2"
      dir1=`echo "$dir1" | sed -e "$sed_butlast"`
    done
    func_note_Makefile_am_edit "$dir1" EXTRA_DIST "${dir2}gnulib-cache.m4"
  }

  # Create library makefile.
  func_dest_tmpfilename $sourcebase/$makefile_am
  destfile="$sourcebase/$makefile_am"
  modules="$main_modules"
  func_emit_lib_Makefile_am > "$tmpfile"
  if test -f "$destdir"/$sourcebase/$makefile_am; then
    if cmp -s "$destdir"/$sourcebase/$makefile_am "$tmpfile"; then
      rm -f "$tmpfile"
    else
      if $doit; then
        echo "Updating $sourcebase/$makefile_am (backup in $sourcebase/$makefile_am~)"
        mv -f "$destdir"/$sourcebase/$makefile_am "$destdir"/$sourcebase/$makefile_am~
        mv -f "$tmpfile" "$destdir"/$sourcebase/$makefile_am
      else
        echo "Update $sourcebase/$makefile_am (backup in $sourcebase/$makefile_am~)"
        rm -f "$tmpfile"
      fi
    fi
  else
    if $doit; then
      echo "Creating $sourcebase/$makefile_am"
      mv -f "$tmpfile" "$destdir"/$sourcebase/$makefile_am
    else
      echo "Create $sourcebase/$makefile_am"
      rm -f "$tmpfile"
    fi
    func_append added_files "$sourcebase/$makefile_am$nl"
  fi

  # Create po/ directory.
  if test -n "$pobase"; then
    # Create po makefile and auxiliary files.
    for file in Makefile.in.in remove-potcdate.sin; do
      func_dest_tmpfilename $pobase/$file
      func_lookup_file build-aux/po/$file
      cat "$lookedup_file" > "$tmpfile"
      if test -f "$destdir"/$pobase/$file; then
        if cmp -s "$destdir"/$pobase/$file "$tmpfile"; then
          rm -f "$tmpfile"
        else
          if $doit; then
            echo "Updating $pobase/$file (backup in $pobase/$file~)"
            mv -f "$destdir"/$pobase/$file "$destdir"/$pobase/$file~
            mv -f "$tmpfile" "$destdir"/$pobase/$file
          else
            echo "Update $pobase/$file (backup in $pobase/$file~)"
            rm -f "$tmpfile"
          fi
        fi
      else
        if $doit; then
          echo "Creating $pobase/$file"
          mv -f "$tmpfile" "$destdir"/$pobase/$file
        else
          echo "Create $pobase/$file"
          rm -f "$tmpfile"
        fi
        func_append added_files "$pobase/$file$nl"
      fi
    done
    # Create po makefile parameterization, part 1.
    func_dest_tmpfilename $pobase/Makevars
    func_emit_po_Makevars > "$tmpfile"
    if test -f "$destdir"/$pobase/Makevars; then
      if cmp -s "$destdir"/$pobase/Makevars "$tmpfile"; then
        rm -f "$tmpfile"
      else
        if $doit; then
          echo "Updating $pobase/Makevars (backup in $pobase/Makevars~)"
          mv -f "$destdir"/$pobase/Makevars "$destdir"/$pobase/Makevars~
          mv -f "$tmpfile" "$destdir"/$pobase/Makevars
        else
          echo "Update $pobase/Makevars (backup in $pobase/Makevars~)"
          rm -f "$tmpfile"
        fi
      fi
    else
      if $doit; then
        echo "Creating $pobase/Makevars"
        mv -f "$tmpfile" "$destdir"/$pobase/Makevars
      else
        echo "Create $pobase/Makevars"
        rm -f "$tmpfile"
      fi
      func_append added_files "$pobase/Makevars$nl"
    fi
    # Create po makefile parameterization, part 2.
    func_dest_tmpfilename $pobase/POTFILES.in
    func_emit_po_POTFILES_in > "$tmpfile"
    if test -f "$destdir"/$pobase/POTFILES.in; then
      if cmp -s "$destdir"/$pobase/POTFILES.in "$tmpfile"; then
        rm -f "$tmpfile"
      else
        if $doit; then
          echo "Updating $pobase/POTFILES.in (backup in $pobase/POTFILES.in~)"
          mv -f "$destdir"/$pobase/POTFILES.in "$destdir"/$pobase/POTFILES.in~
          mv -f "$tmpfile" "$destdir"/$pobase/POTFILES.in
        else
          echo "Update $pobase/POTFILES.in (backup in $pobase/POTFILES.in~)"
          rm -f "$tmpfile"
        fi
      fi
    else
      if $doit; then
        echo "Creating $pobase/POTFILES.in"
        mv -f "$tmpfile" "$destdir"/$pobase/POTFILES.in
      else
        echo "Create $pobase/POTFILES.in"
        rm -f "$tmpfile"
      fi
      func_append added_files "$pobase/POTFILES.in$nl"
    fi
    # Fetch PO files.
    TP_URL="http://translationproject.org/latest/"
    TP_RSYNC_URI="translationproject.org::tp/latest/"
    if $doit; then
      echo "Fetching gnulib PO files from $TP_URL"
      (cd "$destdir"/$pobase \
       && { # Prefer rsync over wget if it is available, since it consumes
            # less network bandwidth, due to compression.
            if type rsync 2>/dev/null | grep / > /dev/null; then
              rsync -Lrtz "${TP_RSYNC_URI}gnulib/" .
            else
              wget --quiet -r -l1 -nd -np -A.po "${TP_URL}gnulib"
            fi
          }
      )
    else
      echo "Fetch gnulib PO files from $TP_URL"
    fi
    # Create po/LINGUAS.
    if $doit; then
      func_dest_tmpfilename $pobase/LINGUAS
      (cd "$destdir"/$pobase \
       && { echo '# Set of available languages.'
            LC_ALL=C ls -1 *.po | sed -e 's,\.po$,,'
          }
      ) > "$tmpfile"
      if test -f "$destdir"/$pobase/LINGUAS; then
        if cmp -s "$destdir"/$pobase/LINGUAS "$tmpfile"; then
          rm -f "$tmpfile"
        else
          echo "Updating $pobase/LINGUAS (backup in $pobase/LINGUAS~)"
          mv -f "$destdir"/$pobase/LINGUAS "$destdir"/$pobase/LINGUAS~
          mv -f "$tmpfile" "$destdir"/$pobase/LINGUAS
        fi
      else
        echo "Creating $pobase/LINGUAS"
        mv -f "$tmpfile" "$destdir"/$pobase/LINGUAS
        func_append added_files "$pobase/LINGUAS$nl"
      fi
    else
      if test -f "$destdir"/$pobase/LINGUAS; then
        echo "Update $pobase/LINGUAS (backup in $pobase/LINGUAS~)"
      else
        echo "Create $pobase/LINGUAS"
      fi
    fi
  fi

  # Create m4/gnulib-cache.m4.
  func_dest_tmpfilename $m4base/gnulib-cache.m4
  (
    func_emit_copyright_notice
    echo "#"
    echo "# This file represents the specification of how gnulib-tool is used."
    echo "# It acts as a cache: It is written and read by gnulib-tool."
    echo "# In projects that use version control, this file is meant to be put under"
    echo "# version control, like the configure.ac and various Makefile.am files."
    echo
    echo
    echo "# Specification in the form of a command-line invocation:"
    echo "#   $actioncmd"
    echo
    echo "# Specification in the form of a few gnulib-tool.m4 macro invocations:"
    # Store the local_gnulib_dir relative to destdir.
    case "$local_gnulib_dir" in
      "" | /*)
        relative_local_gnulib_dir="$local_gnulib_dir" ;;
      * )
        case "$destdir" in
          /*) relative_local_gnulib_dir="$local_gnulib_dir" ;;
          *)
            # destdir, local_gnulib_dir are both relative.
            func_relativize "$destdir" "$local_gnulib_dir"
            relative_local_gnulib_dir="$reldir" ;;
        esac ;;
    esac
    echo "gl_LOCAL_DIR([$relative_local_gnulib_dir])"
    echo "gl_MODULES(["
    echo "$specified_modules" | sed -e 's/^/  /g'
    echo "])"
    test -z "$incobsolete" || echo "gl_WITH_OBSOLETE"
    test -z "$inc_cxx_tests" || echo "gl_WITH_CXX_TESTS"
    test -z "$inc_longrunning_tests" || echo "gl_WITH_LONGRUNNING_TESTS"
    test -z "$inc_privileged_tests" || echo "gl_WITH_PRIVILEGED_TESTS"
    test -z "$inc_unportable_tests" || echo "gl_WITH_UNPORTABLE_TESTS"
    test -z "$inc_all_tests" || echo "gl_WITH_ALL_TESTS"
    echo "gl_AVOID([$avoidlist])"
    echo "gl_SOURCE_BASE([$sourcebase])"
    echo "gl_M4_BASE([$m4base])"
    echo "gl_PO_BASE([$pobase])"
    echo "gl_DOC_BASE([$docbase])"
    echo "gl_TESTS_BASE([$testsbase])"
    test -z "$inctests" || echo "gl_WITH_TESTS"
    echo "gl_LIB([$libname])"
    if test -n "$lgpl"; then
      if test "$lgpl" = yes; then
        echo "gl_LGPL"
      else
        echo "gl_LGPL([$lgpl])"
      fi
    fi
    echo "gl_MAKEFILE_NAME([$makefile_name])"
    if test "$cond_dependencies" = true; then
      echo "gl_CONDITIONAL_DEPENDENCIES"
    fi
    if test "$libtool" = true; then
      echo "gl_LIBTOOL"
    fi
    echo "gl_MACRO_PREFIX([$macro_prefix])"
    echo "gl_PO_DOMAIN([$po_domain])"
    echo "gl_WITNESS_C_DOMAIN([$witness_c_macro])"
    if test -n "$vc_files"; then
      echo "gl_VC_FILES([$vc_files])"
    fi
  ) > "$tmpfile"
  if test -f "$destdir"/$m4base/gnulib-cache.m4; then
    if cmp -s "$destdir"/$m4base/gnulib-cache.m4 "$tmpfile"; then
      rm -f "$tmpfile"
    else
      if $doit; then
        echo "Updating $m4base/gnulib-cache.m4 (backup in $m4base/gnulib-cache.m4~)"
        mv -f "$destdir"/$m4base/gnulib-cache.m4 "$destdir"/$m4base/gnulib-cache.m4~
        mv -f "$tmpfile" "$destdir"/$m4base/gnulib-cache.m4
      else
        echo "Update $m4base/gnulib-cache.m4 (backup in $m4base/gnulib-cache.m4~)"
        if false; then
          cat "$tmpfile"
          echo
          echo "# gnulib-cache.m4 ends here"
        fi
        rm -f "$tmpfile"
      fi
    fi
  else
    if $doit; then
      echo "Creating $m4base/gnulib-cache.m4"
      mv -f "$tmpfile" "$destdir"/$m4base/gnulib-cache.m4
    else
      echo "Create $m4base/gnulib-cache.m4"
      cat "$tmpfile"
      rm -f "$tmpfile"
    fi
  fi

  # Create m4/gnulib-comp.m4.
  func_dest_tmpfilename $m4base/gnulib-comp.m4
  (
    echo "# DO NOT EDIT! GENERATED AUTOMATICALLY!"
    func_emit_copyright_notice
    echo "#"
    echo "# This file represents the compiled summary of the specification in"
    echo "# gnulib-cache.m4. It lists the computed macro invocations that need"
    echo "# to be invoked from configure.ac."
    echo "# In projects that use version control, this file can be treated like"
    echo "# other built files."
    echo
    echo
    echo "# This macro should be invoked from $configure_ac, in the section"
    echo "# \"Checks for programs\", right after AC_PROG_CC, and certainly before"
    echo "# any checks for libraries, header files, types and library functions."
    echo "AC_DEFUN([${macro_prefix}_EARLY],"
    echo "["
    echo "  m4_pattern_forbid([^gl_[A-Z]])dnl the gnulib macro namespace"
    echo "  m4_pattern_allow([^gl_ES\$])dnl a valid locale name"
    echo "  m4_pattern_allow([^gl_LIBOBJS\$])dnl a variable"
    echo "  m4_pattern_allow([^gl_LTLIBOBJS\$])dnl a variable"
    echo "  AC_REQUIRE([gl_PROG_AR_RANLIB])"
    if test -n "$uses_subdirs"; then
      echo "  AC_REQUIRE([AM_PROG_CC_C_O])"
    fi
    for module in $final_modules; do
      func_verify_module
      if test -n "$module"; then
        echo "# Code from module $module:"
        func_get_autoconf_early_snippet "$module"
      fi
    done \
      | sed -e '/^$/d;' -e 's/^/  /'
    echo "])"
    echo
    echo "# This macro should be invoked from $configure_ac, in the section"
    echo "# \"Check for header files, types and library functions\"."
    echo "AC_DEFUN([${macro_prefix}_INIT],"
    echo "["
    if test "$libtool" = true; then
      echo "  AM_CONDITIONAL([GL_COND_LIBTOOL], [true])"
      echo "  gl_cond_libtool=true"
    else
      echo "  AM_CONDITIONAL([GL_COND_LIBTOOL], [false])"
      echo "  gl_cond_libtool=false"
      echo "  gl_libdeps="
      echo "  gl_ltlibdeps="
    fi
    if test "$auxdir" != "build-aux"; then
      sed_replace_build_aux='
        :a
        /AC_CONFIG_FILES(.*:build-aux\/.*)/{
          s|AC_CONFIG_FILES(\(.*\):build-aux/\(.*\))|AC_CONFIG_FILES(\1:'"$auxdir"'/\2)|
          ba
        }'
    else
      sed_replace_build_aux="$sed_noop"
    fi
    echo "  gl_m4_base='$m4base'"
    func_emit_initmacro_start $macro_prefix
    echo "  gl_source_base='$sourcebase'"
    if test -n "$witness_c_macro"; then
      echo "  m4_pushdef([gl_MODULE_INDICATOR_CONDITION], [$witness_c_macro])"
    fi
    func_emit_autoconf_snippets "$main_modules" func_verify_module true false true
    if test -n "$witness_c_macro"; then
      echo "  m4_popdef([gl_MODULE_INDICATOR_CONDITION])"
    fi
    echo "  # End of code from modules"
    func_emit_initmacro_end $macro_prefix
    echo "  gltests_libdeps="
    echo "  gltests_ltlibdeps="
    func_emit_initmacro_start ${macro_prefix}tests
    echo "  gl_source_base='$testsbase'"
    # Define a tests witness macro that depends on the package.
    # PACKAGE is defined by AM_INIT_AUTOMAKE, PACKAGE_TARNAME is defined by AC_INIT.
    # See <http://lists.gnu.org/archive/html/automake/2009-05/msg00145.html>.
    echo "changequote(,)dnl"
    echo "  ${macro_prefix}tests_WITNESS=IN_\`echo \"\${PACKAGE-\$PACKAGE_TARNAME}\" | LC_ALL=C tr abcdefghijklmnopqrstuvwxyz ABCDEFGHIJKLMNOPQRSTUVWXYZ | LC_ALL=C sed -e 's/[^A-Z0-9_]/_/g'\`_GNULIB_TESTS"
    echo "changequote([, ])dnl"
    echo "  AC_SUBST([${macro_prefix}tests_WITNESS])"
    echo "  gl_module_indicator_condition=\$${macro_prefix}tests_WITNESS"
    echo "  m4_pushdef([gl_MODULE_INDICATOR_CONDITION], [\$gl_module_indicator_condition])"
    func_emit_autoconf_snippets "$testsrelated_modules" func_verify_module true true true
    echo "  m4_popdef([gl_MODULE_INDICATOR_CONDITION])"
    func_emit_initmacro_end ${macro_prefix}tests
    # _LIBDEPS and _LTLIBDEPS variables are not needed if this library is
    # created using libtool, because libtool already handles the dependencies.
    if test "$libtool" != true; then
      libname_upper=`echo "$libname" | LC_ALL=C tr '[a-z]-' '[A-Z]_'`
      echo "  ${libname_upper}_LIBDEPS=\"\$gl_libdeps\""
      echo "  AC_SUBST([${libname_upper}_LIBDEPS])"
      echo "  ${libname_upper}_LTLIBDEPS=\"\$gl_ltlibdeps\""
      echo "  AC_SUBST([${libname_upper}_LTLIBDEPS])"
    fi
    if $use_libtests; then
      echo "  LIBTESTS_LIBDEPS=\"\$gltests_libdeps\""
      echo "  AC_SUBST([LIBTESTS_LIBDEPS])"
    fi
    echo "])"
    func_emit_initmacro_done $macro_prefix $sourcebase
    func_emit_initmacro_done ${macro_prefix}tests $testsbase
    echo
    echo "# This macro records the list of files which have been installed by"
    echo "# gnulib-tool and may be removed by future gnulib-tool invocations."
    echo "AC_DEFUN([${macro_prefix}_FILE_LIST], ["
    echo "$files" | sed -e 's,^,  ,'
    echo "])"
  ) > "$tmpfile"
  if test -f "$destdir"/$m4base/gnulib-comp.m4; then
    if cmp -s "$destdir"/$m4base/gnulib-comp.m4 "$tmpfile"; then
      rm -f "$tmpfile"
    else
      if $doit; then
        echo "Updating $m4base/gnulib-comp.m4 (backup in $m4base/gnulib-comp.m4~)"
        mv -f "$destdir"/$m4base/gnulib-comp.m4 "$destdir"/$m4base/gnulib-comp.m4~
        mv -f "$tmpfile" "$destdir"/$m4base/gnulib-comp.m4
      else
        echo "Update $m4base/gnulib-comp.m4 (backup in $m4base/gnulib-comp.m4~)"
        if false; then
          cat "$tmpfile"
          echo
          echo "# gnulib-comp.m4 ends here"
        fi
        rm -f "$tmpfile"
      fi
    fi
  else
    if $doit; then
      echo "Creating $m4base/gnulib-comp.m4"
      mv -f "$tmpfile" "$destdir"/$m4base/gnulib-comp.m4
    else
      echo "Create $m4base/gnulib-comp.m4"
      cat "$tmpfile"
      rm -f "$tmpfile"
    fi
  fi

  if test -n "$inctests"; then
    # Create tests makefile.
    func_dest_tmpfilename $testsbase/$makefile_am
    destfile="$testsbase/$makefile_am"
    modules="$testsrelated_modules"
    func_emit_tests_Makefile_am "${macro_prefix}tests_WITNESS" > "$tmpfile"
    if test -f "$destdir"/$testsbase/$makefile_am; then
      if cmp -s "$destdir"/$testsbase/$makefile_am "$tmpfile"; then
        rm -f "$tmpfile"
      else
        if $doit; then
          echo "Updating $testsbase/$makefile_am (backup in $testsbase/$makefile_am~)"
          mv -f "$destdir"/$testsbase/$makefile_am "$destdir"/$testsbase/$makefile_am~
          mv -f "$tmpfile" "$destdir"/$testsbase/$makefile_am
        else
          echo "Update $testsbase/$makefile_am (backup in $testsbase/$makefile_am~)"
          rm -f "$tmpfile"
        fi
      fi
    else
      if $doit; then
        echo "Creating $testsbase/$makefile_am"
        mv -f "$tmpfile" "$destdir"/$testsbase/$makefile_am
      else
        echo "Create $testsbase/$makefile_am"
        rm -f "$tmpfile"
      fi
    func_append added_files "$testsbase/$makefile_am$nl"
    fi
  fi

  if test "$vc_files" != false; then
    # Update the .cvsignore and .gitignore files.
    { echo "$added_files" | sed -e '/^$/d' -e 's,\([^/]*\)$,|A|\1,'
      echo "$removed_files" | sed -e '/^$/d' -e 's,\([^/]*\)$,|R|\1,'
      # Treat gnulib-comp.m4 like an added file, even if it already existed.
      echo "$m4base/|A|gnulib-comp.m4"
    } | LC_ALL=C sort -t'|' -k1,1 > "$tmp"/fileset-changes
    { # Rearrange file descriptors. Needed because "while ... done < ..."
      # constructs are executed in a subshell e.g. by Solaris 10 /bin/sh.
      exec 5<&0 < "$tmp"/fileset-changes
      func_update_ignorelist ()
      {
        ignore="$1"
        if test "$ignore" = .gitignore; then
          # In a .gitignore file, "foo" applies to the current directory and all
          # subdirectories, whereas "/foo" applies to the current directory only.
          anchor='/'
          escaped_anchor='\/'
          doubly_escaped_anchor='\\/'
        else
          anchor=''
          escaped_anchor=''
          doubly_escaped_anchor=''
        fi
        if test -f "$destdir/$dir$ignore"; then
          if test -n "$dir_added" || test -n "$dir_removed"; then
            sed -e "s|^$anchor||" < "$destdir/$dir$ignore" | LC_ALL=C sort > "$tmp"/ignore
            (echo "$dir_added" | sed -e '/^$/d' | LC_ALL=C sort -u \
               | LC_ALL=C join -v 1 - "$tmp"/ignore > "$tmp"/ignore-added
             echo "$dir_removed" | sed -e '/^$/d' | LC_ALL=C sort -u \
               | LC_ALL=C join -v 1 - "$tmp"/ignore > "$tmp"/ignore-removed
            )
            if test -s "$tmp"/ignore-added || test -s "$tmp"/ignore-removed; then
              if $doit; then
                echo "Updating $destdir/$dir$ignore (backup in $destdir/$dir${ignore}~)"
                mv -f "$destdir/$dir$ignore" "$destdir/$dir$ignore"~
                { sed -e 's,/,\\/,g' -e 's,^,/^,' -e 's,$,\$/d,' < "$tmp"/ignore-removed
                  if test -n "$anchor"; then sed -e 's,/,\\/,g' -e "s,^,/^${doubly_escaped_anchor}," -e 's,$,$/d,' < "$tmp"/ignore-removed; fi
                } > "$tmp"/sed-ignore-removed
                { cat "$destdir/$dir$ignore"~
                  sed -e "s|^|$anchor|" < "$tmp"/ignore-added
                } | sed -f "$tmp"/sed-ignore-removed \
                  > "$destdir/$dir$ignore"
              else
                echo "Update $destdir/$dir$ignore (backup in $destdir/$dir${ignore}~)"
              fi
            fi
          fi
        else
          if test -n "$dir_added"; then
            if $doit; then
              echo "Creating $destdir/$dir$ignore"
              {
                if test "$ignore" = .cvsignore; then
                  echo ".deps"
                  # Automake generates Makefile rules that create .dirstamp files.
                  echo ".dirstamp"
                fi
                echo "$dir_added" | sed -e '/^$/d' -e "s|^|$anchor|" | LC_ALL=C sort -u
              } > "$destdir/$dir$ignore"
            else
              echo "Create $destdir/$dir$ignore"
            fi
          fi
        fi
      }
      func_done_dir ()
      {
        dir="$1"
        dir_added="$2"
        dir_removed="$3"
        if test -d "$destdir/CVS" || test -d "$destdir/${dir}CVS" || test -f "$destdir/${dir}.cvsignore"; then
          func_update_ignorelist .cvsignore
        fi
        if test -d "$destdir/.git" || test -f "$destdir/${dir}.gitignore"; then
          func_update_ignorelist .gitignore
        fi
      }
      last_dir=
      last_dir_added=
      last_dir_removed=
      while read line; do
        # Why not ''read next_dir op file'' ? Because the dir column can be empty.
        next_dir=`echo "$line" | sed -e 's,|.*,,'`
        op=`echo "$line" | sed -e 's,^[^|]*|\([^|]*\)|.*$,\1,'`
        file=`echo "$line" | sed -e 's,^[^|]*|[^|]*|,,'`
        if test "$next_dir" != "$last_dir"; then
          func_done_dir "$last_dir" "$last_dir_added" "$last_dir_removed"
          last_dir="$next_dir"
          last_dir_added=
          last_dir_removed=
        fi
        case $op in
          A) func_append last_dir_added "$file$nl";;
          R) func_append last_dir_removed "$file$nl";;
        esac
      done
      func_done_dir "$last_dir" "$last_dir_added" "$last_dir_removed"
      exec 0<&5 5<&-
    }
  fi

  echo "Finished."
  echo
  echo "You may need to add #include directives for the following .h files."
  # Intersect $specified_modules and $main_modules
  # (since $specified_modules is not necessarily of subset of $main_modules
  # - some may have been skipped through --avoid, and since the elements of
  # $main_modules but not in $specified_modules can go away without explicit
  # notice - through changes in the module dependencies).
  echo "$specified_modules" > "$tmp"/modules1 # a sorted list, one module per line
  echo "$main_modules" > "$tmp"/modules2 # also a sorted list, one module per line
  # First the #include <...> directives without #ifs, sorted for convenience,
  # then the #include "..." directives without #ifs, sorted for convenience,
  # then the #include directives that are surrounded by #ifs. Not sorted.
  for module in `LC_ALL=C join "$tmp"/modules1 "$tmp"/modules2`; do
    include_directive=`func_get_include_directive "$module"`
    case "$nl$include_directive" in
      *"$nl#if"*)
        echo "$include_directive" 1>&5
        ;;
      *)
        echo "$include_directive" | grep -v 'include "' 1>&6
        echo "$include_directive" | grep 'include "' 1>&7
        ;;
    esac
  done 5> "$tmp"/include-if 6> "$tmp"/include-angles 7> "$tmp"/include-quotes
  (
   LC_ALL=C sort -u "$tmp"/include-angles
   LC_ALL=C sort -u "$tmp"/include-quotes
   cat "$tmp"/include-if
  ) | sed -e '/^$/d' -e 's/^/  /'
  rm -f "$tmp"/include-angles "$tmp"/include-quotes "$tmp"/include-if

  for module in $main_modules; do
    func_get_link_directive "$module"
  done \
    | LC_ALL=C sort -u | sed -e '/^$/d' -e 's/^/  /' > "$tmp"/link
  if test `wc -l < "$tmp"/link` != 0; then
    echo
    echo "You may need to use the following Makefile variables when linking."
    echo "Use them in <program>_LDADD when linking a program, or"
    echo "in <library>_a_LDFLAGS or <library>_la_LDFLAGS when linking a library."
    cat "$tmp"/link
  fi
  rm -f "$tmp"/link

  echo
  echo "Don't forget to"
  if test "$makefile_am" = Makefile.am; then
    echo "  - add \"$sourcebase/Makefile\" to AC_CONFIG_FILES in $configure_ac,"
  else
    echo "  - \"include $makefile_name\" from within \"$sourcebase/Makefile.am\","
  fi
  if test -n "$pobase"; then
    echo "  - add \"$pobase/Makefile.in\" to AC_CONFIG_FILES in $configure_ac,"
  fi
  if test -n "$inctests"; then
    if test "$makefile_am" = Makefile.am; then
      echo "  - add \"$testsbase/Makefile\" to AC_CONFIG_FILES in $configure_ac,"
    else
      echo "  - \"include $makefile_name\" from within \"$testsbase/Makefile.am\","
    fi
  fi
  edit=0
  while test $edit != $makefile_am_edits; do
    edit=`expr $edit + 1`
    eval dir=\"\$makefile_am_edit${edit}_dir\"
    eval var=\"\$makefile_am_edit${edit}_var\"
    eval val=\"\$makefile_am_edit${edit}_val\"
    if test -n "$var"; then
      echo "  - mention \"${val}\" in ${var} in ${dir}Makefile.am,"
    fi
  done
  if grep '^ *AC_PROG_CC_STDC' "$configure_ac" > /dev/null; then
    position_early_after=AC_PROG_CC_STDC
  else
    if grep '^ *AC_PROG_CC_C99' "$configure_ac" > /dev/null; then
      position_early_after=AC_PROG_CC_C99
    else
      position_early_after=AC_PROG_CC
    fi
  fi
  echo "  - invoke ${macro_prefix}_EARLY in $configure_ac, right after $position_early_after,"
  echo "  - invoke ${macro_prefix}_INIT in $configure_ac."
}

# func_create_testdir testdir modules
# Input:
# - local_gnulib_dir  from --local-dir
# - modcache        true or false, from --cache-modules/--no-cache-modules
# - auxdir          directory relative to destdir where to place build aux files
# - inctests        true if tests should be included, blank otherwise
# - incobsolete     true if obsolete modules among dependencies should be
#                   included, blank otherwise
# - excl_cxx_tests   true if C++ interoperability tests should be excluded,
#                    blank otherwise
# - excl_longrunning_tests  true if long-runnings tests should be excluded,
#                           blank otherwise
# - excl_privileged_tests  true if tests that require root privileges should be
#                          excluded, blank otherwise
# - excl_unportable_tests  true if tests that fail on some platforms should be
#                          excluded, blank otherwise
# - single_configure  true if a single configure file should be generated,
#                     false for a separate configure file for the tests
# - avoidlist       list of modules to avoid
# - cond_dependencies  true if --conditional-dependencies was given, false if
#                      --no-conditional-dependencies was given, blank otherwise
# - libtool         true if --libtool was given, false if --no-libtool was
#                   given, blank otherwise
# - symbolic        true if files should be symlinked, copied otherwise
# - lsymbolic       true if files from local_gnulib_dir should be symlinked,
#                   copied otherwise
func_create_testdir ()
{
  testdir="$1"
  modules="$2"
  if test -z "$modules"; then
    # All modules together.
    # Except config-h, which breaks all modules which use HAVE_CONFIG_H.
    # Except ftruncate, mountlist, which abort the configuration on mingw. FIXME.
    # Except lib-ignore, which leads to link errors when Sun C++ is used. FIXME.
    modules=`func_all_modules`
    modules=`for m in $modules; do case $m in config-h | ftruncate | mountlist | lib-ignore) ;; *) echo $m;; esac; done`
  fi
  specified_modules="$modules"

  # Canonicalize the list of specified modules.
  specified_modules=`for m in $specified_modules; do echo $m; done | LC_ALL=C sort -u`

  # Unlike in func_import, here we want to include all kinds of tests for the
  # directly specified modules, but not for dependencies.
  inc_all_direct_tests=true
  inc_all_indirect_tests="$inc_all_tests"

  # Check that the license of every module is consistent with the license of
  # its dependencies.
  saved_inctests="$inctests"
  # When computing transitive closures, don't consider $module to depend on
  # $module-tests. Need this because tests are implicitly GPL and may depend
  # on GPL modules - therefore we don't want a warning in this case.
  inctests=""
  for requested_module in $specified_modules; do
    requested_license=`func_get_license "$requested_module"`
    if test "$requested_license" != GPL; then
      # Here we use func_modules_transitive_closure, not just
      # func_get_dependencies, so that we also detect weird situations like
      # an LGPL module which depends on a GPLed build tool module which depends
      # on a GPL module.
      modules="$requested_module"
      func_modules_transitive_closure
      for module in $modules; do
        license=`func_get_license "$module"`
        case "$license" in
          'GPLed build tool') ;;
          'public domain' | 'unlimited' | 'unmodifiable license text') ;;
          *)
            case "$requested_license" in
              GPLv2+)
                case "$license" in
                  GPLv2+ | LGPLv2+) ;;
                  *) func_warning "module $requested_module depends on a module with an incompatible license: $module" ;;
                esac
                ;;
              LGPL)
                case "$license" in
                  LGPL | LGPLv2+) ;;
                  *) func_warning "module $requested_module depends on a module with an incompatible license: $module" ;;
                esac
                ;;
              LGPLv2+)
                case "$license" in
                  LGPLv2+) ;;
                  *) func_warning "module $requested_module depends on a module with an incompatible license: $module" ;;
                esac
                ;;
            esac
            ;;
        esac
      done
    fi
  done
  inctests="$saved_inctests"

  # Subdirectory names.
  sourcebase=gllib
  m4base=glm4
  pobase=
  docbase=gldoc
  testsbase=gltests
  macro_prefix=gl
  po_domain=
  witness_c_macro=
  vc_files=

  # Determine final module list.
  modules="$specified_modules"
  func_modules_transitive_closure
  if test $verbose -ge 0; then
    func_show_module_list
  fi
  final_modules="$modules"

  if $single_configure; then
    # Determine main module list and tests-related module list separately.
    func_modules_transitive_closure_separately
  fi

  if $single_configure; then
    # Determine whether a $testsbase/libtests.a is needed.
    func_determine_use_libtests
  fi

  # Add the dummy module if needed.
  if $single_configure; then
    func_modules_add_dummy_separately
  else
    func_modules_add_dummy
  fi

  # Show banner notice of every module.
  if $single_configure; then
    modules="$main_modules"
    func_modules_notice
  else
    func_modules_notice
  fi

  # Determine final file list.
  if $single_configure; then
    func_modules_to_filelist_separately
  else
    func_modules_to_filelist
    if test $verbose -ge 0; then
      echo "File list:"
      echo "$files" | sed -e 's/^/  /'
    fi
  fi
  # Add files for which the copy in gnulib is newer than the one that
  # "automake --add-missing --copy" would provide.
  files="$files build-aux/config.guess"
  files="$files build-aux/config.sub"
  files=`for f in $files; do echo $f; done | LC_ALL=C sort -u`

  rewritten='%REWRITTEN%'
  sed_rewrite_files="\
    s,^build-aux/,$rewritten$auxdir/,
    s,^doc/,$rewritten$docbase/,
    s,^lib/,$rewritten$sourcebase/,
    s,^m4/,$rewritten$m4base/,
    s,^tests/,$rewritten$testsbase/,
    s,^tests=lib/,$rewritten$testsbase/,
    s,^top/,$rewritten,
    s,^$rewritten,,"

  # Create directories.
  for f in $files; do echo $f; done \
    | sed -e "$sed_rewrite_files" \
    | sed -n -e 's,^\(.*\)/[^/]*,\1,p' \
    | LC_ALL=C sort -u \
    > "$tmp"/dirs
  { # Rearrange file descriptors. Needed because "while ... done < ..."
    # constructs are executed in a subshell e.g. by Solaris 10 /bin/sh.
    exec 5<&0 < "$tmp"/dirs
    while read d; do
      mkdir -p "$testdir/$d"
    done
    exec 0<&5 5<&-
  }

  # Copy files or make symbolic links.
  delimiter='	'
  for f in $files; do echo $f; done \
    | sed -e "s,^.*\$,&$delimiter&," -e "$sed_rewrite_files" \
    | LC_ALL=C sort \
    > "$tmp"/files
  { # Rearrange file descriptors. Needed because "while ... done < ..."
    # constructs are executed in a subshell e.g. by Solaris 10 /bin/sh.
    exec 5<&0 < "$tmp"/files
    while read g f; do
      case "$f" in
        tests=lib/*) f=`echo "$f" | sed -e 's,^tests=lib/,lib/,'` ;;
      esac
      func_lookup_file "$f"
      if test -n "$lookedup_tmp"; then
        cp -p "$lookedup_file" "$testdir/$g"
      else
        ln "$lookedup_file" "$testdir/$g" 2>/dev/null ||
        if { test -n "$symbolic" \
             || { test -n "$lsymbolic" \
                  && test "$lookedup_file" = "$local_gnulib_dir/$f"; }; }; then
          func_ln "$lookedup_file" "$testdir/$g"
        else
          cp -p "$lookedup_file" "$testdir/$g"
        fi
      fi
    done
    exec 0<&5 5<&-
  }

  # Determine include_guard_prefix.
  func_compute_include_guard_prefix

  # Create Makefile.ams that are for testing.
  for_test=true

  # No special edits are needed.
  makefile_am_edits=0

  # Create $sourcebase/Makefile.am.
  mkdir -p "$testdir/$sourcebase"
  destfile="$sourcebase/Makefile.am"
  if $single_configure; then
    modules="$main_modules"
  fi
  func_emit_lib_Makefile_am > "$testdir/$sourcebase/Makefile.am"
  any_uses_subdirs="$uses_subdirs"

  # Create $m4base/Makefile.am.
  mkdir -p "$testdir/$m4base"
  (echo "## Process this file with automake to produce Makefile.in."
   echo
   echo "EXTRA_DIST ="
   for f in $files; do
     case "$f" in
       m4/* )
         echo "EXTRA_DIST += "`echo "$f" | sed -e 's,^m4/,,'` ;;
     esac
   done
  ) > "$testdir/$m4base/Makefile.am"

  subdirs="$sourcebase $m4base"
  subdirs_with_configure_ac=""

  if false && test -f "$testdir"/$m4base/gettext.m4; then
    # Avoid stupid error message from automake:
    # "AM_GNU_GETTEXT used but `po' not in SUBDIRS"
    mkdir -p "$testdir/po"
    (echo "## Process this file with automake to produce Makefile.in."
    ) > "$testdir/po/Makefile.am"
    func_append subdirs " po"
  fi

  if test -n "$inctests"; then
    test -d "$testdir/$testsbase" || mkdir "$testdir/$testsbase"
    if $single_configure; then
      # Create $testsbase/Makefile.am.
      destfile="$testsbase/Makefile.am"
      modules="$testsrelated_modules"
      func_emit_tests_Makefile_am "${macro_prefix}tests_WITNESS" > "$testdir/$testsbase/Makefile.am"
    else
      # Viewed from the $testsbase subdirectory, $auxdir is different.
      saved_auxdir="$auxdir"
      auxdir=`echo "$testsbase/" | sed -e 's%[^/][^/]*//*%../%g'`"$auxdir"
      # Create $testsbase/Makefile.am.
      use_libtests=false
      destfile="$testsbase/Makefile.am"
      func_emit_tests_Makefile_am "" > "$testdir/$testsbase/Makefile.am"
      any_uses_subdirs="$any_uses_subdirs$uses_subdirs"
      # Create $testsbase/configure.ac.
      (echo "# Process this file with autoconf to produce a configure script."
       echo "AC_INIT([dummy], [0])"
       echo "AC_CONFIG_AUX_DIR([$auxdir])"
       echo "AM_INIT_AUTOMAKE"
       echo
       echo "AC_CONFIG_HEADERS([config.h])"
       echo
       echo "AC_PROG_CC"
       echo "AC_PROG_INSTALL"
       echo "AC_PROG_MAKE_SET"
       echo "gl_PROG_AR_RANLIB"
       echo
       if test -n "$uses_subdirs"; then
         echo "AM_PROG_CC_C_O"
         echo
       fi
       for module in $modules; do
         func_verify_module
         if test -n "$module"; then
           case $module in
             gnumakefile | maintainer-makefile)
               # These modules are meant to be used only in the top-level directory.
               ;;
             *)
               func_get_autoconf_early_snippet "$module"
               ;;
           esac
         fi
       done \
         | sed -e '/^$/d;' -e 's/AC_REQUIRE(\[\([^()]*\)\])/\1/'
       if test "$libtool" = true; then
         echo "LT_INIT([win32-dll])"
         echo "LT_LANG([C++])"
         echo "AM_CONDITIONAL([GL_COND_LIBTOOL], [true])"
         echo "gl_cond_libtool=true"
       else
         echo "AM_CONDITIONAL([GL_COND_LIBTOOL], [false])"
         echo "gl_cond_libtool=false"
         echo "gl_libdeps="
         echo "gl_ltlibdeps="
       fi
       # Wrap the set of autoconf snippets into an autoconf macro that is then
       # invoked. This is needed because autoconf does not support AC_REQUIRE
       # at the top level:
       #   error: AC_REQUIRE(gt_CSHARPCOMP): cannot be used outside of an AC_DEFUN'd macro
       # but we want the AC_REQUIRE to have its normal meaning (provide one
       # expansion of the required macro before the current point, and only one
       # expansion total).
       echo "AC_DEFUN([gl_INIT], ["
       sed_replace_build_aux='
         :a
         /AC_CONFIG_FILES(.*:build-aux\/.*)/{
           s|AC_CONFIG_FILES(\(.*\):build-aux/\(.*\))|AC_CONFIG_FILES(\1:'"$auxdir"'/\2)|
           ba
         }'
       echo "gl_m4_base='../$m4base'"
       func_emit_initmacro_start $macro_prefix
       # We don't have explicit ordering constraints between the various
       # autoconf snippets. It's cleanest to put those of the library before
       # those of the tests.
       echo "gl_source_base='../$sourcebase'"
       func_emit_autoconf_snippets "$modules" func_verify_nontests_module false false false
       echo "gl_source_base='.'"
       func_emit_autoconf_snippets "$modules" func_verify_tests_module false false false
       func_emit_initmacro_end $macro_prefix
       # _LIBDEPS and _LTLIBDEPS variables are not needed if this library is
       # created using libtool, because libtool already handles the dependencies.
       if test "$libtool" != true; then
         libname_upper=`echo "$libname" | LC_ALL=C tr '[a-z]-' '[A-Z]_'`
         echo "  ${libname_upper}_LIBDEPS=\"\$gl_libdeps\""
         echo "  AC_SUBST([${libname_upper}_LIBDEPS])"
         echo "  ${libname_upper}_LTLIBDEPS=\"\$gl_ltlibdeps\""
         echo "  AC_SUBST([${libname_upper}_LTLIBDEPS])"
       fi
       echo "])"
       func_emit_initmacro_done $macro_prefix $sourcebase # FIXME use $sourcebase or $testsbase?
       echo
       echo "gl_INIT"
       echo
       # Usually $testsbase/config.h will be a superset of config.h. Verify this
       # by "merging" config.h into $testsbase/config.h; look out for gcc warnings.
       echo "AH_TOP([#include \"../config.h\"])"
       echo
       echo "AC_CONFIG_FILES([Makefile])"
       echo "AC_OUTPUT"
      ) > "$testdir/$testsbase/configure.ac"
      auxdir="$saved_auxdir"
      subdirs_with_configure_ac="$subdirs_with_configure_ac $testsbase"
    fi
    func_append subdirs " $testsbase"
  fi

  # Create Makefile.am.
  (echo "## Process this file with automake to produce Makefile.in."
   echo
   echo "AUTOMAKE_OPTIONS = 1.5 foreign"
   echo
   echo "SUBDIRS = $subdirs"
   echo
   echo "ACLOCAL_AMFLAGS = -I $m4base"
  ) > "$testdir/Makefile.am"

  # Create configure.ac.
  (echo "# Process this file with autoconf to produce a configure script."
   echo "AC_INIT([dummy], [0])"
   if test "$auxdir" != "."; then
     echo "AC_CONFIG_AUX_DIR([$auxdir])"
   fi
   echo "AM_INIT_AUTOMAKE"
   echo
   echo "AC_CONFIG_HEADERS([config.h])"
   echo
   echo "AC_PROG_CC"
   echo "AC_PROG_INSTALL"
   echo "AC_PROG_MAKE_SET"
   echo
   echo "# For autobuild."
   echo "AC_CANONICAL_BUILD"
   echo "AC_CANONICAL_HOST"
   echo
   echo "m4_pattern_forbid([^gl_[A-Z]])dnl the gnulib macro namespace"
   echo "m4_pattern_allow([^gl_ES\$])dnl a valid locale name"
   echo "m4_pattern_allow([^gl_LIBOBJS\$])dnl a variable"
   echo "m4_pattern_allow([^gl_LTLIBOBJS\$])dnl a variable"
   echo
   echo "gl_PROG_AR_RANLIB"
   echo
   if test -n "$any_uses_subdirs"; then
     echo "AM_PROG_CC_C_O"
     echo
   fi
   for module in $final_modules; do
     if $single_configure; then
       func_verify_module
     else
       func_verify_nontests_module
     fi
     if test -n "$module"; then
       func_get_autoconf_early_snippet "$module"
     fi
   done \
     | sed -e '/^$/d;' -e 's/AC_REQUIRE(\[\([^()]*\)\])/\1/'
   if test "$libtool" = true; then
     echo "LT_INIT([win32-dll])"
     echo "LT_LANG([C++])"
     echo "AM_CONDITIONAL([GL_COND_LIBTOOL], [true])"
     echo "gl_cond_libtool=true"
   else
     echo "AM_CONDITIONAL([GL_COND_LIBTOOL], [false])"
     echo "gl_cond_libtool=false"
     echo "gl_libdeps="
     echo "gl_ltlibdeps="
   fi
   # Wrap the set of autoconf snippets into an autoconf macro that is then
   # invoked. This is needed because autoconf does not support AC_REQUIRE
   # at the top level:
   #   error: AC_REQUIRE(gt_CSHARPCOMP): cannot be used outside of an AC_DEFUN'd macro
   # but we want the AC_REQUIRE to have its normal meaning (provide one
   # expansion of the required macro before the current point, and only one
   # expansion total).
   echo "AC_DEFUN([gl_INIT], ["
   if test "$auxdir" != "build-aux"; then
     sed_replace_build_aux='
       :a
       /AC_CONFIG_FILES(.*:build-aux\/.*)/{
         s|AC_CONFIG_FILES(\(.*\):build-aux/\(.*\))|AC_CONFIG_FILES(\1:'"$auxdir"'/\2)|
         ba
       }'
   else
     sed_replace_build_aux="$sed_noop"
   fi
   echo "gl_m4_base='$m4base'"
   func_emit_initmacro_start $macro_prefix
   echo "gl_source_base='$sourcebase'"
   if $single_configure; then
     func_emit_autoconf_snippets "$main_modules" func_verify_module true false false
   else
     func_emit_autoconf_snippets "$modules" func_verify_nontests_module true false false
   fi
   func_emit_initmacro_end $macro_prefix
   if $single_configure; then
     echo "  gltests_libdeps="
     echo "  gltests_ltlibdeps="
     func_emit_initmacro_start ${macro_prefix}tests
     echo "  gl_source_base='$testsbase'"
     # Define a tests witness macro.
     echo "  ${macro_prefix}tests_WITNESS=IN_GNULIB_TESTS"
     echo "  AC_SUBST([${macro_prefix}tests_WITNESS])"
     echo "  gl_module_indicator_condition=\$${macro_prefix}tests_WITNESS"
     echo "  m4_pushdef([gl_MODULE_INDICATOR_CONDITION], [\$gl_module_indicator_condition])"
     func_emit_autoconf_snippets "$testsrelated_modules" func_verify_module true false false
     echo "  m4_popdef([gl_MODULE_INDICATOR_CONDITION])"
     func_emit_initmacro_end ${macro_prefix}tests
   fi
   # _LIBDEPS and _LTLIBDEPS variables are not needed if this library is
   # created using libtool, because libtool already handles the dependencies.
   if test "$libtool" != true; then
     libname_upper=`echo "$libname" | LC_ALL=C tr '[a-z]-' '[A-Z]_'`
     echo "  ${libname_upper}_LIBDEPS=\"\$gl_libdeps\""
     echo "  AC_SUBST([${libname_upper}_LIBDEPS])"
     echo "  ${libname_upper}_LTLIBDEPS=\"\$gl_ltlibdeps\""
     echo "  AC_SUBST([${libname_upper}_LTLIBDEPS])"
   fi
   if $single_configure; then
     if $use_libtests; then
       echo "  LIBTESTS_LIBDEPS=\"\$gltests_libdeps\""
       echo "  AC_SUBST([LIBTESTS_LIBDEPS])"
     fi
   fi
   echo "])"
   func_emit_initmacro_done $macro_prefix $sourcebase
   if $single_configure; then
     func_emit_initmacro_done ${macro_prefix}tests $testsbase
   fi
   echo
   echo "gl_INIT"
   echo
   if test -n "$subdirs_with_configure_ac"; then
     echo "AC_CONFIG_SUBDIRS(["`echo $subdirs_with_configure_ac`"])"
   fi
   makefiles="Makefile"
   for d in $subdirs; do
     # For subdirs that have a configure.ac by their own, it's the subdir's
     # configure.ac which creates the subdir's Makefile.am, not this one.
     case " $subdirs_with_configure_ac " in
       *" $d "*) ;;
       *) func_append makefiles " $d/Makefile" ;;
     esac
   done
   echo "AC_CONFIG_FILES([$makefiles])"
   echo "AC_OUTPUT"
  ) > "$testdir/configure.ac"

  # Create autogenerated files.
  (cd "$testdir"
   # Do not use "${AUTORECONF} --force --install", because it may invoke
   # autopoint, which brings in older versions of some of our .m4 files.
   if test -f $m4base/gettext.m4; then
     func_execute_command ${AUTOPOINT} --force || func_exit 1
     for f in $m4base/*.m4~; do
       if test -f $f; then
         mv -f $f `echo $f | sed -e 's,~$,,'` || func_exit 1
       fi
     done
   fi
   if test "$libtool" = true; then
     func_execute_command ${LIBTOOLIZE} --copy || func_exit 1
   fi
   func_execute_command ${ACLOCAL} -I $m4base || func_exit 1
   if ! test -d build-aux; then
     func_execute_command mkdir build-aux || func_exit 1
   fi
   func_execute_command ${AUTOCONF} || func_exit 1
   func_execute_command ${AUTOHEADER} || func_exit 1
   func_execute_command ${AUTOMAKE} --add-missing --copy || func_exit 1
  ) || func_exit 1
  if test -n "$inctests" && ! $single_configure; then
    # Create autogenerated files.
    (cd "$testdir/$testsbase" || func_exit 1
     # Do not use "${AUTORECONF} --force --install", because it may invoke
     # autopoint, which brings in older versions of some of our .m4 files.
     if test -f ../$m4base/gettext.m4; then
       func_execute_command ${AUTOPOINT} --force || func_exit 1
       for f in ../$m4base/*.m4~; do
         if test -f $f; then
           mv -f $f `echo $f | sed -e 's,~$,,'` || func_exit 1
         fi
       done
     fi
     func_execute_command ${ACLOCAL} -I ../$m4base || func_exit 1
     if ! test -d ../build-aux; then
       func_execute_command mkdir ../build-aux
     fi
     func_execute_command ${AUTOCONF} || func_exit 1
     func_execute_command ${AUTOHEADER} || func_exit 1
     func_execute_command ${AUTOMAKE} --add-missing --copy || func_exit 1
    ) || func_exit 1
  fi
  # Need to run configure and make once, to create built files that are to be
  # distributed (such as parse-datetime.c).
  sed_remove_make_variables='s,[$]([A-Za-z0-9_]*),,g'
  # Extract the value of "CLEANFILES += ..." and "MOSTLYCLEANFILES += ...".
  cleaned_files=`sed -e "$sed_remove_backslash_newline" < "$testdir/$sourcebase/Makefile.am" \
                 | sed -n -e 's,^CLEANFILES[	 ]*+=\([^#]*\).*$,\1,p' -e 's,^MOSTLYCLEANFILES[	 ]*+=\([^#]*\).*$,\1,p'`
  cleaned_files=`for file in $cleaned_files; do echo " $file "; done`
  # Extract the value of "BUILT_SOURCES += ...". Remove variable references
  # such $(FOO_H) because they don't refer to distributed files.
  built_sources=`sed -e "$sed_remove_backslash_newline" < "$testdir/$sourcebase/Makefile.am" \
                 | sed -n -e 's,^BUILT_SOURCES[	 ]*+=\([^#]*\).*$,\1,p' \
                 | sed -e "$sed_remove_make_variables"`
  distributed_built_sources=`for file in $built_sources; do
                               case "$cleaned_files" in
                                 *" "$file" "*) ;;
                                 *) echo $file ;;
                               esac;
                             done`
  tests_distributed_built_sources=
  if test -n "$inctests"; then
    # Likewise for built files in the $testsbase directory.
    tests_cleaned_files=`sed -e "$sed_remove_backslash_newline" < "$testdir/$testsbase/Makefile.am" \
                         | sed -n -e 's,^CLEANFILES[	 ]*+=\([^#]*\).*$,\1,p' -e 's,^MOSTLYCLEANFILES[	 ]*+=\([^#]*\).*$,\1,p'`
    tests_cleaned_files=`for file in $tests_cleaned_files; do echo " $file "; done`
    tests_built_sources=`sed -e "$sed_remove_backslash_newline" < "$testdir/$testsbase/Makefile.am" \
                         | sed -n -e 's,^BUILT_SOURCES[	 ]*+=\([^#]*\).*$,\1,p' \
                         | sed -e "$sed_remove_make_variables"`
    tests_distributed_built_sources=`for file in $tests_built_sources; do
                                       case "$tests_cleaned_files" in
                                         *" "$file" "*) ;;
                                         *) echo $file ;;
                                       esac;
                                     done`
  fi
  if test -n "$distributed_built_sources" || test -n "$tests_distributed_built_sources"; then
    (cd "$testdir"
     ./configure || func_exit 1
       if test -n "$distributed_built_sources"; then
         cd "$sourcebase"
         echo 'built_sources: $(BUILT_SOURCES)' >> Makefile
         $MAKE AUTOCONF="${AUTOCONF}" AUTOHEADER="${AUTOHEADER}" ACLOCAL="${ACLOCAL}" AUTOMAKE="${AUTOMAKE}" AUTORECONF="${AUTORECONF}" AUTOPOINT="${AUTOPOINT}" LIBTOOLIZE="${LIBTOOLIZE}" \
               built_sources \
           || func_exit 1
         cd ..
       fi
       if test -n "$tests_distributed_built_sources"; then
         cd "$testsbase"
         echo 'built_sources: $(BUILT_SOURCES)' >> Makefile
         $MAKE AUTOCONF="${AUTOCONF}" AUTOHEADER="${AUTOHEADER}" ACLOCAL="${ACLOCAL}" AUTOMAKE="${AUTOMAKE}" AUTORECONF="${AUTORECONF}" AUTOPOINT="${AUTOPOINT}" LIBTOOLIZE="${LIBTOOLIZE}" \
               built_sources \
           || func_exit 1
         cd ..
       fi
     $MAKE AUTOCONF="${AUTOCONF}" AUTOHEADER="${AUTOHEADER}" ACLOCAL="${ACLOCAL}" AUTOMAKE="${AUTOMAKE}" AUTORECONF="${AUTORECONF}" AUTOPOINT="${AUTOPOINT}" LIBTOOLIZE="${LIBTOOLIZE}" \
           distclean \
       || func_exit 1
    ) || func_exit 1
  fi
}

# func_create_megatestdir megatestdir allmodules
# Input:
# - local_gnulib_dir  from --local-dir
# - modcache        true or false, from --cache-modules/--no-cache-modules
# - auxdir          directory relative to destdir where to place build aux files
func_create_megatestdir ()
{
  megatestdir="$1"
  allmodules="$2"
  if test -z "$allmodules"; then
    allmodules=`func_all_modules`
  fi

  megasubdirs=
  # First, all modules one by one.
  for onemodule in $allmodules; do
    func_create_testdir "$megatestdir/$onemodule" $onemodule
    func_append megasubdirs "$onemodule "
  done
  # Then, all modules all together.
  # Except config-h, which breaks all modules which use HAVE_CONFIG_H.
  allmodules=`for m in $allmodules; do if test $m != config-h; then echo $m; fi; done`
  func_create_testdir "$megatestdir/ALL" "$allmodules"
  func_append megasubdirs "ALL"

  # Create autobuild.
  cvsdate=`if test -f "$gnulib_dir/CVS/Entries"; then \
             vc_witness="$gnulib_dir/CVS/Entries"; \
           else \
             vc_witness="$gnulib_dir/.git/refs/heads/master"; \
           fi; \
           sh "$gnulib_dir/build-aux/mdate-sh" "$vc_witness" \
             | sed -e 's,January,01,'   -e 's,Jan,01,' \
                   -e 's,February,02,'  -e 's,Feb,02,' \
                   -e 's,March,03,'     -e 's,Mar,03,' \
                   -e 's,April,04,'     -e 's,Apr,04,' \
                   -e 's,May,05,'                      \
                   -e 's,June,06,'      -e 's,Jun,06,' \
                   -e 's,July,07,'      -e 's,Jul,07,' \
                   -e 's,August,08,'    -e 's,Aug,08,' \
                   -e 's,September,09,' -e 's,Sep,09,' \
                   -e 's,October,10,'   -e 's,Oct,10,' \
                   -e 's,November,11,'  -e 's,Nov,11,' \
                   -e 's,December,12,'  -e 's,Dec,12,' \
                   -e 's,^,00,' -e 's,^[0-9]*\([0-9][0-9] \),\1,' \
                   -e 's,^\([0-9]*\) \([0-9]*\) \([0-9]*\),\3\2\1,'`
  (echo '#!/bin/sh'
   echo "CVSDATE=$cvsdate"
   echo ": \${MAKE=make}"
   echo "test -d logs || mkdir logs"
   echo "for module in $megasubdirs; do"
   echo "  echo \"Working on module \$module...\""
   echo "  safemodule=\`echo \$module | sed -e 's|/|-|g'\`"
   echo "  (echo \"To: gnulib@autobuild.josefsson.org\""
   echo "   echo"
   echo "   set -x"
   echo "   : autobuild project... \$module"
   echo "   : autobuild revision... cvs-\$CVSDATE-000000"
   echo "   : autobuild timestamp... \`date \"+%Y%m%d-%H%M%S\"\`"
   echo "   : autobuild hostname... \`hostname\`"
   echo "   cd \$module && ./configure \$CONFIGURE_OPTIONS && \$MAKE && \$MAKE check && \$MAKE distclean"
   echo "   echo rc=\$?"
   echo "  ) 2>&1 | { if test -n \"\$AUTOBUILD_SUBST\"; then sed -e \"\$AUTOBUILD_SUBST\"; else cat; fi; } > logs/\$safemodule"
   echo "done"
  ) > "$megatestdir/do-autobuild"
  chmod a+x "$megatestdir/do-autobuild"

  # Create Makefile.am.
  (echo "## Process this file with automake to produce Makefile.in."
   echo
   echo "AUTOMAKE_OPTIONS = 1.5 foreign"
   echo
   echo "SUBDIRS = $megasubdirs"
   echo
   echo "EXTRA_DIST = do-autobuild"
  ) > "$megatestdir/Makefile.am"

  # Create configure.ac.
  (echo "# Process this file with autoconf to produce a configure script."
   echo "AC_INIT([dummy], [0])"
   if test "$auxdir" != "."; then
     echo "AC_CONFIG_AUX_DIR([$auxdir])"
   fi
   echo "AM_INIT_AUTOMAKE"
   echo
   echo "AC_PROG_MAKE_SET"
   echo
   echo "AC_CONFIG_SUBDIRS([$megasubdirs])"
   echo "AC_CONFIG_FILES([Makefile])"
   echo "AC_OUTPUT"
  ) > "$megatestdir/configure.ac"

  # Create autogenerated files.
  (cd "$megatestdir"
   # Do not use "${AUTORECONF} --install", because autoreconf operates
   # recursively, but the subdirectories are already finished, therefore
   # calling autoreconf here would only waste lots of CPU time.
   func_execute_command ${ACLOCAL} || func_exit 1
   func_execute_command mkdir build-aux
   func_execute_command ${AUTOCONF} || func_exit 1
   func_execute_command ${AUTOMAKE} --add-missing --copy || func_exit 1
  ) || func_exit 1
}

case $mode in
  "" )
    func_fatal_error "no mode specified" ;;

  list )
    func_all_modules
    ;;

  find )
    # sed expression that converts a literal to a basic regular expression.
    # Needs to handle . [ \ * ^ $.
    sed_literal_to_basic_regex='s/\\/\\\\/g
s/\[/\\[/g
s/\^/\\^/g
s/\([.*$]\)/[\1]/g'
    for filename
    do
      if test -f "$gnulib_dir/$filename" \
         || { test -n "$local_gnulib_dir" && test -f "$local_gnulib_dir/$filename"; }; then
        filename_anywhere_regex=`echo "$filename" | sed -e "$sed_literal_to_basic_regex"`
        filename_line_regex='^'"$filename_anywhere_regex"'$'
        module_candidates=`
          {
            (cd "$gnulib_dir" && find modules -type f -print | xargs -n 100 grep -l "$filename_line_regex" /dev/null | sed -e 's,^modules/,,')
            if test -n "$local_gnulib_dir" && test -d "$local_gnulib_dir/modules"; then
              (cd "$local_gnulib_dir" && find modules -type f -print | xargs -n 100 grep -l "$filename_anywhere_regex" /dev/null | sed -e 's,^modules/,,' -e 's,\.diff$,,')
            fi
          } \
            | func_sanitize_modulelist \
            | LC_ALL=C sort -u
          `
        for module in $module_candidates; do
          if func_get_filelist $module | grep "$filename_line_regex" > /dev/null; then
            echo $module
          fi
        done
      else
        func_warning "file $filename does not exist"
      fi
    done
    ;;

  import | add-import | remove-import | update )

    # Where to import.
    if test -z "$destdir"; then
      destdir=.
    fi
    test -d "$destdir" \
      || func_fatal_error "destination directory does not exist: $destdir"

    # Prefer configure.ac to configure.in.
    if test -f "$destdir"/configure.ac; then
      configure_ac="$destdir/configure.ac"
    else
      if test -f "$destdir"/configure.in; then
        configure_ac="$destdir/configure.in"
      else
        func_fatal_error "cannot find $destdir/configure.ac - make sure you run gnulib-tool from within your package's directory"
      fi
    fi

    # Analyze configure.ac.
    guessed_auxdir="."
    guessed_libtool=false
    my_sed_traces='
      s,#.*$,,
      s,^dnl .*$,,
      s, dnl .*$,,
      /AC_CONFIG_AUX_DIR/ {
        s,^.*AC_CONFIG_AUX_DIR([[ ]*\([^]"$`\\)]*\).*$,guessed_auxdir="\1",p
      }
      /A[CM]_PROG_LIBTOOL/ {
        s,^.*$,guessed_libtool=true,p
      }'
    eval `sed -n -e "$my_sed_traces" < "$configure_ac"`

    if test -z "$auxdir"; then
      auxdir="$guessed_auxdir"
    fi

    # Determine where to apply func_import.
    if test "$mode" = import; then
      # Apply func_import to a particular gnulib directory.
      # The command line contains the complete specification; don't look at
      # the contents of gnulib-cache.m4.
      test -n "$supplied_libname" || supplied_libname=true
      test -n "$sourcebase" || sourcebase="lib"
      test -n "$m4base" || m4base="m4"
      test -n "$docbase" || docbase="doc"
      test -n "$testsbase" || testsbase="tests"
      test -n "$macro_prefix" || macro_prefix="gl"
      func_import "$*"
    else
      if test -n "$m4base"; then
        # Apply func_import to a particular gnulib directory.
        # Any number of additional modules can be given.
        if test ! -f "$destdir/$m4base"/gnulib-cache.m4; then
          # First use of gnulib in the given m4base.
          test -n "$supplied_libname" || supplied_libname=true
          test -n "$sourcebase" || sourcebase="lib"
          test -n "$docbase" || docbase="doc"
          test -n "$testsbase" || testsbase="tests"
          test -n "$macro_prefix" || macro_prefix="gl"
        fi
        func_import "$*"
      else
        # Apply func_import to all gnulib directories.
        # To get this list of directories, look at Makefile.am. (Not at
        # configure, because it may be omitted from version control. Also,
        # don't run "find $destdir -name gnulib-cache.m4", as it might be
        # too expensive.)
        m4dirs=
        m4dirs_count=0
        if test -f "$destdir"/Makefile.am; then
          aclocal_amflags=`sed -n -e 's/^ACLOCAL_AMFLAGS[	 ]*=\(.*\)$/\1/p' "$destdir"/Makefile.am`
          m4dir_is_next=
          for arg in $aclocal_amflags; do
            if test -n "$m4dir_is_next"; then
              # Ignore absolute directory pathnames, like /usr/local/share/aclocal.
              case "$arg" in
                /*) ;;
                *)
                  if test -f "$destdir/$arg"/gnulib-cache.m4; then
                    func_append m4dirs " $arg"
                    m4dirs_count=`expr $m4dirs_count + 1`
                  fi
                  ;;
              esac
              m4dir_is_next=
            else
              if test "X$arg" = "X-I"; then
                m4dir_is_next=yes
              else
                m4dir_is_next=
              fi
            fi
          done
        else
          # No Makefile.am! Oh well. Look at the last generated aclocal.m4.
          if test -f "$destdir"/aclocal.m4; then
            sedexpr1='s,^m4_include(\[\(.*\)])$,\1,p'
            sedexpr2='s,^[^/]*$,.,'
            sedexpr3='s,/[^/]*$,,'
            m4dirs=`sed -n -e "$sedexpr1" aclocal.m4 | sed -e "$sedexpr2" -e "$sedexpr3" | LC_ALL=C sort -u`
            m4dirs=`for arg in $m4dirs; do if test -f "$destdir/$arg"/gnulib-cache.m4; then echo $arg; fi; done`
            m4dirs_count=`for arg in $m4dirs; do echo "$arg"; done | wc -l`
          fi
        fi
        if test $m4dirs_count = 0; then
          # First use of gnulib in a package.
          # Any number of additional modules can be given.
          test -n "$supplied_libname" || supplied_libname=true
          test -n "$sourcebase" || sourcebase="lib"
          m4base="m4"
          test -n "$docbase" || docbase="doc"
          test -n "$testsbase" || testsbase="tests"
          test -n "$macro_prefix" || macro_prefix="gl"
          func_import "$*"
        else
          if test $m4dirs_count = 1; then
            # There's only one use of gnulib here. Assume the user means it.
            # Any number of additional modules can be given.
            for m4base in $m4dirs; do
              func_import "$*"
            done
          else
            # Ambiguous - guess what the user meant.
            if test $# = 0; then
              # No further arguments. Guess the user wants to update all of them.
              for m4base in $m4dirs; do
                # Perform func_import in a subshell, so that variable values
                # such as
                #   local_gnulib_dir, incobsolete, inc_cxx_tests,
                #   inc_longrunning_tests, inc_privileged_tests,
                #   inc_unportable_tests, inc_all_tests, avoidlist, sourcebase,
                #   m4base, pobase, docbase, testsbase, inctests, libname, lgpl,
                #   makefile_name, libtool, macro_prefix, po_domain,
                #   witness_c_macro, vc_files
                # don't propagate from one directory to another.
                (func_import) || func_exit 1
              done
            else
              # Really ambiguous.
              func_fatal_error "Ambiguity: to which directory should the modules be added? Please specify at least --m4-base=..."
            fi
          fi
        fi
      fi
    fi
    ;;

  create-testdir )
    if test -z "$destdir"; then
      func_fatal_error "please specify --dir option"
    fi
    mkdir "$destdir"
    test -d "$destdir" \
      || func_fatal_error "could not create destination directory"
    test -n "$auxdir" || auxdir="build-aux"
    func_create_testdir "$destdir" "$*"
    ;;

  create-megatestdir )
    if test -z "$destdir"; then
      func_fatal_error "please specify --dir option"
    fi
    mkdir "$destdir" || func_fatal_error "could not create destination directory"
    test -n "$auxdir" || auxdir="build-aux"
    func_create_megatestdir "$destdir" "$*"
    ;;

  test )
    test -n "$destdir" || destdir=testdir$$
    mkdir "$destdir" || func_fatal_error "could not create destination directory"
    test -n "$auxdir" || auxdir="build-aux"
    func_create_testdir "$destdir" "$*"
    cd "$destdir"
      mkdir build
      cd build
        ../configure || func_exit 1
        $MAKE || func_exit 1
        $MAKE check || func_exit 1
        $MAKE distclean || func_exit 1
        remaining=`find . -type f -print`
        if test -n "$remaining"; then
          echo "Remaining files:" $remaining 1>&2
          echo "gnulib-tool: *** Stop." 1>&2
          func_exit 1
        fi
      cd ..
    cd ..
    rm -rf "$destdir"
    ;;

  megatest )
    test -n "$destdir" || destdir=testdir$$
    mkdir "$destdir" || func_fatal_error "could not create destination directory"
    test -n "$auxdir" || auxdir="build-aux"
    func_create_megatestdir "$destdir" "$*"
    cd "$destdir"
      mkdir build
      cd build
        ../configure
        $MAKE
        $MAKE check
        $MAKE distclean
        remaining=`find . -type f -print`
        if test -n "$remaining"; then
          echo "Remaining files:" $remaining 1>&2
          echo "gnulib-tool: *** Stop." 1>&2
          func_exit 1
        fi
      cd ..
    cd ..
    rm -rf "$destdir"
    ;;

  extract-description )
    for module
    do
      func_verify_module
      if test -n "$module"; then
        func_get_description "$module"
      fi
    done
    ;;

  extract-comment )
    for module
    do
      func_verify_module
      if test -n "$module"; then
        func_get_comment "$module"
      fi
    done
    ;;

  extract-status )
    for module
    do
      func_verify_module
      if test -n "$module"; then
        func_get_status "$module"
      fi
    done
    ;;

  extract-notice )
    for module
    do
      func_verify_module
      if test -n "$module"; then
        func_get_notice "$module"
      fi
    done
    ;;

  extract-applicability )
    for module
    do
      func_verify_module
      if test -n "$module"; then
        func_get_applicability "$module"
      fi
    done
    ;;

  extract-filelist )
    for module
    do
      func_verify_module
      if test -n "$module"; then
        func_get_filelist "$module"
      fi
    done
    ;;

  extract-dependencies )
    if test -n "$avoidlist"; then
      func_fatal_error "cannot combine --avoid and --extract-dependencies"
    fi
    for module
    do
      func_verify_module
      if test -n "$module"; then
        func_get_dependencies "$module"
      fi
    done
    ;;

  extract-autoconf-snippet )
    for module
    do
      func_verify_module
      if test -n "$module"; then
        func_get_autoconf_snippet "$module"
      fi
    done
    ;;

  extract-automake-snippet )
    for module
    do
      func_verify_module
      if test -n "$module"; then
        func_get_automake_snippet "$module"
      fi
    done
    ;;

  extract-include-directive )
    for module
    do
      func_verify_module
      if test -n "$module"; then
        func_get_include_directive "$module"
      fi
    done
    ;;

  extract-link-directive )
    for module
    do
      func_verify_module
      if test -n "$module"; then
        func_get_link_directive "$module"
      fi
    done
    ;;

  extract-license )
    for module
    do
      func_verify_module
      if test -n "$module"; then
        func_get_license "$module"
      fi
    done
    ;;

  extract-maintainer )
    for module
    do
      func_verify_module
      if test -n "$module"; then
        func_get_maintainer "$module"
      fi
    done
    ;;

  extract-tests-module )
    for module
    do
      func_verify_module
      if test -n "$module"; then
        func_get_tests_module "$module"
      fi
    done
    ;;

  copy-file )
    # Verify the number of arguments.
    if test $# -lt 1 || test $# -gt 2; then
      func_fatal_error "invalid number of arguments for --$mode"
    fi

    # The first argument is the file to be copied.
    f="$1"
    # Verify the file exists.
    func_lookup_file "$f"

    # The second argument is the destination; either a directory ot a file.
    # It defaults to the current directory.
    dest="$2"
    test -n "$dest" || dest='.'
    test -n "$sourcebase" || sourcebase="lib"
    test -n "$m4base" || m4base="m4"
    test -n "$docbase" || docbase="doc"
    test -n "$testsbase" || testsbase="tests"
    test -n "$auxdir" || auxdir="build-aux"
    rewritten='%REWRITTEN%'
    sed_rewrite_files="\
      s,^build-aux/,$rewritten$auxdir/,
      s,^doc/,$rewritten$docbase/,
      s,^lib/,$rewritten$sourcebase/,
      s,^m4/,$rewritten$m4base/,
      s,^tests/,$rewritten$testsbase/,
      s,^top/,$rewritten,
      s,^$rewritten,,"
    if test -d "$dest"; then
      destdir="$dest"
      g=`echo "$f" | sed -e "$sed_rewrite_files"`
    else
      destdir=`dirname "$dest"`
      g=`basename "$dest"`
    fi

    # Create the directory for destfile.
    d=`dirname "$destdir/$g"`
    if $doit; then
      if test -n "$d" && test ! -d "$d"; then
        mkdir -p "$d" || func_fatal_error "failed"
      fi
    fi
    # Copy the file.
    func_dest_tmpfilename "$g"
    cp "$lookedup_file" "$tmpfile" || func_fatal_error "failed"
    already_present=true
    if test -f "$destdir/$g"; then
      # The file already exists.
      func_update_file
    else
      # Install the file.
      # Don't protest if the file should be there but isn't: it happens
      # frequently that developers don't put autogenerated files under version
      # control.
      func_add_file
    fi
    rm -f "$tmpfile"
    ;;

  * )
    func_fatal_error "unknown operation mode --$mode" ;;
esac

rm -rf "$tmp"
# Undo the effect of the previous 'trap' command. Some shellology:
# We cannot use "trap - 0 1 2 3 13 15", because Solaris sh would attempt to
# execute the command "-". "trap '' ..." is fine only for signal 0 (= normal
# exit); for the others we need to call 'exit' explicitly. The value of $? is
# 128 + signal number and is set before the trap-registered command is run.
trap '' 0
trap 'func_exit $?' 1 2 3 13 15

exit 0

# Local Variables:
# indent-tabs-mode: nil
# whitespace-check-buffer-indent: nil
# End:
