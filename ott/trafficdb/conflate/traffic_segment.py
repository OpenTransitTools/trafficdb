import enum

from sqlalchemy import Column, String, Numeric, Enum
from sqlalchemy.orm import deferred, relationship
from geoalchemy2 import Geometry

from ott.trafficdb.gtfs.base import Base

import logging
log = logging.getLogger(__file__)


class TrafficVendor(enum.Enum):
    inrix = 1
    mapbox = 2
    tomtom = 3


class StreetType(enum.Enum):
    highway = 1
    major_arterial = 2
    arterial = 3
    neighborhood = 4


class TrafficSegment(Base):
    __tablename__ = 'traffic_segment'

    stop_segment_id = Column(String(255), index=True, nullable=False)
    traffic_segment_id = Column(String(255), index=True, nullable=False)
    vendor_id = Column(Enum(TrafficVendor), nullable=False, default=TrafficVendor.inrix)
    vendor_segment_table_id = Column(String(255), nullable=False)

    lanes = Column(Numeric(20, 10), nullable=False, default=1.0)
    distance = Column(Numeric(20, 10), nullable=False, default=0.0)
    speed_limit = Column(Numeric(20, 10), nullable=False, default=0.0)
    street_type = Column(Enum(StreetType), nullable=False, default=StreetType.arterial)

    speeds = relationship(
        'TrafficSegmentSpeed',
        primaryjoin='TrafficSegment.id==TrafficSegmentSpeed.segment_id',
        foreign_keys='(TrafficSegment.id)',
        #order_by='StopTime.stop_sequence',
        uselist=True, viewonly=True)

    def __init__(self):
        super(TrafficSegment, self).__init__()

    @classmethod
    def inrix_factory(cls, blah):
        pass

    @classmethod
    def add_geometry_column(cls):
        if not hasattr(cls, 'geom'):
            cls.geom = deferred(Column(Geometry(geometry_type='LINESTRING', srid=4326)))
