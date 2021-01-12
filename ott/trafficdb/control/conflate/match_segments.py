from sqlalchemy import and_, or_
from geoalchemy2 import func

from ott.utils import geo_utils

from gtfsdb import Shape
from ott.trafficdb.model.database import Database
from ott.trafficdb.model.stop_segment import StopSegment
from ott.trafficdb.model.traffic_segment import TrafficSegment, StreetType
from ott.trafficdb.control.utils import make_session

import logging
log = logging.getLogger(__file__)


class Conflate(object):
    """
    """
    def __init__(self, session, traffic_class, stop_class=StopSegment):
        self.session = session
        self.stop_class = stop_class
        self.traffic_class = traffic_class
        self._shapes = []

    @property
    def shapes(self):
        """ get shape.txt for the 'current_shape_id' (see query_segments for where that's stored) """
        # import pdb; pdb.set_trace()
        try:
            if len(self._shapes) < 1 or self._shapes[0].shape_id != self._current_shape_id:
                self._shapes = self.session.query(Shape).filter(Shape.shape_id == self._current_shape_id).\
                    order_by(Shape.shape_pt_sequence).all()
        except Exception as e:
            log.warning(e)
            pass
        return self._shapes

    def ordered_segments(self, shape_id):
        """
        will query all the traffic segments, match them to the stops, then sort based on shape pt sequence
        """
        ret_val = []
        qsegs = self.query_segments(shape_id)
        for k in qsegs.keys():
            for g in qsegs[k]:
                if self.closest_points_are_different(g):
                    continue

                m = self.rs_to_obj(g)
                if not self.in_sequence(m):
                    continue

                ret_val.append(m)
                #print(self.format_info(m))
        # sort ret_val
        return ret_val

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


def match_traffic_to_stop_segments(session, traffic_segments_cls):
    """
    will find all traffic segments in the database that align up with
    """
    ret_val = []

    try:
        # step 1: find intersections and some buffer of the two geoms
        # import pdb; pdb.set_trace()
        cfl = Conflate(session, traffic_segments_cls)

        segments = []
        for s in session.query(StopSegment.shape_id).distinct():
            shape_id = s[0]

            segments = cfl.ordered_segments(shape_id)
            for s in segments:
                print(cfl.format_info(s))
            import pdb; pdb.set_trace()
            x = False
            if x:
              break

        import pdb; pdb.set_trace()


        def is_match(res):
            is_match = False

            # step 1: parse out the result set from the query above
            stop_seg = res[0]
            traffic_seg = res[1]
            is_match_tight = res[2]
            is_match_mid = res[3]
            is_match_loose = res[4]
            msg = "\n{} {} - {} {} {}".format(stop_seg.id, traffic_seg.id, is_match_tight, is_match_mid, is_match_loose)
            # why? debug?
            #log.debug(msg)

            # step 2: first check direction
            if stop_seg.direction in traffic_seg.direction or traffic_seg.direction in stop_seg.direction:
                # step 3: a tight match means things overlap well ... conflated
                if is_match_tight:
                    is_match = True
                # step 4: mid match plus XXXXXX ... conflated
                elif is_match_mid:
                    # TODO: add a bit more overlap testing here...
                    is_match = True
                # step 5: loose match plus XXXX & ZZZZ ... conflated
                elif is_match_loose:
                    # TODO: test on shared points within the 2 shapes
                    is_match = True

            return is_match

        # step b: loop thru and find matches based on a set of rules that follow, etc...
        for s in segments.all():
            if is_match(s):
                ts = TrafficSegment.factory(s[0], s[1])
                ret_val.append(ts)

    except Exception as e:
        log.warning(e)

    return ret_val


def main(cmd_name="bin/match_segments"):
    """ simple demo """
    from ott.trafficdb.model.inrix.inrix_segment import InrixSegment
    session = make_session(cmd_name)
    segments = match_traffic_to_stop_segments(session, InrixSegment)

    if segments:
        TrafficSegment.clear_tables(session)
        Database.persist_data(segments)


if __name__ == '__main__':
    main()
