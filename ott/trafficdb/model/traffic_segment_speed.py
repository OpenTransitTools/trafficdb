import enum
import datetime
from sqlalchemy import Column, String, Integer, Boolean, DateTime, Numeric, Enum
from ott.trafficdb.model.base import Base
from ott.utils import num_utils, object_utils

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
        tss.traffic_segment_id = object_utils.safe_get_str(rec, 'code', 'BOGUS')
        tss.average_speed = object_utils.safe_get_float(rec, 'average')
        tss.freeflow_speed = object_utils.safe_get_float(rec, 'reference')
        tss.current_speed = object_utils.safe_get_float(rec, 'speed', 0.000111)
        tss.travel_time = object_utils.safe_get_float(rec, 'travelTimeMinutes')

        if object_utils.safe_get_int(rec, 'score') == 30:
            tss.is_realtime = True
            tss.rt_confidence = object_utils.safe_get_int(rec, 'c-Value')
        else:
            tss.is_realtime = False

        if object_utils.is_list(rec, 'subSegments'):
            tss.slowest_speed = tss.fastest_speed = tss.current_speed
            tss.all_speeds = "{}".format(tss.current_speed)
            for sub in rec['subSegments']:
                sub_speed = object_utils.safe_get_float(sub, 'speed')
                tss.all_speeds += ":{}".format(sub_speed)
                if sub_speed < tss.slowest_speed:
                    tss.slowest_speed = sub_speed
                if sub_speed > tss.fastest_speed:
                    tss.fastest_speed = sub_speed

        return tss

    def print(self, do_print=True):
        ret_val = "{s.capture_time:%Y-%m-%d %I:%M%p} -- speed:{s.current_speed:5.1f}  freeflow:{s.freeflow_speed:5.1f}" \
                  "  avg:{s.average_speed:5.1f}  time:{s.travel_time:6.3f}  (realtime is {s.is_realtime}" \
                  " with {s.rt_confidence:>3}% confidence)".format(s=self).lower()
        if do_print:
            print(ret_val)
        return ret_val
