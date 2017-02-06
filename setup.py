#!/usr/bin/env python
#
# Copyright (C) 2007-2013 CEA
#
# This file is part of shine
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#

from distutils.core import setup
import os

setup(name='shine',
      version=os.environ['SHINEVERSION'],
      license='GPL',
      description='Lustre administration utility',
      author='Stephane Thiell',
      author_email='stephane.thiell@cea.fr',
      url='http://lustre-shine.sourceforge.net/',
      package_dir={'': 'lib'},
      packages=['Shine',
               'Shine.CLI',
               'Shine.Commands',
               'Shine.Commands.Base',
               'Shine.Configuration',
               'Shine.Configuration.Backend',
               'Shine.HA',
               'Shine.HA.plugins',
               'Shine.Lustre',
               'Shine.Lustre.Actions'],
      data_files=[('/usr/sbin', ['scripts/shine']),
                  ('/var/cache/shine/conf', ['conf/cache/README']),
                  ('/usr/share/vim/vim70/syntax', ['doc/extras/vim/syntax/shine.vim']),
                  ('/usr/share/vim/vim70/syntax', ['doc/extras/vim/syntax/shinefs.vim']),
                  ('/usr/share/vim/vim70/ftdetect', ['doc/extras/vim/ftdetect/shine.vim']),
                  ('/usr/share/shine', ['scripts/shine.init.redhat'])]
     )

