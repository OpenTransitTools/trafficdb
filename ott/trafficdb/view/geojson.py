from ott.trafficdb.model.stop_segment import StopSegment
from ott.trafficdb.control.utils import make_session
from ott.utils import file_utils
from .server import local_server


def stop_geojson(session, file="segments.geojson", dir="docs"):
    if file is None or len(file) < 1:
        file = "segments.geojson"
    elif ".geojson" not in file:
        file = file + ".geojson"
    geojson = StopSegment.to_geojson(session)
    file_utils.cat(dir, file, geojson)


def main(cmd_name="bin/view_map"):
    session, schema = make_session(cmd_name, return_schema=True)
    stop_geojson(session, schema)
    local_server()
