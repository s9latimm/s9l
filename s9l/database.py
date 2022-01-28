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

from __future__ import annotations

__all__ = [
    'ARRAY',
    'BLOB',
    'BOOL',
    'DATE',
    'INTEGER',
    'NOT_NULL',
    'PRIMARY_KEY',
    'TEXT',
    'TUPLE',
    'UNIQUE',
    'Database',
]

import logging
import sqlite3
import threading
import typing

from s9l import config

_LOGGER: logging.Logger = logging.getLogger('s9l.database')


class Database:
    __instance: typing.Optional[_Database] = None

    def __init__(self, uri: str) -> None:
        if not Database.__instance:
            Database.__instance = self._Database(uri)
        elif uri != Database.__instance.uri:
            Database.__instance.__del__()
            Database.__instance = self._Database(uri)
        else:
            _LOGGER.info('reuse instance \'%s\'', uri)

    def __getattr__(self, name: str) -> typing.Any:
        return getattr(self.__instance, name)

    def __getitem__(self, identifier: str) -> typing.Optional[_Table]:
        return Database.__instance.__getitem__(identifier)

    def __setitem__(
            self, identifier: str,
            columns: typing.List[typing.Tuple[str, Database.Column]]) -> None:
        return Database.__instance.__setitem__(identifier, columns)

    class _Database:

        def __init__(self, uri: str) -> None:
            _LOGGER.debug('connect \'%s\'', uri)
            self.__uri: str = uri
            self.__connection: sqlite3.Connection = sqlite3.connect(
                f'file://{self.__uri}?mode=rw', uri=True)
            self.__lock: threading.Lock = threading.Lock()
            self.__tables: typing.Dict[str, Database._Table] = {
                identifier: Database._Table(self, identifier, columns)
                for identifier, columns in [
                    self.execute(f'PRAGMA table_info({k});',
                                 post=lambda i: (k, [(j[1], _DataType(j[2]))
                                                     for j in i]))
                    for k in self.execute(
                        'SELECT name FROM sqlite_master WHERE type = \'table\';',
                        post=lambda i: i[0] if i else [])
                ]
            }

        def __del__(self) -> None:
            _LOGGER.debug('close \'%s\'', self.__uri)
            self.__connection.close()

        def __getitem__(self,
                        identifier: str) -> typing.Optional[Database._Table]:
            if identifier in self.__tables.keys():
                return self.__tables[identifier]
            _LOGGER.warning('missing table \'%s\'', identifier)
            return None

        def __setitem__(
                self, identifier: str,
                columns: typing.List[typing.Tuple[str,
                                                  Database.Column]]) -> None:
            if identifier in self.__tables.keys():
                _LOGGER.warning('replace table \'%s\'', identifier)
                self.drop(self.__tables[identifier])
            self.__tables[identifier] = Database._Table(self, identifier,
                                                        columns).create()

        @property
        def uri(self):
            return self.__uri

        def drop(self, table: Database._Table) -> None:
            self.commit(f'DROP TABLE IF EXISTS {table.identifier};')
            del self.__tables[table.identifier]

        __T = typing.TypeVar('__T')

        def execute(
            self,
            sql: str,
            post: typing.Callable[[typing.List[str]],
                                  __T] = lambda i: i) -> __T:
            with self.__lock:
                _LOGGER.info(
                    'execute \'%s\'',
                    sql.replace(config.STX,
                                '[STX]').replace(config.ETX, '[ETX]'))
                return post(list(self.__connection.execute(sql)))

        def commit(self, sql: str) -> None:
            with self.__lock:
                _LOGGER.info(
                    'execute \'%s\'',
                    sql.replace(config.STX,
                                '[STX]').replace(config.ETX, '[ETX]'))
                self.__connection.execute(sql)
                self.__connection.commit()

    class _Table:

        IGNORED = {'modified'}

        def __init__(
                self, database: Database._Database, identifier: str,
                columns: typing.List[typing.Tuple[str,
                                                  Database.Column]]) -> None:
            self.__database: Database._Database = database
            self.__identifier: str = identifier
            self.__columns: typing.List[typing.Tuple[str, Database.Column]] = [
                column for column in columns if identifier not in self.IGNORED
            ]

        @property
        def identifier(self) -> str:
            return self.__identifier

        def __repr__(self) -> str:
            csv = ', '.join([column[0] for column in self.__columns])
            return f'Table(identifier: \'{self.__identifier}\', columns: [{csv}])'

        def create(self) -> Database._Table:
            csv = ', '.join([
                f'{column[0]} {column[1].typename}' for column in self.__columns
            ])
            self.__database.commit(
                f'CREATE TABLE IF NOT EXISTS {self.__identifier}({csv}, modified date);'
            )
            return self

        def insert(self, values: typing.Dict[str, typing.Any]) -> None:
            # if (self.select(where=' AND '.join([
            #         f'{column.identifier}=\'{values[column.identifier]}\''
            #         for column in self.__columns
            #         if column.identifier in values.keys()
            # ]))):
            #     _LOGGER.warning('duplicate entry %s', values)
            #     return

            for column in values.keys() - {
                    column[0] for column in self.__columns
            }:
                _LOGGER.warning('missing column \'%s\'', column)
            for column in {column[0] for column in self.__columns
                          } - values.keys():
                _LOGGER.warning('missing value for column \'%s\'', column)

            csv = ', '.join([
                f'\'{column[1].encode(values[column[0]])}\''
                if column[0] in values.keys() else 'NULL'
                for column in self.__columns
            ])
            self.__database.commit(
                f'INSERT INTO {self.__identifier} VALUES({csv}, CURRENT_TIMESTAMP);'
            )

        def select(self,
                   columns: typing.List[str] = None,
                   where: typing.Optional[str] = None) -> typing.List[_Row]:
            if columns:
                for column in set(columns) - {
                        column[0] for column in self.__columns
                }:
                    _LOGGER.error('missing value for column \'%s\'', column)

                columns = [
                    column for column in self.__columns if column in columns
                ]
            else:
                columns = self.__columns

            csv = ', '.join([f'{column[0]}' for column in columns])
            return [
                self._Row({
                    column[0]: column[1].decode(value[index])
                    for index, column in enumerate(columns)
                })
                for value in self.__database.execute(
                    f'SELECT {csv} FROM {self.identifier} WHERE {where};'
                    if where else f'SELECT {csv} FROM {self.identifier};')
            ]

        def delete(self, where: str = 'TRUE') -> None:
            self.__database.execute(
                f'DELETE FROM {self.identifier} WHERE {where};')

        class _Row:

            def __init__(self, values: typing.Dict['str', typing.Any]) -> None:
                self.__values = values

            def __getitem__(self, identifier: str) -> typing.Any:
                return self.__values[identifier]

            def __getattr__(self, name) -> typing.Any:
                if name in self.__values:
                    return self[name]
                return None

            def __repr__(self) -> str:
                return str(self.__values)

            def keys(self) -> typing.Any:
                return self.__values.keys()


