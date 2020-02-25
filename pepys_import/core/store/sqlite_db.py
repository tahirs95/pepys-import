from datetime import datetime

from sqlalchemy import Column, Integer, String, Boolean, DATE, DateTime
from sqlalchemy.dialects.sqlite import TIMESTAMP, REAL

from geoalchemy2 import Geometry

from pepys_import.core.store.db_base import BaseSpatiaLite
from pepys_import.core.store.db_status import TableTypes
from pepys_import.core.store import constants


class Entry(BaseSpatiaLite):
    __tablename__ = constants.ENTRY
    table_type = TableTypes.METADATA

    entry_id = Column(Integer, primary_key=True)
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


class TableType(BaseSpatiaLite):
    __tablename__ = constants.TABLE_TYPE
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
class HostedBy(BaseSpatiaLite):
    __tablename__ = constants.HOSTED_BY
    table_type = TableTypes.METADATA
    table_type_id = 1

    hosted_by_id = Column(Integer, primary_key=True)
    subject_id = Column(Integer, nullable=False)
    host_id = Column(Integer, nullable=False)
    hosted_from = Column(DATE, nullable=False)
    host_to = Column(DATE, nullable=False)
    privacy_id = Column(Integer, nullable=False)
    created_date = Column(DateTime, default=datetime.utcnow)


class Sensor(BaseSpatiaLite):
    __tablename__ = constants.SENSOR
    table_type = TableTypes.METADATA
    table_type_id = 2

    sensor_id = Column(Integer, primary_key=True)
    name = Column(String(150), nullable=False)
    sensor_type_id = Column(Integer, nullable=False)
    platform_id = Column(Integer, nullable=False)
    created_date = Column(DateTime, default=datetime.utcnow)

    @classmethod
    def find_sensor(cls, data_store, sensor_name):
        """
        This method tries to find a Sensor entity with the given sensor_name. If it
        finds, it returns the entity. If it is not found, it searches synonyms.

        :param data_store: A :class:`DataStore` object
        :type data_store: :class:`DataStore`
        :param sensor_name: Name of :class:`Sensor`
        :type sensor_name: String
        :return:
        """
        sensor = (
            data_store.session.query(data_store.db_classes.Sensor)
            .filter(data_store.db_classes.Sensor.name == sensor_name)
            .first()
        )
        if sensor:
            return sensor

        # Sensor is not found, try to find a synonym
        return data_store.synonym_search(
            name=sensor_name,
            table=data_store.db_classes.Sensor,
            pk_field=data_store.db_classes.Sensor.sensor_id,
        )

    @classmethod
    def add_to_sensors(cls, session, name, sensor_type, host):
        sensor_type = SensorType().search_sensor_type(session, sensor_type)
        host = Platform().search_platform(session, host)

        entry_id = Entry().add_to_entries(
            session, Sensor.table_type_id, Sensor.__tablename__
        )

        sensor_obj = Sensor(
            sensor_id=entry_id,
            name=name,
            sensor_type_id=sensor_type.sensor_type_id,
            platform_id=host.platform_id,
        )
        session.add(sensor_obj)
        session.flush()

        return sensor_obj


