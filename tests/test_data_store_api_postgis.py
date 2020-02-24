import unittest
import os
from sqlite3 import OperationalError

from unittest import TestCase
from testing.postgresql import Postgresql
from datetime import datetime
from sqlalchemy import event
from sqlalchemy.sql.ddl import DropSchema
from pepys_import.core.store.data_store import DataStore
from pepys_import.core.store.db_base import BasePostGIS

FILE_PATH = os.path.dirname(__file__)
TEST_DATA_PATH = os.path.join(FILE_PATH, "sample_data", "csv_files")


class DataStoreCacheTestCase(TestCase):
    def setUp(self) -> None:
        self.postgres = None
        self.store = None
        try:
            self.postgres = Postgresql(
                database="test",
                host="localhost",
                user="postgres",
                password="postgres",
                port=55527,
            )
        except RuntimeError:
            print("PostgreSQL database couldn't be created! Test is skipping.")
            return
        try:
            self.store = DataStore(
                db_name="test",
                db_host="localhost",
                db_username="postgres",
                db_password="postgres",
                db_port=55527,
            )
            self.store.initialise()
        except OperationalError:
            print("Database schema and data population failed! Test is skipping.")

    def tearDown(self) -> None:
        try:
            event.listen(
                BasePostGIS.metadata, "before_create", DropSchema("datastore_schema")
            )
            self.postgres.stop()
        except AttributeError:
            return

    def test_cached_comment_types(self):
        """Test whether a new comment type entity cached and returned"""
        with self.store.session_scope():
            comment_types = self.store.session.query(
                self.store.db_classes.CommentType
            ).all()

            # there must be no entity at the beginning
            self.assertEqual(len(comment_types), 0)

            comment_type_1 = self.store.add_to_comment_types("Comment-1")
            # This one shouldn't duplicate, it must return existing entity
            comment_type_2 = self.store.add_to_comment_types("Comment-1")

            # objects must be the same since the second object
            # is cached of first the one
            self.assertEqual(comment_type_1, comment_type_2)

            comment_types = self.store.session.query(
                self.store.db_classes.CommentType
            ).all()
            # there must be only one entity at the beginning
            self.assertEqual(len(comment_types), 1)

    def test_cached_table_type(self):
        """Test whether a new table type entity cached and returned"""
        with self.store.session_scope():
            table_types = self.store.session.query(
                self.store.db_classes.TableType
            ).all()

            # there must be no entity at the beginning
            self.assertEqual(len(table_types), 0)

            table_type_1 = self.store.add_to_table_types(
                table_type_id=1, table_name="test"
            )
            # This one shouldn't duplicate, it should return existing entity
            table_type_2 = self.store.add_to_table_types(
                table_type_id=1, table_name="test"
            )

            # objects must be the same
            self.assertEqual(table_type_1, table_type_2)
            table_types = self.store.session.query(
                self.store.db_classes.TableType
            ).all()

            # there must be only one entity at the beginning
            self.assertEqual(len(table_types), 1)

    def test_cached_platform_types(self):
        """Test whether a new platform type entity cached and returned"""
        with self.store.session_scope():
            platform_types = self.store.session.query(
                self.store.db_classes.PlatformType
            ).all()

            # there must be no entity at the beginning
            self.assertEqual(len(platform_types), 0)

            platform_type_1 = self.store.add_to_platform_types(
                platform_type_name="test"
            )
            # This one shouldn't duplicate, it should return existing entity
            platform_type_2 = self.store.add_to_platform_types(
                platform_type_name="test"
            )

            # objects must be the same
            self.assertEqual(platform_type_1, platform_type_2)
            platform_types = self.store.session.query(
                self.store.db_classes.PlatformType
            ).all()

            # there must be only one entity at the beginning
            self.assertEqual(len(platform_types), 1)

    def test_cached_nationalities(self):
        """Test whether a new nationality entity cached and returned"""
        with self.store.session_scope():
            nationalities = self.store.session.query(
                self.store.db_classes.Nationality
            ).all()

            # there must be no entity at the beginning
            self.assertEqual(len(nationalities), 0)

            nationality_1 = self.store.add_to_nationalities(nationality_name="test")
            # This one shouldn't duplicate, it should return existing entity
            nationality_2 = self.store.add_to_nationalities(nationality_name="test")

            # objects must be the same
            self.assertEqual(nationality_1, nationality_2)
            nationalities = self.store.session.query(
                self.store.db_classes.Nationality
            ).all()

            # there must be only one entity at the beginning
            self.assertEqual(len(nationalities), 1)

    def test_cached_privacies(self):
        """Test whether a new privacy entity cached and returned"""
        with self.store.session_scope():
            privacies = self.store.session.query(self.store.db_classes.Privacy).all()

            # there must be no entity at the beginning
            self.assertEqual(len(privacies), 0)

            privacy_1 = self.store.add_to_privacies(privacy_name="test")
            # This one shouldn't duplicate, it should return existing entity
            privacy_2 = self.store.add_to_privacies(privacy_name="test")

            # objects must be the same
            self.assertEqual(privacy_1, privacy_2)
            privacies = self.store.session.query(self.store.db_classes.Privacy).all()

            # there must be only one entity at the beginning
            self.assertEqual(len(privacies), 1)

    def test_cached_datafile_types(self):
        """Test whether a new datafile type entity cached and returned"""
        with self.store.session_scope():
            datafile_types = self.store.session.query(
                self.store.db_classes.DatafileType
            ).all()

            # there must be no entity at the beginning
            self.assertEqual(len(datafile_types), 0)

            datafile_type_1 = self.store.add_to_datafile_types(datafile_type="test")
            # This one shouldn't duplicate, it should return existing entity
            datafile_type_2 = self.store.add_to_datafile_types(datafile_type="test")

            # objects must be the same
            self.assertEqual(datafile_type_1, datafile_type_2)
            datafile_types = self.store.session.query(
                self.store.db_classes.DatafileType
            ).all()

            # there must be only one entity at the beginning
            self.assertEqual(len(datafile_types), 1)

    def test_cached_sensor_types(self):
        """Test whether a new sensor type entity cached and returned"""
        with self.store.session_scope():
            sensor_types = self.store.session.query(
                self.store.db_classes.SensorType
            ).all()

            # there must be no entity at the beginning
            self.assertEqual(len(sensor_types), 0)

            sensor_type_1 = self.store.add_to_sensor_types(sensor_type_name="test")
            # This one shouldn't duplicate, it should return existing entity
            sensor_type_2 = self.store.add_to_sensor_types(sensor_type_name="test")

            # objects must be the same
            self.assertEqual(sensor_type_1, sensor_type_2)
            sensor_types = self.store.session.query(
                self.store.db_classes.SensorType
            ).all()

            # there must be only one entity at the beginning
            self.assertEqual(len(sensor_types), 1)


