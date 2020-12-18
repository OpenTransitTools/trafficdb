import requests
from ott.utils import token_utils
from .base import ini


def get_inrix_token(renew=False):
    """
    http://na.api.inrix.com/traffic/Inrix.ashx?format=json&action=getsecuritytoken&vendorid=<your vid>&consumerid=<your cid>
    will return json, ala { result: { token: < me> }, ... }

    FYI: git update-index --assume-unchanged config/base.ini
    """
    #import pdb; pdb.set_trace()
    token = None

    # step 1: try to get a cached token from someplace
    if not renew:
        if hasattr(get_inrix_token, '_TOKEN_'):
            token = get_inrix_token._TOKEN_
        else:
            token = token_utils.get_cached_token()

    # step 2: renew either invalid token or 'forced' renew
    if token is None or renew:
        url = ini().get('traffic_url')
        vendorid = ini().get('vendorid')
        consumerid = ini().get('consumerid')
        token_url = "{}?action=getsecuritytoken&format=json&vendorid={}&consumerid={}".format(url, vendorid, consumerid)
        resp = requests.get(token_url)
        token = resp.json()['result']['token']

        # step 3: cache newly gotten token
        if token and len(token) > 1:
            get_inrix_token._TOKEN_ = token  # in memory cache
            token_utils.put_cached_token(token)  # file cache
        else:
            token = None

    return token


def main(argv=None):
    try:
        token = get_inrix_token()
        print(token)
    except:
        print("error: does ./config/base.ini have an 'inrix' section, with valid vendorid and consumerid values?")
