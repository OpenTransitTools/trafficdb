from .conflate import Conflate
from ott.trafficdb.control.utils import make_session
from ott.trafficdb.model.database import Database
from ott.trafficdb.model.stop_segment import StopSegment
from ott.trafficdb.model.traffic_segment import TrafficSegment

import logging
log = logging.getLogger(__file__)


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
            segments = cfl.ordered_segments(shape_id=s[0])
            for s in segments:
                #print(cfl.format_info(s))
                pass
            #import pdb; pdb.set_trace()
            x = False
            if x:
              break

        #import pdb; pdb.set_trace()


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
