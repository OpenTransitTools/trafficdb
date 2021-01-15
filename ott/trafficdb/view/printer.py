import time
from ott.utils import json_utils
import json

from ott.trafficdb.model.traffic_segment import TrafficSegment
from ott.trafficdb.control.utils import make_session


def publisher(cmd_name="bin/publisher"):
    """ simple demo """
    session = make_session(cmd_name)
    segments = TrafficSegment.query_segments(session, limit=4)

    s = {
        "date": int(time.time()),
        "numSpeedRecords": len(segments.all()),
        "speeds": []
    }
    #print(s);    return
    json_str = json_utils.dict_to_json_str(s, pretty_print=True, indent=2)
    print(json_str)


def main(cmd_name="bin/printer", just_speeds=False):
    """ simple demo """
    #import pdb;    pdb.set_trace()
    session = make_session(cmd_name)
    TrafficSegment.print_all(session, just_speeds=just_speeds)
