#!/usr/bin/python
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


from __future__ import unicode_literals
################################################################################
# Define global imports
################################################################################
from pygnulib import constants
from pygnulib import classes
from pygnulib import testing
from pprint import pprint
APP = constants.APP


################################################################################
# Define global constants
################################################################################
if __name__ == '__main__':
  import time
  import codecs
  with codecs.open('modules.txt', 'rb', 'UTF-8') as file:
    modules = file.read().split()
  localdir = './pygnulib/testfiles'
  modulesystem = classes.GLModuleSystem(localdir=localdir, modcache=False)
  # NOTE: It seems we don't need modcache argument since we are all agree that
  # modules will now use caching by default. Try it, it allows to access the
  # methods of GLModule at least twice faster!
  # NOTE:this testing doesn't tests situation when we patch a lot of files
  # from localdir. There is only one file, pygnulib module.
  modules = [modulesystem.find(module) for module in modules]
  
  # First test: print all informtion about module #275
  print('=' *80)
  print('FIRST TEST: SHOW INFORMATION')
  print('=' *80)
  module = modules[275]
  print('Name:\t\t%s'         % repr(module.getName()))
  print('Patched:\t%s'        % repr(module.isPatched()))
  print('Tests:\t\t%s'        % repr(module.isTests()))
  print('Description:\t%s'    % repr(module.getDescription()))
  print('Comment:\t%s'        % repr(module.getComment()))
  print('Status:\t\t%s'       % repr(module.getStatus()))
  print('Notice:\t\t%s'       % repr(module.getNotice()))
  print('Applicability:\t%s'  % repr(module.getApplicability()))
  print('Files:\t\t%s'        % repr(module.getFiles()))
  print('Dependencies:\t%s'   % repr(module.getDependencies()))
  print('Autoconf_Early:\t%s' % repr(module.getAutoconf_Early()))
  print('Autoconf:\t%s'       % repr(module.getAutoconf()))
  print('Include:\t%s'        % repr(module.getInclude()))
  print('Link:\t\t%s'         % repr(module.getLink()))
  print('Maintainer:\t%s'     % repr(module.getMaintainer()))
  print('')
  
  # Second test: check how much time it takes to get values for every module
  # for the first time (we want to compare it with cache)
  print('=' *80)
  print('SECOND TEST: CREATION OF THE CACHE')
  print('=' *80)
  start_time = time.time()
  for module in modules:
    module.getName()
    module.getDescription()
    module.getStatus()
    module.getAutoconf_Early()
    module.getAutoconf()
    module.getFiles()
    module.getDependencies()
    module.getInclude()
    module.getLink()
    module.getMaintainer()
  finish_time = time.time() -start_time
  print('TIME WAS NEEDED: %s' % finish_time)
  print('')
  
  # Third test: check how much time it takes to get cached values for every
  # module when we run cycle for the second time
  start_time = time.time()
  print('=' *80)
  print('THIRD TEST: ACCESS TO THE CACHE')
  print('=' *80)
  start_time = time.time()
  for module in modules:
    module.getName()
    module.getDescription()
    module.getStatus()
    module.getAutoconf_Early()
    module.getAutoconf()
    module.getFiles()
    module.getDependencies()
    module.getInclude()
    module.getLink()
    module.getMaintainer()
  finish_time = time.time() -start_time
  print('TIME WAS NEEDED: %s' % finish_time)
  print('')