#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2018-2021 Clémence Frioux & Arnaud Belcour - Inria Dyliss - Pleiade
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Lesser General Public License for more details.

# You should have received a copy of the GNU Lesser General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>

from setuptools import setup
import miscoto

setup(
    name             = 'Miscoto',
    version          = miscoto.__version__,
    url              = 'https://github.com/cfrioux/miscoto',
    license          = 'GPLv3+',
    description      = 'Microbiome Screening and COmmunity selection using TOpology',
    long_description = 'MiSCoTo is a Python3 tool to explore microbiomes and select minimal communities within them. It uses Answer Set Programming (ASP) to optimize community selection. \
Inputs: metabolic models, seeds (growth medium) and metabolic targets. \
Computations can be performed with a set of symbionts or a set of symbionts and a host. In the latter case, targets will be produced by the host, whereas in the former they will be produced by any member of the microbiome. \
More information on usage and troubleshooting on Github: https://github.com/cfrioux/miscoto',
    author           = 'Clemence Frioux',
    author_email     = 'clemence.frioux@inria.fr',
    classifiers      =[
                            'Programming Language :: Python :: 3.6',
                            'Programming Language :: Python :: 3.6',
                            'Programming Language :: Python :: 3.7',
                            'Programming Language :: Python :: 3.8',
                            'Operating System :: MacOS :: MacOS X',
                            'Operating System :: Unix',
                        ],
    packages         = ['miscoto'],
    package_dir      = {'miscoto' : 'miscoto'},
    package_data     = {'miscoto' : ['encodings/*.lp']},
    #scripts          = ['miscoto/miscoto_instance.py','miscoto/miscoto_mincom.py','miscoto/miscoto_scopes.py'],
    entry_points     = {'console_scripts': ['miscoto = miscoto.__main__:main']},
    install_requires = ['clyngor_with_clingo', 'clyngor']
)
