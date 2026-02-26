#!/usr/bin/env python3
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

from setuptools import setup
import re
from pathlib import Path
import os

def get_version():
    v = os.environ.get("SHINEVERSION")
    if v:
        return v
    init_py = Path(__file__).parent / "lib" / "Shine" / "__init__.py"
    m = re.search(r'^public_version\s*=\s*"([^"]+)"', init_py.read_text(), re.M)
    if not m:
        raise RuntimeError("Cannot determine version")
    return m.group(1)

setup(name='shine',
      version=get_version(),
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
                  ('/usr/share/vim/vim70/syntax', ['doc/extras/vim/syntax/shine.vim']),
                  ('/usr/share/vim/vim70/syntax', ['doc/extras/vim/syntax/shinefs.vim']),
                  ('/usr/share/vim/vim70/ftdetect', ['doc/extras/vim/ftdetect/shine.vim'])]
     )

