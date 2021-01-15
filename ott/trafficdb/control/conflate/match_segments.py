from .conflate import Conflate
from ott.trafficdb.control.utils import make_session
from ott.trafficdb.model.database import Database
from ott.trafficdb.model.stop_segment import StopSegment
from ott.trafficdb.model.traffic_segment import TrafficSegment

import logging
log = logging.getLogger(__file__)


def filter_best_segments(segs):
    """
    filter segments

    note: this is kinda working ... but not sure it's great

    going to move on for now, but here's another algorithm:
    - loop #1 - in a class that manages groups of segments,
      sub-loop #1 (goal is to find sequential segments):
              - loop thru each stop segment
              - sub loop, find sequential traffic segments 1-4, 4-7, etc...
              - when 2 segments overlap, choose which segment is closer ... move other segment aside
      sub-loop #2
              - try to find places for the reject list (is there an overall better set of points than loop 1)

    - loop 2: - another query to fill in any stop-segments missing traffic data
    .....
    """
    #import pdb; pdb.set_trace()
    ret_val = []
    for s in segs:
        prev = ret_val[-1] if ret_val else s
        do_pop = not s.is_prev(prev)

        if s.is_prev(prev):
            ret_val.append(s)
        elif s.is_closer(prev):
            if do_pop and ret_val:
                ret_val.pop()
            ret_val.append(s)
        elif s.is_very_close:
            ret_val.append(s)
        # elif s.is_kinda_close
        # other_segs.append(s) put segs aside, and see if they fit into ret_val with a second pass

    return ret_val


def match_traffic_to_stop_segments(session, traffic_segments_cls):
    """
    will find all traffic segments in the database that align up with
    """
    ret_val = []

    try:
        # step 1: create the conflate query object / controller
        cfl = Conflate(session, traffic_segments_cls)

        # step 2: for each shape used in the stop segments, query and filter matching traffic segments
        # import pdb; pdb.set_trace()
        segments = []
        for s in session.query(StopSegment.shape_id).distinct():
            segments_all = cfl.ordered_segments(shape_id=s[0])
            segments += filter_best_segments(segments_all)

        # step 3: loop thru the found traffic segment data and create ORM objects for these things
        for s in segments:
            ts = TrafficSegment.factory(s.stop_segment, s.traffic_segment)
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