class LookUpDBAndAddToCacheTestCase(TestCase):
    """Test searching functionality and adding existing DB entities to the cache of
    DataStore"""

    def setUp(self) -> None:
        self.postgres = None
        self.store = None
        try:
            self.postgres = Postgresql(
                database="test",
                host="localhost",
                user="postgres",
                password="postgres",
                port=55527,
            )
        except RuntimeError:
            print("PostgreSQL database couldn't be created! Test is skipping.")
            return
        try:
            self.store = DataStore(
                db_name="test",
                db_host="localhost",
                db_username="postgres",
                db_password="postgres",
                db_port=55527,
            )
            self.store.initialise()
        except OperationalError:
            print("Database schema and data population failed! Test is skipping.")

    def tearDown(self) -> None:
        try:
            event.listen(
                BasePostGIS.metadata, "before_create", DropSchema("datastore_schema")
            )
            self.postgres.stop()
        except AttributeError:
            return

    def test_comment_types(self):
        with self.store.session_scope():
            comment_type = self.store.db_classes.CommentType(name="test")
            self.store.session.add(comment_type)
            self.store.session.flush()

            comment_types = self.store.session.query(
                self.store.db_classes.CommentType
            ).all()

            # there must be one entity at the beginning
            self.assertEqual(len(comment_types), 1)

            self.store.add_to_comment_types("test")

            comment_types = self.store.session.query(
                self.store.db_classes.CommentType
            ).all()

            # there must be only one entity again
            self.assertEqual(len(comment_types), 1)

    def test_table_type(self):
        with self.store.session_scope():
            table_type = self.store.db_classes.TableType(table_type_id=1, name="test")
            self.store.session.add(table_type)
            self.store.session.flush()

            table_types = self.store.session.query(
                self.store.db_classes.TableType
            ).all()

            # there must be one entity at the beginning
            self.assertEqual(len(table_types), 1)

            self.store.add_to_table_types(1, "test")

            table_types = self.store.session.query(
                self.store.db_classes.TableType
            ).all()

            # there must be only one entity again
            self.assertEqual(len(table_types), 1)

    def test_platform_types(self):
        with self.store.session_scope():
            platform_type = self.store.db_classes.PlatformType(name="test")
            self.store.session.add(platform_type)
            self.store.session.flush()

            platform_types = self.store.session.query(
                self.store.db_classes.PlatformType
            ).all()

            # there must be one entity at the beginning
            self.assertEqual(len(platform_types), 1)

            self.store.add_to_platform_types("test")

            platform_types = self.store.session.query(
                self.store.db_classes.PlatformType
            ).all()

            # there must be only one entity again
            self.assertEqual(len(platform_types), 1)

    def test_nationalities(self):
        with self.store.session_scope():
            nationality = self.store.db_classes.Nationality(name="test")
            self.store.session.add(nationality)
            self.store.session.flush()

            nationalities = self.store.session.query(
                self.store.db_classes.Nationality
            ).all()

            # there must be one entity at the beginning
            self.assertEqual(len(nationalities), 1)

            self.store.add_to_nationalities("test")

            nationalities = self.store.session.query(
                self.store.db_classes.Nationality
            ).all()

            # there must be only one entity again
            self.assertEqual(len(nationalities), 1)

    def test_privacies(self):
        with self.store.session_scope():
            privacy = self.store.db_classes.Privacy(name="test")
            self.store.session.add(privacy)
            self.store.session.flush()

            privacies = self.store.session.query(self.store.db_classes.Privacy).all()

            # there must be one entity at the beginning
            self.assertEqual(len(privacies), 1)

            self.store.add_to_privacies("test")

            privacies = self.store.session.query(self.store.db_classes.Privacy).all()

            # there must be only one entity again
            self.assertEqual(len(privacies), 1)

    def test_datafile_types(self):
        with self.store.session_scope():
            datafile_type = self.store.db_classes.DatafileType(name="test")
            self.store.session.add(datafile_type)
            self.store.session.flush()

            datafile_types = self.store.session.query(
                self.store.db_classes.DatafileType
            ).all()

            # there must be one entity at the beginning
            self.assertEqual(len(datafile_types), 1)

            self.store.add_to_datafile_types("test")

            datafile_types = self.store.session.query(
                self.store.db_classes.DatafileType
            ).all()

            # there must be only one entity again
            self.assertEqual(len(datafile_types), 1)

    def test_sensor_types(self):
        with self.store.session_scope():
            sensor_type = self.store.db_classes.SensorType(name="test")
            self.store.session.add(sensor_type)
            self.store.session.flush()

            sensor_types = self.store.session.query(
                self.store.db_classes.SensorType
            ).all()

            # there must be one entity at the beginning
            self.assertEqual(len(sensor_types), 1)

            self.store.add_to_sensor_types("test")

            sensor_types = self.store.session.query(
                self.store.db_classes.SensorType
            ).all()

            # there must be only one entity again
            self.assertEqual(len(sensor_types), 1)


