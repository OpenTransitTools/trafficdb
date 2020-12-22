from sqlalchemy import and_, or_
from geoalchemy2 import func

from ott.utils import string_utils

from ott.trafficdb.model.database import Database
from ott.trafficdb.model.traffic_segment import TrafficSegment
from ott.trafficdb.model.traffic_segment_speed import TrafficSegmentSpeed

from .inrix.speed_data import call_data_service
from .inrix.urls import speeds_url_segments

import logging
log = logging.getLogger(__file__)


def main(cmd_name="bin/speeds_to_segments"):
    """ simple demo """
    from ott.trafficdb.loader import make_args_config, make_db_url_schema

    config, args = make_args_config(cmd_name)
    url, schema = make_db_url_schema(config, args)
    is_geospatial = string_utils.get_val(args.schema, config.get('is_geospatial'))
    session = Database.make_session(url, schema, is_geospatial)

    segment_ids = TrafficSegment.get_segment_ids(session, 16)
    s = ','.join(map(str, segment_ids))
    data = call_data_service(speeds_url_segments, s)

    # import pdb; pdb.set_trace()
    speed_recs = []
    for ss in data['result']['segmentSpeeds']:
        for r in ss['segments']:
            sr = TrafficSegmentSpeed.inrix_factory(r)
            speed_recs.append(sr)


    session.add_all(speed_recs)
    session.commit()
    session.flush()
    session.flush()

    print(data)
    print("")
    import pdb; pdb.set_trace()
    segments = session.query(TrafficSegment).all()
    for s in segments:
        print(s.__dict__)
        print(s.speeds.__dict__)


if __name__ == '__main__':
    main()
