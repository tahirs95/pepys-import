from sqlalchemy import Column, Integer, String, Boolean, FetchedValue, DATE, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, TIMESTAMP, DOUBLE_PRECISION

from geoalchemy2 import Geometry

from .db_base import base_postgres as base
from .db_status import TableTypes
from uuid import uuid4


def map_uuid_type(val):
    # postgres needs to map to string
    return str(val)


class Entry(base):
    __tablename__ = "Entry"
    table_type = TableTypes.METADATA

    entry_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    table_type_id = Column(Integer, nullable=False)
    created_user = Column(Integer)


class TableType(base):
    __tablename__ = "TableTypes"
    table_type = TableTypes.METADATA

    table_type_id = Column(Integer, nullable=False, primary_key=True)
    name = Column(String(150))


# Metadata Tables
class HostedBy(base):
    __tablename__ = "HostedBy"
    table_type = TableTypes.METADATA
    table_type_id = 1
    table_name = "HostedBy"

    hosted_by_id = Column(UUID(), primary_key=True, server_default=FetchedValue())
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


class Sensors(base):
    __tablename__ = "Sensors"
    table_type = TableTypes.METADATA
    table_type_id = 2

    sensor_id = Column(
        UUID(as_uuid=True), primary_key=True, server_default=FetchedValue()
    )
    name = Column(String(150), nullable=False)
    sensor_type_id = Column(
        UUID(as_uuid=True), ForeignKey("SensorTypes.sensor_type_id"), nullable=False
    )
    platform_id = Column(
        UUID(as_uuid=True), ForeignKey("Platforms.platform_id"), nullable=False
    )


class Platforms(base):
    __tablename__ = "Platforms"
    table_type = TableTypes.METADATA
    table_type_id = 3

    platform_id = Column(
        UUID(as_uuid=True), primary_key=True, server_default=FetchedValue()
    )
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


class Tasks(base):
    __tablename__ = "Tasks"
    table_type = TableTypes.METADATA
    table_type_id = 4
    table_name = "Tasks"

    task_id = Column(UUID(), primary_key=True, server_default=FetchedValue())
    parent_id = Column(UUID(as_uuid=True), ForeignKey("Tasks.task_id"), nullable=False)
    start = Column(TIMESTAMP, nullable=False)
    end = Column(TIMESTAMP, nullable=False)
    environment = Column(String(150))
    location = Column(String(150))
    privacy_id = Column(
        UUID(as_uuid=True), ForeignKey("Privacies.privacy_id"), nullable=False
    )


class Participants(base):
    __tablename__ = "Participants"
    table_type = TableTypes.METADATA
    table_type_id = 5
    table_name = "Participants"

    participant_id = Column(UUID(), primary_key=True, server_default=FetchedValue())
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


class Datafiles(base):
    __tablename__ = "Datafiles"
    table_type = TableTypes.METADATA
    table_type_id = 6  # Only needed for tables referenced by Entry table

    datafile_id = Column(
        UUID(as_uuid=True), primary_key=True, server_default=FetchedValue()
    )
    simulated = Column(Boolean)
    privacy_id = Column(
        UUID(as_uuid=True), ForeignKey("Privacies.privacy_id"), nullable=False
    )
    datafile_type_id = Column(
        UUID(as_uuid=True), ForeignKey("DatafileTypes.datafile_type_id"), nullable=False
    )
    reference = Column(String(150))
    url = Column(String(150))


class Synonyms(base):
    __tablename__ = "Synonyms"
    table_type = TableTypes.METADATA
    table_type_id = 7
    table_name = "Synonyms"

    synonym_id = Column(UUID(), primary_key=True, server_default=FetchedValue())
    table = Column(String(150), nullable=False)
    synonym = Column(String(150), nullable=False)


class Changes(base):
    __tablename__ = "Changes"
    table_type = TableTypes.METADATA
    table_type_id = 8
    table_name = "Changes"

    change_id = Column(UUID(), primary_key=True, server_default=FetchedValue())
    user = Column(String(150), nullable=False)
    modified = Column(DATE, nullable=False)
    reason = Column(String(500), nullable=False)


class Logs(base):
    __tablename__ = "Logs"
    table_type = TableTypes.METADATA
    table_type_id = 9
    table_name = "Log"

    log_id = Column(UUID(), primary_key=True, server_default=FetchedValue())
    table = Column(String(150), nullable=False)
    id = Column(UUID(as_uuid=True), ForeignKey("Logs.log_id"), nullable=False)
    field = Column(String(150), nullable=False)
    new_value = Column(String(150), nullable=False)
    change_id = Column(UUID, nullable=False)


