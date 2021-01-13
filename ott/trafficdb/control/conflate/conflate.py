from sqlalchemy import and_, or_
from geoalchemy2 import func

from ott.utils import geo_utils
from gtfsdb import Shape
from ott.trafficdb.model.stop_segment import StopSegment
from ott.trafficdb.model.traffic_segment import StreetType

import logging
log = logging.getLogger(__file__)

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
            self._shapes = self.session.query(Shape).filter(Shape.shape_id == self._current_shape_id). \
                order_by(Shape.shape_pt_sequence).all()
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

            , func.ST_ClosestPoint(func.ST_Points(a.geom), func.ST_StartPoint(b.geom))
            , func.ST_ClosestPoint(func.ST_Points(a.geom), func.ST_EndPoint(b.geom))
            , func.ST_ClosestPoint(func.ST_Points(b.geom), func.ST_StartPoint(a.geom))
            , func.ST_ClosestPoint(func.ST_Points(b.geom), func.ST_EndPoint(a.geom))
            , func.ST_Contains(func.ST_Buffer(a.geom, 0.00001), b.geom)
            , func.ST_Contains(func.ST_Buffer(a.geom, 0.0001), b.geom)
            , func.ST_Contains(func.ST_Buffer(a.geom, 0.001), b.geom)
        ).filter(
            and_(
              a.shape_id == shape_id,
              func.ST_DWithin(a.geom, b.geom, 0.001)
            )
        ).order_by(a.id)

        qsegs = self.group_results(rez)
        return qsegs

    def rs_to_obj(self, rez):
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
        st = Shape.get_sequence_from_coord(slat, slon, self.shapes[x - 1:y])
        ed = Shape.get_sequence_from_coord(elat, elon, self.shapes[x - 1:y])

        ret_val = {
            'stop_segment': rez[0],
            'traffic_segment': rez[1],
            'street_type': StreetType.get_name(rez[1].frc),

            # the range is the shape's pt. sequence of the stop_segment
            'range_start': x,
            'range_end': y,

            # the start_sequence / end_sequence is the shape's nearest sequence pt(s) for traffic seg's start/end
            'start_sequence': st,
            'end_sequence': ed,

            'start_distance': rez[4],
            'end_distance': rez[5]
        }
        return ret_val

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
                m = self.rs_to_obj(g)

                # filter 2: filter records if the start point is closer to a larger shp pt index than the end
                # (e.g., the traffic line (street) is probably the opposite street direction from stop segment)
                if not self.in_sequence(m):
                    continue

                ret_val.append(m)

        # sort the results
        if do_sort:
            ret_val = sorted(ret_val, key = lambda i: (i['range_start'], i['start_sequence']))

        return ret_val

    @classmethod
    def format_info(cls, obj):
        #import pdb; pdb.set_trace()
        msg = "{stop_segment.id:<11} ({stop_segment.direction:^2}) " \
            "{traffic_segment.id:>11} ({traffic_segment.direction} " \
            "{street_type:^14}): {range_start:>3} to {range_end:>3} - {start_sequence:>3} {end_sequence:>3} " \
            "(sd: {start_distance:5.6f} ed: {end_distance:5.6f}) ".format(**obj)
        return msg

    @classmethod
    def in_sequence(cls, obj):
        """
        check the order of the start / end sequence
        (e.g., a street (line) in the opposite direction with have shape sequence pts in the wrong order)
        """
        ret_val = obj['start_sequence'] < obj['end_sequence']
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
