. ~/OsmLoader/bin/db-common.sh

cd $BASEDIR

echo "START > > > > > "
date

# check to see the size of the dump and load it if there
size=`ls -Hltr ${OSM_DUMP}.gz | awk -F" " '{ print $5 }'`
if [[ $size -gt $OSM_MIN_SIZE ]]
then
  echo "gunzip ${OSM_DUMP}.gz"
  rm -f ${OSM_DUMP}
  gunzip ${OSM_DUMP}.gz
else
  echo "ERROR: ${OSM_DUMP}.gz ($CARTO_SCHEMA and $OSM_SCHEMA SCHEMAs) dump is not big enough at $size (less than $OSM_MIN_SIZE bytes)"
fi

size=`ls -Hltr ${OSM_DUMP} | awk -F" " '{ print $5 }'`
if [[ $size -gt $OSM_TAR_MIN_SIZE ]]
then
  # test integrity of the dump file 
  # TODO - or maybe move osm schema aside and move it back if )

  # drop the old osm schema
  echo "drop schema osm"
  psql -p $PGPORT -d $PGDBNAME -U $PGUSER -c "drop schema $CARTO_SCHEMA cascade;"
  psql -p $PGPORT -d $PGDBNAME -U $PGUSER -c "drop schema $OSM_SCHEMA cascade;"

  # load osm schema db from tar
  echo "restore osm dump"
  pg_restore -d $PGDBNAME ${OSM_DUMP}

  grantor "$CARTO_SCHEMA";
  grantor "$OSM_SCHEMA";

  # vacuum analyze db
  echo "vacuum analyze"
  psql -p $PGPORT -d $PGDBNAME -U $PGUSER -c "vacuum analyze;"

  rm -f ${OSM_DUMP}.old
  mv ${OSM_DUMP} ${OSM_DUMP}.old
else
  echo "ERROR: ${OSM_DUMP} ($CARTO_SCHEMA and $OSM_SCHEMA SCHEMAs) dump is not big enough at $size (less than $OSM_TAR_MIN_SIZE bytes)"
fi

date
echo "END < < < < < < "