class Extractions(base):
    __tablename__ = "Extractions"
    table_type = TableTypes.METADATA
    table_type_id = 10
    table_name = "Extractions"

    extraction_id = Column(UUID(), primary_key=True, server_default=FetchedValue())
    table = Column(String(150), nullable=False)
    field = Column(String(150), nullable=False)
    chars = Column(String(150), nullable=False)


class Tags(base):
    __tablename__ = "Tags"
    table_type = TableTypes.METADATA
    table_type_id = 11
    table_name = "Tags"

    tag_id = Column(UUID(), primary_key=True, server_default=FetchedValue())
    name = Column(String(150), nullable=False)


class TaggedItems(base):
    __tablename__ = "TaggedItems"
    table_type = TableTypes.METADATA
    table_type_id = 12
    table_name = "TaggedItems"

    tagged_item_id = Column(UUID(), primary_key=True, server_default=FetchedValue())
    tag_id = Column(UUID(as_uuid=True), ForeignKey("Tags.tag_id"), nullable=False)
    # TODO: what is fk measurements?
    item_id = Column(UUID(as_uuid=True), nullable=False)
    tagged_by_id = Column(
        UUID(as_uuid=True), ForeignKey("Users.user_id"), nullable=False
    )
    private = Column(Boolean, nullable=False)
    tagged_on = Column(DATE, nullable=False)


# Reference Tables
class PlatformTypes(base):
    __tablename__ = "PlatformTypes"
    table_type = TableTypes.REFERENCE
    table_type_id = 13

    platform_type_id = Column(
        UUID(as_uuid=True), primary_key=True, server_default=FetchedValue()
    )
    name = Column(String(150), nullable=False)


class Nationalities(base):
    __tablename__ = "Nationalities"
    table_type = TableTypes.REFERENCE

    nationality_id = Column(
        UUID(as_uuid=True), primary_key=True, server_default=FetchedValue()
    )
    name = Column(String(150), nullable=False)


class GeometryTypes(base):
    __tablename__ = "GeometryTypes"
    table_type = TableTypes.REFERENCE
    table_type_id = 14

    geo_type_id = Column(
        UUID(as_uuid=True), primary_key=True, server_default=FetchedValue()
    )
    name = Column(String(150), nullable=False)


class GeometrySubTypes(base):
    __tablename__ = "GeometrySubTypes"
    table_type = TableTypes.REFERENCE
    table_type_id = 15

    geo_sub_type_id = Column(
        UUID(as_uuid=True), primary_key=True, server_default=FetchedValue()
    )
    name = Column(String(150), nullable=False)
    # parent = Column(UUID(as_uuid=True), ForeignKey("GeometryTypes.geometry_type_id"))
    parent = Column(UUID, nullable=False)


class Users(base):
    __tablename__ = "Users"
    table_type = TableTypes.REFERENCE
    table_type_id = 16

    user_id = Column(
        UUID(as_uuid=True), primary_key=True, server_default=FetchedValue()
    )
    name = Column(String(150), nullable=False)


class UnitTypes(base):
    __tablename__ = "UnitTypes"
    table_type = TableTypes.REFERENCE
    table_type_id = 17

    unit_type_id = Column(
        UUID(as_uuid=True), primary_key=True, server_default=FetchedValue()
    )
    units = Column(String(150), nullable=False)


class ClassificationTypes(base):
    __tablename__ = "ClassificationTypes"
    table_type = TableTypes.REFERENCE
    table_type_id = 18

    class_type_id = Column(
        UUID(as_uuid=True), primary_key=True, server_default=FetchedValue()
    )
    class_type = Column(String(150), nullable=False)


class ContactTypes(base):
    __tablename__ = "ContactTypes"
    table_type = TableTypes.REFERENCE
    table_type_id = 19

    contact_type_id = Column(
        UUID(as_uuid=True), primary_key=True, server_default=FetchedValue()
    )
    contact_type = Column(String(150), nullable=False)


class SensorTypes(base):
    __tablename__ = "SensorTypes"
    table_type = TableTypes.REFERENCE
    table_type_id = 20

    sensor_type_id = Column(
        UUID(as_uuid=True), primary_key=True, server_default=FetchedValue()
    )
    name = Column(String(150), nullable=False)


