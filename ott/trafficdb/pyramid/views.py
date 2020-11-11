from pyramid.response import Response
from pyramid.view import view_config

from ott.utils import otp_utils
from ott.utils import json_utils

from ott.utils.svr.pyramid import response_utils
from ott.utils.svr.pyramid import globals

import logging
log = logging.getLogger(__file__)


APP_CONFIG = None
def set_app_config(app_cfg):
    """
    called set the singleton AppConfig object
    :see ott.utils.svr.pyramid.app_config.AppConfig :
    """
    global APP_CONFIG
    APP_CONFIG = app_cfg


def do_view_config(cfg):
    cfg.add_route('check_cache', '/check_cache')


@view_config(route_name='check_cache', renderer='json', http_cache=globals.CACHE_LONG)
def check_cache(request):
    """
    :returns ...
    """
    # import pdb; pdb.set_trace()
    return {'hi': 'yo'}
