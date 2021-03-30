##
## crete OTT spatial db for OTT
##

# cmds ... might be overridded by Docker versions
psql=${PSQL:=psql}
ipsql=${iPSQL:=psql}
pg_dump=${PG_DUMP:=pg_dump}
pg_restore=${PG_RESTORE:=pg_restore}

# creds
def_db=postgres
user=ott
db=ott

def_user=${DB_USER:=postgres}
host=${DB_HOST:=localhost}
port=${DB_PORT:=5432}

schema=${1:-'test'}
dump_file="$schema.sql"
