from ott.trafficdb.model.database import Database
from ott.trafficdb.model.stop_segment import StopSegment
from ott.trafficdb.model.traffic_segment import TrafficSegment
from ott.trafficdb.view.geojson import stop_geojson, local_server
from ott.trafficdb.control.inrix.segment_data import load as inrix_segment_loader
from ott.trafficdb.control.conflate.match_segments import match_traffic_to_stop_segments
from ott.trafficdb.control.speeds_to_segments import speeds_via_bbox

from gtfsdb.scripts import get_args, make_kwargs
import logging
log = logging.getLogger(__file__)

# customize the cmdline parser with room for traffic segments .geojson file
parser, kwargs = get_args(do_parse=False)
parser.add_argument('--transit_segments', '-t', default=None, nargs='*', help="transit segment file(s)")
args = parser.parse_args()
kwargs = make_kwargs(args)


def load_gtfsdb(session=None):
    """
    loads gtfs feed .zip data
    note: will also call the method below to calculate stop segments from the new schedule data
    bin/load_gtfsdb -c -g -s test -d postgres://ott@localhost:5432/ott ott/trafficdb/model/inrix/test/gtfs.zip
    """
    from gtfsdb.api import database_load
    database_load(args.file, **kwargs)


def load_stop_segments(session=None):
    """
    calculate stop segments from the gtfs schedule data
    note: will also
    bin/load_stop_segments -g -s test -d postgres://ott@localhost:5432/ott ott/trafficdb/model/inrix/test/gtfs.zip
    """
    # import pdb; pdb.set_trace()
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
     - step 4: load speed data from INRIX into db (on-going ... run every 5 mintutes?)
       - bin/load_speed_data should be run after the initial db load
     - step 5: plot lastest segment / speed data on the example map
       - bin/generate-speed-geojson --show-map

    bin/load_all -c -g -s trimet -d postgres://ott@localhost:5432/ott https://developer.trimet.org/schedule/gtfs.zip
    bin/load_all -c -g -s test -d postgres://ott@localhost:5432/ott ott/trafficdb/model/inrix/test/gtfs.zip
    """

    # step 1: create db session for the traffic tables
    create_new_db = args.create and args.file not in "skippp"  # if skipping load steps (below), don't blow away old db
    session = Database.make_session(args.database_url, args.schema, args.is_geospatial, create_new_db)

    # step 2: load gtfsdb + calculate all stop-to-stop segments in the data
    if args.file not in "skippp":
        load_gtfsdb(session)

    # step 3: load traffic vendor's street / segment data
    if args.file not in "skipp":
        inrix_segment_loader(files=args.transit_segments, schema=args.schema)

    # step 4: load stops, then conflate traffic vendor data with transit (stop segment) data from above
    if args.file not in "skip":
        load_stop_segments(session)

        # import pdb; pdb.set_trace()
        from ott.trafficdb.model.inrix.inrix_segment import InrixSegment
        segments = match_traffic_to_stop_segments(session, InrixSegment)
        if segments:
            TrafficSegment.clear_tables(session)
            Database.persist_data(session, segments)

    # step 5: grab initial set of speed data an put it into the database
    # note: subsequent calls to 'bin/load_speed_data' can now be used to populate the db with new traffic data
    bbox = TrafficSegment.bbox(session, 0.001, normalize=True)
    speed_data = speeds_via_bbox(bbox)
    Database.persist_data(session, speed_data)

    # step 6: show some data...
    TrafficSegment.print_all(session, just_speeds=True)

    # step 7: load stop segments and launch simple web server to host map
    stop_geojson(session, args.schema)
    local_server()


def main():
    load_all()


if __name__ == '__main__':
    main()
