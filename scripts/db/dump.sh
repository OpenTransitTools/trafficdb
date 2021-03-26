. ~/OsmLoader/bin/db-common.sh

echo "START > > > > > "
date

cd $BASEDIR

# dump trimet postgres database to tar.gz, include only the following schemas;
echo "pg_dump -n $OSM_SCHEMA -n $CARTO_SCHEMA $PGDBNAME -F t > $OSM_DUMP"
pg_dump -n $OSM_SCHEMA -n $CARTO_SCHEMA $PGDBNAME -F t > $OSM_DUMP

# check to see the size of the dump
size=`ls -ltr $OSM_DUMP | awk -F" " '{ print $5 }'`
if [[ $size -gt $OSM_TAR_MIN_SIZE ]]
then
  echo "gzip $OSM_DUMP"
  rm -f ${OSM_DUMP}.gz
  gzip $OSM_DUMP
  ./bin/db-dump-scp.sh $*
else
  echo "ERROR: ${OSM_DUMP} ($CARTO_SCHEMA and $OSM_SCHEMA SCHEMAs) dump is not big enough at $size (less than $OSM_TAR_MIN_SIZE bytes)"
fi

date
echo "END < < < < < "
