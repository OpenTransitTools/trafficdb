from ott.utils.parse.cmdline import db_cmdline
from ott.utils.config_util import ConfigUtil
from ott.utils import string_utils

from ott.trafficdb.gtfs.database import Database
from ott.trafficdb.gtfs.stop_segment import StopSegment

import logging
logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__file__)


def load_speed_data(section="db"):
    # TODO: put this config / cmd-line into a util
    config = ConfigUtil.factory(section=section)
    args = db_cmdline.db_parser('bin/speeds-load', do_parse=True, url_required=False, add_misc=True)
    url = string_utils.get_val(args.database_url, config.get('database_url'))
    schema = string_utils.get_val(args.schema, config.get('schema'))
    is_geospatial = string_utils.get_val(args.schema, config.get('is_geospatial'))
    session = Database.make_session(url, schema, is_geospatial, args.create)

    StopSegment.load(session)

    session.commit()
    session.commit()  # think I need 2 commits due to session create + begin_nested being created above.
    session.flush()


def main():
    load_speed_data()


if __name__ == '__main__':
    main()
