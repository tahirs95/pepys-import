from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    FetchedValue,
    DATE,
    ForeignKey,
    DateTime,
)
from sqlalchemy.dialects.postgresql import UUID, TIMESTAMP, DOUBLE_PRECISION

from geoalchemy2 import Geometry

from .db_base import BasePostGIS
from .db_status import TableTypes
from uuid import uuid4


class Entry(BasePostGIS):
    __tablename__ = "Entry"
    table_type = TableTypes.METADATA

    entry_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    table_type_id = Column(Integer, nullable=False)
    created_user = Column(Integer)
    created_date = Column(DateTime, default=datetime.utcnow)

    @classmethod
    def add_to_entries(cls, session, table_type_id, table_name):
        # ensure table type exists to satisfy foreign key constraint
        TableType().add_to_table_types(session, table_type_id, table_name)

        # No cache for entries, just add new one when called
        entry_obj = Entry(table_type_id=table_type_id, created_user=1)

        session.add(entry_obj)
        session.flush()

        return entry_obj.entry_id


class TableType(BasePostGIS):
    __tablename__ = "TableTypes"
    table_type = TableTypes.METADATA

    table_type_id = Column(Integer, nullable=False, primary_key=True)
    name = Column(String(150))
    created_date = Column(DateTime, default=datetime.utcnow)

    @classmethod
    def search_table_type(cls, session, table_type_id):
        # search for any table type with this id
        return (
            session.query(TableType)
            .filter(TableType.table_type_id == table_type_id)
            .first()
        )

    @classmethod
    def add_to_table_types(cls, session, table_type_id, table_name):
        table_type = cls.search_table_type(session, table_type_id)
        if table_type is None:
            # enough info to proceed and create entry
            table_type = TableType(table_type_id=table_type_id, name=table_name)
            session.add(table_type)
            session.flush()

        return table_type


# Metadata Tables
class HostedBy(BasePostGIS):
    __tablename__ = "HostedBy"
    table_type = TableTypes.METADATA
    table_type_id = 1
    table_name = "HostedBy"

    hosted_by_id = Column(UUID(), primary_key=True, default=uuid4)
    subject_id = Column(
        UUID(as_uuid=True), ForeignKey("Platforms.platform_id"), nullable=False
    )
    host_id = Column(
        UUID(as_uuid=True), ForeignKey("Platforms.platform_id"), nullable=False
    )
    hosted_from = Column(DATE, nullable=False)
    host_to = Column(DATE, nullable=False)
    privacy_id = Column(
        UUID(as_uuid=True), ForeignKey("Privacies.privacy_id"), nullable=False
    )
    created_date = Column(DateTime, default=datetime.utcnow)


class Sensors(BasePostGIS):
    __tablename__ = "Sensors"
    table_type = TableTypes.METADATA
    table_type_id = 2

    sensor_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    name = Column(String(150), nullable=False)
    sensor_type_id = Column(
        UUID(as_uuid=True), ForeignKey("SensorTypes.sensor_type_id"), nullable=False
    )
    platform_id = Column(
        UUID(as_uuid=True), ForeignKey("Platforms.platform_id"), nullable=False
    )
    created_date = Column(DateTime, default=datetime.utcnow)

    @classmethod
    def add_to_sensors(cls, session, name, sensor_type, host):
        sensor_type = SensorTypes().search_sensor_type(session, sensor_type)
        host = Platforms().search_platform(session, host)

        if sensor_type is None or host is None:
            text = f"There is missing value(s) in '{sensor_type}, {host}'!"
            raise Exception(text)

        entry_id = Entry().add_to_entries(
            session, Sensors.table_type_id, Sensors.__tablename__
        )

        sensor_obj = Sensors(
            sensor_id=entry_id,
            name=name,
            sensor_type_id=sensor_type.sensor_type_id,
            platform_id=host.platform_id,
        )
        session.add(sensor_obj)
        session.flush()

        return sensor_obj


