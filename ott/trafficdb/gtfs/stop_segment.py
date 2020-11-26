from sqlalchemy import Column, Index, Integer, Numeric, String, DateTime
from ott.trafficdb.gtfs.base import Base

import logging
log = logging.getLogger(__file__)


class StopSegment(Base):
    __tablename__ = 'traffic_stop_segments'

    segment_id = Column(String, nullable=False)
    begin_stop_id = Column(String, index=True)
    end_stop_id = Column(String, index=True)

    """
    entities = relationship(
        'StopSegmentEntity',
        primaryjoin='StopSegment.StopSegment_id == StopSegmentEntity.StopSegment_id',
        foreign_keys='(StopSegment.StopSegment_id)',
        backref=backref("StopSegment", lazy="joined", uselist=False),
        uselist=True, viewonly=True
    )
    """

    def __init__(self, begin_stop, end_stop):
        self.segment_id = format("{}-{}", begin_stop.stop_id, end_stop.stop_id)

    @classmethod
    def factory(cls, begin_stop, end_stop):
        """
        will create...
        """
        ret_val = None
        return ret_val

    @classmethod
    def load(cls, session):
        """
        will find ...
        """
        try:
            from gtfsdb import Trip
            t = session.query(Trip).limit(1).one()
            stop_times = t.stop_times
            stop_times_len = len(stop_times)
            if stop_times_len > 1:
                for i, st in enumerate(stop_times):
                    begin_stop = stop_times[i]
                    end_stop = stop_times[i+1]
                    print(begin_stop.stop_sequence, end_stop.stop_sequence)
                    if i+2 >= stop_times_len:
                        break

        except Exception as e:
            log.exception(e)

    @classmethod
    def clear_tables(cls, session, agency):
        """
        clear out stop segments
        """
        session.query(StopSegment).filter(StopSegment.agency == agency).delete()
