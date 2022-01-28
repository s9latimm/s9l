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

# pylint: disable=wildcard-import,unused-wildcard-import

from s9l.config import *
from s9l.database import *


def test_database() -> None:
    database = Database(DATABASE_PATH, mode='memory')
    database['test'] = [
        ('id', PRIMARY_KEY(INTEGER)),
        ('content', UNIQUE(NOT_NULL(ARRAY(TUPLE(TEXT, ARRAY(TEXT)))))),
    ]
    expected = {
        'id': 1,
        'content': [['first', ['1']], ['second', ['2', '42']]],
    }
    database['test'].insert(expected)

    actual = database['test'].select()
    assert actual

    assert expected['content'] == actual[0].content
    assert expected['id'] == actual[0].id
