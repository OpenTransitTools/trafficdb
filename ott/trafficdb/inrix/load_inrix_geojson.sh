DIR=`dirname $0`

name=${DB_NAME:=ott}
user=${DB_USER:=ott}
schema=${DB_SCHEMA:=trimet}
geojson_file=${1:-"$DIR/test/inrix.geojson"}

db_opts="-f 'PostgreSQL' PG:'dbname=$name user=$user active_schema=$schema' -lco GEOMETRY_NAME=geom"
table_name="-nln traffic_inrix_segments"

cmd="ogr2ogr $db_opts $table_name -overwrite $geojson_file"
echo $cmd
eval $cmd
