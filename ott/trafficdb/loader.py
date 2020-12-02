from ott.utils.parse.cmdline import db_cmdline
from ott.utils.config_util import ConfigUtil
from ott.utils import string_utils
from ott.utils import file_utils
from ott.utils import exe_utils

from ott.trafficdb.gtfs.database import Database
from ott.trafficdb.gtfs.stop_segment import StopSegment

import logging
logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__file__)


def make_args_config(cmd_name, section="db"):
    config = ConfigUtil.factory(section=section)
    args = db_cmdline.db_parser(cmd_name, do_parse=True, url_required=False, add_misc=True)
    return config, args

def make_db_url_schema(config=None, args=None, cmd_name='bin/blah', section="db"):
    if config is None or args is None:
        config, args = make_args_config(cmd_name, section)
    url = string_utils.get_val(args.database_url, config.get('database_url'))
    schema = string_utils.get_val(args.schema, config.get('schema'))
    return url, schema

def load_speed_data(cmd_name='bin/load-speed-data'):
    # TODO: put this config / cmd-line into a util
    config, args = make_args_config(cmd_name)
    url, schema = make_db_url_schema(config, args)
    is_geospatial = string_utils.get_val(args.schema, config.get('is_geospatial'))

    session = Database.make_session(url, schema, is_geospatial, args.create)
    StopSegment.load(session)
    session.commit()
    session.commit()  # think I need 2 commits due to session create + begin_nested being created above.
    session.flush()


def load_gtfs_and_speed_data(cmd_name='bin/load-gtfs-and-speed-data'):
    """
    complete load: will load gtfs and then do stop segmentation, etc...
    bin/load-gtfs-and-speed-data -c -g -s tm -d postgres://localhost/ott https://developer.trimet.org/schedule/gtfs.zip
    """
    from gtfsdb.scripts import get_args
    from gtfsdb.api import database_load

    # step 1: reload gtfsdb
    args, kwargs = get_args()
    if args.file not in "skip":
        database_load(args.file, **kwargs)
        pass

    # step 2: load stop segments
    if args.file not in "skip":
        session = Database.make_session(args.database_url, args.schema, args.is_geospatial, create_db=True)
        StopSegment.load(session)
        session.commit()
        session.flush()
    else:
        session = Database.make_session(args.database_url, args.schema, args.is_geospatial)

    # step 3: speed data ....
    pass # TODO

    # step 4: output geojson for map
    geojson = StopSegment.to_geojson(session)
    dir = "ott/trafficdb/examples"
    file = "segments.geojson"
    file_utils.cat(dir, file, geojson)

    # step 5: start simple server & open the browser to the map
    print("run simple python server and open map")
    exe_utils.run_cmd("scripts/start_static.sh", shell_script=True)


def segments_to_geojson():
    url, schema = make_db_url_schema(cmd_name='bin/geojson-segments')
    session = Database.make_session(url, schema, is_geospatial=True)
    geojson = StopSegment.to_geojson(session)
    print(geojson)


def main():
    load_speed_data()


if __name__ == '__main__':
    main()
