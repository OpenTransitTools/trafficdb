##
## crete OTT spatial db for OTT
##
psql=`which psql`
def_db=postgres
user=ott
db=ott

for d in $db
do
  $psql -d $def_db -c "CREATE USER ${user};"
  $psql -d $def_db -c "CREATE DATABASE ${d} WITH OWNER ${user};"
  $psql -d ${d} -c "CREATE EXTENSION postgis;"
done