class PlatformAndDatafileTestCase(TestCase):
    def setUp(self) -> None:
        self.postgres = None
        self.store = None
        try:
            self.postgres = Postgresql(
                database="test",
                host="localhost",
                user="postgres",
                password="postgres",
                port=55527,
            )
        except RuntimeError:
            print("PostgreSQL database couldn't be created! Test is skipping.")
            return
        try:
            self.store = DataStore(
                db_name="test",
                db_host="localhost",
                db_username="postgres",
                db_password="postgres",
                db_port=55527,
            )
            self.store.initialise()
            with self.store.session_scope():
                self.nationality = self.store.add_to_nationalities(
                    "test_nationality"
                ).name
                self.platform_type = self.store.add_to_platform_types(
                    "test_platform_type"
                ).name
                self.privacy = self.store.add_to_privacies("test_privacy").name
        except OperationalError:
            print("Database schema and data population failed! Test is skipping.")

    def tearDown(self) -> None:
        try:
            event.listen(
                BasePostGIS.metadata, "before_create", DropSchema("datastore_schema")
            )
            self.postgres.stop()
        except AttributeError:
            return

    def test_new_datafile_added_successfully(self):
        """Test whether a new datafile is created successfully or not"""

        with self.store.session_scope():
            datafiles = self.store.session.query(self.store.db_classes.Datafile).all()

        # there must be no entry at the beginning
        self.assertEqual(len(datafiles), 0)

        with self.store.session_scope():
            self.store.get_datafile("test_file.csv", "csv")

        # there must be one entry
        with self.store.session_scope():
            datafiles = self.store.session.query(self.store.db_classes.Datafile).all()
            self.assertEqual(len(datafiles), 1)
            self.assertEqual(datafiles[0].reference, "test_file.csv")

    def test_present_datafile_not_added(self):
        """Test whether present datafile is not created"""

        with self.store.session_scope():
            datafiles = self.store.session.query(self.store.db_classes.Datafile).all()

        # there must be no entry at the beginning
        self.assertEqual(len(datafiles), 0)

        with self.store.session_scope():
            self.store.get_datafile("test_file.csv", "csv")
            self.store.get_datafile("test_file.csv", "csv")

            # there must be one entry
            datafiles = self.store.session.query(self.store.db_classes.Datafile).all()
            self.assertEqual(len(datafiles), 1)
            self.assertEqual(datafiles[0].reference, "test_file.csv")

    def test_find_datafile(self):
        """Test whether find_datafile method returns the correct Datafile entity"""
        with self.store.session_scope():
            # Create a datafile
            datafile = self.store.get_datafile("test_file.csv", "csv")
            datafile_2 = self.store.get_datafile("test_file_2.csv", "csv")
            found_datafile = self.store.find_datafile("test_file.csv")

            self.assertEqual(datafile.datafile_id, found_datafile.datafile_id)
            self.assertEqual(found_datafile.reference, "test_file.csv")

    def test_find_datafile_synonym(self):
        """Test whether find_datafile method finds the correct Datafile entity from Synonyms table"""
        with self.store.session_scope():
            datafile = self.store.get_datafile("test_file.csv", "csv")
            datafile_2 = self.store.get_datafile("test_file_2.csv", "csv")
            self.store.add_to_synonyms(
                table="Datafiles", name="TEST", entity=datafile.datafile_id
            )

            found_datafile = self.store.find_datafile("TEST")
            self.assertEqual(datafile.datafile_id, found_datafile.datafile_id)

    def test_new_platform_added_successfully(self):
        """Test whether a new platform is created successfully or not"""

        with self.store.session_scope():
            platforms = self.store.session.query(self.store.db_classes.Platform).all()

        # there must be no entry at the beginning
        self.assertEqual(len(platforms), 0)

        with self.store.session_scope():
            self.platform = self.store.get_platform(
                platform_name="Test Platform",
                nationality=self.nationality,
                platform_type=self.platform_type,
                privacy=self.privacy,
            )

        # there must be one entry
        with self.store.session_scope():
            platforms = self.store.session.query(self.store.db_classes.Platform).all()

            self.assertEqual(len(platforms), 1)
            self.assertEqual(platforms[0].name, "Test Platform")

    def test_present_platform_not_added(self):
        """Test whether present platform is not created"""

        with self.store.session_scope():
            platforms = self.store.session.query(self.store.db_classes.Platform).all()

        # there must be no entry at the beginning
        self.assertEqual(len(platforms), 0)

        with self.store.session_scope():
            self.platform = self.store.get_platform(
                platform_name="Test Platform",
                nationality=self.nationality,
                platform_type=self.platform_type,
                privacy=self.privacy,
            )
            self.platform = self.store.get_platform(
                platform_name="Test Platform",
                nationality=self.nationality,
                platform_type=self.platform_type,
                privacy=self.privacy,
            )

        # there must be one entry
        with self.store.session_scope():
            platforms = self.store.session.query(self.store.db_classes.Platform).all()

            self.assertEqual(len(platforms), 1)
            self.assertEqual(platforms[0].name, "Test Platform")

    def test_find_platform(self):
        """Test whether find_platform method returns the correct Platform entity"""
        with self.store.session_scope() as session:
            # Create two platforms
            platform = self.store.get_platform(
                platform_name="Test Platform",
                nationality=self.nationality,
                platform_type=self.platform_type,
                privacy=self.privacy,
            )
            platform_2 = self.store.get_platform(
                platform_name="Test Platform 2",
                nationality=self.nationality,
                platform_type=self.platform_type,
                privacy=self.privacy,
            )

            found_platform = self.store.find_platform("Test Platform")
            self.assertEqual(platform.platform_id, found_platform.platform_id)
            self.assertEqual(found_platform.name, "Test Platform")

    def test_find_platform_synonym(self):
        """Test whether find_platform method finds the correct Platform entity from Synonyms table"""
        with self.store.session_scope() as session:
            # Create two platforms
            platform = self.store.get_platform(
                platform_name="Test Platform",
                nationality=self.nationality,
                platform_type=self.platform_type,
                privacy=self.privacy,
            )
            platform_2 = self.store.get_platform(
                platform_name="Test Platform 2",
                nationality=self.nationality,
                platform_type=self.platform_type,
                privacy=self.privacy,
            )
            self.store.add_to_synonyms(
                table="Platforms", name="TEST", entity=platform.platform_id
            )

            found_platform = self.store.find_platform("TEST")
            self.assertEqual(platform.platform_id, found_platform.platform_id)
            self.assertEqual(found_platform.name, "Test Platform")


