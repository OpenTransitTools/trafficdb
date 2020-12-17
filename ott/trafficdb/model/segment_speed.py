import enum
import datetime
from sqlalchemy import Column, String, Integer, DateTime, Numeric, Enum
from ott.trafficdb.model.base import Base
from ott.utils import num_utils

import logging
log = logging.getLogger(__file__)


class CongestionLevel(enum.Enum):
    unknown = 0
    free_flow = 1   # speed averages 71% 100% of limit
    slow = 2        # 51% 70%
    heavy = 3       # 36% 50%
    queuing = 4     # N/A N/A
    standstill = 5  # 21% 35%
    no_flow = 6     # 0% 20%

    @classmethod
    def get_name(cls, val):
        val = num_utils.to_int_range(val, 0, 6, 0)
        return CongestionLevel(val).name


class TrafficSegmentSpeed(Base):
    __tablename__ = 'traffic_segment_speed'

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    segment_id = Column(String(255), index=True, nullable=False)
    average_speed = Column(Numeric(20, 10), nullable=False, default=0.0)
    current_speed = Column(Numeric(20, 10), nullable=False, default=0.0)
    travel_time = Column(Numeric(20, 10), nullable=False, default=0.0)
    congestion_level = Column(Enum(CongestionLevel), nullable=False, default=CongestionLevel.unknown)
    capture_time = Column(DateTime, default=datetime.datetime.now())

    def __init__(self):
        super(TrafficSegmentSpeed, self).__init__()

    @classmethod
    def inrix_factory(cls, blah):
        pass
