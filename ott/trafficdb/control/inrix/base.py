import requests
from ott.utils.config_util import ConfigUtil


def ini(section='inrix'):
    if not hasattr(ini, '_INI_'):
        ini._INI_ = ConfigUtil.factory(section)
    return ini._INI_


def get_inrix_token(renew=False):
    """
    http://na.api.inrix.com/traffic/Inrix.ashx?format=json&action=getsecuritytoken&vendorid=<your vid>&consumerid=<your cid>
    will return json, ala { result: { token: < me> }, ... }
    """
    #import pdb; pdb.set_trace()
    if not hasattr(get_inrix_token, '_TOKEN_') or renew:
        url = ini().get('traffic_url')
        vendorid = ini().get('vendorid')
        consumerid = ini().get('consumerid')
        token_url = "{}?action=getsecuritytoken&format=json&vendorid={}&consumerid={}".format(url, vendorid, consumerid)
        #print(token_url)
        resp = requests.get(token_url)
        get_inrix_token._TOKEN_ = resp.json()['result']['token']
    return get_inrix_token._TOKEN_


def main(argv=None):
    print(get_inrix_token())