class DataStoreStatusTestCase(TestCase):
    def setUp(self) -> None:
        self.postgres = None
        self.store = None
        try:
            self.postgres = Postgresql(
                database="test",
                host="localhost",
                user="postgres",
                password="postgres",
                port=55527,
            )
        except RuntimeError:
            print("PostgreSQL database couldn't be created! Test is skipping.")
            return
        try:
            self.store = DataStore(
                db_name="test",
                db_host="localhost",
                db_username="postgres",
                db_password="postgres",
                db_port=55527,
            )
            self.store.initialise()
            self.store.populate_reference(TEST_DATA_PATH)
            self.store.populate_metadata(TEST_DATA_PATH)
            self.store.populate_measurement(TEST_DATA_PATH)
        except OperationalError:
            print("Database schema and data population failed! Test is skipping.")

    def tearDown(self) -> None:
        try:
            event.listen(
                BasePostGIS.metadata, "before_create", DropSchema("datastore_schema")
            )
            self.postgres.stop()
        except AttributeError:
            return

    def test_get_status_of_measurement(self):
        """Test whether summary contents correct for measurement tables"""

        table_summary_object = self.store.get_status(report_measurement=True)
        report = table_summary_object.report()

        self.assertNotEqual(report, "")
        self.assertIn("States", report)
        self.assertIn("Contacts", report)
        self.assertIn("Activations", report)

    def test_get_status_of_metadata(self):
        """Test whether summary contents correct for metadata tables"""

        table_summary_object = self.store.get_status(report_metadata=True)
        report = table_summary_object.report()

        self.assertNotEqual(report, "")
        self.assertIn("Sensors", report)
        self.assertIn("Platforms", report)
        self.assertIn("Datafiles", report)

    def test_get_status_of_reference(self):
        """Test whether summary contents correct for reference tables"""

        table_summary_object = self.store.get_status(report_reference=True)
        report = table_summary_object.report()

        self.assertNotEqual(report, "")
        self.assertIn("Nationalities", report)
        self.assertIn("Privacies", report)
        self.assertIn("PlatformTypes", report)


