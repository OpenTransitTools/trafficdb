##
## drop OTT database
##
DIR=`dirname $0`
. $DIR/db_base.sh

$psql -h $host -p $port -U $def_user -d $def_db -c "DROP DATABASE ${db};"
