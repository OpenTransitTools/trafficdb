from ott.trafficdb.model.database import Database
from ott.trafficdb.model.traffic_segment import TrafficSegment
from ott.trafficdb.control.utils import make_session

import logging
log = logging.getLogger(__file__)


# TODO how to make this vendor agnostic?
# TODO do all vendors have a similar query by id and bbox?
def speeds_via_bbox(bbox):
    """
    GET traffic speed data via bbox and return Speed ORM objects
    :param bbox: string in the form of 45.5,-122.5,45.6,-122.6
    :return: list of TrafficSegmentSpeed ORM objects
    """
    from .inrix.speed_data import speeds_via_bbox as inrix_speeds_via_bbox
    return inrix_speeds_via_bbox(bbox)


def speeds_via_id(ids):
    """
    GET traffic speed data via segment id(s) and return Speed ORM objects
    :param ids: string in the form of 33333 or 22222,33333,44444,55555
    :return: list of TrafficSegmentSpeed ORM objects
    """
    from .inrix.speed_data import speeds_via_id as inrix_speeds_via_id
    inrix_speeds_via_id(ids)


def main(cmd_name="bin/load_speed_data", via_bbox=True):
    # step 1: cmd line options to obtain session
    # import pdb; pdb.set_trace()
    session = make_session(cmd_name)

    # step 2: http get the latest traffic speed data from vendor (either via bbox or vendor's segment ids)
    if via_bbox:
        bbox = TrafficSegment.bbox(session, 0.001, normalize=True)
        speed_recs = speeds_via_bbox(bbox)
    else:
        segment_ids = TrafficSegment.get_segment_ids(session)
        ids = ','.join(map(str, segment_ids))
        speed_recs = speeds_via_id(ids)

    # step 3: persist that data to database
    Database.persist_data(session, speed_recs)

    # step 4: query the db and print out the speed data
    TrafficSegment.print_all(session, just_speeds=True)


if __name__ == '__main__':
    main()
