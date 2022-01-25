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

import logging
import sqlite3
from typing import Any, Callable, Dict, List, Optional

import config

LOGGER: logging.Logger = logging.getLogger(__name__)


class Database:
    __instance: Optional[_Database] = None

    def __init__(self, uri: str = config.DATABASE) -> None:
        if not Database.__instance:
            Database.__instance = self._Database(uri)
        elif uri != Database.__instance.uri:
            Database.__instance.__del__()
            Database.__instance = self._Database(uri)
        else:
            LOGGER.info('reuse instance \'%s\'', uri)

    def __getattr__(self, identifier: str) -> Any:
        return getattr(self.__instance, identifier)

    def __getitem__(self, identifier: str) -> Optional[_Table]:
        return Database.__instance.__getitem__(identifier)

    def __setitem__(self, identifier: str, columns: List[Column]) -> None:
        return Database.__instance.__setitem__(identifier, columns)

    class _Database:

        def __init__(self, uri: str) -> None:
            LOGGER.debug('connect \'%s\'', uri)
            self.__uri = uri
            self.__connection = sqlite3.connect(f'file://{self.__uri}?mode=rw',
                                                uri=True)
            self.__tables = {
                identifier: Database._Table(self, identifier, columns)
                for identifier, columns in [
                    self.execute(f'PRAGMA table_info({k});',
                                 post=lambda i:
                                 (k, [Database.Column(j[1], j[2])
                                      for j in i]))
                    for k in self.execute(
                        'SELECT name FROM sqlite_master WHERE type = \'table\';',
                        post=lambda i: i[0] if i else [])
                ]
            }

        def __del__(self) -> None:
            LOGGER.debug('close \'%s\'', self.__uri)
            self.__connection.close()

        def __getitem__(self, identifier: str) -> Optional[Database._Table]:
            if identifier in self.__tables.keys():
                return self.__tables[identifier]
            LOGGER.error('missing table \'%s\'', identifier)
            return None

        def __setitem__(self, identifier: str,
                        columns: List[Database.Column]) -> None:
            if identifier in self.__tables.keys():
                LOGGER.info('replace table \'%s\'', identifier)
                self.drop(self.__tables[identifier])
            self.__tables[identifier] = Database._Table(self, identifier,
                                                        columns).create()

        @property
        def uri(self):
            return self.__uri

        def drop(self, table: Database._Table) -> None:
            self.commit(f'DROP TABLE IF EXISTS {table.identifier};')
            del self.__tables[table.identifier]

        def execute(self,
                    sql: str,
                    post: Callable[[List[str]], Any] = lambda i: i) -> Any:
            LOGGER.debug('execute \'%s\'', sql)
            return post(list(self.__connection.execute(sql)))

        def commit(self, sql: str) -> None:
            LOGGER.debug('execute \'%s\'', sql)
            self.__connection.execute(sql)
            self.__connection.commit()

    class _Table:

        def __init__(self, database: Database._Database, identifier: str,
                     columns: List[Database.Column]) -> None:
            self.__database = database
            self.__identifier = identifier
            self.__columns = [
                column for column in columns if column.identifier != 'modified'
            ]

        @property
        def identifier(self):
            return self.__identifier

        def __repr__(self) -> str:
            csv = ', '.join([str(column) for column in self.__columns])
            return f'Table(identifier: \'{self.__identifier}\', columns: [{csv}])'

        def create(self) -> Database._Table:
            csv = ', '.join([
                f'{column.identifier} {column.typename}'
                for column in self.__columns
            ])
            self.__database.commit(
                f'CREATE TABLE IF NOT EXISTS {self.__identifier}({csv}, modified date);'
            )
            return self

        def insert(self, values: Dict[str, Any]) -> None:
            if (self.select(where=' AND '.join([
                    f'{column.identifier}=\'{values[column.identifier]}\''
                    for column in self.__columns
                    if column.identifier in values.keys()
            ]))):
                LOGGER.error('duplicate entry %s', values)
                return

            for column in values.keys() - {
                    column.identifier for column in self.__columns
            }:
                LOGGER.error('missing column \'%s\'', column)
            for column in {column.identifier for column in self.__columns
                          } - values.keys():
                LOGGER.error('missing value for column \'%s\'', column)

            csv = ', '.join([
                f'\'{values[column.identifier]}\''
                if column.identifier in values.keys() else 'NULL'
                for column in self.__columns
            ])
            self.__database.commit(
                f'INSERT INTO {self.__identifier} VALUES({csv}, CURRENT_TIMESTAMP);'
            )

        def select(self,
                   columns: List[str] = None,
                   where: Optional[str] = None) -> List[_Row]:
            if columns:
                for column in set(columns) - {
                        column.identifier for column in self.__columns
                }:
                    LOGGER.error('missing value for column \'%s\'', column)

                columns = [
                    column for column in columns if column in
                    [column.identifier for column in self.__columns]
                ]
            else:
                columns = [column.identifier for column in self.__columns]

            csv = ', '.join([f'{column}' for column in columns])
            return [
                self._Row(
                    {column: value[idx]
                     for idx, column in enumerate(columns)})
                for value in self.__database.execute(
                    f'SELECT {csv} FROM {self.identifier} WHERE {where};'
                    if where else f'SELECT {csv} FROM {self.identifier};')
            ]

        def delete(self, where: str = 'TRUE') -> None:
            self.__database.execute(
                f'DELETE FROM {self.identifier} WHERE {where};')

        class _Row:

            def __init__(self, values: Dict['str', Any]) -> None:
                self.__values = values

            def __getitem__(self, identifier: str) -> Any:
                return self.__values[identifier]

            def __getattr__(self, identifier) -> Any:
                if identifier in self.__values:
                    return self[identifier]
                return None

            def __repr__(self) -> str:
                return str(self.__values)

            def keys(self) -> Any:
                return self.__values.keys()

    class Column:

        def __init__(self,
                     identifier: str,
                     typename: str,
                     not_null: bool = False) -> None:
            self.__identifier = identifier
            self.typename = typename
            self.not_null = not_null

        def __repr__(self) -> str:
            return f'Entry(identifier: \'{self.identifier}\', typename: \'{self.typename}\')'

        @property
        def identifier(self):
            return self.__identifier

    class Bool(Column):

        def __init__(self, value: str) -> None:
            super(Database.Bool, self).__init__(value, 'BOOL')

    class Integer(Column):

        def __init__(self, value: str) -> None:
            super(Database.Integer, self).__init__(value, 'INTEGER')

    class Date(Column):

        def __init__(self, value: str) -> None:
            super(Database.Date, self).__init__(value, 'DATE')

    class String(Column):

        def __init__(self, value: str) -> None:
            super(Database.String, self).__init__(value, 'TEXT')


if __name__ == '__main__':
    # pylint: disable=import-self
    from s9l.database import Database  # noqa

    db = Database(config.DATABASE)
    db['test'] = [db.Integer('id'), db.String('content')]
    db['test'].insert({'id': 1, 'content': "42"})
    LOGGER.info(db['test'].select()[0].content)
