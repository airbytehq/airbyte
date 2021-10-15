FROM yandex/clickhouse-server:latest

EXPOSE 8443
EXPOSE 9000
EXPOSE 8123
EXPOSE 9009

COPY clickhouse_certs.sh /docker-entrypoint-initdb.d/

