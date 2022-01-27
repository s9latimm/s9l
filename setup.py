#!/usr/bin/python3

# https://github.com/s9latimm/s9l
# ------------------------------------------------------------------------------
#
# ███████╗  █████╗  ██╗
# ██╔════╝ ██╔══██╗ ██║
# ███████╗ ╚██████║ ██║
# ╚════██║  ╚═══██║ ██║
# ███████║  █████╔╝ ███████╗
# ╚══════╝  ╚════╝  ╚══════╝
#
# Copyright (c) 2022 Lauritz Timm <https://github.com/s9latimm>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
#  of this software and associated documentation files (the "Software"), to deal
#  in the Software without restriction, including without limitation the rights
#  to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#  copies of the Software, and to permit persons to whom the Software is
#  furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
#  all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#  OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#  SOFTWARE.
# ------------------------------------------------------------------------------

# -*- coding: utf-8 -*-

import typing
from setuptools import setup

__author__: str = 'Lauritz Timm <https://github.com/s9latimm>'

with open('VERSION', 'r', encoding='utf-8') as file:
    __version__: str = file.read().strip()

with open('README.md', 'r', encoding='utf-8') as file:
    README: str = file.read()

with open('requirements.txt', 'r', encoding='utf-8') as file:
    REQUIREMENTS: typing.List[str] = [
        requirement.strip() for requirement in file.readlines()
    ]

setup(name='s9l',
      version=__version__,
      description='s9l',
      long_description=README,
      long_description_content_type='text/markdown',
      url='https://github.com/s9latimm/s9l',
      author=__author__,
      author_email='s9latimm@stud.uni-saarland.de',
      license='MIT',
      python_requires='>=3.8.0',
      install_requires=REQUIREMENTS,
      packages=['s9l'],
      include_package_data=True,
      package_data={
          's9l': [],
      })