class _DataType:

    def __init__(self, typename: str, not_null: bool = False) -> None:
        self.__typename = typename
        self.__not_null = not_null

    def __repr__(self) -> str:
        return f'Column(typename: \'{self.typename}\')'

    @property
    def typename(self):
        return self.__typename

    __T = typing.TypeVar('__T')

    @staticmethod
    def encode(values: __T) -> __T:
        return values

    @staticmethod
    def decode(values: __T) -> __T:
        return values


BOOL: _DataType = _DataType('BOOL')
INTEGER: _DataType = _DataType('INTEGER')
DATE: _DataType = _DataType('DATE')
TEXT: _DataType = _DataType('TEXT')
BLOB: _DataType = _DataType('BLOB')


class _Array(_DataType):

    def __init__(self, item: _DataType) -> None:
        super().__init__('BLOB')
        self.__item: _DataType = item

    def encode(self, values: typing.List[_DataType | str]) -> str:
        return ''.join([
            config.STX + self.__item.encode(value) + config.ETX
            for value in values
        ])

    def decode(self, values: str) -> typing.List[str]:
        inner = []
        level = 0
        for character in values:
            if level > 0:
                inner[-1] += character
            else:
                inner.append(character)

            if character is config.STX:
                level += 1
            elif character is config.ETX:
                level -= 1

        return [self.__item.decode(value[1:-1]) for value in inner]


ARRAY: typing.Type[_Array] = _Array


class _Tuple(_Array):

    def __init__(self, *items: _DataType) -> None:
        super().__init__(BLOB)
        self.__items: typing.Tuple[_DataType, ...] = items

    def encode(self, values: typing.List[_DataType | str]) -> str:
        if len(values) != len(self.__items):
            _LOGGER.critical('could not encode tuple')
            raise TypeError()

        return ''.join([
            config.STX + self.__items[index].encode(value) + config.ETX
            for index, value in enumerate(values)
        ])

    def decode(self, values: str) -> typing.Optional[typing.List[str]]:
        inner = super().decode(values)

        if len(inner) != len(self.__items):
            _LOGGER.critical('could not decode tuple')
            return None

        return [
            self.__items[index].decode(value)
            for index, value in enumerate(inner)
        ]


TUPLE: typing.Type[_Tuple] = _Tuple


class _Decorator:

    def __init__(self, decorated: _DataType | _Decorator) -> None:
        self.__decorated: _DataType = decorated

    @property
    def typename(self) -> str:
        return self.__decorated.typename

    def __getattr__(self, name: str) -> typing.Any:
        return getattr(self.__decorated, name)


class _Unique(_Decorator):

    @property
    def typename(self) -> str:
        return f'{super().typename} UNIQUE'


UNIQUE: typing.Type[_Unique] = _Unique


class _NotNull(_Decorator):

    @property
    def typename(self) -> str:
        return f'{super().typename} NOT NULL'


NOT_NULL: typing.Type[_NotNull] = _NotNull


class _PrimaryKey(_NotNull):

    @property
    def typename(self) -> str:
        return f'{super().typename} PRIMARY KEY'


PRIMARY_KEY: typing.Type[_PrimaryKey] = _PrimaryKey
