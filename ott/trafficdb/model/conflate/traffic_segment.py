import enum

from sqlalchemy import Column, String, Integer, Numeric, Enum
from sqlalchemy.orm import deferred, relationship
from geoalchemy2 import Geometry

from ott.trafficdb.model.base import Base, Vendor
from ott.utils import num_utils

import logging
log = logging.getLogger(__file__)


class StreetType(enum.Enum):
    highway = 1
    major_arterial = 2
    arterial = 3
    neighborhood = 4

    @classmethod
    def get_name(cls, val):
        val = num_utils.to_int_range(val, 1, 4, 4)
        return StreetType(val).name

class TrafficSegment(Base):
    __tablename__ = 'traffic_segment'

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)

    stop_segment_id = Column(String(255), index=True, nullable=False)
    traffic_segment_id = Column(String(255), index=True, nullable=False)
    vendor_id = Column(Enum(Vendor), nullable=False, default=Vendor.inrix)

    lanes = Column(Numeric(20, 10), nullable=False, default=1.0)
    distance = Column(Numeric(20, 10), nullable=False, default=0.0)
    direction = Column(String(2))
    speed_limit = Column(Numeric(20, 10), nullable=False, default=0.0)
    street_type = Column(Enum(StreetType), nullable=False, default=StreetType.arterial)

    speeds = relationship(
        'TrafficSegmentSpeed',
        primaryjoin='TrafficSegment.id==TrafficSegmentSpeed.segment_id',
        foreign_keys='(TrafficSegment.id)',
        #order_by='StopTime.stop_sequence',
        uselist=True, viewonly=True)

    def __init__(self, stop_segment, traffic_segment):
        super(TrafficSegment, self).__init__()
        self.stop_segment_id = stop_segment.id
        self.traffic_segment_id = traffic_segment.id
        self.vendor_id = traffic_segment.vendor_id
        self.geom = traffic_segment.geom

    @classmethod
    def factory(cls, stop_segment, traffic_segment):
        return cls.inrix_factory(stop_segment, traffic_segment)

    @classmethod
    def inrix_factory(cls, stop_segment, traffic_segment):
        ts = TrafficSegment(stop_segment, traffic_segment)

        # custom inrix parsing
        ts.lanes = num_utils.to_float(traffic_segment.lanes, 0.0)
        ts.distance = num_utils.to_float(traffic_segment.distance, 0.0)
        ts.direction = traffic_segment.direction
        ts.street_type = StreetType.get_name(traffic_segment.frc)

        return ts

    @classmethod
    def add_geometry_column(cls):
        if not hasattr(cls, 'geom'):
            cls.geom = deferred(Column(Geometry(geometry_type='LINESTRING', srid=4326)))
