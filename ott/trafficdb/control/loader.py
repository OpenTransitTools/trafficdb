from gtfsdb.scripts import get_args

from ott.trafficdb.model.database import Database
from ott.trafficdb.model.stop_segment import StopSegment
from ott.trafficdb.view.geojson import stop_geojson

import logging
log = logging.getLogger(__file__)
args, kwargs = get_args()


def load_gtfsdb():
    """
    complete load: will load gtfs and then do stop segmentation, etc...
    bin/load_gtfsdb -c -g -s test -d postgres://ott@localhost:5432/ott ott/trafficdb/model/inrix/test/gtfs.zip
    """
    from gtfsdb.api import database_load
    database_load(args.file, **kwargs)
    load_stop_segments()


def load_stop_segments(session=None):
    if session is None:
        session = Database.make_session(args.database_url, args.schema, args.is_geospatial, create_db=True)
    StopSegment.load(session)
    session.commit()
    session.flush()


def load_all():
    """
    complete load: will load gtfs and then do stop segmentation, etc...

    bin/load_all -c -g -s trimet -d postgres://ott@localhost:5432/ott https://developer.trimet.org/schedule/gtfs.zip
    bin/load_all -c -g -s test -d postgres://ott@localhost:5432/ott ott/trafficdb/model/inrix/test/gtfs.zip
    """

    # step 1: reload gtfsdb
    if args.file not in "skippp":
        load_gtfsdb(args, kwargs)

    # step 2: load stop segments
    session = Database.make_session(args.database_url, args.schema, args.is_geospatial)
    stop_geojson(session)


def main():
    load_all()


if __name__ == '__main__':
    main()
