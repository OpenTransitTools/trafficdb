##
## dump trafficdb schema
##
DIR=`dirname $0`
. $DIR/base.sh

echo "START > > > > > "
date

# dump the schema provided on the command line ('test' is the default)
rm -f $dump_file
dump_cmd="$pg_dump -h $host -p $port -U $user -n $schema $db -F t > $dump_file"
echo $dump_cmd
eval $dump_cmd

# check to see the size of the dump
size=`ls -ltr $dump_file | awk -F" " '{ print $5 }'`
if [[ $size -gt 500000 ]]
then
  mv ${dump_file}.gz /tmp/
  zip="gzip $dump_file"
  gzip $dump_file
else
  echo "ERROR: ${dump_file} not big enough at $size"
fi

date
echo "END < < < < < "
