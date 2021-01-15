from sqlalchemy import and_, or_
from geoalchemy2 import func

from ott.utils import geo_utils
from gtfsdb import Shape
from ott.trafficdb.model.stop_segment import StopSegment
from ott.trafficdb.model.traffic_segment import StreetType

import logging
log = logging.getLogger(__file__)


class ConflatedSegment(object):
    stop_segment = None
    traffic_segment = None
    street_type = None

    # the range is the shape's pt. sequence of the stop_segment
    range_start = 1111111
    range_end = -1

    # the start_sequence / end_sequence is the shape's nearest sequence pt(s) for traffic seg's start/end
    start_sequence = 111111
    end_sequence = -1
    start_distance = 111.111
    end_distance = 111.111

    # distance and percent that this transit segment occupies of the stop segment (pattern)
    transit_shp_distance = 0.0
    transit_shp_percent = 0.0

    is_very_close = False
    is_kinda_close = False
    rank = 111

    def __init__(self, rez, range_start, range_end, start_seq, end_seq):
        self.stop_segment = rez[0]
        self.traffic_segment = rez[1]
        self.street_type = StreetType.get_name(rez[1].frc)
        self.range_start = range_start
        self.range_end = range_end
        self.start_sequence = start_seq
        self.end_sequence = end_seq
        self.start_distance = rez[4]
        self.end_distance = rez[5]

        if self.start_distance <= 0.0001 and self.end_distance <= 0.0001:
            self.is_very_close = True
        elif self.start_distance < 0.001 and self.end_distance <= 0.001:
            self.is_kinda_close = False

    def in_sequence(self):
        """
        check the order of the start / end sequence
        (e.g., a street (line) in the opposite direction with have shape sequence pts in the wrong order)
        """
        ret_val = self.start_sequence < self.end_sequence and self.end_sequence > self.range_start
        return ret_val

    def overlap(self, obj):
        ret_val = False
        if self.traffic_segment != obj.traffic_segment and \
           self.start_sequence <= obj.end_sequence and obj.start_sequence <= self.end_sequence:
            ret_val = True
        return ret_val

    def is_next(self, obj):
        return self.end_sequence == obj.start_sequence

    def is_prev(self, obj):
        return obj.end_sequence == self.start_sequence

    def is_closer(self, obj):
        ret_val = False
        if self.start_distance <= obj.start_distance and self.end_distance <= obj.end_distance:
            ret_val = True
        return ret_val

    def calculate_distance_percent(self, cfl, def_val=0.0):
        """ calculates percents and distance of transit segment on the stop segment """
        transit_dist = cfl.calculate_distance(self.stop_segment.shape_id, self.start_sequence, self.end_sequence, def_val)
        self.transit_shp_distance = transit_dist

        percent = 0.0
        stop_dist = float(self.stop_segment.distance)
        if stop_dist:
            percent = float(transit_dist) / stop_dist
        if percent > 1.0 or percent <= 0.05:
            #import pdb; pdb.set_trace()
            stop_dist = self.range_end - self.range_start
            if stop_dist > 0.0:
                percent = (self.end_sequence - self.start_sequence) / stop_dist
        if percent > 1.0 or percent <= 0.0:
            percent = 0.05
        self.transit_shp_percent = percent

    def format_info(self):
        # import pdb; pdb.set_trace()
        msg = "{s.stop_segment.id:<11} ({s.stop_segment.direction:^2}) " \
          "{s.traffic_segment.id:>11} ({s.traffic_segment.direction} " \
          "{s.street_type:^14}): {s.range_start:>3} to {s.range_end:>3} - {s.start_sequence:>3} {s.end_sequence:>3} " \
          "(sd: {s.start_distance:5.6f} ed: {s.end_distance:5.6f}) ".format(s = self)
        return msg


