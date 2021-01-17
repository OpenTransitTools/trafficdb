import time
from ott.utils import json_utils, num_utils

from ott.trafficdb.model.stop_segment import StopSegment
from ott.trafficdb.control.utils import make_session

import logging
log = logging.getLogger(__file__)


def cmdline(cmd_name="bin/publisher"):
    # todo ... add options for output file and directory, etc...
    session = make_session(cmd_name)
    return session


def calculate_segment_speed_data(rec, date):
    """
    loop thru segments and speeds, and find junk
    """
    ret_val = {
        "hasSpeedData": False,
        "date": date
    }

    has_speed = False
    total_percent = 0.0
    percent_realtime = 0.0

    numberOfLanes = 0.0
    minSpeed = 1000.0
    maxSpeed = 0.0
    currentSpeed = 0.0
    freeflowSpeed = 0.0
    averageSpeed = 0.0
    travelTime = 0.0
    confidence = 0.0

    for t in rec.traffic_segment:
        numberOfLanes += float(t.lanes * t.percent_of_stop_segment)
        total_percent += float(t.percent_of_stop_segment)
        time_percent = float(rec.distance / t.distance)
        if time_percent > 1.0 or time_percent <= 0.0:
            time_percent = 1.0
        # if rec.begin_stop_id == "9962" and rec.end_stop_id == "12884": import pdb; pdb.set_trace()

        for s in t.speeds:
            has_speed = True
            date = int(s.capture_time.timestamp())

            if s.slowest_speed < minSpeed:
                minSpeed = float(s.slowest_speed)
            if s.fastest_speed > maxSpeed:
                maxSpeed = float(s.fastest_speed)

            currentSpeed += float(t.percent_of_stop_segment * s.current_speed)
            freeflowSpeed += float(t.percent_of_stop_segment * s.freeflow_speed)
            averageSpeed += float(t.percent_of_stop_segment * s.average_speed)
            travelTime += float(t.percent_of_stop_segment * s.travel_time) * time_percent

            confidence += float(t.percent_of_stop_segment * s.rt_confidence)
            if s.is_realtime:
                percent_realtime += float(t.percent_of_stop_segment * s.rt_confidence)

    if has_speed:
        if total_percent == 0.0 or total_percent > 5.0:
            total_percent = 1.0
            log.warning("% == {} seems wrong for stop segment's traffic/speed data {}".format(total_percent, rec.id))

        currentSpeed = num_utils.to_float(currentSpeed / total_percent, round_to=2)
        freeflowSpeed = num_utils.to_float(freeflowSpeed / total_percent, round_to=2)
        averageSpeed = num_utils.to_float(averageSpeed / total_percent, round_to=2)
        travelTime = num_utils.to_float(travelTime / total_percent, round_to=4)
        numberOfLanes = num_utils.to_float(numberOfLanes / total_percent, round_to=2)
        confidence = num_utils.to_float(confidence / total_percent, round_to=2)
        percent_realtime = percent_realtime / total_percent
        isRealtime = True if percent_realtime > 0.5 else False

        # note travel time needs to be adjusted based on length of the stop segment (

        ret_val = {
            "hasSpeedData": True,
            "date": date,

            "numberOfLanes": numberOfLanes,
            "travelTimeInMins": travelTime,
            "isRealtime": isRealtime,
            "confidence": confidence,

            "minSpeed": minSpeed,
            "maxSpeed": maxSpeed,
            "currentSpeed": currentSpeed,
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
    # import pdb; pdb.set_trace()
    date = int(time.time())
    session = cmdline()
    segments = StopSegment.query_segments(session)
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
