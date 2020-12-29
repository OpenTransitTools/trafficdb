import os
from ott.utils.config_util import ConfigUtil
from ott.utils import exe_utils, file_utils, object_utils


def load(files=None, database=None, schema=None, user=None):
    """"""
    # step 1: build cmd line for load_inrix_geojson.sh
    dir = file_utils.get_file_dir(__file__)
    load_sh = os.path.join(dir, "load_inrix_geojson.sh")
    if files:
        load_sh = "{} {}".format(load_sh, object_utils.list_to_str(files))

    # step 2: set env vars for  load_inrix_geojson.sh
    if database: os.environ['DB_NAME'] = database
    if schema: os.environ['DB_SCHEMA'] = schema
    if user: os.environ['DB_USER'] = user

    # step 3: run script
    #import pdb; pdb.set_trace()
    exe_utils.run_cmd_get_stdout(load_sh)


def get_inrix_geojson_files():
    pass


def main():
    from ott.utils.parse.cmdline.db_cmdline import db_parser
    parser = db_parser(prog_name="bin/inrix_segment_data", url_required=False)
    parser.add_argument("files", nargs='*', help="list of .geojson files to load")
    cmd = parser.parse_args()


    #cmd = make_cmd_line(services_enum=urls.InrixService)
    #inrix_url_method = urls.InrixService.find_service(cmd.service)
    load(cmd.files, cmd.database_url, cmd.schema, cmd.user)
