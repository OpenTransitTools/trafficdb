from gtfsdb.scripts import get_args

from ott.trafficdb.model.database import Database
from ott.trafficdb.model.stop_segment import StopSegment
from ott.trafficdb.view.geojson import stop_geojson, local_server

import logging
log = logging.getLogger(__file__)
args, kwargs = get_args()


def load_gtfsdb(session=None):
    """
    loads gtfs feed .zip data
    note: will also call the method below to calculate stop segments from the new schedule data
    bin/load_gtfsdb -c -g -s test -d postgres://ott@localhost:5432/ott ott/trafficdb/model/inrix/test/gtfs.zip
    """
    from gtfsdb.api import database_load
    database_load(args.file, **kwargs)
    load_stop_segments(session)


def load_stop_segments(session=None):
    """
    calculate stop segments from the gtfs schedule data
    note: will also
    bin/load_stop_segments -g -s test -d postgres://ott@localhost:5432/ott ott/trafficdb/model/inrix/test/gtfs.zip
    """
    #import pdb; pdb.set_trace()
    if session is None:
        session = Database.make_session(args.database_url, args.schema, args.is_geospatial, args.create)
    StopSegment.load(session)
    session.commit()
    session.flush()


def load_all():
    """
    complete load: will load gtfs and then do stop segmentation, etc...

    - step 1: load gtfs data ... calculate all stop-to-stop segments in the data
    - step 2: load traffic vendor street / segment data (INRIX in this case)
    - step 3: match/conflate stop-segments with traffic segment data
       - bin/match_segments
     - step 4: load speed data from INRIX into db (on-going ... run every 5 mintutes?)
       - bin/load_speed_data
     - step 5: plot lastest segment / speed data on the example map
       - bin/generate-speed-geojson --show-map

    bin/load_all -c -g -s trimet -d postgres://ott@localhost:5432/ott https://developer.trimet.org/schedule/gtfs.zip
    bin/load_all -c -g -s test -d postgres://ott@localhost:5432/ott ott/trafficdb/model/inrix/test/gtfs.zip
    """

    # step 1: load gtfsdb + calculate all stop-to-stop segments in the data
    if args.file not in "skippp":
        load_gtfsdb()

    # step 2: load traffic vendor data
    f


    # step 2: load stop segments
    session = Database.make_session(args.database_url, args.schema, args.is_geospatial)
    stop_geojson(session)
    #local_server()


def main():
    load_all()


if __name__ == '__main__':
    main()
