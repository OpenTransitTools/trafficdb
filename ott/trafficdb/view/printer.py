from ott.trafficdb.model.traffic_segment import TrafficSegment
from ott.trafficdb.control.utils import make_session


def main(cmd_name="bin/printer", just_speeds=False):
    """ simple demo """
    session = make_session(cmd_name)
    TrafficSegment.print_all(session, just_speeds=just_speeds)
