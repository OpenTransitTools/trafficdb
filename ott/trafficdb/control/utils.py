from ott.utils.config_util import ConfigUtil
from ott.utils.parse.cmdline import db_cmdline
from ott.utils import exe_utils, file_utils, string_utils
from ott.trafficdb.model.database import Database

def make_args_config(cmd_name, section="db"):
    config = ConfigUtil.factory(section=section)
    args = db_cmdline.db_parser(cmd_name, do_parse=True, url_required=False, add_misc=True)
    return config, args


def make_db_url_schema(config=None, args=None, cmd_name='bin/blah', section="db"):
    if config is None or args is None:
        config, args = make_args_config(cmd_name, section)
    url = string_utils.get_val(args.database_url, config.get('database_url'))
    schema = string_utils.get_val(args.schema, config.get('schema'))
    return url, schema


def make_session(cmd_name="bin/blah"):
    config, args = make_args_config(cmd_name)
    url, schema = make_db_url_schema(config, args)
    is_geospatial = string_utils.get_val(args.schema, config.get('is_geospatial'))
    session = Database.make_session(url, schema, is_geospatial)
    return session