class Platform(BaseSpatiaLite):
    __tablename__ = constants.PLATFORM
    table_type = TableTypes.METADATA
    table_type_id = 3

    platform_id = Column(Integer, primary_key=True)
    name = Column(String(150), nullable=False)
    pennant = Column(String(10))
    trigraph = Column(String(3))
    quadgraph = Column(String(4))
    nationality_id = Column(Integer, nullable=False)
    platform_type_id = Column(Integer, nullable=False)
    privacy_id = Column(Integer, nullable=False)
    created_date = Column(DateTime, default=datetime.utcnow)

    @classmethod
    def search_platform(cls, session, name):
        # search for any platform with this name
        return session.query(Platform).filter(Platform.name == name).first()

    def get_sensor(self, data_store, sensor_name=None, sensor_type=None, privacy=None):
        """
         Lookup or create a sensor of this name for this :class:`Platform`.
         Specified sensor will be added to the :class:`Sensor` table.
         It uses find_sensor method to search existing sensors.

        :param data_store: DataStore object to to query DB and use missing data resolver
        :type data_store: :class:`DataStore`
        :param sensor_name: Name of :class:`Sensor`
        :type sensor_name: String
        :param sensor_type: Type of :class:`Sensor`
        :type sensor_type: SensorType
        :param privacy: Privacy of :class:`Sensor`
        :type privacy: Privacy
        :return: Created :class:`Sensor` entity
        :rtype: Sensor
        """
        sensor = Sensor().find_sensor(data_store, sensor_name)
        if sensor:
            return sensor

        if sensor_type is None or privacy is None:
            (
                sensor_name,
                sensor_type,
                privacy,
            ) = data_store.missing_data_resolver.resolve_sensor(
                data_store, sensor_name, sensor_type, privacy
            )

        assert type(sensor_type), SensorType
        assert type(privacy), Privacy

        return Sensor().add_to_sensors(
            session=data_store.session,
            name=sensor_name,
            sensor_type=sensor_type.name,
            host=self.name,
        )


class Task(BaseSpatiaLite):
    __tablename__ = constants.TASK
    table_type = TableTypes.METADATA
    table_type_id = 4

    task_id = Column(Integer, primary_key=True)
    name = Column(String(150), nullable=False)
    parent_id = Column(Integer, nullable=False)
    start = Column(TIMESTAMP, nullable=False)
    end = Column(TIMESTAMP, nullable=False)
    environment = Column(String(150))
    location = Column(String(150))
    privacy_id = Column(Integer, nullable=False)
    created_date = Column(DateTime, default=datetime.utcnow)


class Participant(BaseSpatiaLite):
    __tablename__ = constants.PARTICIPANT
    table_type = TableTypes.METADATA
    table_type_id = 5

    participant_id = Column(Integer, primary_key=True)
    platform_id = Column(Integer, nullable=False)
    task_id = Column(Integer, nullable=False)
    start = Column(TIMESTAMP)
    end = Column(TIMESTAMP)
    force = Column(String(150))
    privacy_id = Column(Integer, nullable=False)
    created_date = Column(DateTime, default=datetime.utcnow)


