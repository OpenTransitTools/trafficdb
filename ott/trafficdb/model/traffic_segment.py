import enum

from sqlalchemy import Column, String, Integer, Numeric
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

    vendor_id = Column(String(255), nullable=False, default=Vendor.inrix.name)
    stop_segment_id = Column(String(255), index=True, nullable=False)
    traffic_segment_id = Column(String(255), index=True, nullable=False)
    percent_of_stop_segment = Column(Numeric(6, 3), nullable=False, default=0.0)

    lanes = Column(Numeric(6, 3), nullable=False, default=1.0)
    distance = Column(Numeric(20, 10), nullable=False, default=0.0)
    street_type = Column(String(255), nullable=False, default=StreetType.arterial.name)
    direction = Column(String(2))

    stop_segment = relationship(
        'StopSegment',
        primaryjoin='TrafficSegment.stop_segment_id==StopSegment.id',
        foreign_keys='(TrafficSegment.stop_segment_id)',
        uselist=False, viewonly=True)

    speeds = relationship(
        'TrafficSegmentSpeed',
        primaryjoin='TrafficSegment.traffic_segment_id==TrafficSegmentSpeed.traffic_segment_id',
        foreign_keys='(TrafficSegment.traffic_segment_id)',
        # order_by='StopTime.stop_sequence',
        uselist=True, viewonly=True)

    def __init__(self, stop_segment, traffic_segment):
        super(TrafficSegment, self).__init__()
        self.stop_segment_id = stop_segment.id
        self.traffic_segment_id = traffic_segment.id
        #self.vendor_id = traffic_segment.vendor_id
        self.geom = traffic_segment.geom

    @classmethod
    def factory(cls, segment_conflate):
        return cls.inrix_factory(segment_conflate)

    @classmethod
    def inrix_factory(cls, segment_conflate):
        ts = TrafficSegment(segment_conflate.stop_segment, segment_conflate.traffic_segment)

        # custom inrix parsing
        # import pdb; pdb.set_trace()
        # TODO: Gtfs might be in different units ... here we're converting to feet (since I think that's what TM's gtfs is)
        ts.distance = num_utils.to_float(segment_conflate.traffic_segment.distance, 0.0) * 5280
        ts.direction = segment_conflate.traffic_segment.direction
        ts.lanes = num_utils.to_float(segment_conflate.traffic_segment.lanes, 0.0, round_to=2)
        ts.street_type = StreetType.get_name(segment_conflate.traffic_segment.frc)
        ts.percent_of_stop_segment = num_utils.to_float(segment_conflate.transit_shp_percent, round_to=2)

        return ts

    @classmethod
    def get_segment_ids(cls, session, limit=None):
        ret_val = []
        segs = session.query(TrafficSegment)
        if limit:
            segs = segs.limit(limit)
        for s in segs.all():
            ret_val.append(s.traffic_segment_id)
        return ret_val

    @classmethod
    def add_geometry_column(cls):
        if not hasattr(cls, 'geom'):
            cls.geom = deferred(Column(Geometry(geometry_type='LINESTRING', srid=4326)))

    @classmethod
    def print_all(cls, session, limit=None, just_speeds=False):
        q = session.query(TrafficSegment).order_by(TrafficSegment.stop_segment_id)
        if limit and type(limit) is int:
            segments = q.limit(limit)
        else:
            segments = q.all()

        for s in segments:
            if just_speeds and (s.speeds is None or len(s.speeds) < 1):
                continue
            s.print()

    def print(self, latest_speed_filter=False):
        out = "\nsegments: {s.stop_segment_id} ({s.stop_segment.direction} {s.stop_segment.distance:5.1f}') -- " \
              "{s.traffic_segment_id} ({s.direction} {s.distance:5.1f}'):\n".format(s = self)

        if self.speeds and len(self.speeds) > 0:
            for s in self.speeds:  # TODO: (maybe / optionally) only show latest and/or sort by capture time
                out += " {}\n".format(s.print(do_print=False))

        print(out)

    def print_avg(self, latest_speed_filter=False):
        # import pdb; pdb.set_trace()
        out = "\nsegments: {s.stop_segment_id} ({s.stop_segment.direction} {s.stop_segment.distance:5.1f}') -- " \
              "{s.traffic_segment_id} ({s.direction} {s.distance:5.1f}'):\n".format(s = self)

        if self.speeds and len(self.speeds) > 0:
            for s in self.speeds:  # TODO: (maybe / optionally) only show latest and/or sort by capture time
                out += " {}\n".format(s.print(do_print=False))

        print(out)
