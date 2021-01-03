from sqlalchemy import Column, String, Numeric, func
from sqlalchemy.orm import relationship
from gtfsdb import Stop, Trip, Shape, PatternBase

from ott.trafficdb.model.base import Base
from ott.utils import geo_utils

import logging
log = logging.getLogger(__file__)


# todo: make util ... py2 and py3
def printer(content, end='\n', flush=False, do_print=True):
    try:
        if do_print:
            pass #print(content, end=end, flush=flush)
    except:
        # if here ... py 2.x 
        print(content)


class StopSegment(Base, PatternBase):
    __tablename__ = 'traffic_stop_segments'

    begin_stop_id = Column(String(255), index=True, nullable=False)
    end_stop_id = Column(String(255), index=True, nullable=False)

    begin_time = Column(String(9), nullable=False)
    end_time = Column(String(9), nullable=False)
    distance = Column(Numeric(20, 10), nullable=False)
    bearing = Column(Numeric(20, 10))
    direction = Column(String(2))
    shape_id = Column(String(255)) # note: the actual geom is only a partial shape .. line between the two stops
    begin_distance = Column(Numeric(20, 10), nullable=False)
    end_distance = Column(Numeric(20, 10), nullable=False)

    traffic_segment = relationship(
        'TrafficSegment',
        primaryjoin='TrafficSegment.stop_segment_id==StopSegment.id',
        foreign_keys='(TrafficSegment.stop_segment_id)',
        uselist=True, viewonly=True)

    ## define relationships (usually do this above outside constructor, but doesn't work for some reason)
    """
    '''
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
    '''
    shape_id = Column(String(255), ForeignKey(Shape.shape_id))
    shapes = relationship(
        Shape,
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
        self.begin_distance = begin_stop.shape_dist_traveled
        self.end_distance = end_stop.shape_dist_traveled

        self.bearing = geo_utils.bearing(begin_stop.stop.stop_lat, begin_stop.stop.stop_lon, end_stop.stop.stop_lat, end_stop.stop.stop_lon)
        self.direction = geo_utils.compass(self.bearing)

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
            .filter(Shape.shape_dist_traveled <= end_stop.shape_dist_traveled) \
            .order_by(Shape.shape_pt_sequence)
        return ret_val

    @classmethod
    def _cache_segment(cls, session, begin_stop, end_stop, trip, segment_cache, segment_trip_cache):
        # step 1: make segment id
        id = "{}-{}".format(begin_stop.stop_id, end_stop.stop_id)

        # step 2: make / update segment
        stop_segment = None
        if id not in segment_cache:
            stop_segment = cls(session, id, begin_stop, end_stop, trip)
            segment_cache[id] = stop_segment
        else:
            stop_segment = segment_cache[id]

            # check for earlier segment begin_time than what's cached
            if begin_stop.arrival_time < stop_segment.begin_time:
                stop_segment.begin_time = begin_stop.arrival_time
            # check for later segment end_time than what's cached
            if end_stop.departure_time > stop_segment.end_time:
                stop_segment.end_time = end_stop.departure_time

        # step 3: create trip record for this segment
        # note:  use of hash will filter out trips (thus sst records) that loop back on same segment
        # import pdb; pdb.set_trace()
        if segment_trip_cache is not None:
            from .stop_segment_trip import StopSegmentTrip
            sst = StopSegmentTrip(session, stop_segment, trip)
            segment_trip_cache[sst.id] = sst

    @classmethod
    def load(cls, session, do_trip_segments=True, chunk_size=10000, do_print=True):
        """
        will find all stop-stop pairs from stop_times/trip data, and create stop-stop segments in the database
        """
        # import pdb; pdb.set_trace()
        try:
            segment_cache = {}
            trip_cache = {} if do_trip_segments else None

            # step 1: query gtfsdb and build a cache of stop-stop segments
            trips = session.query(Trip)
            #trips = session.query(Trip).filter(Trip.route_id == '57')
            #trips = session.query(Trip).filter(Trip.route_id == '99')
            #trips = session.query(Trip).filter(Trip.route_id == '70')
            for j, t in enumerate(trips.all()):
                stop_times = t.stop_times
                stop_times_len = len(stop_times)
                if stop_times_len > 1:
                    printer('.', end='', flush=True, do_print=do_print and j % chunk_size == 0)
                    for i, st in enumerate(stop_times):
                        begin_stop = stop_times[i]
                        end_stop = stop_times[i+1]
                        cls._cache_segment(session, begin_stop, end_stop, t, segment_cache, trip_cache)
                        if i+2 >= stop_times_len:
                            break

            # step 2: write the stop_segment data to db
            if len(segment_cache) > 0:
                # step 2a: clear old segment data from db
                from .stop_segment_trip import StopSegmentTrip
                printer(" ", do_print=do_print)
                StopSegmentTrip.clear_tables(session)
                cls.clear_tables(session)

                printer("There are {:,} stop to stop segments".format(len(segment_cache)), do_print=do_print)
                session.add_all(segment_cache.values())
                session.flush()
                session.commit()
                session.flush()

                # step 3: write the stop_segment_trip data to db
                if trip_cache and len(trip_cache) > 0:
                    segment_trip_cache = list(trip_cache.values())
                    printer("and {:,} trips cross these segments".format(len(segment_trip_cache)), do_print=do_print)
                    for i in range(0, len(segment_trip_cache), chunk_size):
                        chunk = segment_trip_cache[i:i + chunk_size]
                        printer('.', end='', flush=True, do_print=do_print)
                        session.bulk_save_objects(chunk)

        except Exception as e:
            log.exception(e)

    @classmethod
    def to_geojson(cls, session):
        """
        override the default to_geojson
        {
          "type": "FeatureCollection",
          "features": [
            {"type":"Feature", "properties":{"id":"1-2"}, "geometry":{"type":"LineString","coordinates":[[-122.677388,45.522879],[-122.677396,45.522913]]}},
            {"type":"Feature", "properties":{"id":"2-3"}, "geometry":{"type":"LineString","coordinates":[[-122.675715,45.522215],[-122.67573,45.522184]]}},
          ]
        }
        """
        feature_tmpl = '    {{"type": "Feature", "properties": {{' \
                       '"id": "{}", ' \
                       '"info": "{}", ' \
                       '"layer": "{}" ' \
                       '}}, "geometry": {}}}{}'

        stop_cache ={}
        stops = session.query(Stop.stop_id, Stop.geom.ST_AsGeoJSON()).all()
        for s in stops:
            stop_cache[s[0]] = s[1]

        # import pdb; pdb.set_trace()
        features = session.query(StopSegment).all()
        ln = len(features) - 1
        featgeo = ""
        last_stop = "xxx"
        for i, f in enumerate(features):
            geom = session.scalar(func.ST_AsGeoJSON(f.geom))
            if last_stop != f.begin_stop_id:
                featgeo += feature_tmpl.format(f.begin_stop_id, "", "stop", stop_cache[f.begin_stop_id], ",\n")
            featgeo += feature_tmpl.format(f.id, f.direction, "stop", geom, ",\n")
            for t in f.traffic_segment:
                tgeo = session.scalar(func.ST_AsGeoJSON(t.geom))
                featgeo += feature_tmpl.format(t.traffic_segment_id + " (" + f.id + ")", t.direction, "traffic", tgeo, ",\n")
            comma = ",\n" if i < ln else "\n"  # don't add a comma to last feature
            featgeo += feature_tmpl.format(f.end_stop_id, "", "stop", stop_cache[f.end_stop_id], comma)
            last_stop = f.end_stop_id

        geojson = '{{\n  "type": "FeatureCollection",\n  "features": [\n{}  ]\n}}'.format(featgeo)
        return geojson
