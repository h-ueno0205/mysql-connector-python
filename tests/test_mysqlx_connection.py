# -*- coding: utf-8 -*-
# MySQL Connector/Python - MySQL driver written in Python.
# Copyright (c) 2016, Oracle and/or its affiliates. All rights reserved.

# MySQL Connector/Python is licensed under the terms of the GPLv2
# <http://www.gnu.org/licenses/old-licenses/gpl-2.0.html>, like most
# MySQL Connectors. There are special exceptions to the terms and
# conditions of the GPLv2 as it is applied to this software, see the
# FOSS License Exception
# <http://www.mysql.com/about/legal/licensing/foss-exception.html>.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA 02110-1301 USA

"""Unittests for mysqlx.connection
"""

import logging
import unittest

import tests
import mysqlx


LOGGER = logging.getLogger(tests.LOGGER_NAME)

_URI_TEST_RESULTS = (  # (uri, result)
    ("127.0.0.1", None),
    ("localhost", None),
    ("domain.com", None),
    ("user:password@127.0.0.1", {"schema": "", "host": "127.0.0.1",
                                 "password": "password", "port": 33060,
                                 "user": "user"}),
    ("user:password@127.0.0.1:33061", {"schema": "", "host": "127.0.0.1",
                                       "password": "password", "port": 33061,
                                       "user": "user"}),
    ("user:@127.0.0.1", {"schema": "", "host": "127.0.0.1", "password": "",
                         "port": 33060, "user": "user"}),
    ("user:@127.0.0.1/schema", {"schema": "schema", "host": "127.0.0.1",
                                "password": "", "port": 33060,
                                "user": "user"}),
    ("mysqlx://user:@127.0.0.1", {"schema": "", "host": "127.0.0.1",
                                  "password": "", "port": 33060,
                                  "user": "user"}),
    ("mysqlx://user:@127.0.0.1:33060/schema",
     {"schema": "schema", "host": "127.0.0.1", "password": "", "port": 33060,
      "user": "user"}),
    ("mysqlx://user@[2001:db8:85a3:8d3:1319:8a2e:370:7348]:1", None),
    ("mysqlx://user:password@[2001:db8:85a3:8d3:1319:8a2e:370:7348]:1",
     {"schema": "", "host": "2001:db8:85a3:8d3:1319:8a2e:370:7348",
      "password": "password", "port": 1, "user": "user"}),
    ("mysqlx://user:password@[2001:db8:85a3:8d3:1319:8a2e:370:7348]:1/schema",
     {"schema": "schema", "host": "2001:db8:85a3:8d3:1319:8a2e:370:7348",
      "password": "password", "port": 1, "user": "user"}),
    ("áé'í'óú:unicode@127.0.0.1",
     {"schema": "", "host": "127.0.0.1", "password": "unicode",
      "port": 33060, "user": "áé'í'óú"}),
)


@unittest.skipIf(tests.MYSQL_VERSION < (5, 7, 12), "XPlugin not compatible")
class MySQLxXSessionTests(tests.MySQLxTests):

    def setUp(self):
        self.connect_kwargs = tests.get_mysqlx_config()
        self.schema_name = self.connect_kwargs["schema"]
        try:
            self.session = mysqlx.get_session(self.connect_kwargs)
        except mysqlx.Error as err:
            self.fail("{0}".format(err))

    def test___init__(self):
        bad_config = {
            "host": "bad_host",
            "port": "",
            "username": "root",
            "password": ""
        }
        self.assertRaises(TypeError, mysqlx.XSession, bad_config)

    def test_connection_uri(self):
        uri = ("mysqlx://{user}:{password}@{host}:{port}/{schema}"
               "".format(user=self.connect_kwargs["user"],
                         password=self.connect_kwargs["password"],
                         host=self.connect_kwargs["host"],
                         port=self.connect_kwargs["port"],
                         schema=self.connect_kwargs["schema"]))
        session = mysqlx.get_session(uri)
        self.assertIsInstance(session, mysqlx.XSession)

        # Test URI parser function
        for uri, res in _URI_TEST_RESULTS:
            try:
                settings = mysqlx._get_connection_settings(uri)
                self.assertEqual(res, settings)
            except mysqlx.Error:
                self.assertEqual(res, None)

    def test_get_schema(self):
        schema = self.session.get_schema(self.schema_name)
        self.assertTrue(schema, mysqlx.Schema)
        self.assertEqual(schema.get_name(), self.schema_name)

    def test_get_default_schema(self):
        schema = self.session.get_default_schema()
        self.assertTrue(schema, mysqlx.Schema)
        self.assertEqual(schema.get_name(), self.connect_kwargs["schema"])

        # Test without default schema configured at connect time
        settings = self.connect_kwargs.copy()
        settings["schema"] = None
        session = mysqlx.get_session(settings)
        self.assertRaises(mysqlx.ProgrammingError, session.get_default_schema)
        session.close()

    def test_drop_schema(self):
        self.session.drop_schema(self.schema_name)
        schema = self.session.get_schema(self.schema_name)
        self.assertFalse(schema.exists_in_database())

    def test_create_schema(self):
        schema = self.session.create_schema(self.schema_name)
        self.assertTrue(schema.exists_in_database())

    def test_close(self):
        session = mysqlx.get_session(self.connect_kwargs)
        schema = session.get_schema(self.schema_name)

        session.close()
        self.assertRaises(mysqlx.OperationalError, schema.exists_in_database)