class SensorTestCase(TestCase):
    def setUp(self) -> None:
        self.postgres = None
        self.store = None
        try:
            self.postgres = Postgresql(
                database="test",
                host="localhost",
                user="postgres",
                password="postgres",
                port=55527,
            )
        except RuntimeError:
            print("PostgreSQL database couldn't be created! Test is skipping.")
            return
        try:
            self.store = DataStore(
                db_name="test",
                db_host="localhost",
                db_username="postgres",
                db_password="postgres",
                db_port=55527,
            )
            self.store.initialise()
            with self.store.session_scope():
                self.nationality = self.store.add_to_nationalities(
                    "test_nationality"
                ).name
                self.platform_type = self.store.add_to_platform_types(
                    "test_platform_type"
                ).name
                self.sensor_type = self.store.add_to_sensor_types("test_sensor_type")
                self.privacy = self.store.add_to_privacies("test_privacy").name

                self.platform = self.store.get_platform(
                    platform_name="Test Platform",
                    nationality=self.nationality,
                    platform_type=self.platform_type,
                    privacy=self.privacy,
                )
                self.store.session.expunge(self.platform)
                self.store.session.expunge(self.sensor_type)
        except OperationalError:
            print("Database schema and data population failed! Test is skipping.")

    def tearDown(self) -> None:
        try:
            event.listen(
                BasePostGIS.metadata, "before_create", DropSchema("datastore_schema")
            )
            self.postgres.stop()
        except AttributeError:
            return

    def test_new_sensor_added_successfully(self):
        """Test whether a new sensor is created"""
        with self.store.session_scope():
            sensors = self.store.session.query(self.store.db_classes.Sensor).all()

            # there must be no entry at the beginning
            self.assertEqual(len(sensors), 0)

            self.platform.get_sensor(self.store, "gps", self.sensor_type)

            # there must be one entry
            sensors = self.store.session.query(self.store.db_classes.Sensor).all()
            self.assertEqual(len(sensors), 1)
            self.assertEqual(sensors[0].name, "gps")

    def test_present_sensor_not_added(self):
        """Test whether present sensor is not created"""
        with self.store.session_scope():
            sensors = self.store.session.query(self.store.db_classes.Sensor).all()

            # there must be no entry at the beginning
            self.assertEqual(len(sensors), 0)

            self.platform.get_sensor(self.store, "gps", self.sensor_type)

            # try to add the same entity
            self.platform.get_sensor(self.store, "gps", self.sensor_type)

            # there must be one entry
            sensors = self.store.session.query(self.store.db_classes.Sensor).all()

            self.assertEqual(len(sensors), 1)

    def test_find_sensor(self):
        """Test whether find_sensor method returns the correct Sensor entity"""
        with self.store.session_scope():
            sensors = self.store.session.query(self.store.db_classes.Sensor).all()

            # there must be no entry at the beginning
            self.assertEqual(len(sensors), 0)

            sensor = self.platform.get_sensor(self.store, "gps", self.sensor_type)
            sensor_2 = self.platform.get_sensor(self.store, "gps_2", self.sensor_type)

            found_sensor = self.store.db_classes.Sensor().find_sensor(self.store, "gps")
            self.assertEqual(sensor.sensor_id, found_sensor.sensor_id)
            self.assertEqual(found_sensor.name, "gps")

    def test_find_sensor_synonym(self):
        """Test whether find_sensor method finds the correct Sensor entity from Synonyms table"""
        with self.store.session_scope():
            sensors = self.store.session.query(self.store.db_classes.Sensor).all()

            # there must be no entry at the beginning
            self.assertEqual(len(sensors), 0)

            sensor = self.platform.get_sensor(self.store, "gps", self.sensor_type)
            sensor_2 = self.platform.get_sensor(self.store, "gps_2", self.sensor_type)
            self.store.add_to_synonyms(
                table="Sensors", name="TEST", entity=sensor.sensor_id
            )

            found_sensor = self.store.db_classes.Sensor().find_sensor(
                self.store, "TEST"
            )
            self.assertEqual(sensor.sensor_id, found_sensor.sensor_id)
            self.assertEqual(found_sensor.name, "gps")


