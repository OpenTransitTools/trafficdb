from sqlalchemy import Column, String
from sqlalchemy.orm import relationship

from ott.trafficdb.model.base import Base

import logging
log = logging.getLogger(__file__)


class StopSegmentTrip(Base):
    __tablename__ = 'traffic_stop_segment_trips'

    segment_id = Column(String(255), index=True, nullable=False)
    trip_id = Column(String(255), index=True, nullable=False)
    shape_id = Column(String(255), nullable=False)
    service_id = Column(String(255), nullable=False)
    route_id = Column(String(255), nullable=False)
    mode = Column(String(255))

    ## define relationships
    stop_segment = relationship(
        'StopSegment',
        primaryjoin='StopSegmentTrip.segment_id==StopSegment.id',
        foreign_keys='(StopSegmentTrip.segment_id)',
        uselist=False, viewonly=True
    )

    """
    trip = relationship(
        Trip,
        primaryjoin='Trip.trip_id==StopSegmentTrip.trip_id',
        foreign_keys='(StopSegmentTrip.trip_id)',
        uselist=False, viewonly=True)
    """

    def __init__(self, session, segment, trip):
        super(StopSegmentTrip, self).__init__()
        self.id = "{}-{}".format(segment.id, trip.trip_id)
        self.segment_id = segment.id
        self.trip_id = trip.trip_id
        self.shape_id = trip.shape_id
        self.service_id = trip.service_id
        self.route_id = trip.route.route_id
        self.mode = trip.route.type.otp_type
