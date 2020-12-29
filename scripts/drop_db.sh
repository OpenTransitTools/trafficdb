##
## drop OTT database
##
psql=`which psql`
def_db=postgres
user=ott
db=ott
$psql -d $def_db -c "DROP DATABASE ${db};"
