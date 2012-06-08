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
from pygnulib import utilities
from pygnulib import testing
from pprint import pprint
APP = constants.APP


################################################################################
# Define global constants
################################################################################
if __name__ == '__main__':
  gnulibimport = utilities.GNULibImport(1, m4base='ltdl/m4')
  pprint(gnulibimport.cache)
  
  