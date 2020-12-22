import requests

from . import urls
from .get_token import get_inrix_token
from ott.utils import string_utils

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
    def inner(service_name, param, force=False):
        # step 1: get url (existing token)
        url = "{}&token={}".format(func(service_name, param), get_inrix_token(renew=force))
        log.info(url)

        # step 2: call service
        ret_val = requests.get(url).json()

        # step 3: if token is bad, call things again (via recursion) and ask to renew token
        if(ret_val['statusText'] in ['TokenExpired', 'BadToken'] and not force):
            ret_val = inner(service_name, param, force=True)
        return ret_val
    return inner


@download_speed_data
def call_data_service(service_name=None, param=None):
    #import pdb; pdb.set_trace()
    inrix_svc = urls.InrixService.find_service(service_name)
    data = inrix_svc(param)
    return data


def make_cmd_line(prog_name="bin/inrix_speed_data", services_enum=None, do_parse=True):
    """
    todo: make generic for other traffic/speed vendors
    """
    from ott.utils.parse.cmdline.base_cmdline import empty_parser
    parser = empty_parser(prog_name)

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
        # finalize the parser
        ret_val = parser.parse_args()
    return ret_val


def main():
    cmd = make_cmd_line(services_enum=urls.InrixService)
    data = call_data_service(cmd.service, string_utils.safe_replace(cmd.param, '"', ''))
    print(data)
