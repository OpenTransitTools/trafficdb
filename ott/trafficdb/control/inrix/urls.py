from .base import ini
from .get_token import get_inrix_token


def make_inrix_url(service, token=None, force=False, units="0", format="json"):
    """
    main url routine
    units=0 is English (default), and units=1 is Metric
    """
    if token is None or force:
        token = get_inrix_token(renew=force)

    url = "{}?action={}&units={}&format={}&token={}".format(ini().get('traffic_url'), service, units, format, token)
    return url


def speeds_url_state(geo_id="243", force=False):
    """
    Oregon is geoID=243
    http://api.inrix.com/Traffic/Inrix.ashx?action=GetSegmentSpeedInGeography&geoID=243&token=
    :see: http://docs.inrix.com/traffic/speed/
    """
    url = "{}&geoID={}".format(make_inrix_url("GetSegmentSpeedInGeography", force=force), geo_id)
    return url


def speeds_url_bbox(bbox=None, force=False):
    """
    ?Action=GetSegmentSpeedinBox
    :see: http://docs.inrix.com/traffic/speed/
    """
    url = "{}&bbox={}".format(make_inrix_url("GetSegmentSpeedinBox", force=force), bbox)
    return url


def speeds_url_segments(segment_ids="385703529,385862590,385869437,385869437,440964536,440964537", force=False):
    """
    13th & Bybee Blvd are 385703529,385862590,385869437,385869437,440964536,440964537

    http://{serverPath}.INRIX.com/traffic/Inrix.ashx?Action=GetSegmentSpeed&token={tokenHere}
    &Segments=5908854|XDS,5898079|XDS,5898012|XDS,111%2B11479|TMC,113-04803|TMC
    &Duration=0&Units=1&Resolution=250&format=json

    :see: http://docs.inrix.com/traffic/speed/#get-getsegmentspeed

    resolution: If resolution is specified, the speed of sub-segment is returned for a subsegment length which closely
                matches the value provided for the Resolution parameter which is in meters. The sub-segment is specified
                in terms of offsets. The length of the sub-segment will be based on the resolution specified. The
                default is 0, which means "full resolution" or one section per segment. Sub-segments are only returned
                if the sub-segment speed is more than 5 mph different from the speed on the overall segment.

    """
    # url = "{}&segments={}".format(make_inrix_url("GetSegmentSpeed", force=force), segment_ids)
    url = "{}&segments={}&resolution=10".format(make_inrix_url("GetSegmentSpeed", force=force), segment_ids)
    print(url)
    return url
