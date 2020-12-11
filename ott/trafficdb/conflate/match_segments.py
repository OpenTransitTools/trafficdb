from ott.utils import string_utils

from ott.trafficdb.gtfs.database import Database
from ott.trafficdb.gtfs.stop_segment import StopSegment

import logging
log = logging.getLogger(__file__)


def traffic_segments_to_stop_segments(session, traffic_cls, do_print=True):
    """
    will find all traffic segments in the database that align up with
    """
    # import pdb; pdb.set_trace()
    try:
        stops = session.query(StopSegment).limit(5)
        for ss in stops:
            print(ss.__dict__)
    except:
        pass


def match_inrix_segments(session):
    matches = traffic_segments_to_stop_segments(session, None)


def main(cmd_name="bin/match-segments"):
    from ..loader import make_args_config, make_db_url_schema

    config, args = make_args_config(cmd_name)
    url, schema = make_db_url_schema(config, args)
    is_geospatial = string_utils.get_val(args.schema, config.get('is_geospatial'))
    session = Database.make_session(url, schema, is_geospatial, args.create)

    match_inrix_segments(session)


if __name__ == '__main__':
    main()
