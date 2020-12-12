from sqlalchemy import and_, or_
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
    try:
        # step 1: find intersections and some buffer of the two geoms
        # import pdb; pdb.set_trace()
        a = StopSegment
        b = traffic_segments_cls
        segments = session.query(
            a, b
            , func.ST_Contains(func.ST_Buffer(a.geom, 0.00001), b.geom)
            , func.ST_Contains(func.ST_Buffer(a.geom, 0.0001), b.geom)
            , func.ST_Contains(func.ST_Buffer(a.geom, 0.001), b.geom)
        ).filter(
            and_(
            func.ST_Intersects(a.geom, b.geom)
            , or_(a.id.like('%844'), a.id.like('843%')))
        ).limit(20)

        # step b: loop thru and find matches based on a set of rules that follow, et...
        for s in segments.all():
            print(s[0].id, s[1].id, s[2:])
    except Exception as e:
        log.warning(e)


def main(cmd_name="bin/match-segments"):
    """ simple demo """
    from ..loader import make_args_config, make_db_url_schema

    config, args = make_args_config(cmd_name)
    url, schema = make_db_url_schema(config, args)
    is_geospatial = string_utils.get_val(args.schema, config.get('is_geospatial'))
    session = Database.make_session(url, schema, is_geospatial, args.create)

    from ..inrix.inrix_segment import InrixSegment
    match_traffic_to_stop_segments(session, InrixSegment)


if __name__ == '__main__':
    main()
