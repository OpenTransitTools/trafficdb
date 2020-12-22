from sqlalchemy import create_engine, event
from sqlalchemy.pool import QueuePool
from sqlalchemy.orm import sessionmaker, scoped_session

from ott.utils import db_utils
from ott.trafficdb.model.base import Base

import logging
log = logging.getLogger(__file__)


class Database(object):
    """
    NOTE: Dec 2020 I was getting errors loading gtfsdb (stops in the stop_times often), so found these changes to create_engine
          https://stackoverflow.com/questions/55457069/how-to-fix-operationalerror-psycopg2-operationalerror-server-closed-the-conn

    TODO: maybe inherit from GTFSDB's Database object?  Do we need two?
    TODO: Also have to init GTFSDB, so maybe inherit is better
          @see: loader.py  import gtfsdb
           gtfsdb.Database.prep_gtfsdb_model_classes(schema, args.is_geospatial)

    """
    db_singleton = None

    def __init__(self, url, schema=None, is_geospatial=False, pool_size=20, session_extenstion=None):
        self.url = url
        self.engine = create_engine(
            url,
            poolclass=QueuePool,
            pool_size=pool_size,
            max_overflow = 2,
            pool_recycle = 300,
            pool_pre_ping = True,
            pool_use_lifo = True
        )
        event.listen(self.engine, 'connect', Database.connection)

        # note ... set these after creating self.engine
        self._make_session_class(session_extenstion)
        self.schema = schema
        self.is_geospatial = is_geospatial

    def create(self):
        Base.metadata.drop_all(bind=self.engine)
        Base.metadata.create_all(bind=self.engine)

    @property
    def is_geospatial(self):
        return self._is_geospatial

    @is_geospatial.setter
    def is_geospatial(self, val):
        self._is_geospatial = val
        Base.set_geometry(self._is_geospatial)

    @property
    def schema(self):
        return self._schema

    @schema.setter
    def schema(self, val):
        # import pdb; pdb.set_trace()
        self._schema = val
        try:
            if self._schema and len(self._schema) > 0:
                Base.set_schema(self._schema)
                from sqlalchemy.schema import CreateSchema
                self.engine.execute(CreateSchema(self._schema))
        except Exception as e:
            log.info("NOTE: couldn't create schema {0} (schema might already exist)\n{1}".format(self._schema, e))

    def _make_session_class(self, extension=None):
        """
        this makes the Session() class ... the extension is for things like
        :see http://docs.sqlalchemy.org/en/latest/orm/contextual.html?highlight=scoped%20session :
        :see https://www.programcreek.com/python/example/97518/zope.sqlalchemy.ZopeTransactionExtension :
        """
        self.session_factory = sessionmaker(bind=self.engine, extension=extension)
        self.Session = scoped_session(self.session_factory)

    @property
    def session(self):
        session = self.Session()
        return session

    @classmethod
    def make_session(cls, url, schema, is_geospatial=False, create_db=False, prep_gtfsdb=True):
        # note: include all ORM objects here, so the db finds them
        from .stop_segment import StopSegment
        from .stop_segment_trip import StopSegmentTrip
        from .inrix.inrix_segment import InrixSegment
        from .traffic_segment import TrafficSegment
        from .traffic_segment_speed import TrafficSegmentSpeed

        if cls.db_singleton is None:
            cls.db_singleton = Database(url, schema, is_geospatial)
            if create_db:
                cls.db_singleton.create()
            if prep_gtfsdb:
                import gtfsdb
                gtfsdb.Database.prep_gtfsdb_model_classes(schema, is_geospatial)
        return cls.db_singleton.session

    @classmethod
    def connection(cls, raw_con, connection_record):
        if 'sqlite' in type(raw_con).__module__:
            db_utils.add_math_to_sqllite(raw_con, connection_record)
