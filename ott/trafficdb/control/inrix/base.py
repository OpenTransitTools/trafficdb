from ott.utils.config_util import ConfigUtil


def ini(section='inrix'):
    if not hasattr(ini, '_INI_'):
        ini._INI_ = ConfigUtil.factory(section)
    return ini._INI_


def make_inrix_url(service, token=None, force=False, format="json"):
    if token is None or force:
        from .get_token import get_inrix_token
        token = get_inrix_token(renew=force)

    url = "{}?action={}&format={}&token={}".format(ini().get('traffic_url'), service, format, token)
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
    """
    url = "{}&segments={}".format(make_inrix_url("GetSegmentSpeed", force=force), segment_ids)
    #print(url)
    return url