class Platforms(BasePostGIS):
    __tablename__ = "Platforms"
    table_type = TableTypes.METADATA
    table_type_id = 3

    platform_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    name = Column(String(150))
    nationality_id = Column(
        UUID(as_uuid=True), ForeignKey("Nationalities.nationality_id"), nullable=False
    )
    platform_type_id = Column(
        UUID(as_uuid=True), ForeignKey("PlatformTypes.platform_type_id"), nullable=False
    )
    privacy_id = Column(
        UUID(as_uuid=True), ForeignKey("Privacies.privacy_id"), nullable=False
    )
    created_date = Column(DateTime, default=datetime.utcnow)

    @classmethod
    def search_platform(cls, session, name):
        # search for any platform with this name
        return session.query(Platforms).filter(Platforms.name == name).first()

    @staticmethod
    def get_sensor(session, all_sensors, sensor_name, sensor_type=None, privacy=None):
        """
        Lookup or create a sensor of this name for this platform. Specified sensor
        will be added to the sensors table.
        Args:
            sensor_name: {String} -- Name of Sensor
            sensor_type: {String} -- Type of Sensor
            privacy: {String} -- Name of Privacy

        Returns:
            A Sensor object that can be passed to the add_state() function of Datafile.
        """

        # return True if provided sensor exists
        def check_sensor(name):
            if next((sensor for sensor in all_sensors if sensor.name == name), None):
                # A sensor already exists with that name
                return False

            return True

        if len(sensor_name) == 0:
            raise Exception("Please enter sensor name!")
        elif check_sensor(sensor_name):
            platform = session.query(Platforms).first()
            return Sensors().add_to_sensors(
                session=session,
                name=sensor_name,
                sensor_type=sensor_type,
                host=platform.name
                # privacy=privacy,
            )
        else:
            return session.query(Sensors).filter(Sensors.name == sensor_name).first()


class Tasks(BasePostGIS):
    __tablename__ = "Tasks"
    table_type = TableTypes.METADATA
    table_type_id = 4
    table_name = "Tasks"

    task_id = Column(UUID(), primary_key=True, default=uuid4)
    parent_id = Column(UUID(as_uuid=True), ForeignKey("Tasks.task_id"), nullable=False)
    start = Column(TIMESTAMP, nullable=False)
    end = Column(TIMESTAMP, nullable=False)
    environment = Column(String(150))
    location = Column(String(150))
    privacy_id = Column(
        UUID(as_uuid=True), ForeignKey("Privacies.privacy_id"), nullable=False
    )
    created_date = Column(DateTime, default=datetime.utcnow)


class Participants(BasePostGIS):
    __tablename__ = "Participants"
    table_type = TableTypes.METADATA
    table_type_id = 5
    table_name = "Participants"

    participant_id = Column(UUID(), primary_key=True, default=uuid4)
    platform_id = Column(
        UUID(as_uuid=True), ForeignKey("Platforms.platform_id"), nullable=False
    )
    task_id = Column(UUID(as_uuid=True), ForeignKey("Tasks.task_id"), nullable=False)
    start = Column(TIMESTAMP)
    end = Column(TIMESTAMP)
    force = Column(String(150))
    privacy_id = Column(
        UUID(as_uuid=True), ForeignKey("Privacies.privacy_id"), nullable=False
    )
    created_date = Column(DateTime, default=datetime.utcnow)


class Datafiles(BasePostGIS):
    __tablename__ = "Datafiles"
    table_type = TableTypes.METADATA
    table_type_id = 6  # Only needed for tables referenced by Entry table

    datafile_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    simulated = Column(Boolean)
    privacy_id = Column(
        UUID(as_uuid=True), ForeignKey("Privacies.privacy_id"), nullable=False
    )
    datafile_type_id = Column(
        UUID(as_uuid=True), ForeignKey("DatafileTypes.datafile_type_id"), nullable=False
    )
    reference = Column(String(150))
    url = Column(String(150))
    created_date = Column(DateTime, default=datetime.utcnow)

    def create_state(self, sensor, timestamp):
        state = States(
            sensor_id=sensor.sensor_id, time=timestamp, source_id=self.datafile_id
        )
        return state

    def create_contact(self, sensor, timestamp):
        contact = Contacts(
            sensor_id=sensor.sensor_id, time=timestamp, source_id=self.datafile_id
        )
        return contact

    def create_comment(self, sensor, timestamp, comment, comment_type):
        comment = Comments(
            time=timestamp,
            content=comment,
            comment_type_id=comment_type.comment_type_id,
            source_id=self.datafile_id,
        )
        return comment

    def validate(self):
        return True

    # def verify(self):
    #     pass


