export PSQL="docker run --rm --net=host postgis/postgis psql"
export PG_DUMP="docker run --rm --net=host postgis/postgis pg_dump"
export PG_RESTORE="docker run --rm --net=host postgis/postgis pg_restore"

export GDAL="docker run --rm -v $PWD:$PWD --net=host osgeo/gdal:ubuntu-small-latest"
export OGR_2_OGR="$PWD/scripts/ogr2ogr.sh"

# show that ogr can connect to PostGIS in a Docker
# (woke up this mornging, won't believe what I saw...100 million records...sending out an SOS.)
# https://stackoverflow.com/a/28036259
$GDAL ogrinfo PG:"host=127.0.0.1 port=5432 user='ott' dbname='ott'"

echo "ogr errors? is postgres running? don't forget to run 'docker-compose up &'"
