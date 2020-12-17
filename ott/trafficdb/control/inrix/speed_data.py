import time
from .get_token import get_inrix_token

import logging
log = logging.getLogger(__file__)


def download_speed_data(count=2, num_tries=3):
    """
    http://na.api.inrix.com/traffic/Inrix.ashx?format=json&action=getsecuritytoken&vendorid=<your vid>&consumerid=<your cid>
    will return json, ala { result: { token: < me> }, ... }

    FYI: git update-index --assume-unchanged config/base.ini
    """
    ret_val = None
    try:
        log.info("get speed data")
        token = get_inrix_token()
        ret_val = token
    except Exception as e:
        if count <= num_tries:
            time.sleep(5)
            ret_val = download_speed_data(count + 1)
        else:
            log.error("does ./config/base.ini have an 'inrix' section, with valid vendorid and consumerid values?")
    return ret_val


def main(argv=None):
    ret_val = download_speed_data()
    print(ret_val)
