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


def speeds_url_state(geo_id="243"):
    """
    Oregon is geoID=243
    http://api.inrix.com/Traffic/Inrix.ashx?action=GetSegmentSpeedInGeography&geoID=243&token=
    :see: http://docs.inrix.com/traffic/speed/
    """
    url = "{}&geoID={}".format(make_inrix_url("GetSegmentSpeedInGeography"), geo_id)
    return url


def speeds_url_bbox(bbox=None):
    """
    ?Action=GetSegmentSpeedinBox
    :see: http://docs.inrix.com/traffic/speed/
    """
    url = "{}&bbox={}".format(make_inrix_url("GetSegmentSpeedinBox"), bbox)
    return url
