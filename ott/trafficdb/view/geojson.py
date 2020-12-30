from ott.trafficdb.model.stop_segment import StopSegment
from ott.trafficdb.control.utils import make_session


def local_server():
    print("run simple python server and open map")
    exe_utils.run_cmd("scripts/start_static.sh", shell_script=True)


def stop_geojson(session, dir="docs", file="segments.geojson"):
    geojson = StopSegment.to_geojson(session)
    file_utils.cat(dir, file, geojson)


def main(cmd_name="bin/geojson"):
    session = make_session(cmd_name)
    stop_geojson(session)
    local_server()
