##
## restore trafficdb schema from a dump file
##
DIR=`dirname $0`
. $DIR/base.sh

echo "START > > > > > "
date

# unzip any new dump file
if [ -f $dump_file.gz ]; then
  rm -f $dump_file
  gunzip $dump_file.gz
fi

# check to see the size of the dump.tar file exists and is sized
size=`ls -ltr $dump_file | awk -F" " '{ print $5 }'`
if [[ $size -gt 500000 ]]
then
  # drop the old traffic data schema
  echo "drop schema $schema"
  $psql -h $host -p $port -U $user -d $db -c "drop schema $schema cascade;"

  # load osm schema db from dump file
  echo "restore $dump_file dump"
  $pg_restore -h $host -p $port -U $user -d $db < $dump_file

  # vacuum analyze db
  echo "vacuum full analyze"
  $psql -h $host -p $port -U $user -d $db -c "vacuum full analyze;"
else
  echo "ERROR: ${dump_file} not big enough at $size"
fi

date
echo "END < < < < < < "