class Conflate(object):
    """
    collection of routines for querying and filtering transit segments that match stop segment(s)
    """
    def __init__(self, session, traffic_class, stop_class=StopSegment):
        self.session = session
        self.stop_class = stop_class
        self.traffic_class = traffic_class
        self._shapes = []

    @property
    def shapes(self):
        """ get list of Shape(s) for the 'current_shape_id' (see query_segments for where that's stored) """
        # import pdb; pdb.set_trace()
        try:
            if not self._shapes or self._shapes[0].shape_id != self._current_shape_id:
                self._shapes = self.session.query(Shape).filter(Shape.shape_id == self._current_shape_id). \
                    order_by(Shape.shape_pt_sequence).all()
                #print(self._shapes[0].shape_id)
        except Exception as e:
            log.warning(e)
            pass
        return self._shapes

    def query_segments(self, shape_id):
        self._current_shape_id = shape_id

        a = self.stop_class
        b = self.traffic_class
        rez = self.session.query(
            self.stop_class, self.traffic_class
            , func.ST_AsText(func.ST_ClosestPoint(func.ST_Points(a.geom), func.ST_StartPoint(b.geom)))
            , func.ST_AsText(func.ST_ClosestPoint(func.ST_Points(a.geom), func.ST_EndPoint(b.geom)))
            , func.ST_Distance(func.ST_StartPoint(b.geom), a.geom)
            , func.ST_Distance(func.ST_EndPoint(b.geom), a.geom)
            , func.ST_Distance(a.geom, b.geom)
        ).filter(
            and_(
              a.shape_id == shape_id,
              func.ST_DWithin(a.geom, b.geom, 0.001)
            )
        ).order_by(a.id)

        """
        , func.ST_ClosestPoint(func.ST_Points(a.geom), func.ST_StartPoint(b.geom))
        , func.ST_ClosestPoint(func.ST_Points(a.geom), func.ST_EndPoint(b.geom))
        , func.ST_ClosestPoint(func.ST_Points(b.geom), func.ST_StartPoint(a.geom))
        , func.ST_ClosestPoint(func.ST_Points(b.geom), func.ST_EndPoint(a.geom))
        , func.ST_Contains(func.ST_Buffer(a.geom, 0.00001), b.geom)
        , func.ST_Contains(func.ST_Buffer(a.geom, 0.0001), b.geom)
        , func.ST_Contains(func.ST_Buffer(a.geom, 0.001), b.geom)
        """

        qsegs = self.group_results(rez)
        return qsegs

    def segment_factory(self, rez):
        """
        takes a single result set, from the above query (e.g., rez param), and turns it into a 'usable' named dict
        """
        # import pdb; pdb.set_trace()
        a = rez[0]
        x = Shape.get_sequence_from_dist(a.begin_distance, self.shapes)
        y = Shape.get_sequence_from_dist(a.end_distance, self.shapes)

        # will make sure the index of the nearest transit segments are in the right order
        slat, slon = geo_utils.ll_from_point_str(rez[2])
        elat, elon = geo_utils.ll_from_point_str(rez[3])
        st = Shape.get_sequence_from_coord(slat, slon, self.shapes[x-1:y], def_val=-1)
        ed = Shape.get_sequence_from_coord(elat, elon, self.shapes[x-1:y], def_val=-11)

        # factory
        cs = ConflatedSegment(rez, x, y, st, ed)
        return cs

    def ordered_segments(self, shape_id, do_sort=True):
        """
        will query all the traffic segments, filter then match them to the stops, then sort based on shape pt sequence
        """
        ret_val = []
        qsegs = self.query_segments(shape_id)
        for k in qsegs.keys():
            for g in qsegs[k]:
                # filter 1: filter records if traffic's stop & end point are closest to same stop segment point
                if self.closest_points_are_different(g):
                    continue

                # parse the database result set into an dictionary
                s = self.segment_factory(g)

                # filter 2: filter records if the start point is closer to a larger shp pt index than the end
                # (e.g., the traffic line (street) is probably the opposite street direction from stop segment)
                if not s.in_sequence():
                    continue

                ret_val.append(s)

        # sort the results
        if do_sort:
            ret_val = sorted(ret_val, key = lambda i: (i.range_start, i.start_sequence))

        return ret_val

    def calculate_distance(self, shape_id, shape_start, shape_end, def_val=0.0):
        """
        """
        try:
            self._current_shape_id = shape_id
            st = self.shapes[shape_start].shape_dist_traveled
            ed = self.shapes[shape_end].shape_dist_traveled
            ret_val = ed - st
        except:
            ret_val = def_val
        return ret_val


    @classmethod
    def closest_points_are_different(cls, rez):
        """
        make sure the stop sequence coords nearest to the start & end of transit segment are different
        note: in the result set above (rez param), items 3 & 4 are the nearest points
        """
        ret_val = rez[2] == rez[3]
        return ret_val

    @classmethod
    def group_results(cls, rez):
        """
        will group the query results by the stop-segment id
        :return: dictionary of various stop segments, and the query results
        """
        ret_val = {}
        curr_i = 'ZZZ'
        for r in rez:
            ss = r[0]
            if curr_i != ss.id:
                curr_i = ss.id
                ret_val[ss.id] = []
            ret_val[ss.id].append(r)
        return ret_val
