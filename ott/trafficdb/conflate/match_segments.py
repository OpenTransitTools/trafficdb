from sqlalchemy import select, MetaData, Table
from geoalchemy2 import func

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
        t1 = StopSegment
        t2 = traffic_segments_cls
        segments = session.query(
            t1, t2

        ).filter(
            func.ST_Intersects(t1.geom, t2.geom)
        ).limit(5)
        for s in segments.all():
            print(s)
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
