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


def group_results(rez):
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
        a = StopSegment
        b = traffic_segments_cls

        segments = []
        for s in session.query(StopSegment.shape_id).distinct():
            shape_id = s[0]
            shapes = session.query(Shape).filter(Shape.shape_id == shape_id).order_by(Shape.shape_pt_sequence).all()

            rez = session.query(
                a, b
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

            #import pdb; pdb.set_trace()
            qsegs = group_results(rez)
            for k in qsegs.keys():
                for g in qsegs[k]:
                    # make sure the stop sequence coords nearest to the start & end of transit segment are different
                    if g[2] == g[3]:
                        continue

                    a = g[0]
                    b = g[1]

                    x = Shape.get_sequence_from_dist(a.begin_distance, shapes)
                    y = Shape.get_sequence_from_dist(a.end_distance, shapes)

                    # will make sure the index of the nearest transit segments are in the right order
                    slat, slon = geo_utils.ll_from_point_str(g[2])
                    elat, elon = geo_utils.ll_from_point_str(g[3])
                    st = Shape.get_sequence_from_coord(slat, slon, shapes[x-1:y])
                    ed = Shape.get_sequence_from_coord(elat, elon, shapes[x-1:y])
                    if st >= ed:
                        continue

                    st_dist = g[4]
                    ed_dist = g[5]
                    k_dist = g[6]
                    m = "{:<11} ({:^2}) {:>11} ({} {:^14}): {:>3} to {:>3} - {:>3} {:>3} (sd: {:5.6f} ed: {:5.6f} k: {:5.6f})".format(
                        a.id, a.direction, b.id, b.direction, StreetType.get_name(b.frc), x, y, st, ed, st_dist, ed_dist, k_dist
                    )
                    print(m)
                    # import pdb; pdb.set_trace()

            #import pdb; pdb.set_trace()

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
