from ott.utils import exe_utils, file_utils, string_utils
from ott.trafficdb.model.database import Database
from ott.trafficdb.model.stop_segment import StopSegment


def local_server():
    print("run simple python server and open map")
    exe_utils.run_cmd("scripts/start_static.sh", shell_script=True)


def stop_geojson(session, dir="docs", file="segments.geojson"):
    geojson = StopSegment.to_geojson(session)
    file_utils.cat(dir, file, geojson)


def main(cmd_name="bin/printer"):
    """ simple demo """
    from ott.trafficdb.control.utils import make_args_config, make_db_url_schema

    config, args = make_args_config(cmd_name)
    url, schema = make_db_url_schema(config, args)
    is_geospatial = string_utils.get_val(args.schema, config.get('is_geospatial'))
    session = Database.make_session(url, schema, is_geospatial)
    stop_geojson(session)
    local_server()
