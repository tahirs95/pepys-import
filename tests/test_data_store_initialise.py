import unittest

from pepys_import.core.store.data_store import DataStore
from testing.postgresql import Postgresql
from sqlalchemy import inspect
from unittest import TestCase

import platform


class DataStoreInitialisePostGISTestCase(TestCase):
    def setUp(self):
        self.store = None
        try:
            self.store = Postgresql(
                database="test",
                host="localhost",
                user="postgres",
                password="postgres",
                port=55527,
            )
        except RuntimeError:
            print("PostgreSQL database couldn't be created! Test is skipping.")

    def tearDown(self):
        try:
            self.store.stop()
        except AttributeError:
            return

    def test_postgres_initialise(self):
        """Test whether schemas created successfully on PostgresSQL"""
        if self.store is None:
            self.skipTest("Postgres is not available. Test is skipping")

        data_store_postgres = DataStore(
            db_username="postgres",
            db_password="postgres",
            db_host="localhost",
            db_port=55527,
            db_name="test",
        )

        # inspector makes it possible to load lists of schema, table, column
        # information for the sqlalchemy engine
        inspector = inspect(data_store_postgres.engine)
        table_names = inspector.get_table_names()
        schema_names = inspector.get_schema_names()

        # there must be no table and no schema for datastore at the beginning
        self.assertEqual(len(table_names), 0)
        self.assertNotIn("pepys", schema_names)

        # creating database from schema
        data_store_postgres.initialise()

        inspector = inspect(data_store_postgres.engine)
        table_names = inspector.get_table_names(schema="pepys")
        schema_names = inspector.get_schema_names()

        # 34 tables must be created to default schema
        self.assertEqual(len(table_names), 34)
        self.assertIn("Platforms", table_names)
        self.assertIn("States", table_names)
        self.assertIn("Datafiles", table_names)
        self.assertIn("Nationalities", table_names)

        # pepys must be created
        self.assertIn("pepys", schema_names)

        # 1 table for spatial objects (spatial_ref_sys) must be created to default schema
        table_names = inspector.get_table_names()
        self.assertEqual(len(table_names), 1)
        self.assertIn("spatial_ref_sys", table_names)


class DataStoreInitialiseSpatiaLiteTestCase(TestCase):
    def test_sqlite_initialise(self):
        """Test whether schemas created successfully on SQLite"""
        data_store_sqlite = DataStore("", "", "", 0, ":memory:", db_type="sqlite")

        # inspector makes it possible to load lists of schema, table, column
        # information for the sqlalchemy engine
        inspector = inspect(data_store_sqlite.engine)
        table_names = inspector.get_table_names()

        # there must be no table at the beginning
        self.assertEqual(len(table_names), 0)

        # creating database from schema
        data_store_sqlite.initialise()

        inspector = inspect(data_store_sqlite.engine)
        table_names = inspector.get_table_names()

        SYSTEM = platform.system()

        if SYSTEM == "Windows":
            correct_n_tables = 72
        else:
            correct_n_tables = 70

        # 36 tables + 36 spatial tables must be created. A few of them tested
        self.assertEqual(len(table_names), correct_n_tables)
        self.assertIn("Platforms", table_names)
        self.assertIn("States", table_names)
        self.assertIn("Datafiles", table_names)
        self.assertIn("Nationalities", table_names)

        # tables created by Spatialite
        self.assertIn("geometry_columns", table_names)
        self.assertIn("views_geometry_columns", table_names)
        self.assertIn("virts_geometry_columns", table_names)
        self.assertIn("spatialite_history", table_names)


if __name__ == "__main__":
    unittest.main()
