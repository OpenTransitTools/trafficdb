##
## geojson -> postgis load script via ogr2ogr
## note: it should be generic to bring any geojson file in, but is written with INRIX in mind
##
DIR=`dirname $0`

name=${DB_NAME:=ott}
user=${DB_USER:=ott}
schema=${DB_SCHEMA:=trimet}
table_name=${TABLE_NAME:=traffic_inrix_segments}
rename_columns=${COL_RENAME:="xdsegid AS id, bearing AS direction"}
geojson_files=${*:-"$DIR/test/inrix.geojson"}

db_opts="-f 'PostgreSQL' PG:'dbname=$name user=$user active_schema=$schema' -lco GEOMETRY_NAME=geom"
table_cmd="-nln $table_name"
overwrite="-overwrite"

##
## will iterate over one or more geojson files, and import them all into a table name
## NOTES:
## explode multilinestrings into linestrings use switch -explodecollections.
##
for f in $geojson_files
do
  sql=""
  if [[ ! -z "$rename_columns" ]]; then
    sql="-sql 'SELECT $rename_columns FROM $(basename "${f%.*}")'"
  fi
  cmd="ogr2ogr $db_opts $table_cmd $overwrite $sql -skipfailures -explodecollections $f"
  echo $cmd
  eval $cmd
  overwrite=""
done

