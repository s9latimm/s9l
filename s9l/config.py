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

__all__ = [
    'DATABASE_PATH',
    'DEBUG',
    'ETX',
    'ROOT_PATH',
    'STX',
]

import pathlib

DEBUG: bool = False

ROOT_PATH: str = f'{pathlib.Path(__file__).parent.parent.absolute()}'
DATABASE_PATH: str = f'{ROOT_PATH}/resources/sqlite.db'

STX: str = '\x02'
ETX: str = '\x03'
