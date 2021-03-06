import unittest
import os

from geoalchemy2 import WKBElement, WKTElement
from sqlalchemy import func
from sqlalchemy.exc import OperationalError
from testing.postgresql import Postgresql

from pepys_import.core.store.data_store import DataStore
from pepys_import.core.formats.location import Location


FILE_PATH = os.path.dirname(__file__)
TEST_DATA_PATH = os.path.join(FILE_PATH, "sample_data", "csv_files")


class SpatialDataSpatialiteTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.store = DataStore("", "", "", 0, ":memory:", db_type="sqlite")
        with self.store.session_scope():
            self.store.initialise()
            self.store.populate_reference(TEST_DATA_PATH)
            self.store.populate_metadata(TEST_DATA_PATH)
            self.store.populate_measurement(TEST_DATA_PATH)

    def tearDown(self) -> None:
        pass

    def test_location(self):
        """Test location saved as Geo Point and it is possible to filter State objects on SpatiaLite"""
        with self.store.session_scope():
            # Filter state object by spatial location
            first_state = (
                self.store.session.query(self.store.db_classes.State)
                .filter(
                    func.ST_Contains(
                        self.store.db_classes.State.location,
                        WKTElement("POINT(46.000 32.000)", srid=4326),
                    )
                )
                .one()
            )
            correct_loc = Location()
            correct_loc.set_latitude_decimal_degrees(32)
            correct_loc.set_longitude_decimal_degrees(46)

            assert first_state.location == correct_loc

    def test_non_existing_location(self):
        """Test filtering State objects by non existing point returns None on SpatiaLite"""

        with self.store.session_scope():
            # Filter state object by spatial location
            first_state = (
                self.store.session.query(self.store.db_classes.State)
                .filter(
                    func.ST_Contains(
                        self.store.db_classes.State.location,
                        WKTElement("POINT(123456 123456)", srid=4326),
                    )
                )
                .one_or_none()
            )
            # There is no State object with location (123456 123456). Should return None
            self.assertIsNone(first_state)


class SpatialDataPostGISTestCase(unittest.TestCase):
    def setUp(self):
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
            with self.store.session_scope():
                self.store.initialise()
                self.store.populate_reference(TEST_DATA_PATH)
                self.store.populate_metadata(TEST_DATA_PATH)
                self.store.populate_measurement(TEST_DATA_PATH)
        except OperationalError:
            print("Database schema and data population failed! Test is skipping.")

    def tearDown(self):
        try:
            self.postgres.stop()
        except AttributeError:
            return

    def test_location(self):
        """Test location saved as Geo Point and it is possible to filter State objects on PostGIS"""
        if self.postgres is None:
            self.skipTest("Postgres is not available. Test is skipping")

        with self.store.session_scope():
            # Filter state object by spatial location
            first_state = (
                self.store.session.query(self.store.db_classes.State)
                .filter(
                    func.ST_Contains(
                        self.store.db_classes.State.location,
                        WKTElement("POINT(46.000 32.000)", srid=4326),
                    )
                )
                .one()
            )

            correct_loc = Location()
            correct_loc.set_latitude_decimal_degrees(32)
            correct_loc.set_longitude_decimal_degrees(46)

            assert first_state.location == correct_loc

    def test_non_existing_location(self):
        """Test filtering State objects by non existing point returns None on PostGIS"""

        if self.store is None:
            self.skipTest("Postgres is not available. Test is skipping")

        with self.store.session_scope():
            # Filter state object by spatial location
            first_state = (
                self.store.session.query(self.store.db_classes.State)
                .filter(
                    func.ST_Contains(
                        self.store.db_classes.State.location,
                        WKTElement("POINT(123456 123456)", srid=4326),
                    )
                )
                .one_or_none()
            )
            # There is no State object with location (123456 123456). Should return None
            self.assertIsNone(first_state)


if __name__ == "__main__":
    unittest.main()