class MeasurementsTestCase(TestCase):
    def setUp(self) -> None:
        self.postgres = None
        self.store = None
        try:
            self.postgres = Postgresql(
                database="test",
                host="localhost",
                user="postgres",
                password="postgres",
                port=55527,
            )
        except RuntimeError:
            print("PostgreSQL database couldn't be created! Test is skipping.")
            return
        try:
            self.store = DataStore(
                db_name="test",
                db_host="localhost",
                db_username="postgres",
                db_password="postgres",
                db_port=55527,
            )
            self.store.initialise()
            with self.store.session_scope():
                self.nationality = self.store.add_to_nationalities(
                    "test_nationality"
                ).name
                self.platform_type = self.store.add_to_platform_types(
                    "test_platform_type"
                ).name
                self.sensor_type = self.store.add_to_sensor_types("test_sensor_type")
                self.privacy = self.store.add_to_privacies("test_privacy").name

                self.platform = self.store.get_platform(
                    platform_name="Test Platform",
                    nationality=self.nationality,
                    platform_type=self.platform_type,
                    privacy=self.privacy,
                )
                self.sensor = self.platform.get_sensor(
                    self.store, "gps", self.sensor_type
                )
                self.comment_type = self.store.add_to_comment_types("test_type")
                self.file = self.store.get_datafile("test_file", "csv")
                self.current_time = datetime.utcnow()

                self.store.session.expunge(self.sensor)
                self.store.session.expunge(self.platform)
                self.store.session.expunge(self.file)
                self.store.session.expunge(self.comment_type)
        except OperationalError:
            print("Database schema and data population failed! Test is skipping.")

    def tearDown(self) -> None:
        try:
            event.listen(
                BasePostGIS.metadata, "before_create", DropSchema("datastore_schema")
            )
            self.postgres.stop()
        except AttributeError:
            return

    def test_new_state_created_successfully(self):
        """Test whether a new state is created"""
        with self.store.session_scope():
            states = self.store.session.query(self.store.db_classes.State).all()

            # there must be no entry at the beginning
            self.assertEqual(len(states), 0)

            state = self.file.create_state(self.sensor, self.current_time)

            # there must be no entry because it's kept in-memory
            states = self.store.session.query(self.store.db_classes.State).all()
            self.assertEqual(len(states), 0)

            self.assertEqual(state.time, self.current_time)

            if self.file.validate():
                state.submit(self.store.session)
                states = self.store.session.query(self.store.db_classes.State).all()
            self.assertEqual(len(states), 1)

    def test_new_contact_created_successfully(self):
        """Test whether a new contact is created"""

        with self.store.session_scope() as session:
            contacts = self.store.session.query(self.store.db_classes.Contact).all()

            # there must be no entry at the beginning
            self.assertEqual(len(contacts), 0)

            contact = self.file.create_contact(self.sensor, self.current_time)

            # there must be no entry because it's kept in-memory
            contacts = self.store.session.query(self.store.db_classes.Contact).all()
            self.assertEqual(len(contacts), 0)

            # Fill null constraint field
            contact.name = "TEST"
            contact.subject_id = self.platform.platform_id
            if self.file.validate():
                contact.submit(self.store.session)
                contacts = self.store.session.query(self.store.db_classes.Contact).all()
                self.assertEqual(len(contacts), 1)

    def test_new_comment_created_successfully(self):
        """Test whether a new comment is created"""

        with self.store.session_scope() as session:
            comments = self.store.session.query(self.store.db_classes.Comment).all()

            # there must be no entry at the beginning
            self.assertEqual(len(comments), 0)

            comment = self.file.create_comment(
                self.sensor, self.current_time, "Comment", self.comment_type,
            )

            # there must be no entry because it's kept in-memory
            comments = self.store.session.query(self.store.db_classes.Comment).all()
            self.assertEqual(len(comments), 0)

            # Fill null constraint field
            comment.platform_id = self.platform.platform_id
            if self.file.validate():
                comment.submit(self.store.session)
                comments = self.store.session.query(self.store.db_classes.Comment).all()
                self.assertEqual(len(comments), 1)


if __name__ == "__main__":
    unittest.main()
