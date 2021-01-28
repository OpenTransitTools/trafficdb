##
## geojson -> postgis load script via ogr2ogr
##
##
## note: it should be generic to bring any geojson file in, but is written with INRIX in mind
## note: this script assumes a "LOCAL" PostGIS db running on port 5432
##
DIR=`dirname $0`

ogr2ogr=${OGR_2_OGR:=ogr2ogr}
psql=${PSQL:=psql}
host=${DB_HOST:=127.0.0.1}
port=${DB_PORT:=5432}
name=${DB_NAME:=ott}
user=${DB_USER:=ott}
schema=${DB_SCHEMA:=test}
table_name=${TABLE_NAME:=traffic_inrix_segments}
rename_columns=${COL_RENAME:="xdsegid=id, bearing=direction, miles=distance"}
geojson_files=${*:-"$DIR/inrix.geojson"}

db_opts="-f \"PostgreSQL\" PG:\"host=$host port=$port active_schema=$schema dbname='${name}' user='${user}' \" -lco GEOMETRY_NAME=geom"
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
  cmd="$ogr2ogr $db_opts $table_cmd $overwrite -skipfailures -explodecollections $f"
  echo $cmd
  eval $cmd
  overwrite=""
done

## rename columns
if [[ ! -z "$rename_columns" ]]; then
  frmto=(${rename_columns//,/ })
  for i in "${!frmto[@]}"
  do
    f=${frmto[i]%=*}
    t=${frmto[i]#*=}
    alter="$psql -h $host -p $port $name $user -c 'ALTER TABLE $schema.$table_name RENAME $f TO $t;'"
    echo $alter
    eval $alter
  done
fi

