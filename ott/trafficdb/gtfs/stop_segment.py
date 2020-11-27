from sqlalchemy import Column, String

from gtfsdb import Trip
from gtfsdb import Shape

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
    def _make_shapes(cls, session, begin_stop, end_stop, trip):
        """
        return the shape points between two stops along a trip
        TODO: could be a gtfsdb utility belonging to Shape. class
        """
        ret_val = session.query(Shape)\
            .filter(Shape.shape_id == trip.shape_id)\
            .filter(Shape.shape_dist_traveled >= begin_stop.shape_dist_traveled)\
            .filter(Shape.shape_dist_traveled <= end_stop.shape_dist_traveled)\
            .all()
        return ret_val

    @classmethod
    def _cache_segment(cls, session, cache, begin_stop, end_stop, trip):
        id = cls._make_id(begin_stop, end_stop)
        if id not in cache:
            cache[id] = {
                'id': id,
                'begin_time': begin_stop.arrival_time,
                'end_time': end_stop.departure_time,
                'begin_stop': begin_stop.stop,
                'end_stop': end_stop.stop,
                'distance': end_stop.shape_dist_traveled - begin_stop.shape_dist_traveled,
                'shape': cls._make_shapes(session, begin_stop, end_stop, trip)
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
            trips = session.query(Trip).filter(Trip.route_id == '70')
            for t in trips.all():
                stop_times = t.stop_times
                stop_times_len = len(stop_times)
                if stop_times_len > 1:
                    for i, st in enumerate(stop_times):
                        begin_stop = stop_times[i]
                        end_stop = stop_times[i+1]
                        cls._cache_segment(session, cache, begin_stop, end_stop, t)
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
