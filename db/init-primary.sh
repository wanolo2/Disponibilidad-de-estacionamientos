
#!/bin/bash
set -e

echo "Configurando usuario de replicacion..."

psql -v ON_ERROR_STOP=1 \
  --username "$POSTGRES_USER" \
  --dbname "$POSTGRES_DB" \
  -v replica_password="$REPLICATION_PASSWORD" <<'EOSQL'
CREATE ROLE replicator WITH REPLICATION LOGIN PASSWORD :'replica_password';
EOSQL

echo "Configurando acceso de la replica..."

echo "host replication replicator all scram-sha-256" >> "$PGDATA/pg_hba.conf"

echo "Configuracion de replicacion completada."
