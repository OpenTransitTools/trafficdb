from sqlalchemy import Column, String
from geoalchemy2 import Geometry
from sqlalchemy.orm import deferred

from ott.trafficdb.model.base import Base, Vendor

import logging
log = logging.getLogger(__file__)


class InrixSegment(Base):
    __tablename__ = 'traffic_inrix_segments'

    vendor_id = Vendor.inrix

    direction = Column(String)
    distance = Column(String)
    lanes = Column(String)
    frc = Column(String)

    def __init__(self, session, segment, trip):
        super(InrixSegment, self).__init__()

    @classmethod
    def add_geometry_column(cls):
        if not hasattr(cls, 'geom'):
            cls.geom = deferred(Column(Geometry(geometry_type='LINESTRING', srid=4326)))
