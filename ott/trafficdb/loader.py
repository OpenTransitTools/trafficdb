from ott.utils.parse.cmdline import db_cmdline
from ott.utils.config_util import ConfigUtil
from ott.utils import string_utils

import logging
logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__file__)


def load_speed_data(section="db"):
    config = ConfigUtil.factory(section=section)
    args = db_cmdline.db_parser('bin/speeds-load', do_parse=True, url_required=False, add_misc=True)
    url = string_utils.get_val(args.database_url, config.get('db_url'))
    print(url)


def main():
    load_speed_data()


if __name__ == '__main__':
    main()
