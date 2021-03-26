##
## crete OTT spatial db for OTT
##
DIR=`dirname $0`
. $DIR/db_base.sh

for d in $db
do
  $psql -h $host -p $port -U $def_user -d $def_db -c "CREATE USER ${user};"
  $psql -h $host -p $port -U $def_user -d $def_db -c "CREATE DATABASE ${d} WITH OWNER ${user};"
  $psql -h $host -p $port -U $def_user -d ${d} -c "CREATE EXTENSION postgis;"
done
