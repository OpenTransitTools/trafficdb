import enum

from sqlalchemy import Column, String, Numeric, func
from sqlalchemy.orm import relationship
from gtfsdb import Stop, Trip, Shape, PatternBase, util

from ott.trafficdb.model.base import Base
from ott.utils import geo_utils
from ott.utils import object_utils

import logging
log = logging.getLogger(__file__)


class StopSegment(Base, PatternBase):
    __tablename__ = 'traffic_stop_segments'

    prev_seg_id = Column(String(255))
    next_seg_id = Column(String(255))

    begin_stop_id = Column(String(255), index=True, nullable=False)
    begin_stop_code = Column(String(255), nullable=False)
    end_stop_id = Column(String(255), index=True, nullable=False)
    end_stop_code = Column(String(255), nullable=False)

    begin_time = Column(String(9), nullable=False)
    end_time = Column(String(9), nullable=False)
    distance = Column(Numeric(20, 10), nullable=False)
    bearing = Column(Numeric(20, 10))
    direction = Column(String(2))

    shape_id = Column(String(255))  # note: the actual geom is only a partial shape .. line between the two stops
    shape_begin_distance = Column(Numeric(20, 10), nullable=False)
    shape_end_distance = Column(Numeric(20, 10), nullable=False)

    traffic_segment = relationship(
        'TrafficSegment',
        primaryjoin='TrafficSegment.stop_segment_id==StopSegment.id',
        foreign_keys='(TrafficSegment.stop_segment_id)',
        uselist=True, viewonly=True)

    def __init__(self, session, id, begin_stop, end_stop, trip):
        super(StopSegment, self).__init__()
        self.id = id

        self.begin_stop_id = begin_stop.stop_id
        self.begin_stop_code = begin_stop.stop.stop_code
        self.end_stop_id = end_stop.stop_id
        self.end_stop_code = end_stop.stop.stop_code

        self.shape_id = trip.shape_id
        self.begin_time = begin_stop.arrival_time
        self.end_time = end_stop.departure_time

        bsd = object_utils.safe_float(begin_stop.shape_dist_traveled)
        esd = object_utils.safe_float(end_stop.shape_dist_traveled)
        self.distance = esd - bsd
        self.shape_begin_distance = bsd
        self.shape_end_distance = esd

        self.bearing = geo_utils.bearing(begin_stop.stop.stop_lat, begin_stop.stop.stop_lon, end_stop.stop.stop_lat, end_stop.stop.stop_lon)
        self.direction = geo_utils.compass(self.bearing)

        if hasattr(self, 'geom'):
            self.make_shapes(session, begin_stop, end_stop, trip)

    @property
    def code_id(self):
        id = "{}-{}".format(self.begin_stop_code, self.end_stop_code)
        return id

    def make_shapes(self, session, begin_stop, end_stop, trip):
        """
        make a shape
        note: begin_stop and end_stop are StopTime objects
        """
        # import pdb; pdb.set_trace()
        try:
            # step 1: try to make a line between 2 stops via the shapes and the distance travelled
            shp = session.query(Shape) \
                .filter(Shape.shape_id == trip.shape_id) \
                .filter(Shape.shape_dist_traveled >= begin_stop.shape_dist_traveled) \
                .filter(Shape.shape_dist_traveled <= end_stop.shape_dist_traveled) \
                .order_by(Shape.shape_pt_sequence)
            good_line = self.geom_from_shape(shp)

            # step 2: if the line doesn't look long enough, let's hack a line together with 2 points.
            if good_line is False:
                log.warning("segment too short for shape {}, so creating 2-point line between stops {} and {}".format(
                    trip.shape_id, begin_stop.stop.stop_code, end_stop.stop.stop_code))
                self.geom = util.make_linestring_from_two_stops(begin_stop.stop, end_stop.stop)
        except:
            log.warning("can't make geom for {}".format(id))

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

        return stop_segment

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
                prev = None
                if stop_times_len > 1:
                    printer('.', end='', flush=True, do_print=do_print and j % chunk_size == 0)
                    for i, st in enumerate(stop_times):
                        # build a segment between this and next stop
                        begin_stop = stop_times[i]
                        end_stop = stop_times[i+1]
                        curr = cls._cache_segment(session, begin_stop, end_stop, t, segment_cache, trip_cache)

                        # start to build a linked list of segment to segment ids (used later in conflation)
                        if prev:
                            prev.next_seg_id = curr.id
                            curr.prev_seg_id = prev.id
                        prev = curr

                        # stop condition: need 2 stops to build a segment
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
    def query_segments(cls, session, limit=None):
        q = session.query(StopSegment).order_by(StopSegment.id)
        if limit and type(limit) is int:
            segments = q.limit(limit)
        else:
            segments = q.all()
        return segments

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
                       '"code": "{}", ' \
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
                featgeo += feature_tmpl.format(f.begin_stop_id, f.begin_stop_code, "", "stop", stop_cache[f.begin_stop_id], ",\n")
            featgeo += feature_tmpl.format(f.id, f.code_id, f.direction, "stop", geom, ",\n")
            for t in f.traffic_segment:
                tgeo = session.scalar(func.ST_AsGeoJSON(t.geom))
                featgeo += feature_tmpl.format(t.traffic_segment_id, t.traffic_segment_id + " (" + f.code_id + ")", t.direction, "traffic", tgeo, ",\n")
            comma = ",\n" if i < ln else "\n"  # don't add a comma to last feature
            featgeo += feature_tmpl.format(f.end_stop_id, f.end_stop_code, "", "stop", stop_cache[f.end_stop_id], comma)
            last_stop = f.end_stop_id

        geojson = '{{\n  "type": "FeatureCollection",\n  "features": [\n{}  ]\n}}'.format(featgeo)
        return geojson


# todo: make util ... py2 and py3
def printer(content, end='\n', flush=False, do_print=True):
   if do_print:
       #pass #print(content, end=end, flush=flush)
       print(content)
