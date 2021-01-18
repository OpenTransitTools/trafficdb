##
## crete OTT spatial db for OTT
##
psql=`which psql`
def_db=postgres
user=ott
db=ott

host=${DB_HOST:=localhost}
port=${DB_PORT:=5432}
