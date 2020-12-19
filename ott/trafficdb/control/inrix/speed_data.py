import sys
import time
import requests
from  . import urls

import logging
log = logging.getLogger(__file__)


def download_speed_data(func=speeds_url_segments, first_param=None, count=0, num_tries=3):
    """
    http://na.api.inrix.com/traffic/Inrix.ashx?format=json&action=getsecuritytoken&vendorid=<your vid>&consumerid=<your cid>
    will return json, ala { result: { token: < me> }, ... }

    confidence:
      - 'score': 30 (real-time data) and 'c-Value': 0-100 (% confidence)
      - 'score': 20 (mix of historic and real-time) and 'c-Value': ??? (not sure there is a value here)
      - 'score': 10 (historic data .. no probes) and 'c-Value': ??? (not sure there is a value here)

    FYI: git update-index --assume-unchanged config/base.ini
    """
    ret_val = None
    try:
        log.info("get speed data")

        # TODO: figure out how decorators and/or closures would clean this func / first_param crap way up...
        # TODO SEE: Decorating Functions with Parameters at https://www.programiz.com/python-programming/decorator
        if first_param:
            url = func(first_param, force=(count > 0))
        else:
            url = func(force=(count > 0))
        ret_val = requests.get(url).json()
        if ret_val['statusText'] in ['TokenExpired', 'BadToken']:
            if count < num_tries:
                time.sleep(count * 5)
                ret_val = download_speed_data(func, first_param, count + 1)
    except:
        if count < num_tries:
            time.sleep(count * 5)
            ret_val = download_speed_data(func, first_param, count + 1)
        else:
            log.error("does ./config/base.ini have an 'inrix' section, with valid vendorid and consumerid values?")
    return ret_val



def smart_divide(func):
    def inner(a, b):
        print("I am going to divide", a, "and", b)
        if b == 0:
            print("Whoops! cannot divide")
            return

        print(func)
        return func(a, b)
    return inner


@smart_divide
def xdivide(a, b):
    print(a * b)


def x(segment_ids=None):
    url = urls.speeds_url_segments(segment_ids)
    print(url)
    return url


def main(argv=sys.argv):
    segments_ids = None if len(argv) < 2 else argv[1]
    speed_data = download_speed_data(first_param=segments_ids)
    print(speed_data)


def main(argv=sys.argv):
    a = 9 if len(argv) < 2 else int(argv[1])
    b = 3 if len(argv) < 3 else int(argv[2])
    xdivide(a, b)

def main(argv=sys.argv):
    segments_ids = None if len(argv) < 2 else argv[1]
    x(segments_ids)