import time
from ott.utils import json_utils

from ott.trafficdb.model.stop_segment import StopSegment
from ott.trafficdb.control.utils import make_session


def cmdline(cmd_name="bin/publisher"):
    # todo ... add options for output file and directory, etc...
    session = make_session(cmd_name)
    return session


def calculate_segment_speed_data(rec, date):
    """
    loop thru
    """
    ret_val = {
        "hasSpeedData": False,
        "date": date
    }

    has_speed = False
    for t in rec.traffic_segment:
        for s in t.speeds:
            has_speed =  True
            break

    if has_speed:
        #date = rec.speeds.date()
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


def make_segment_json(rec, date):
    """
    makes a json object for publishing
    """
    ret_val = {
        "id": rec.id,
        "beginStopId": rec.begin_stop_id,
        "endStopId": rec.end_stop_id,
        "lengthInFeet": int(rec.distance)
    }

    speed = calculate_segment_speed_data(rec, date)
    ret_val.update(speed)

    return ret_val


def publisher():
    """
    """
    #import pdb; pdb.set_trace()
    date = int(time.time())
    session = cmdline()
    segments = StopSegment.query_segments(session, limit=4).all()
    speeds = []
    for s in segments:
        spd = make_segment_json(s, date)
        speeds.append(spd)

    rec = {
        "numSpeedRecords": len(segments),
        "speeds": speeds
    }
    json_str = json_utils.dict_to_json_str(rec, pretty_print=True, indent=2)
    print(json_str)


def main():
    publisher()
