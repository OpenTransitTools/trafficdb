from sqlalchemy import select, MetaData, Table, inspect

from ott.utils import string_utils

from ott.trafficdb.gtfs.database import Database
from ott.trafficdb.gtfs.stop_segment import StopSegment

import logging
log = logging.getLogger(__file__)


def match_traffic_to_stop_segments(session, traffic_segments_cls):
    """
    will find all traffic segments in the database that align up with
    """
    # import pdb; pdb.set_trace()
    try:
        segments = session.query(traffic_segments_cls).limit(5)
        for s in segments.all():
            print(s.__dict__)
    except Exception as e:
        print(e)


def jnk(session):
    metadata = MetaData(bind=None)
    tname = 'traffic_inrix_segments'
    traffic_table_name = StopSegment.get_full_table_name(tname)
    traffic_table = Table(tname, metadata, autoload=True, autoload_with=engine)
    # traffic_table = Table(traffic_table_name, metadata, autoload=True, autoload_with=engine)
    traffic_table = Table(tname, metadata, autoload=True, autoload_with=engine)
    s = select([traffic_table])
    print(s)
    #results = session.execute(s).fetchall()
    #matches = traffic_segments_to_stop_segments(session, '')


def main(cmd_name="bin/match-segments"):
    from ..loader import make_args_config, make_db_url_schema

    config, args = make_args_config(cmd_name)
    url, schema = make_db_url_schema(config, args)
    is_geospatial = string_utils.get_val(args.schema, config.get('is_geospatial'))
    session = Database.make_session(url, schema, is_geospatial, args.create)

    from ..inrix.inrix_segment import InrixSegment
    match_traffic_to_stop_segments(session, InrixSegment)


if __name__ == '__main__':
    main()
