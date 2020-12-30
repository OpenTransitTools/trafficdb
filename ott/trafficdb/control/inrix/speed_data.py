import requests

from ott.trafficdb.model.traffic_segment_speed import TrafficSegmentSpeed
from ott.utils import string_utils

from . import urls
from .get_token import get_inrix_token

import logging
log = logging.getLogger(__file__)


def speeds_via_bbox(bbox):
    """
    query INRIX via bbox and return Speed ORM objects
    :param bbox: string in the form of 45.5,-122.5,45.6,-122.6
    :return: list of TrafficSegmentSpeed ORM objects
    """
    inrix_response = call_data_service(urls.speeds_url_bbox, bbox)
    speed_recs = parse_speed_data(inrix_response)
    return speed_recs


def speeds_via_id(ids):
    """
    query INRIX via bbox and return Speed ORM objects
    :param ids: string of INRIX xid segment ids in the form of 33333 or 22222,33333,44444,55555
    :return: list of TrafficSegmentSpeed ORM objects
    """
    inrix_response = call_data_service(urls.speeds_url_segments, ids)
    speed_recs = parse_speed_data(inrix_response)
    return speed_recs


def parse_speed_data(inrix_speeds_response):
    """
    will parse the speed response data, and return an array of ORM objects
    :param data: from call to call_data_service()
    :return: list of TrafficSegmentSpeed ORM objects
    """
    # import pdb; pdb.set_trace()
    speed_recs = []
    for ss in inrix_speeds_response['result']['segmentSpeeds']:
        for r in ss['segments']:
            sr = TrafficSegmentSpeed.inrix_factory(r)
            speed_recs.append(sr)

    return speed_recs


def call_data_service(inrix_url_method=None, param=None):
    """
    grab data from a given service...

    confidence:
      - 'score': 30 (real-time data) and 'c-Value': 0-100 (% confidence)
      - 'score': 20 (mix of historic and real-time) and 'c-Value': ??? (not sure there is a value here)
      - 'score': 10 (historic data .. no probes) and 'c-Value': ??? (not sure there is a value here)
    """
    # import pdb; pdb.set_trace()

    # step 1: grab the URL (sans token) for the service
    inrix_url = inrix_url_method(param)

    def http_get_inrix(force=False):
        """ this inner method will build the inrix url including token, then HTTP GET data from that service """

        # step 2: build the get url (existing token)
        url = "{}&token={}".format(inrix_url, get_inrix_token(renew=force))
        log.info(url)

        # step 2: call service
        ret_val = requests.get(url).json()

        return ret_val

    # step 3: call inrix service to retrieve data
    data = http_get_inrix()
    if data['statusText'] in ['TokenExpired', 'BadToken']:
        # step 4: token looks bad in first call above, so force renew the api token and call INRIX a second time
        data = http_get_inrix(force=True)

    return data


def make_cmd_line(prog_name="bin/inrix_speed_data", services_enum=None, do_parse=True):
    """
    simply build a command line processor for main() below
    todo: make generic for other traffic/speed vendors beyond INRIX
    """
    from ott.utils.parse.cmdline.base_cmdline import empty_parser
    parser = empty_parser(prog_name)

    if services_enum:
        parser.add_argument(
            '--service',
            '-svc',
            '-s',
            choices = services_enum.get_service_names(),
            help="service name"
        )

    parser.add_argument(
        '--param',
        '-param',
        '-p',
        help="optional service parameter"
    )

    ret_val = parser
    if do_parse:
        ret_val = parser.parse_args()

    return ret_val


def main():
    """
    bin/inrix_speed_data -s GetSegmentSpeedinBox -p \"45.5,-122.5,45.6,-122.6\"
    """
    cmd = make_cmd_line(services_enum=urls.InrixService)
    inrix_url_method = urls.InrixService.find_service(cmd.service)
    param = string_utils.safe_replace(cmd.param, '"', '')
    data = call_data_service(inrix_url_method, param)
    print(data)
