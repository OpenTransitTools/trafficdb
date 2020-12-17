import time
import requests
from .base import speeds_url_segments

import logging
log = logging.getLogger(__file__)


def download_speed_data(count=0, num_tries=3):
    """
    http://na.api.inrix.com/traffic/Inrix.ashx?format=json&action=getsecuritytoken&vendorid=<your vid>&consumerid=<your cid>
    will return json, ala { result: { token: < me> }, ... }

    FYI: git update-index --assume-unchanged config/base.ini
    """
    ret_val = None
    try:
        log.info("get speed data")
        url = speeds_url_segments(force=(count > 0))
        ret_val = requests.get(url).json()
        if ret_val['statusText'] == 'TokenExpired':
            if count < num_tries:
                time.sleep(count * 5)
                ret_val = download_speed_data(count + 1)
    except:
        if count < num_tries:
            time.sleep(count * 5)
            ret_val = download_speed_data(count + 1)
        else:
            log.error("does ./config/base.ini have an 'inrix' section, with valid vendorid and consumerid values?")
    return ret_val


def main(argv=None):
    ret_val = download_speed_data()
    print(ret_val)
