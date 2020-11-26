from sqlalchemy import Column, Index, Integer, Numeric, String, DateTime
from ott.trafficdb.gtfs.base import Base

import logging
log = logging.getLogger(__file__)


class StopSegment(Base):
    __tablename__ = 'traffic_stop_segments'

    segment_id = Column(String, nullable=False)
    begin_stop_id = Column(String, index=True)
    end_stop_id = Column(String, index=True)

    """
    entities = relationship(
        'StopSegmentEntity',
        primaryjoin='StopSegment.StopSegment_id == StopSegmentEntity.StopSegment_id',
        foreign_keys='(StopSegment.StopSegment_id)',
        backref=backref("StopSegment", lazy="joined", uselist=False),
        uselist=True, viewonly=True
    )
    """

    def __init__(self, begin_stop, end_stop):
        self.segment_id = self.make_id(begin_stop, end_stop)

    @classmethod
    def factory(cls, begin_stop, end_stop):
        """
        will create...
        """
        ret_val = None
        return ret_val

    @classmethod
    def _make_id(cls, begin_stop, end_stop):
        return "{}-{}".format(begin_stop.stop_id, end_stop.stop_id)

    @classmethod
    def _cache_segment(cls, cache, begin_stop, end_stop, trip):
        id = cls._make_id(begin_stop, end_stop)
        if id not in cache:
            cache[id] = {
                'id': id,
                'begin_time': begin_stop.arrival_time,
                'end_time': end_stop.departure_time,
                'begin_stop': begin_stop,
                'end_stop': end_stop,
            }
        else:
            # check for earlier segment begin_time than what's cached
            if begin_stop.arrival_time < cache[id]['begin_time']:
                cache[id]['begin_time'] = begin_stop.arrival_time
            # check for later segment end_time than what's cached
            if end_stop.departure_time > cache[id]['end_time']:
                cache[id]['end_time'] = end_stop.departure_time


    @classmethod
    def load(cls, session):
        """
        will find ...
        """
        cache = {}
        try:
            # step 1: query gtfsdb and build a cache of stop-stop segments
            from gtfsdb import Trip
            trips = session.query(Trip).filter(Trip.route_id == '70')
            for t in trips.all():
                stop_times = t.stop_times
                stop_times_len = len(stop_times)
                if stop_times_len > 1:
                    for i, st in enumerate(stop_times):
                        begin_stop = stop_times[i]
                        end_stop = stop_times[i+1]
                        cls._cache_segment(cache, begin_stop, end_stop, t)
                        if i+2 >= stop_times_len:
                            break

            # step 2: write this cache to db
            print(len(cache))
            for c in cache:
                print(cache[c])
        except Exception as e:
            log.exception(e)


    @classmethod
    def clear_tables(cls, session, agency):
        """
        clear out stop segments
        """
        session.query(StopSegment).filter(StopSegment.agency == agency).delete()
