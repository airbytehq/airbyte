FROM clickhouse/clickhouse-server:22.5

EXPOSE 8123
EXPOSE 8443
EXPOSE 9000
EXPOSE 9440

COPY clickhouse_certs.sh /docker-entrypoint-initdb.d/