class Synonyms(BasePostGIS):
    __tablename__ = "Synonyms"
    table_type = TableTypes.METADATA
    table_type_id = 7
    table_name = "Synonyms"

    synonym_id = Column(UUID(), primary_key=True, default=uuid4)
    table = Column(String(150), nullable=False)
    synonym = Column(String(150), nullable=False)
    created_date = Column(DateTime, default=datetime.utcnow)


class Changes(BasePostGIS):
    __tablename__ = "Changes"
    table_type = TableTypes.METADATA
    table_type_id = 8
    table_name = "Changes"

    change_id = Column(UUID(), primary_key=True, default=uuid4)
    user = Column(String(150), nullable=False)
    modified = Column(DATE, nullable=False)
    reason = Column(String(500), nullable=False)
    created_date = Column(DateTime, default=datetime.utcnow)


class Logs(BasePostGIS):
    __tablename__ = "Logs"
    table_type = TableTypes.METADATA
    table_type_id = 9
    table_name = "Log"

    log_id = Column(UUID(), primary_key=True, default=uuid4)
    table = Column(String(150), nullable=False)
    id = Column(UUID(as_uuid=True), ForeignKey("Logs.log_id"), nullable=False)
    field = Column(String(150), nullable=False)
    new_value = Column(String(150), nullable=False)
    change_id = Column(UUID, nullable=False)
    created_date = Column(DateTime, default=datetime.utcnow)


class Extractions(BasePostGIS):
    __tablename__ = "Extractions"
    table_type = TableTypes.METADATA
    table_type_id = 10
    table_name = "Extractions"

    extraction_id = Column(UUID(), primary_key=True, default=uuid4)
    table = Column(String(150), nullable=False)
    field = Column(String(150), nullable=False)
    chars = Column(String(150), nullable=False)
    created_date = Column(DateTime, default=datetime.utcnow)


class Tags(BasePostGIS):
    __tablename__ = "Tags"
    table_type = TableTypes.METADATA
    table_type_id = 11
    table_name = "Tags"

    tag_id = Column(UUID(), primary_key=True, default=uuid4)
    name = Column(String(150), nullable=False)
    created_date = Column(DateTime, default=datetime.utcnow)


class TaggedItems(BasePostGIS):
    __tablename__ = "TaggedItems"
    table_type = TableTypes.METADATA
    table_type_id = 12
    table_name = "TaggedItems"

    tagged_item_id = Column(UUID(), primary_key=True, default=uuid4)
    tag_id = Column(UUID(as_uuid=True), ForeignKey("Tags.tag_id"), nullable=False)
    # TODO: what is fk measurements?
    item_id = Column(UUID(as_uuid=True), nullable=False)
    tagged_by_id = Column(
        UUID(as_uuid=True), ForeignKey("Users.user_id"), nullable=False
    )
    private = Column(Boolean, nullable=False)
    tagged_on = Column(DATE, nullable=False)
    created_date = Column(DateTime, default=datetime.utcnow)


# Reference Tables
class PlatformTypes(BasePostGIS):
    __tablename__ = "PlatformTypes"
    table_type = TableTypes.REFERENCE
    table_type_id = 13

    platform_type_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    name = Column(String(150), nullable=False)
    created_date = Column(DateTime, default=datetime.utcnow)


class Nationalities(BasePostGIS):
    __tablename__ = "Nationalities"
    table_type = TableTypes.REFERENCE
    table_type_id = 14

    nationality_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    name = Column(String(150), nullable=False)
    created_date = Column(DateTime, default=datetime.utcnow)