class Datafile(BaseSpatiaLite):
    __tablename__ = constants.DATAFILE
    table_type = TableTypes.METADATA
    table_type_id = 6

    datafile_id = Column(Integer, primary_key=True)
    simulated = Column(Boolean, nullable=False)
    privacy_id = Column(Integer, nullable=False)
    datafile_type_id = Column(Integer, nullable=False)
    reference = Column(String(150))
    url = Column(String(150))
    created_date = Column(DateTime, default=datetime.utcnow)

    def create_state(self, sensor, timestamp):
        state = State(
            sensor_id=sensor.sensor_id, time=timestamp, source_id=self.datafile_id
        )
        return state

    def create_contact(self, sensor, timestamp):
        contact = Contact(
            sensor_id=sensor.sensor_id, time=timestamp, source_id=self.datafile_id
        )
        return contact

    def create_comment(self, sensor, timestamp, comment, comment_type):
        comment = Comment(
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


class Synonym(BaseSpatiaLite):
    __tablename__ = constants.SYNONYM
    table_type = TableTypes.METADATA
    table_type_id = 7

    synonym_id = Column(Integer, primary_key=True)
    table = Column(String(150), nullable=False)
    entity = Column(Integer, nullable=False)
    synonym = Column(String(150), nullable=False)
    created_date = Column(DateTime, default=datetime.utcnow)


class Change(BaseSpatiaLite):
    __tablename__ = constants.CHANGE
    table_type = TableTypes.METADATA
    table_type_id = 8

    change_id = Column(Integer, primary_key=True)
    user = Column(String(150), nullable=False)
    modified = Column(DATE, nullable=False)
    reason = Column(String(500), nullable=False)
    created_date = Column(DateTime, default=datetime.utcnow)


class Log(BaseSpatiaLite):
    __tablename__ = constants.LOG
    table_type = TableTypes.METADATA
    table_type_id = 9

    log_id = Column(Integer, primary_key=True)
    table = Column(String(150), nullable=False)
    id = Column(Integer, nullable=False)
    field = Column(String(150), nullable=False)
    new_value = Column(String(150), nullable=False)
    change_id = Column(Integer, nullable=False)
    created_date = Column(DateTime, default=datetime.utcnow)


class Extraction(BaseSpatiaLite):
    __tablename__ = constants.EXTRACTION
    table_type = TableTypes.METADATA
    table_type_id = 10

    extraction_id = Column(Integer, primary_key=True)
    table = Column(String(150), nullable=False)
    field = Column(String(150), nullable=False)
    chars = Column(String(150), nullable=False)
    created_date = Column(DateTime, default=datetime.utcnow)


class Tag(BaseSpatiaLite):
    __tablename__ = constants.TAG
    table_type = TableTypes.METADATA
    table_type_id = 11

    tag_id = Column(Integer, primary_key=True)
    name = Column(String(150), nullable=False)
    created_date = Column(DateTime, default=datetime.utcnow)


class TaggedItem(BaseSpatiaLite):
    __tablename__ = constants.TAGGED_ITEM
    table_type = TableTypes.METADATA
    table_type_id = 12

    tagged_item_id = Column(Integer, primary_key=True)
    tag_id = Column(Integer, nullable=False)
    item_id = Column(Integer, nullable=False)
    tagged_by_id = Column(Integer, nullable=False)
    private = Column(Boolean, nullable=False)
    tagged_on = Column(DATE, nullable=False)
    created_date = Column(DateTime, default=datetime.utcnow)


# Reference Tables
class PlatformType(BaseSpatiaLite):
    __tablename__ = constants.PLATFORM_TYPE
    table_type = TableTypes.REFERENCE
    table_type_id = 13

    platform_type_id = Column(Integer, primary_key=True)
    name = Column(String(150))
    created_date = Column(DateTime, default=datetime.utcnow)


class Nationality(BaseSpatiaLite):
    __tablename__ = constants.NATIONALITY
    table_type = TableTypes.REFERENCE
    table_type_id = 14

    nationality_id = Column(Integer, primary_key=True)
    name = Column(String(150), nullable=False)
    created_date = Column(DateTime, default=datetime.utcnow)


class GeometryType(BaseSpatiaLite):
    __tablename__ = constants.GEOMETRY_TYPE
    table_type = TableTypes.REFERENCE
    table_type_id = 15

    geo_type_id = Column(Integer, primary_key=True)
    name = Column(String(150), nullable=False)
    created_date = Column(DateTime, default=datetime.utcnow)


class GeometrySubType(BaseSpatiaLite):
    __tablename__ = constants.GEOMETRY_SUBTYPE
    table_type = TableTypes.REFERENCE
    table_type_id = 16

    geo_sub_type_id = Column(Integer, primary_key=True)
    name = Column(String(150), nullable=False)
    parent = Column(Integer, nullable=False)
    created_date = Column(DateTime, default=datetime.utcnow)


class User(BaseSpatiaLite):
    __tablename__ = constants.USER
    table_type = TableTypes.REFERENCE
    table_type_id = 17

    user_id = Column(Integer, primary_key=True)
    name = Column(String(150), nullable=False)
    created_date = Column(DateTime, default=datetime.utcnow)


class UnitType(BaseSpatiaLite):
    __tablename__ = constants.UNIT_TYPE
    table_type = TableTypes.REFERENCE
    table_type_id = 18

    unit_type_id = Column(Integer, primary_key=True)
    name = Column(String(150), nullable=False)
    created_date = Column(DateTime, default=datetime.utcnow)


class ClassificationType(BaseSpatiaLite):
    __tablename__ = constants.CLASSIFICATION_TYPE
    table_type = TableTypes.REFERENCE
    table_type_id = 19

    class_type_id = Column(Integer, primary_key=True)
    class_type = Column(String(150), nullable=False)
    created_date = Column(DateTime, default=datetime.utcnow)


class ContactType(BaseSpatiaLite):
    __tablename__ = constants.CONTACT_TYPE
    table_type = TableTypes.REFERENCE
    table_type_id = 20

    contact_type_id = Column(Integer, primary_key=True)
    contact_type = Column(String(150), nullable=False)
    created_date = Column(DateTime, default=datetime.utcnow)


class SensorType(BaseSpatiaLite):
    __tablename__ = constants.SENSOR_TYPE
    table_type = TableTypes.REFERENCE
    table_type_id = 21

    sensor_type_id = Column(Integer, primary_key=True)
    name = Column(String(150))
    created_date = Column(DateTime, default=datetime.utcnow)

    @classmethod
    def search_sensor_type(cls, session, name):
        # search for any sensor type featuring this name
        return session.query(SensorType).filter(SensorType.name == name).first()


class Privacy(BaseSpatiaLite):
    __tablename__ = constants.PRIVACY
    table_type = TableTypes.REFERENCE
    table_type_id = 22

    privacy_id = Column(Integer, primary_key=True)
    name = Column(String(150), nullable=False)
    created_date = Column(DateTime, default=datetime.utcnow)


class DatafileType(BaseSpatiaLite):
    __tablename__ = constants.DATAFILE_TYPE
    table_type = TableTypes.REFERENCE
    table_type_id = 23

    datafile_type_id = Column(Integer, primary_key=True)
    name = Column(String(150), nullable=False)
    created_date = Column(DateTime, default=datetime.utcnow)


class MediaType(BaseSpatiaLite):
    __tablename__ = constants.MEDIA_TYPE
    table_type = TableTypes.REFERENCE
    table_type_id = 24

    media_type_id = Column(Integer, primary_key=True)
    name = Column(String(150), nullable=False)
    created_date = Column(DateTime, default=datetime.utcnow)


class CommentType(BaseSpatiaLite):
    __tablename__ = constants.COMMENT_TYPE
    table_type = TableTypes.REFERENCE
    table_type_id = 25

    comment_type_id = Column(Integer, primary_key=True)
    name = Column(String(150), nullable=False)
    created_date = Column(DateTime, default=datetime.utcnow)


class CommodityType(BaseSpatiaLite):
    __tablename__ = constants.COMMODITY_TYPE
    table_type = TableTypes.REFERENCE
    table_type_id = 26

    commodity_type_id = Column(Integer, primary_key=True)
    name = Column(String(150), nullable=False)
    created_date = Column(DateTime, default=datetime.utcnow)


class ConfidenceLevel(BaseSpatiaLite):
    __tablename__ = constants.CONFIDENCE_LEVEL
    table_type = TableTypes.REFERENCE
    table_type_id = 27

    confidence_level_id = Column(Integer, primary_key=True)
    level = Column(String(150), nullable=False)
    created_date = Column(DateTime, default=datetime.utcnow)


# Measurements Tables
class State(BaseSpatiaLite):
    __tablename__ = constants.STATE
    table_type = TableTypes.MEASUREMENT
    table_type_id = 28

    state_id = Column(Integer, primary_key=True)
    time = Column(TIMESTAMP, nullable=False)
    sensor_id = Column(Integer, nullable=False)
    location = Column(Geometry(geometry_type="POINT", management=True))
    heading = Column(REAL)
    course = Column(REAL)
    speed = Column(REAL)
    source_id = Column(Integer, nullable=False)
    privacy_id = Column(Integer)
    created_date = Column(DateTime, default=datetime.utcnow)

    def submit(self, session):
        """Submit intermediate object to the DB"""
        session.add(self)
        session.flush()

        return self


class Contact(BaseSpatiaLite):
    __tablename__ = constants.CONTACT
    table_type = TableTypes.MEASUREMENT
    table_type_id = 29

    contact_id = Column(Integer, primary_key=True)
    name = Column(String(150), nullable=False)
    sensor_id = Column(Integer, nullable=False)
    time = Column(TIMESTAMP, nullable=False)
    bearing = Column(REAL)
    rel_bearing = Column(REAL)
    freq = Column(REAL)
    location = Column(Geometry(geometry_type="POINT", management=True))
    major = Column(REAL)
    minor = Column(REAL)
    orientation = Column(REAL)
    classification = Column(String(150))
    confidence = Column(String(150))
    contact_type = Column(String(150))
    mla = Column(REAL)
    sla = Column(REAL)
    subject_id = Column(Integer)
    source_id = Column(Integer, nullable=False)
    privacy_id = Column(Integer)
    created_date = Column(DateTime, default=datetime.utcnow)

    def submit(self, session):
        """Submit intermediate object to the DB"""
        session.add(self)
        session.flush()

        return self


class Activation(BaseSpatiaLite):
    __tablename__ = constants.ACTIVATION
    table_type = TableTypes.MEASUREMENT
    table_type_id = 30

    activation_id = Column(Integer, primary_key=True)
    name = Column(String(150), nullable=False)
    sensor_id = Column(Integer, nullable=False)
    start = Column(TIMESTAMP, nullable=False)
    end = Column(TIMESTAMP, nullable=False)
    min_range = Column(REAL)
    max_range = Column(REAL)
    left_arc = Column(REAL)
    right_arc = Column(REAL)
    source_id = Column(Integer, nullable=False)
    privacy_id = Column(Integer)
    created_date = Column(DateTime, default=datetime.utcnow)


class LogsHolding(BaseSpatiaLite):
    __tablename__ = constants.LOGS_HOLDING
    table_type = TableTypes.MEASUREMENT
    table_type_id = 31

    logs_holding_id = Column(Integer, primary_key=True)
    time = Column(TIMESTAMP, nullable=False)
    commodity_id = Column(Integer, nullable=False)
    quantity = Column(REAL, nullable=False)
    unit_type_id = Column(Integer, nullable=False)
    platform_id = Column(Integer, nullable=False)
    comment = Column(String(150), nullable=False)
    source_id = Column(Integer, nullable=False)
    privacy_id = Column(Integer)
    created_date = Column(DateTime, default=datetime.utcnow)


class Comment(BaseSpatiaLite):
    __tablename__ = constants.COMMENT
    table_type = TableTypes.MEASUREMENT
    table_type_id = 32

    comment_id = Column(Integer, primary_key=True)
    platform_id = Column(Integer)
    time = Column(TIMESTAMP, nullable=False)
    comment_type_id = Column(Integer, nullable=False)
    content = Column(String(150), nullable=False)
    source_id = Column(Integer, nullable=False)
    privacy_id = Column(Integer)
    created_date = Column(DateTime, default=datetime.utcnow)

    def submit(self, session):
        """Submit intermediate object to the DB"""
        session.add(self)
        session.flush()

        return self


class Geometry1(BaseSpatiaLite):
    __tablename__ = constants.GEOMETRY
    table_type = TableTypes.MEASUREMENT
    table_type_id = 33

    geometry_id = Column(Integer, primary_key=True)
    geometry = Column(
        Geometry(geometry_type="GEOMETRY", management=True), nullable=False
    )
    name = Column(String(150), nullable=False)
    geo_type_id = Column(Integer, nullable=False)
    geo_sub_type_id = Column(Integer, nullable=False)
    start = Column(TIMESTAMP)
    end = Column(TIMESTAMP)
    task_id = Column(Integer)
    subject_platform_id = Column(Integer)
    sensor_platform_id = Column(Integer)
    source_id = Column(Integer, nullable=False)
    privacy_id = Column(Integer)
    created_date = Column(DateTime, default=datetime.utcnow)


class Media(BaseSpatiaLite):
    __tablename__ = constants.MEDIA
    table_type = TableTypes.MEASUREMENT
    table_type_id = 34

    media_id = Column(Integer, primary_key=True)
    platform_id = Column(Integer)
    subject_id = Column(Integer)
    sensor_id = Column(Integer)
    location = Column(Geometry(geometry_type="POINT", management=True))
    time = Column(TIMESTAMP)
    media_type_id = Column(Integer, nullable=False)
    url = Column(String(150), nullable=False)
    source_id = Column(Integer, nullable=False)
    privacy_id = Column(Integer)
    created_date = Column(DateTime, default=datetime.utcnow)