@unittest.skipIf(tests.MYSQL_VERSION < (5, 7, 12), "XPlugin not compatible")
class MySQLxNodeSessionTests(tests.MySQLxTests):

    def setUp(self):
        self.connect_kwargs = tests.get_mysqlx_config()
        self.schema_name = self.connect_kwargs["schema"]
        try:
            self.session = mysqlx.get_node_session(self.connect_kwargs)
        except mysqlx.Error as err:
            self.fail("{0}".format(err))

    def test___init__(self):
        bad_config = {
            "host": "bad_host",
            "port": "",
            "username": "root",
            "password": ""
        }
        self.assertRaises(TypeError, mysqlx.NodeSession, bad_config)

    def test_connection_uri(self):
        uri = ("mysqlx://{user}:{password}@{host}:{port}/{schema}"
               "".format(user=self.connect_kwargs["user"],
                         password=self.connect_kwargs["password"],
                         host=self.connect_kwargs["host"],
                         port=self.connect_kwargs["port"],
                         schema=self.connect_kwargs["schema"]))
        session = mysqlx.get_node_session(uri)
        self.assertIsInstance(session, mysqlx.NodeSession)

        # Test URI parser function
        for uri, res in _URI_TEST_RESULTS:
            try:
                settings = mysqlx._get_connection_settings(uri)
                self.assertEqual(res, settings)
            except mysqlx.Error:
                self.assertEqual(res, None)

    def test_get_schema(self):
        schema = self.session.get_schema(self.schema_name)
        self.assertTrue(schema, mysqlx.Schema)
        self.assertEqual(schema.get_name(), self.schema_name)

    def test_get_default_schema(self):
        schema = self.session.get_default_schema()
        self.assertTrue(schema, mysqlx.Schema)
        self.assertEqual(schema.get_name(), self.connect_kwargs["schema"])

        # Test without default schema configured at connect time
        settings = self.connect_kwargs.copy()
        settings["schema"] = None
        session = mysqlx.get_node_session(settings)
        self.assertRaises(mysqlx.ProgrammingError, session.get_default_schema)
        session.close()

    def test_drop_schema(self):
        self.session.drop_schema(self.schema_name)
        schema = self.session.get_schema(self.schema_name)
        self.assertFalse(schema.exists_in_database())

    def test_create_schema(self):
        schema = self.session.create_schema(self.schema_name)
        self.assertTrue(schema.exists_in_database())

    def test_sql(self):
        statement = self.session.sql("SELECT VERSION()")
        self.assertTrue(isinstance(statement, mysqlx.statement.Statement))

    def test_rollback(self):
        table_name = "t2"
        schema = self.session.get_schema(self.schema_name)

        if not schema.exists_in_database():
            self.session.create_schema(self.schema_name)

        stmt = "CREATE TABLE {0}.{1}(_id INT)"
        self.session.sql(stmt.format(self.schema_name, table_name)).execute()
        table = schema.get_table(table_name)

        self.session.start_transaction()

        table.insert("_id").values(1).execute()
        self.assertEqual(table.count(), 1)

        self.session.rollback()
        self.assertEqual(table.count(), 0)

        schema.drop_table(table_name)

    def test_commit(self):
        table_name = "t2"
        schema = self.session.get_schema(self.schema_name)

        if not schema.exists_in_database():
            self.session.create_schema(self.schema_name)

        stmt = "CREATE TABLE {0}.{1}(_id INT)"
        self.session.sql(stmt.format(self.schema_name, table_name)).execute()
        table = schema.get_table(table_name)

        self.session.start_transaction()

        table.insert("_id").values(1).execute()
        self.assertEqual(table.count(), 1)

        self.session.commit()
        self.assertEqual(table.count(), 1)

        schema.drop_table(table_name)
