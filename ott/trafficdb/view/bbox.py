from ott.trafficdb.model.traffic_segment import TrafficSegment
from ott.trafficdb.control.utils import make_session
from ott.utils import geo_utils


def main(cmd_name="bin/bbox"):
    session = make_session(cmd_name)
    p = TrafficSegment.bbox(session)
    p = geo_utils.normalize_postgis_bbox(p)

    q = TrafficSegment.bbox(session, 0.001)
    q = geo_utils.normalize_postgis_bbox(q)

    print(p)
    print(q)