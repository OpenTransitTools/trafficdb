from sqlalchemy import Column, String, Numeric
from sqlalchemy.orm import relationship

from gtfsdb import Trip
from gtfsdb import Shape
from gtfsdb import Stop
from gtfsdb import PatternBase

from ott.trafficdb.gtfs.base import Base

import logging
log = logging.getLogger(__file__)


class StopSegment(Base, PatternBase):
    __tablename__ = 'traffic_stop_segments'

    begin_stop_id = Column(String(255), index=True, nullable=False)
    end_stop_id = Column(String(255), index=True, nullable=False)

    begin_time = Column(String(9), nullable=False)
    end_time = Column(String(9), nullable=False)
    distance = Column(Numeric(20, 10), nullable=False)
    shape_id = Column(String(255)) # note: this is a sub-shape between 2 stops

    """
    begin_stop = relationship(
        'Stop',
        primaryjoin='Stop.stop_id==StopSegment.begin_stop_id',
        foreign_keys='(StopSegment.begin_stop_id)',
        uselist=False, viewonly=True
    )

    end_stop = relationship(
        'Stop',
        primaryjoin='Stop.stop_id==StopSegment.end_stop_id',
        foreign_keys='(StopSegment.end_stop_id)',
        uselist=False, viewonly=True
    )

    shapes = relationship(
        'Shape',
        primaryjoin='Shape.shape_id==StopSegment.shape_id',
        foreign_keys='(Shape.shape_id)',
        uselist=True, viewonly=True)
    """

    def __init__(self, session, id, begin_stop, end_stop, trip):
        super(StopSegment, self).__init__()
        self.id = id
        self.begin_stop_id = begin_stop.stop_id
        self.end_stop_id = end_stop.stop_id
        self.begin_time = begin_stop.arrival_time
        self.end_time = end_stop.departure_time
        self.distance = end_stop.shape_dist_traveled - begin_stop.shape_dist_traveled
        self.shape_id = trip.shape_id
        if hasattr(self, 'geom'):
            q = self._make_shapes(session, begin_stop, end_stop, trip)
            self.geom_from_shape(q)

    @classmethod
    def _make_shapes(cls, session, begin_stop, end_stop, trip):
        """
        return the shape points between two stops along a trip
        TODO: could be a gtfsdb utility belonging to Shape. class
        """
        ret_val = session.query(Shape) \
            .filter(Shape.shape_id == trip.shape_id) \
            .filter(Shape.shape_dist_traveled >= begin_stop.shape_dist_traveled) \
            .filter(Shape.shape_dist_traveled <= end_stop.shape_dist_traveled)
        return ret_val

    @classmethod
    def _cache_segment(cls, session, cache, begin_stop, end_stop, trip):
        id = "{}-{}".format(begin_stop.stop_id, end_stop.stop_id)
        if id not in cache:
            ss = cls(session, id, begin_stop, end_stop, trip)
            cache[id] = ss
        else:
            # check for earlier segment begin_time than what's cached
            if begin_stop.arrival_time < cache[id].begin_time:
                cache[id].begin_time = begin_stop.arrival_time
            # check for later segment end_time than what's cached
            if end_stop.departure_time > cache[id].end_time:
                cache[id].end_time = end_stop.departure_time

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
            if len(cache) > 0:
                cls.clear_tables(session)
                print(len(cache))
                for c in cache:
                    # import pdb; pdb.set_trace()
                    ss = cache[c]
                    session.add(ss)

        except Exception as e:
            log.exception(e)


    @classmethod
    def clear_tables(cls, session):
        """
        clear out stop segments
        """
        session.query(StopSegment).delete()