class GeometryTypes(BasePostGIS):
    __tablename__ = "GeometryTypes"
    table_type = TableTypes.REFERENCE
    table_type_id = 15

    geo_type_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    name = Column(String(150), nullable=False)
    created_date = Column(DateTime, default=datetime.utcnow)


class GeometrySubTypes(BasePostGIS):
    __tablename__ = "GeometrySubTypes"
    table_type = TableTypes.REFERENCE
    table_type_id = 16

    geo_sub_type_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    name = Column(String(150), nullable=False)
    # parent = Column(UUID(as_uuid=True), ForeignKey("GeometryTypes.geometry_type_id"))
    parent = Column(UUID, nullable=False)
    created_date = Column(DateTime, default=datetime.utcnow)


class Users(BasePostGIS):
    __tablename__ = "Users"
    table_type = TableTypes.REFERENCE
    table_type_id = 17

    user_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    name = Column(String(150), nullable=False)
    created_date = Column(DateTime, default=datetime.utcnow)


class UnitTypes(BasePostGIS):
    __tablename__ = "UnitTypes"
    table_type = TableTypes.REFERENCE
    table_type_id = 18

    unit_type_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    units = Column(String(150), nullable=False)
    created_date = Column(DateTime, default=datetime.utcnow)


class ClassificationTypes(BasePostGIS):
    __tablename__ = "ClassificationTypes"
    table_type = TableTypes.REFERENCE
    table_type_id = 19

    class_type_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    class_type = Column(String(150), nullable=False)
    created_date = Column(DateTime, default=datetime.utcnow)


class ContactTypes(BasePostGIS):
    __tablename__ = "ContactTypes"
    table_type = TableTypes.REFERENCE
    table_type_id = 20

    contact_type_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    contact_type = Column(String(150), nullable=False)
    created_date = Column(DateTime, default=datetime.utcnow)


class SensorTypes(BasePostGIS):
    __tablename__ = "SensorTypes"
    table_type = TableTypes.REFERENCE
    table_type_id = 21

    # TODO: server default doesn't work for sensor_type_id
    sensor_type_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    name = Column(String(150), nullable=False)
    created_date = Column(DateTime, default=datetime.utcnow)

    @classmethod
    def search_sensor_type(cls, session, name):
        # search for any sensor type featuring this name
        return session.query(SensorTypes).filter(SensorTypes.name == name).first()


class Privacies(BasePostGIS):
    __tablename__ = "Privacies"
    table_type = TableTypes.REFERENCE
    table_type_id = 22

    privacy_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    name = Column(String(150), nullable=False)
    created_date = Column(DateTime, default=datetime.utcnow)


class DatafileTypes(BasePostGIS):
    __tablename__ = "DatafileTypes"
    table_type = TableTypes.REFERENCE
    table_type_id = 23

    datafile_type_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    name = Column(String(150), nullable=False)
    created_date = Column(DateTime, default=datetime.utcnow)


class MediaTypes(BasePostGIS):
    __tablename__ = "MediaTypes"
    table_type = TableTypes.REFERENCE
    table_type_id = 24

    media_type_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    name = Column(String(150), nullable=False)
    created_date = Column(DateTime, default=datetime.utcnow)


class CommentTypes(BasePostGIS):
    __tablename__ = "CommentTypes"
    table_type = TableTypes.REFERENCE
    table_type_id = 25

    comment_type_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    name = Column(String(150), nullable=False)
    created_date = Column(DateTime, default=datetime.utcnow)


class CommodityTypes(BasePostGIS):
    __tablename__ = "CommodityTypes"
    table_type = TableTypes.REFERENCE
    table_type_id = 26

    commodity_type_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    name = Column(String(150), nullable=False)
    created_date = Column(DateTime, default=datetime.utcnow)


class ConfidenceLevels(BasePostGIS):
    __tablename__ = "ConfidenceLevels"
    table_type = TableTypes.REFERENCE
    table_type_id = 27  # Only needed for tables referenced by Entry table

    confidence_level_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    level = Column(String(150), nullable=False)
    created_date = Column(DateTime, default=datetime.utcnow)


