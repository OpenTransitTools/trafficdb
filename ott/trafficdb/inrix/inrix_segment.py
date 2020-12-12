from sqlalchemy import Column
from geoalchemy2 import Geometry
from sqlalchemy.orm import deferred


from ott.trafficdb.gtfs.base import Base

import logging
log = logging.getLogger(__file__)


class InrixSegment(Base):
    __tablename__ = 'traffic_inrix_segments'

    direction = Column()
    distance = Column()
    lanes = Column()

    def __init__(self, session, segment, trip):
        super(InrixSegment, self).__init__()

    @classmethod
    def add_geometry_column(cls):
        if not hasattr(cls, 'geom'):
            cls.geom = deferred(Column(Geometry(geometry_type='LINESTRING', srid=4326)))