class Privacies(base):
    __tablename__ = "Privacies"
    table_type = TableTypes.REFERENCE
    table_type_id = 21

    privacy_id = Column(
        UUID(as_uuid=True), primary_key=True, server_default=FetchedValue()
    )
    name = Column(String(150), nullable=False)


class DatafileTypes(base):
    __tablename__ = "DatafileTypes"
    table_type = TableTypes.REFERENCE
    table_type_id = 22

    datafile_type_id = Column(
        UUID(as_uuid=True), primary_key=True, server_default=FetchedValue()
    )
    name = Column(String(150), nullable=False)


class MediaTypes(base):
    __tablename__ = "MediaTypes"
    table_type = TableTypes.REFERENCE
    table_type_id = 23

    media_type_id = Column(
        UUID(as_uuid=True), primary_key=True, server_default=FetchedValue()
    )
    name = Column(String(150), nullable=False)


class CommentTypes(base):
    __tablename__ = "CommentTypes"
    table_type = TableTypes.REFERENCE
    table_type_id = 24

    comment_type_id = Column(
        UUID(as_uuid=True), primary_key=True, server_default=FetchedValue()
    )
    name = Column(String(150), nullable=False)


class CommodityTypes(base):
    __tablename__ = "CommodityTypes"
    table_type = TableTypes.REFERENCE
    table_type_id = 25

    commodity_type_id = Column(
        UUID(as_uuid=True), primary_key=True, server_default=FetchedValue()
    )
    name = Column(String(150), nullable=False)


class ConfidenceLevels(base):
    __tablename__ = "ConfidenceLevels"
    table_type = TableTypes.REFERENCE
    table_type_id = 26

    confidence_level_id = Column(
        UUID(as_uuid=True), primary_key=True, server_default=FetchedValue()
    )
    level = Column(String(150), nullable=False)


# Measurements Tables
class States(base):
    __tablename__ = "States"
    table_type = TableTypes.MEASUREMENT
    table_type_id = 27  # Only needed for tables referenced by Entry table

    state_id = Column(
        UUID(as_uuid=True), primary_key=True, server_default=FetchedValue()
    )
    time = Column(TIMESTAMP, nullable=False)
    sensor_id = Column(
        UUID(as_uuid=True), ForeignKey("Sensors.sensor_id"), nullable=False
    )
    location = Column(Geometry(geometry_type="POINT", srid=4326))
    heading = Column(DOUBLE_PRECISION)
    course = Column(DOUBLE_PRECISION)
    speed = Column(DOUBLE_PRECISION)
    source_id = Column(
        UUID(as_uuid=True), ForeignKey("Datafiles.datafile_id"), nullable=False
    )
    privacy_id = Column(UUID(as_uuid=True), ForeignKey("Privacies.privacy_id"))


class Contacts(base):
    __tablename__ = "Contacts"
    table_type = TableTypes.MEASUREMENT
    table_type_id = 28

    contact_id = Column(
        UUID(as_uuid=True), primary_key=True, server_default=FetchedValue()
    )
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


class Activations(base):
    __tablename__ = "Activations"
    table_type = TableTypes.MEASUREMENT
    table_type_id = 29

    activation_id = Column(
        UUID(as_uuid=True), primary_key=True, server_default=FetchedValue()
    )
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


class LogsHoldings(base):
    __tablename__ = "LogsHoldings"
    table_type = TableTypes.MEASUREMENT
    table_type_id = 30

    logs_holding_id = Column(
        UUID(as_uuid=True), primary_key=True, server_default=FetchedValue()
    )
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


class Comments(base):
    __tablename__ = "Comments"
    table_type = TableTypes.MEASUREMENT
    table_type_id = 31

    comment_id = Column(
        UUID(as_uuid=True), primary_key=True, server_default=FetchedValue()
    )
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


class Geometries(base):
    __tablename__ = "Geometries"
    table_type = TableTypes.MEASUREMENT
    table_type_id = 32

    geometry_id = Column(
        UUID(as_uuid=True), primary_key=True, server_default=FetchedValue()
    )
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


class Media(base):
    __tablename__ = "Media"
    table_type = TableTypes.MEASUREMENT
    table_type_id = 33

    media_id = Column(
        UUID(as_uuid=True), primary_key=True, server_default=FetchedValue()
    )
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
