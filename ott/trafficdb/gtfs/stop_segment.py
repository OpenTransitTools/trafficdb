from sqlalchemy import Column, Index, Integer, Numeric, String, DateTime
from sqlalchemy.orm import deferred, object_session, relationship, backref

from ott.gtfsdb.model.base import Base

import logging
log = logging.getLogger(__file__)


class StopSegment(Base):
    __tablename__ = 'traffic_stop_segments'

    segment_id = Column(String, nullable=False)

    start = Column(Integer, index=True)
    end = Column(Integer)

    cause = Column(String)
    effect = Column(String)

    url = Column(String)
    header_text = Column(String)
    description_text = Column(String)

    route_short_names = Column(String)

    """
    entities = relationship(
        'StopSegmentEntity',
        primaryjoin='StopSegment.StopSegment_id == StopSegmentEntity.StopSegment_id',
        foreign_keys='(StopSegment.StopSegment_id)',
        backref=backref("StopSegment", lazy="joined", uselist=False),
        uselist=True, viewonly=True
    )
    """

    def __init__(self, agency, id):
        self.agency = agency
        self.segment_id = id

    def add_short_names(self, gtfsdb_session, sep=', '):
        """
        will add the route_short_names (from gtfsdb) to the StopSegment record as a comma separated string
        """
        if gtfsdb_session:
            short_names = []
            try:
                route_ids = self.get_route_ids()
                if len(route_ids) > 0:
                    log.debug("query Route table")
                    from gtfsdb import Route
                    routes = gtfsdb_session.query(Route).filter(Route.route_id.in_(route_ids)).order_by(Route.route_sort_order)
                    for r in routes.all():
                        nm = self.make_pretty_short_name(r)
                        if nm and nm not in short_names:
                            short_names.append(nm)
                    self.route_short_names = sep.join([str(x) for x in short_names])
            except Exception as e:
                log.exception(e)

    @classmethod
    def parse_gtfsrt_record(cls, session, agency, record, timestamp):
        """
        create or update new StopSegments and positions
        """
        ret_val = None

        try:
            ret_val = StopSegment(agency, record.id)
            ret_val.set_attributes_via_gtfsrt(record.StopSegment)
            session.add(ret_val)
        except Exception as err:
            log.exception(err)
            session.rollback()
        finally:
            try:
                StopSegmentEntity.make_entities(session, agency, record.id, record.StopSegment)
                session.commit()
                ret_val.add_short_names(session)
                session.commit()
                session.flush()
            except Exception as err:
                log.exception(err)
                session.rollback()

        return ret_val

    @classmethod
    def clear_tables(cls, session, agency):
        """
        clear out stop segments
        """
        session.query(StopSegment).filter(StopSegment.agency == agency).delete()
