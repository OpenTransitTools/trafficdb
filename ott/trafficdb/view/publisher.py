import time
from ott.utils import json_utils

from ott.trafficdb.model.traffic_segment import TrafficSegment
from ott.trafficdb.control.utils import make_session


def cmdline(cmd_name="bin/publisher"):
    # todo ... add options for output file and directory, etc...
    session = make_session(cmd_name)
    return session


def calculate_segment_speed_data(rec):
    """
    loop thru
    """
    ret_val = { "hasSpeedData": False }

    if rec and "speeds" in rec and rec.speeds:
        date = 111111111
        currentSpeed = 60.0
        minSpeed = 10.0
        maxSpeed = 80.0
        freeflowSpeed = 55.0
        averageSpeed = 55.0
        isRealtime = False
        confidence = 0.0

        ret_val = {
            "hasSpeedData": True,

            "date": date,

            "currentSpeed": currentSpeed,
            "minSpeed": minSpeed,
            "maxSpeed": maxSpeed,
            "isRealtime": isRealtime,
            "confidence": confidence,

            "freeflowSpeed": freeflowSpeed,
            "averageSpeed": averageSpeed
        }
    return ret_val


def make_segment_json(rec):
    """
    makes a json object for publishing
    """
    ret_val = {
        "id": "",
        "beginStopId": "",
        "endStopId": "",
        "lenghtInFeet": ""
    }

    speed = calculate_segment_speed_data(rec)
    ret_val.update(speed)

    return ret_val


def publisher():
    """
    """
    #import pdb; pdb.set_trace()
    session = cmdline()
    segments = TrafficSegment.query_segments(session, limit=4)

    speeds = [make_segment_json(None)]

    s = {
        "date": int(time.time()),
        "numSpeedRecords": len(segments.all()),
        "speeds": speeds
    }
    json_str = json_utils.dict_to_json_str(s, pretty_print=True, indent=2)
    print(json_str)


def main():
    publisher()
