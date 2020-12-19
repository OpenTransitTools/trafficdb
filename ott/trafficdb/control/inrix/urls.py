from .base import ini


# service names
SPEED_VIA_BBOX="GetSegmentSpeedinBox"
SPEED_VIA_GEOM_ID="GetSegmentSpeedInGeography"
SPEED_VIA_SEGMENT_IDs="GetSegmentSpeed"


def make_inrix_url(service, units="0", resolution=50, interval=None, start_time=None, format="json"):
    """
    base url routine will build INRIX traffic (speed data) requests
    note: a 'token' is additionally necessary on these urls

    service is the 'name' of the INRIX speed service

    units=0 is English (default), and units=1 is Metric

    resolution: If resolution is specified, the speed of sub-segment is returned for a subsegment length which closely
                matches the value provided for the Resolution parameter which is in meters. The sub-segment is specified
                in terms of offsets. The length of the sub-segment will be based on the resolution specified. The
                default is 0, which means "full resolution" or one section per segment. Sub-segments are only returned
                if the sub-segment speed is more than 5 mph different from the speed on the overall segment.

    startTime:  Query Datetime The expected traffic at this time. The default is the current time. All times should be
                in UTC or have the timezone offset as specified in DateTime Values
    """
    url = "{}?action={}&format={}&units={}&resolution={}".format(
          ini().get('traffic_url'),
          service, format, units, resolution
    )

    """
    interval = 5, 15 (default), 30, 60 -- the period of time in minutes between reports when the duration parameter
               is non-zero. The first set of data in the response will have the real-time timestamp. The timestamp for
               subsequent sets will have a minute value that is a multiple of the interval value. For example, an
               interval value of 30 specifies data sets on the hour and 30 minutes past the hour. The interval parameter
               is used in conjunction with the duration parameter.
    """
    if interval:
        url = "{}&interval={}".format(url, interval)

    """
    startTime:  Query Datetime The expected traffic at this time. The default is the current time. All times should be
                in UTC or have the timezone offset as specified in DateTime Values
    """
    if start_time:
        url = "{}&startTime={}".format(url, start_time)

    return url


def speeds_url_state(geo_id="243"):
    """
    geo_id = INRIX's geoID for Oregon is 243
    http://api.inrix.com/Traffic/Inrix.ashx?action=GetSegmentSpeedInGeography&geoID=243&token=
    :see: http://docs.inrix.com/traffic/speed/
    """
    url = "{}&geoID={}".format(make_inrix_url(SPEED_VIA_GEOM_ID), geo_id)
    return url


def speeds_url_bbox(lat_lon_1="45.55|-122.55", lat_lon_2="45.56|-122.56"):
    """
    ?action=GetSegmentSpeedinBox
    :see: http://docs.inrix.com/traffic/speed/#get-getsegmentspeedinbox
    """
    url = "{}&corner1={}&corner2={}".format(make_inrix_url(SPEED_VIA_BBOX), lat_lon_1, lat_lon_2)
    return url


def speeds_url_segments(segment_ids="385703529,385862590,385869437,385869437,440964536,440964537"):
    """
    segments: 13th & Bybee Blvd are 385703529,385862590,385869437,385869437,440964536,440964537

    http://{serverPath}.INRIX.com/traffic/Inrix.ashx?Action=GetSegmentSpeed&token={tokenHere}
    &segments=385703529,385862590,385869437,385869437,440964536,440964537
    &duration=0&units=0&resolution=10&format=json

    :see: http://docs.inrix.com/traffic/speed/#get-getsegmentspeed
    """
    url = "{}&segments={}".format(make_inrix_url(SPEED_VIA_SEGMENT_IDs), segment_ids)
    return url
