import sys
import requests
from . import urls
from .get_token import get_inrix_token

import logging
log = logging.getLogger(__file__)


def download_speed_data(func=None):
    """
    closure that will grab data from a given service...

    http://na.api.inrix.com/traffic/Inrix.ashx?format=json&action=getsecuritytoken&vendorid=<your vid>&consumerid=<your cid>
    will return json, ala { result: { token: < me> }, ... }

    confidence:
      - 'score': 30 (real-time data) and 'c-Value': 0-100 (% confidence)
      - 'score': 20 (mix of historic and real-time) and 'c-Value': ??? (not sure there is a value here)
      - 'score': 10 (historic data .. no probes) and 'c-Value': ??? (not sure there is a value here)

    FYI: git update-index --assume-unchanged config/base.ini
    """
    def inner(param, force=False):
        # step 1: get url (existing token)
        url = "{}&token={}".format(func(param), get_inrix_token(renew=force))
        log.info(url)

        # step 2: call service
        ret_val = requests.get(url).json()

        # step 3: if token is bad, call things again (via recursion) and ask to renew token
        if(ret_val['statusText'] in ['TokenExpired', 'BadToken'] and not force):
            ret_val = inner(param, force=True)
        return ret_val
    return inner


@download_speed_data
def call_data_service(service=None, param=None):
    if not service:
        url = urls.speeds_url_bbox(param)
    else:
        url = urls.speeds_url_segments(param)
    return url


def main(argv=sys.argv):
    data = call_data_service(argv[1] if len(argv) > 1 else None)
    print(data)