import abc
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String

import logging
log = logging.getLogger(__file__)


class _Base(object):

    id = Column(String(255), primary_key=True, index=True)

    @abc.abstractmethod
    def parse_record(cls, session, record, timestamp):
        raise NotImplementedError("Please implement this method")

    ## TODO: all of this below is boiler plate from gtfsdb_realtime ... so let's add it to ott.utils

    @classmethod
    def clear_tables(cls, session):
        log.info("clearing table {}".format(cls.__name__))
        session.query(cls).delete()

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
    def get_full_table_name(cls, table_name=None):
        if table_name:
            # we were provided a table name, so append any schema name if table name provided
            schema = None if not hasattr(cls, '__table__') else cls.__table__.schema
            if schema:
                ret_val = "{}.{}".format(schema, table_name)
            else:
                ret_val = table_name
        else:
            # get best table name for this object
            if hasattr(cls, '__table__'):
                ret_val = cls.__table__
            elif hasattr(cls, '__tablename__'):
                ret_val = cls.__tablename__
            else:
                ret_val = cls.__name__

        return ret_val

    @classmethod
    def set_geometry(cls, is_geospatial=False):
        # import pdb; pdb.set_trace()
        if is_geospatial:
            if hasattr(cls, 'add_geometry_column'):
                cls.add_geometry_column()

            # bit of recursion to hit sub classes
            for c in cls.__subclasses__():
                c.set_geometry(is_geospatial)

    @classmethod
    def make_mapper(cls, tablename, column='id'):
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
        """
        convert a SQLAlchemy object into a dict that is serializable to JSON
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
        """
        apply to_dict() to all elements in list, and return new / resulting list...
        """
        ret_val = []
        for l in list:
            if hasattr(l,"to_dict"):
                l = l.to_dict()
            ret_val.append(l)
        return ret_val

    @classmethod
    def to_geojson(cls, session):
        """
        query the db for this 'cls' (child class), and dump out a FeatureCollection
        {
          "type": "FeatureCollection",
          "features": [
            {"type":"Feature", "properties":{"id":"1-2"}, "geometry":{"type":"LineString","coordinates":[[-122.677388,45.522879],[-122.677396,45.522913]]}},
            {"type":"Feature", "properties":{"id":"2-3"}, "geometry":{"type":"LineString","coordinates":[[-122.675715,45.522215],[-122.67573,45.522184]]}},
          ]
        }
        """
        feature_tmpl = '    {{"type": "Feature", "properties": {{"id": "{}"}}, "geometry": {}}}{}'
        features = session.query(cls.id, cls.geom.ST_AsGeoJSON()).all()
        ln = len(features) - 1
        featgeo = ""
        for i, f in enumerate(features):
            comma = ",\n" if i < ln else "\n"
            featgeo += feature_tmpl.format(f[0], f[1], comma)

        geojson = '{{\n  "type": "FeatureCollection",\n  "features": [\n  {}  ]\n}}'.format(featgeo)
        return geojson

    @classmethod
    def bulk_load(cls, engine, records, remove_old=True):
        """
        load a bunch of records at once from a list (first clearing out the table).
        note that the records array has to be dict structures, ala
        http://docs.sqlalchemy.org/en/latest/core/connections.html#sqlalchemy.engine.Connection.execute
        """
        table = cls.__table__
        if remove_old:
            engine.execute(table.delete())
        engine.execute(table.insert(), records)


Base = declarative_base(cls=_Base)
