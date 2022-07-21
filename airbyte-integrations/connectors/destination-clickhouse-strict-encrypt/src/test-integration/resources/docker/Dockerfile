FROM clickhouse/clickhouse-server:22.5

EXPOSE 8123
EXPOSE 8443

COPY clickhouse_certs.sh /docker-entrypoint-initdb.d/
