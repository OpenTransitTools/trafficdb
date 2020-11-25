import abc
import datetime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String, Integer, DateTime

import logging
log = logging.getLogger(__file__)


class _Base(object):

    agency = Column(String, nullable=False)

    id = Column(Integer, primary_key=True, nullable=False)
    created = Column(DateTime, default=datetime.datetime.now())
    updated = Column(DateTime, default=datetime.datetime.now())

    lang = "en"

    @classmethod
    def clear_tables(cls, session):
        log.warning("called from parent, so no idea what tables to clear")

    @classmethod
    def get_feed_type(cls, feed):
        """
        :param feed:
        :return: type
        """
        from .stop_segment import StopSegment
        ret_val = None
        for entity in feed.entity:
            if entity.HasField('stop_segment'):
                ret_val = StopSegment
            else:
                continue
            break
        return ret_val

    @classmethod
    def parse_gtfsrt_feed(cls, session, agency, feed):
        """
        generic record processor
        :returns feed header timestamp in POSIX time (i.e., number of seconds since January 1st 1970)
        """
        timestamp = datetime.datetime.utcfromtimestamp(feed.header.timestamp)
        for record in feed.entity:
            cls.parse_gtfsrt_record(session, agency, record, timestamp)
        return feed.header.timestamp

    @abc.abstractmethod
    def parse_gtfsrt_record(cls, session, agency, record, timestamp):
        raise NotImplementedError("Please implement this method")

    ## TODO: all of this below is boiler plate from gtfsdb_realtime ... so let's add it to ott.utils

    @classmethod
    def make_mapper(cls, tablename, column=agency):
        return {
            'polymorphic_on': column,
            'polymorphic_identity': tablename,
            'with_polymorphic': '*'
        }

    @classmethod
    def from_dict(cls, attrs):
        clean_dict = cls.make_record(attrs)
        c = cls(**clean_dict)
        return c

    def to_dict(self):
        """ convert a SQLAlchemy object into a dict that is serializable to JSON
        """ 
        ret_val = self.__dict__.copy()

        # the __dict__ on a SQLAlchemy object contains hidden crap that we delete from the class dict
        # (not crazy about this hack, but ...) 
        if set(['_sa_instance_state']).issubset(ret_val):
            del ret_val['_sa_instance_state']

        # convert time, date & datetime, etc... objects to iso formats
        for k in ret_val.keys():
            v = ret_val[k] 
            if hasattr(v,"isoformat"):
                ret_val[k] = v.isoformat()

        return ret_val

    @classmethod
    def to_dict_list(cls, list):
        """ apply to_dict() to all elements in list, and return new / resulting list...
        """
        ret_val = []
        for l in list:
            if hasattr(l,"to_dict"):
                l = l.to_dict()
            ret_val.append(l)
        return ret_val

    @classmethod
    def bulk_load(cls, engine, records, remove_old=True):
        """ load a bunch of records at once from a list (first clearing out the table).
            note that the records array has to be dict structures, ala
            http://docs.sqlalchemy.org/en/latest/core/connections.html#sqlalchemy.engine.Connection.execute
        """
        table = cls.__table__
        if remove_old:
            engine.execute(table.delete())
        engine.execute(table.insert(), records)

    @classmethod
    def set_schema(cls, schema):
        # if this is a database table, set the schema
        if hasattr(cls, '__table__'):
            cls.__table__.schema = schema

        # bit of recursion to hit sub classes
        for c in cls.__subclasses__():
            c.set_schema(schema)

    @classmethod
    def get_schema(cls, def_val=None):
        ret_val = def_val
        if hasattr(cls, '__table__'):
            ret_val = cls.__table__.schema
        return ret_val

    @classmethod
    def set_geometry(cls, is_geospatial=False):
        if is_geospatial:
            if hasattr(cls, 'add_geometry_column'):
                cls.add_geometry_column()

            # bit of recursion to hit sub classes
            for c in cls.__subclasses__():
                c.set_geometry(is_geospatial)


Base = declarative_base(cls=_Base)