# Measurements Tables
class States(BasePostGIS):
    __tablename__ = "States"
    table_type = TableTypes.MEASUREMENT
    table_type_id = 28

    state_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    time = Column(TIMESTAMP, nullable=False)
    sensor_id = Column(
        UUID(as_uuid=True), ForeignKey("Sensors.sensor_id"), nullable=False
    )
    location = Column(Geometry(geometry_type="POINT", srid=0))
    heading = Column(DOUBLE_PRECISION)
    course = Column(DOUBLE_PRECISION)
    speed = Column(DOUBLE_PRECISION)
    source_id = Column(
        UUID(as_uuid=True), ForeignKey("Datafiles.datafile_id"), nullable=False
    )
    privacy_id = Column(UUID(as_uuid=True), ForeignKey("Privacies.privacy_id"))
    created_date = Column(DateTime, default=datetime.utcnow)

    def submit(self, session):
        """Submit intermediate object to the DB"""
        session.add(self)
        session.flush()

        return self


class Contacts(BasePostGIS):
    __tablename__ = "Contacts"
    table_type = TableTypes.MEASUREMENT
    table_type_id = 29

    contact_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    name = Column(String(150), nullable=False)
    sensor_id = Column(
        UUID(as_uuid=True), ForeignKey("Sensors.sensor_id"), nullable=False
    )
    time = Column(TIMESTAMP, nullable=False)
    bearing = Column(DOUBLE_PRECISION)
    rel_bearing = Column(DOUBLE_PRECISION)
    freq = Column(DOUBLE_PRECISION)
    location = Column(Geometry(geometry_type="POINT", srid=4326))
    major = Column(DOUBLE_PRECISION)
    minor = Column(DOUBLE_PRECISION)
    orientation = Column(DOUBLE_PRECISION)
    classification = Column(String(150))
    confidence = Column(String(150))
    contact_type = Column(String(150))
    mla = Column(DOUBLE_PRECISION)
    sla = Column(DOUBLE_PRECISION)
    subject_id = Column(
        UUID(as_uuid=True), ForeignKey("Platforms.platform_id"), nullable=False
    )
    source_id = Column(
        UUID(as_uuid=True), ForeignKey("Datafiles.datafile_id"), nullable=False
    )
    privacy_id = Column(UUID(as_uuid=True), ForeignKey("Privacies.privacy_id"))
    created_date = Column(DateTime, default=datetime.utcnow)

    def set_name(self, name):
        self.name = name

    def set_subject(self, platform):
        self.subject_id = platform.platform_id

    # def set_bearing(self, bearing):
    #     self.bearing = bearing
    #
    # def set_rel_bearing(self, rel_bearing):
    #     self.rel_bearing = rel_bearing
    #
    # def set_frequency(self, frequency):
    #     self.freq = frequency
    #
    # def set_privacy(self, privacy_type):
    #     self.privacy_id = privacy_type.privacy_id

    def submit(self, session):
        """Submit intermediate object to the DB"""
        session.add(self)
        session.flush()

        return self


class Activations(BasePostGIS):
    __tablename__ = "Activations"
    table_type = TableTypes.MEASUREMENT
    table_type_id = 30

    activation_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    name = Column(String(150), nullable=False)
    sensor_id = Column(
        UUID(as_uuid=True), ForeignKey("Sensors.sensor_id"), nullable=False
    )
    start = Column(TIMESTAMP, nullable=False)
    end = Column(TIMESTAMP, nullable=False)
    min_range = Column(DOUBLE_PRECISION)
    max_range = Column(DOUBLE_PRECISION)
    left_arc = Column(DOUBLE_PRECISION)
    right_arc = Column(DOUBLE_PRECISION)
    source_id = Column(
        UUID(as_uuid=True), ForeignKey("Datafiles.datafile_id"), nullable=False
    )
    privacy_id = Column(UUID(as_uuid=True), ForeignKey("Privacies.privacy_id"))
    created_date = Column(DateTime, default=datetime.utcnow)


