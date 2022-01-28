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
    'ANSI_BG_BLACK',
    'ANSI_BG_BLUE',
    'ANSI_BG_CYAN',
    'ANSI_BG_GREEN',
    'ANSI_BG_MAGENTA',
    'ANSI_BG_RED',
    'ANSI_BG_WHITE',
    'ANSI_BG_YELLOW',
    'ANSI_FG_BLACK',
    'ANSI_FG_BLUE',
    'ANSI_FG_BOLD_BLACK',
    'ANSI_FG_BOLD_BLUE',
    'ANSI_FG_BOLD_CYAN',
    'ANSI_FG_BOLD_GREEN',
    'ANSI_FG_BOLD_MAGENTA',
    'ANSI_FG_BOLD_RED',
    'ANSI_FG_BOLD_WHITE',
    'ANSI_FG_BOLD_YELLOW',
    'ANSI_FG_CYAN',
    'ANSI_FG_GREEN',
    'ANSI_FG_MAGENTA',
    'ANSI_FG_RED',
    'ANSI_FG_WHITE',
    'ANSI_FG_YELLOW',
    'ANSI_LOGGER',
    'ANSI_RESET',
]

import logging
import typing

ANSI_RESET: str = '\x1b[0m'

ANSI_FG_BLACK: str = '\x1b[30m'
ANSI_FG_RED: str = '\x1b[31m'
ANSI_FG_GREEN: str = '\x1b[32m'
ANSI_FG_YELLOW: str = '\x1b[33m'
ANSI_FG_BLUE: str = '\x1b[34m'
ANSI_FG_MAGENTA: str = '\x1b[35m'
ANSI_FG_CYAN: str = '\x1b[36m'
ANSI_FG_WHITE: str = '\x1b[37m'

ANSI_FG_BOLD_BLACK: str = '\x1b[30;1m'
ANSI_FG_BOLD_RED: str = '\x1b[31;1m'
ANSI_FG_BOLD_GREEN: str = '\x1b[32;1m'
ANSI_FG_BOLD_YELLOW: str = '\x1b[33;1m'
ANSI_FG_BOLD_BLUE: str = '\x1b[34;1m'
ANSI_FG_BOLD_MAGENTA: str = '\x1b[35;1m'
ANSI_FG_BOLD_CYAN: str = '\x1b[36;1m'
ANSI_FG_BOLD_WHITE: str = '\x1b[37;1m'

ANSI_BG_BLACK: str = '\x1b[40m'
ANSI_BG_RED: str = '\x1b[41m'
ANSI_BG_GREEN: str = '\x1b[42m'
ANSI_BG_YELLOW: str = '\x1b[43m'
ANSI_BG_BLUE: str = '\x1b[44m'
ANSI_BG_MAGENTA: str = '\x1b[45m'
ANSI_BG_CYAN: str = '\x1b[46m'
ANSI_BG_WHITE: str = '\x1b[47m'


class _AnsiFormatter(logging.Formatter):

    __FORMAT: str = '[%(levelname)s]%(asctime)s %(name)s: %(message)s'
    __DATEFORMAT: str = '[%Y-%m-%d][%H:%M:%S]'

    __COLORS: typing.Dict[int, str] = {
        logging.DEBUG: ANSI_FG_CYAN,
        logging.INFO: ANSI_FG_GREEN,
        logging.WARNING: ANSI_FG_YELLOW,
        logging.ERROR: ANSI_FG_RED,
        logging.CRITICAL: ANSI_FG_RED + ANSI_BG_WHITE,
    }

    def format(self, record: logging.LogRecord) -> str:
        return logging.Formatter(fmt=self.__COLORS.get(record.levelno) +
                                 self.__FORMAT + ANSI_RESET,
                                 datefmt=self.__DATEFORMAT).format(record)


ANSI_LOGGER: logging.StreamHandler = logging.StreamHandler()
ANSI_LOGGER.setFormatter(_AnsiFormatter())
