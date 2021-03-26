from ott.utils import exe_utils


def local_server():
    print("run simple python server and open map")
    exe_utils.run_cmd("scripts/start_static.sh", shell_script=True)