class LogsHoldings(BasePostGIS):
    __tablename__ = "LogsHoldings"
    table_type = TableTypes.MEASUREMENT
    table_type_id = 31

    logs_holding_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    time = Column(TIMESTAMP, nullable=False)
    quantity = Column(DOUBLE_PRECISION, nullable=False)
    unit_type_id = Column(
        UUID(as_uuid=True), ForeignKey("UnitTypes.unit_type_id"), nullable=False
    )
    platform_id = Column(
        UUID(as_uuid=True), ForeignKey("Platforms.platform_id"), nullable=False
    )
    comment = Column(String(150), nullable=False)
    source_id = Column(
        UUID(as_uuid=True), ForeignKey("Datafiles.datafile_id"), nullable=False
    )
    privacy_id = Column(UUID(as_uuid=True), ForeignKey("Privacies.privacy_id"))
    created_date = Column(DateTime, default=datetime.utcnow)


class Comments(BasePostGIS):
    __tablename__ = "Comments"
    table_type = TableTypes.MEASUREMENT
    table_type_id = 32

    comment_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    platform_id = Column(
        UUID(as_uuid=True), ForeignKey("Platforms.platform_id"), nullable=False
    )
    time = Column(TIMESTAMP, nullable=False)
    comment_type_id = Column(UUID(as_uuid=True), nullable=False)
    content = Column(String(150), nullable=False)
    source_id = Column(
        UUID(as_uuid=True), ForeignKey("Datafiles.datafile_id"), nullable=False
    )
    privacy_id = Column(UUID(as_uuid=True), ForeignKey("Privacies.privacy_id"))
    created_date = Column(DateTime, default=datetime.utcnow)

    def set_platform(self, platform):
        self.platform_id = platform.platform_id

    # def set_privacy(self, privacy_type):
    #     self.privacy_id = privacy_type.privacy_id

    def submit(self, session):
        """Submit intermediate object to the DB"""
        session.add(self)
        session.flush()

        return self


class Geometries(BasePostGIS):
    __tablename__ = "Geometries"
    table_type = TableTypes.MEASUREMENT
    table_type_id = 33

    geometry_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    geometry = Column(Geometry, nullable=False)
    name = Column(String(150), nullable=False)
    geo_type_id = Column(
        UUID(as_uuid=True), ForeignKey("GeometryTypes.geo_type_id"), nullable=False
    )
    geo_sub_type_id = Column(
        UUID(as_uuid=True),
        ForeignKey("GeometrySubTypes.geo_sub_type_id"),
        nullable=False,
    )
    start = Column(TIMESTAMP)
    end = Column(TIMESTAMP)
    task_id = Column(UUID(as_uuid=True))
    subject_platform_id = Column(
        UUID(as_uuid=True), ForeignKey("Platforms.platform_id")
    )
    sensor_platform_id = Column(UUID(as_uuid=True), ForeignKey("Platforms.platform_id"))
    source_id = Column(
        UUID(as_uuid=True), ForeignKey("Datafiles.datafile_id"), nullable=False
    )
    privacy_id = Column(UUID(as_uuid=True), ForeignKey("Privacies.privacy_id"))
    created_date = Column(DateTime, default=datetime.utcnow)


class Media(BasePostGIS):
    __tablename__ = "Media"
    table_type = TableTypes.MEASUREMENT
    table_type_id = 34

    media_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    platform_id = Column(UUID(as_uuid=True), ForeignKey("Platforms.platform_id"))
    subject_id = Column(UUID(as_uuid=True), ForeignKey("Platforms.platform_id"))
    sensor_id = Column(UUID(as_uuid=True), ForeignKey("Sensors.sensor_id"))
    location = Column(Geometry(geometry_type="POINT", srid=4326))
    time = Column(TIMESTAMP)
    media_type_id = Column(UUID(as_uuid=True), nullable=False)
    url = Column(String(150), nullable=False)
    source_id = Column(
        UUID(as_uuid=True), ForeignKey("Datafiles.datafile_id"), nullable=False
    )
    privacy_id = Column(UUID(as_uuid=True), ForeignKey("Privacies.privacy_id"))
    created_date = Column(DateTime, default=datetime.utcnow)
