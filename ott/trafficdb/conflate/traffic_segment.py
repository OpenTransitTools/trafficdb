from sqlalchemy import Column, String
from sqlalchemy.orm import relationship

from ott.trafficdb.gtfs.base import Base

import logging
log = logging.getLogger(__file__)


class TrafficSegment(Base):
    __tablename__ = 'traffic_segment'

    segment_id = Column(String(255), index=True, nullable=False)
    vendor_name = Column(String(255), nullable=False)
    vendor_data_table = Column(String(255), nullable=False)

    def __init__(self, session, segment, trip):
        super(TrafficSegment, self).__init__()
        self.id = "{}-{}".format(segment.id, trip.trip_id)
        self.segment_id = segment.id
        self.route_id = trip.route.route_id
