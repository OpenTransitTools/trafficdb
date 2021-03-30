export PSQL="docker run --rm --net=host postgis/postgis psql"
export iPSQL="docker run -i --rm --net=host postgis/postgis psql"  # for file redirects ala < dump.sql
export PG_DUMP="docker run --rm --net=host postgis/postgis pg_dump"

export GDAL="docker run --rm -v $PWD:$PWD --net=host osgeo/gdal:ubuntu-small-latest"

home=${HOME:-$PWD}
export OGR_2_OGR="docker run --rm -v ${home}:${home} --net=host osgeo/gdal:ubuntu-small-latest ogr2ogr"


# show that ogr can connect to PostGIS in a Docker
# (woke up this mornging, won't believe what I saw...100 million records...sending out an SOS.)
# https://stackoverflow.com/a/28036259
$GDAL ogrinfo PG:"host=127.0.0.1 port=5432 user='ott' dbname='ott'"

echo "ogr errors? is postgres running? don't forget to run 'docker-compose up &'"
