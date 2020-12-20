import enum
from ott.utils import geo_utils
from .base import ini

# service names
class InrixService(enum.Enum):
  GetSegmentSpeedinBox = 1
  GetSegmentSpeedInGeography = 2
  GetSegmentSpeed = 3


def make_inrix_url(service, units="0", resolution=50, interval=None, start_time=None, format="json"):
    """
    base url routine will build INRIX traffic (speed data) requests
    note: a 'token' parameter is also necessary on these urls in order to pull data from INRIX

    service is the 'name' of the INRIX speed service

    units=0 is English (default), and units=1 is Metric

    resolution: If resolution is specified, the speed of sub-segment is returned for a subsegment length which closely
                matches the value provided for the Resolution parameter which is in meters. The sub-segment is specified
                in terms of offsets. The length of the sub-segment will be based on the resolution specified. The
                default is 0, which means "full resolution" or one section per segment. Sub-segments are only returned
                if the sub-segment speed is more than 5 mph different from the speed on the overall segment.
    """
    # import pdb; pdb.set_trace()
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
    
    note: not sure this parameter is valid for all speed data services (it's only documented in some bulk services)
    """
    if interval:
        url = "{}&interval={}".format(url, interval)

    """
    startTime:  Query Datetime The expected traffic at this time. The default is the current time. All times should be
                in UTC or have the timezone offset as specified in DateTime Values

    note: not sure this parameter is valid for all speed data services (it's only documented in some bulk services)
    """
    if start_time:
        url = "{}&startTime={}".format(url, start_time)

    return url


def speeds_url_state(geo_id=None):
    """
    geo_id = INRIX's geoID for Oregon is 243
    http://api.inrix.com/Traffic/Inrix.ashx?action=GetSegmentSpeedInGeography&geoID=243&token=
    :see: http://docs.inrix.com/traffic/speed/
    """
    geo_id = geo_id or "243"
    url = "{}&geoID={}".format(make_inrix_url(InrixService.GetSegmentSpeedInGeography.name), geo_id)
    return url


def speeds_url_bbox(bbox=None):
    """
    ?action=GetSegmentSpeedinBox
    :see: http://docs.inrix.com/traffic/speed/#get-getsegmentspeedinbox
    """
    bbox = bbox or "45.596874,-122.657228,45.425134,-122.612066"
    pt1, pt2 = geo_utils.bbox_to_points(bbox, sep="|")
    url = "{}&corner1={}&corner2={}".format(make_inrix_url(InrixService.GetSegmentSpeedinBox.name), pt1, pt2)
    return url


def speeds_url_segments(segment_ids=None):
    """
    segments: 13th & Bybee Blvd are 385703529,385862590,385869437,385869437,440964536,440964537

    http://{serverPath}.INRIX.com/traffic/Inrix.ashx?Action=GetSegmentSpeed&token={tokenHere}
    &segments=385703529,385862590,385869437,385869437,440964536,440964537
    &duration=0&units=0&resolution=10&format=json

    :see: http://docs.inrix.com/traffic/speed/#get-getsegmentspeed
    """
    # import pdb; pdb.set_trace()
    segment_ids = segment_ids or "385703529,385862590,385869437,385869437,440964536,440964537"
    url = "{}&segments={}".format(make_inrix_url(InrixService.GetSegmentSpeed.name), segment_ids)
    return url
