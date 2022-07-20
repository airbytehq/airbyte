FROM clickhouse/clickhouse-server:22.5

EXPOSE 8123
EXPOSE 8443

RUN apt-get update && apt-get install -y net-tools curl

COPY clickhouse_certs.sh /docker-entrypoint-initdb.d/
