import enum
import datetime
from sqlalchemy import Column, String, Integer, Boolean, DateTime, Numeric, Enum
from ott.trafficdb.model.base import Base
from ott.utils import num_utils
from ott.utils.object_utils import safe_get

import logging
log = logging.getLogger(__file__)


class TrafficSegmentSpeed(Base):
    __tablename__ = 'traffic_segment_speed'

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    traffic_segment_id = Column(String(255), index=True, nullable=False)

    is_realtime = Column(Boolean, nullable=False, default=False)
    rt_confidence = Column(Integer, default=0)

    average_speed = Column(Numeric(20, 10), nullable=False, default=0.0)
    freeflow_speed = Column(Numeric(20, 10), nullable=False, default=0.0)
    current_speed = Column(Numeric(20, 10), nullable=False, default=0.0)
    travel_time = Column(Numeric(20, 10), nullable=False, default=0.0)
    capture_time = Column(DateTime, default=datetime.datetime.now())

    # some segments have sub-segment speeds ... including those here
    slowest_speed = Column(Numeric(20, 10))
    fastest_speed = Column(Numeric(20, 10))
    all_speeds = Column(String(512))

    def __init__(self):
        super(TrafficSegmentSpeed, self).__init__()

    @classmethod
    def inrix_factory(cls, rec):
        """
        {
          'code': '448904111',
          'average': 19, 'reference': 19, 'speed': 19, 'subSegments': [{'speed': 25, 'offset': '342,391'}],
          'travelTimeMinutes': 0.757,
          'type': 'XDS',
          'score': 30, ( can be 10, 20 or 30 -- 30 is realtime, 20 is mix, 10 is history)
          'c-Value': 90 ( confidence [in realtime data] is only available if score is 30 --- 0 to 100)
          'speedBucket': 3,
        }
        """
        # TODO - move to inrix code someplace, ala control.inrix.speed_data ???
        # TODO - pro move: scalable to other vendors, maybe cleaner; cons: separates the list of class props from assignment below
        # import pdb; pdb.set_trace()
        tss = TrafficSegmentSpeed()
        tss.traffic_segment_id = rec['code']
        tss.average_speed = safe_get(rec, 'average', 0.0)
        tss.freeflow_speed = safe_get(rec, 'reference', 0.0)
        tss.current_speed = safe_get(rec, 'speed', 0.0)
        # loop thru subSegments to collect all speeds tss.all_speeds = rec['']
        tss.travel_time = safe_get(rec, 'travelTimeMinutes', 0.0)

        if safe_get(rec, 'score', 0) == 30:
            tss.is_realtime = True
            if 'c-Value' in rec:
                tss.rt_confidence = rec['c-Value']
        else:
            tss.is_realtime = False

        if 'subSegments' in rec:
            tss.slowest_speed = tss.fastest_speed = rec['speed']
            tss.all_speeds = "{}".format(rec['speed'])
            for sub in rec['subSegments']:
                tss.all_speeds += ":{}".format(sub['speed'])
                if sub['speed'] < tss.slowest_speed:
                    tss.slowest_speed = sub['speed']
                if sub['speed'] > tss.fastest_speed:
                    tss.fastest_speed = sub['speed']

        return tss
