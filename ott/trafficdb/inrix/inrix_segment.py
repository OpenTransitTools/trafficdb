from sqlalchemy import Column, String, Numeric
from ott.trafficdb.gtfs.base import Base

import logging
log = logging.getLogger(__file__)


class InrixSegment(Base):
    __tablename__ = 'traffic_inrix_segments'

    direction = Column()
    distance = Column()
    lanes = Column()

    def __init__(self, session, segment, trip):
        super(InrixSegment, self).__init__()
